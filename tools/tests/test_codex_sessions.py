import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import codex_sessions as sessions
from codex_runtime import NativeError

IDENT = '11111111-2222-3333-4444-555555555555'
OTHER = '11111111-2222-3333-4444-666666666666'


class FakeClient:
    def __init__(self, root):
        self.root = root
        self.calls = []
        (root/'.codex').mkdir(exist_ok=True)
        (root/'.codex/hooks.json').write_text(json.dumps({'hooks': {name: [{'hooks':[{'type':'command','command':'python3 tools/hooks/codex_dispatch.py'}]}] for name in ('SessionStart','PreToolUse','PostToolUse','SubagentStart')}}))
        self.hooks = [{'eventName': event, 'enabled': True, 'trustStatus': 'trusted',
                       'command': 'python3 tools/hooks/codex_dispatch.py'} for event in
                      ('sessionStart','preToolUse','postToolUse','subagentStart')]
        self.fail_bootstrap = False
        self.closed = 0
    async def call(self, method, params):
        self.calls.append((method, params))
        if method == 'hooks/list':
            assert params == {'cwds': [str(self.root)]}
            return {'data': [{'cwd': str(self.root), 'hooks': self.hooks, 'errors': [], 'warnings': []}]}
        if method in ('thread/start','thread/resume'):
            if method == 'thread/resume':
                assert set(params) == {'threadId', 'excludeTurns'} and params['excludeTurns'] is True
            await asyncio.sleep(.01)
            return {'thread': {'id': IDENT}, 'cwd': str(self.root)}
        if method == 'thread/inject_items':
            assert params['threadId'] == IDENT
            [item] = params['items']
            assert item['type'] == 'message' and item['role'] == 'user'
            [content] = item['content']
            assert content['type'] == 'input_text' and isinstance(content['text'], str)
            assert json.loads((self.root/'.codex/framework/bootstrap.json').read_text()) == {'thread': IDENT,'accepted':False,'bound':False}
            assert not (self.root/'.codex-session-id').exists() or (self.root/'.codex-session-id').read_text().strip() != IDENT
            return {}
        if method == 'turn/start':
            assert params['input'][0]['type'] == 'text'
            assert (self.root/'.codex-session-id').read_text().strip() == params['threadId']
            if self.fail_bootstrap:
                raise NativeError('bootstrap transport failed')
            return {'turn': {'id': 'turn'}}
        raise AssertionError(method)
    async def close(self):
        self.closed += 1


class SessionTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.client = FakeClient(self.root)

    async def start(self, mode='auto'):
        return await sessions.session(self.client, self.root, mode, 600000, 550000)

    async def test_new_binds_before_bootstrap_and_resume_preserves_permissions(self):
        self.assertEqual(await self.start(), IDENT)
        self.assertEqual((self.root/'.codex-session-id').read_text(), IDENT+'\n')
        start = next(params for method,params in self.client.calls if method == 'thread/start')
        self.assertEqual(start['cwd'], str(self.root))
        self.assertEqual(start['runtimeWorkspaceRoots'], [str(self.root)])
        self.assertEqual(start['approvalPolicy'], 'on-request')
        self.assertEqual(start['approvalsReviewer'], 'auto_review')
        self.assertEqual(start['permissions'], ':workspace')
        self.assertNotIn('sandbox', start)
        self.assertIs(start['ephemeral'], False)
        self.assertEqual(start['config'], {'model_context_window':600000,'model_auto_compact_token_limit':550000})
        self.assertEqual([m for m,_ in self.client.calls], ['hooks/list','thread/start','thread/inject_items','turn/start'])
        self.assertIn('python3 tools/resume.py', self.client.calls[-1][1]['input'][0]['text'])
        self.assertNotIn('remember-codex', self.client.calls[-1][1]['input'][0]['text'])
        await self.start('resume')
        self.assertEqual(self.client.calls[-1], ('thread/resume', {'threadId': IDENT, 'excludeTurns': True}))
        self.assertEqual(sum(method=='turn/start' for method,_ in self.client.calls), 1)

    async def test_created_wrong_cwd_or_invalid_id_never_binds_or_injects(self):
        original=self.client.call
        for change in ({'cwd':'/different'},{'thread':{'id':'invalid'}}):
            async def altered(method,params):
                result=await original(method,params)
                return {**result,**change} if method=='thread/start' else result
            with patch.object(self.client,'call',altered),self.assertRaises((NativeError,ValueError)):
                await self.start()
            self.assertFalse((self.root/'.codex-session-id').exists())
            self.assertFalse((self.root/'.codex/framework/bootstrap.json').exists())
        self.assertFalse(any(m=='thread/inject_items' for m,_ in self.client.calls))

    async def test_bootstrap_failure_keeps_exact_identity_for_retry(self):
        self.client.fail_bootstrap = True
        with self.assertRaisesRegex(NativeError, 'bootstrap'):
            await self.start()
        self.assertEqual((self.root/'.codex-session-id').read_text().strip(), IDENT)
        self.client.fail_bootstrap = False
        await self.start()
        self.assertEqual(sum(m=='thread/start' for m,_ in self.client.calls), 1)
        self.assertEqual(sum(m=='thread/resume' for m,_ in self.client.calls), 1)
        self.assertEqual(sum(m=='turn/start' for m,_ in self.client.calls), 2)
        self.assertEqual(json.loads((self.root/'.codex/framework/bootstrap.json').read_text()), {'thread':IDENT,'accepted':True})

    async def test_missing_invalid_and_wrong_worktree_bindings_fail(self):
        with self.assertRaises(NativeError):
            await self.start('resume')
        (self.root/'.codex-session-id').write_text('invalid')
        with self.assertRaises(ValueError):
            await self.start()
        (self.root/'.codex-session-id').write_text(OTHER)
        with self.assertRaisesRegex(NativeError, 'different worktree'):
            await self.start()
        self.assertFalse(any(m=='turn/start' for m,_ in self.client.calls))

    async def test_untrusted_disabled_missing_duplicate_hooks_block_start(self):
        baseline = [dict(h) for h in self.client.hooks]
        cases = [baseline[:-1], baseline+[baseline[0]],
                 [{**h,'trustStatus':'untrusted'} for h in baseline],
                 [{**h,'enabled':False} for h in baseline],
                 [{**h,'command':'echo tools/hooks/codex_dispatch.py'} for h in baseline]]
        for hooks in cases:
            self.client.hooks = hooks
            with self.assertRaisesRegex(NativeError, 'trust review'):
                await self.start()
        self.assertFalse((self.root/'.codex-session-id').exists())
        self.assertTrue(all(m=='hooks/list' for m,_ in self.client.calls))

    async def test_pending_materialized_thread_is_recovered_without_a_new_thread(self):
        pending=self.root/'.codex/framework/bootstrap.json';pending.parent.mkdir(parents=True)
        pending.write_text(json.dumps({'thread':IDENT,'accepted':False,'bound':False}))
        await self.start()
        self.assertEqual([m for m,_ in self.client.calls],['hooks/list','thread/resume','turn/start'])
        self.assertEqual((self.root/'.codex-session-id').read_text().strip(),IDENT)

    async def test_incomplete_discovery_and_added_event_are_refused(self):
        response={'data':[{'cwd':str(self.root),'hooks':self.client.hooks,'errors':[],'warnings':[]}]}
        for field in ('errors','warnings'):
            response['data'][0][field]=['incomplete']
            with patch.object(self.client,'call',AsyncMock(return_value=response)), self.assertRaises(NativeError):
                await self.start()
            response['data'][0][field]=[]
        response['data']=[]
        with patch.object(self.client,'call',AsyncMock(return_value=response)), self.assertRaises(NativeError):
            await self.start()
        self.client.hooks.append({'eventName':'other','command':None})
        await sessions.trusted(self.client,self.root)
        definitions=self.root/'.codex/hooks.json'
        data=json.loads(definitions.read_text());data['hooks']['Stop']=[];definitions.write_text(json.dumps(data))
        with self.assertRaises(NativeError):await self.start()

    async def test_old_external_binding_needs_no_bootstrap_file(self):
        (self.root/'.codex-session-id').write_text(IDENT)
        await self.start()
        self.assertEqual([m for m,_ in self.client.calls],['hooks/list','thread/resume'])

    async def test_wrong_working_directory_never_gets_a_turn(self):
        real=self.client.call
        async def wrong(method,params):
            value=await real(method,params)
            if method=='thread/resume':value['cwd']=str(self.root/'other')
            return value
        with patch.object(self.client,'call',side_effect=wrong):
            (self.root/'.codex-session-id').write_text(IDENT)
            with self.assertRaises(NativeError):await self.start()
            (self.root/'.codex-session-id').unlink()
            pending=self.root/'.codex/framework/bootstrap.json';pending.parent.mkdir(parents=True)
            pending.write_text(json.dumps({'thread':IDENT,'accepted':False,'bound':False}))
            with self.assertRaises(NativeError):await self.start()
            self.assertFalse((self.root/'.codex-session-id').exists())

    async def test_explicit_new_ignores_unbound_pending_identity(self):
        pending=self.root/'.codex/framework/bootstrap.json';pending.parent.mkdir(parents=True)
        pending.write_text(json.dumps({'thread':OTHER,'accepted':False,'bound':False}))
        await self.start('new')
        self.assertFalse(any(m=='thread/resume' for m,_ in self.client.calls))

    async def test_explicit_new_replaces_binding_after_creation(self):
        (self.root/'.codex-session-id').write_text(OTHER)
        self.assertEqual(await self.start('new'), IDENT)
        self.assertFalse(any(m=='thread/resume' for m,_ in self.client.calls))


class LauncherTest(unittest.TestCase):
    def test_concurrent_launchers_share_binding_and_register_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);source=root/'skills/example/SKILL.md'
            source.parent.mkdir(parents=True);source.write_text('source')
            client = FakeClient(root)
            args=argparse.Namespace(worktree='worker',base='main',mode='auto',context=600000,compact=550000)
            with patch.object(sessions,'worktree',return_value=root) as choose, \
                 patch.object(sessions.Client,'connect',AsyncMock(return_value=client)):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    results=list(pool.map(lambda _:asyncio.run(sessions.launch(args)),range(2)))
            self.assertEqual(choose.call_args.args,(sessions.ROOT,'worker','main'))
            self.assertEqual(results,[(root,IDENT),(root,IDENT)])
            startup=next(p for m,p in client.calls if m=='thread/start')
            self.assertEqual(startup['config'],{'model_context_window':600000,'model_auto_compact_token_limit':550000})
            self.assertEqual(sum(m=='thread/start' for m,_ in client.calls),1)
            self.assertEqual(client.closed,2)
            self.assertEqual((root/'.agents/skills/example').resolve(),source.parent)

    def test_real_git_worktree_is_persistent_and_tracks_local_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def git(*args):
                return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True,text=True)
            git('init','-b','main');git('config','user.email','test@example.invalid');git('config','user.name','Test')
            (root/'source').write_text('source');git('add','source');git('commit','-m','fixture')
            target=sessions.worktree(root)
            self.assertEqual(target,root/'.codex/worktrees/codex-main')
            self.assertEqual(sessions.git(target,'rev-parse','--abbrev-ref','@{upstream}'),'main')
            (target/'owned').write_text('retained')
            self.assertEqual(sessions.worktree(root),target)
            self.assertEqual((target/'owned').read_text(),'retained')
            self.assertEqual(sessions.worktree(target),target)
            with self.assertRaises(ValueError):sessions.worktree(target,base='other')
            # An existing checkout may track a remote, not a local integration branch.
            git('remote','add','private','https://example.invalid/repo.git')
            git('update-ref','refs/remotes/private/softeng','HEAD')
            sessions.git(target,'branch','--set-upstream-to=private/softeng')
            self.assertEqual(sessions.worktree(target),target)
            self.assertEqual(sessions.worktree(target,base='private/softeng'),target)
            with self.assertRaises(ValueError):sessions.worktree(target,base='main')
            self.assertEqual(sessions.git(target,'rev-parse','--symbolic-full-name','@{upstream}'),
                             'refs/remotes/private/softeng')
            self.assertEqual((target/'owned').read_text(),'retained')
            git('branch','feature/test')
            self.assertEqual(sessions.worktree(root,base='feature/test').name,'codex-feature-test')
            git('branch','codex-collision')
            with self.assertRaises(subprocess.CalledProcessError):sessions.worktree(root,'codex-collision')
            for name in ('../escape','bad/name','-bad','.hidden'):
                if not name:
                    continue
                with self.assertRaises(ValueError):sessions.worktree(root,name)

    def test_launch_forwards_explicit_new_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=FakeClient(root);(root/'.codex-session-id').write_text(OTHER)
            args=argparse.Namespace(worktree=None,base=None,mode='new',context=600000,compact=550000)
            with patch.object(sessions,'worktree',return_value=root),patch.object(sessions.Client,'connect',AsyncMock(return_value=client)):
                self.assertEqual(asyncio.run(sessions.launch(args)),(root,IDENT))
            self.assertFalse(any(m=='thread/resume' for m,_ in client.calls))

    def test_stalled_startup_times_out_and_releases_connection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=FakeClient(root)
            args=argparse.Namespace(worktree=None,base=None,mode='auto',context=600000,compact=550000)
            real_wait=asyncio.wait_for
            async def hang(*args,**kwargs):await asyncio.sleep(10)
            async def accelerated(awaitable,timeout):
                return await real_wait(awaitable,None if timeout is None else timeout/1000)
            async def check():
                start=time.monotonic()
                with self.assertRaises(asyncio.TimeoutError):
                    await real_wait(sessions.launch(args),.15)
                self.assertLess(time.monotonic()-start,.1)
            with patch.object(sessions,'worktree',return_value=root),patch.object(sessions.Client,'connect',AsyncMock(return_value=client)), \
                 patch.object(sessions,'session',hang),patch.object(asyncio,'wait_for',accelerated):
                asyncio.run(check())
            self.assertEqual(client.closed,1)

    def test_binding_replace_is_local_atomic_and_preserves_prior_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);binding=root/'.codex-session-id';binding.write_text(OTHER)
            replace=os.replace
            def local(source,destination):
                self.assertEqual(Path(source).parent,root)
                return replace(source,destination)
            with patch.object(os,'replace',side_effect=local):sessions.bind(root,IDENT)
            self.assertEqual(binding.read_text(),IDENT+'\n')
            with patch.object(os,'replace',side_effect=OSError('write failed')),self.assertRaises(OSError):
                sessions.bind(root,OTHER)
            self.assertEqual(binding.read_text(),IDENT+'\n')
            self.assertEqual(list(root.iterdir()),[binding])

    def test_cli_modes_required_budgets_worker_refusal_and_errors(self):
        common=['launcher','--context','600000','--compact','550000','--detached']
        for mode,expected in [([], 'auto'),(['--new'],'new')]:
            with patch.dict(os.environ,{'CODEX_THREAD_ID':''}), patch.object(sys,'argv',common+mode+['--worktree','worker','--base','base']), \
                 patch.object(sessions,'launch',AsyncMock(return_value=(Path('/tmp'),IDENT))) as launch,redirect_stdout(io.StringIO()):
                self.assertEqual(sessions.main(),0)
                args=launch.call_args.args[0]
                self.assertEqual((args.mode,args.worktree,args.base,args.context,args.compact),(expected,'worker','base',600000,550000))
        with patch.dict(os.environ,{'CODEX_THREAD_ID':''}),patch.object(sys,'argv',common), \
             patch.object(sessions,'launch',AsyncMock(side_effect=NativeError('actual failure'))),redirect_stderr(io.StringIO()) as err:
            self.assertEqual(sessions.main(),1);self.assertIn('actual failure',err.getvalue())
        for argv,worker in [(['launcher','--context','600000'],''),(['launcher','--compact','550000'],''),(common,'child')]:
            with patch.dict(os.environ,{'CODEX_THREAD_ID':worker}),patch.object(sys,'argv',argv),redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                sessions.main()

    def test_cli_detached_and_attach_never_override_resume_permissions(self):
        for detached in (True,False):
            args=['launcher','--context','600000','--compact','550000','--resume']
            if detached:args.append('--detached')
            with patch.dict(os.environ,{'CODEX_THREAD_ID':''}), patch.object(sys,'argv',args), patch.object(sessions,'launch',AsyncMock(return_value=(Path('/tmp'),IDENT))) as launch, \
                 patch.object(os,'chdir') as chdir, patch.object(os,'execvp') as execute, redirect_stdout(io.StringIO()) as out:
                self.assertEqual(sessions.main(),0)
                self.assertEqual(launch.call_args.args[0].mode,'resume')
                if detached:
                    execute.assert_not_called();self.assertIn('Persistent session',out.getvalue())
                else:
                    chdir.assert_called_once_with(Path('/tmp'))
                    execute.assert_called_once_with('codex',['codex','resume',IDENT,'--remote','unix://'])


if __name__=='__main__':
    unittest.main()
