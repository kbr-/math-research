import asyncio
from collections import deque
import json
import argparse
import io
import subprocess
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from codex_runtime import Client, NativeError, isolated_config, verify_isolation
import codex_reviewer as reviewer


class Socket:
    def __init__(self, messages):
        self.messages = deque(messages)
        self.sent = []
    async def send(self, data):
        self.sent.append(json.loads(data))
    async def recv(self):
        if self.messages:
            return json.dumps(self.messages.popleft())
        await asyncio.sleep(10)
    async def close(self):
        self.closed = True


class NativeRuntimeTest(unittest.IsolatedAsyncioTestCase):
    async def test_rpc_keeps_events_and_declines_approval(self):
        sock = Socket([{'method': 'notice', 'params': {'x': 1}},
                       {'id': 92, 'method': 'approval', 'params': {}},
                       {'id': 1, 'result': {'value': 3}}])
        client = Client(sock)
        self.assertEqual(await client.call('query', {'a': 2}), {'value': 3})
        self.assertEqual(sock.sent[0], {'id': 1, 'method': 'query', 'params': {'a': 2}})
        self.assertEqual(sock.sent[1]['id'], 92)
        self.assertEqual(sock.sent[1]['error']['code'], -32000)
        self.assertIsInstance(sock.sent[1]['error']['message'], str)
        self.assertEqual((await client.event())['method'], 'notice')
        await client.close();self.assertTrue(sock.closed)

    async def test_connect_handshake_and_failure_cleanup(self):
        process = Mock(returncode=0)
        process.communicate = AsyncMock(return_value=(b'{"socketPath":"/tmp/owned.socket"}', b''))
        process.wait = AsyncMock()
        sock = Socket([{'id': 1, 'result': {}}])
        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=process)) as launch, \
             patch('websockets.unix_connect', AsyncMock(return_value=sock)) as connect:
            client = await Client.connect()
            launch.assert_awaited_once_with('codex', 'app-server', 'daemon', 'version',
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            connect.assert_awaited_once_with('/tmp/owned.socket', uri='ws://localhost',
                                            open_timeout=2, close_timeout=.1, max_size=16*1024*1024)
            self.assertEqual(sock.sent[0]['method'], 'initialize')
            self.assertEqual(sock.sent[0]['params']['capabilities'], {'experimentalApi': True})
            self.assertEqual(set(sock.sent[0]['params']['clientInfo']), {'name', 'version'})
            self.assertEqual(sock.sent[1], {'method': 'initialized', 'params': {}})
            await client.close()
            process.returncode = 2
            process.communicate.return_value = (b'', b'daemon unavailable\xff')
            with self.assertRaisesRegex(NativeError, 'daemon unavailable'):
                await Client.connect()
            self.assertEqual(connect.await_count, 1)
            process.returncode = None
            process.communicate.side_effect = asyncio.TimeoutError()
            with self.assertRaises(asyncio.TimeoutError):
                await Client.connect()
            process.kill.assert_called_once();process.wait.assert_awaited_once()

    async def test_connection_timeout_covers_version_command(self):
        process = Mock(returncode=None)
        async def hang():
            await asyncio.sleep(10)
        process.communicate = hang;process.wait = AsyncMock()
        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=process)):
            start = time.monotonic()
            with self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(Client.connect(), 2.4)
            self.assertLess(time.monotonic()-start, 2.3)
            process.kill.assert_called_once()

    async def test_connection_timeout_covers_handshake(self):
        process = Mock(returncode=0)
        process.communicate = AsyncMock(return_value=(b'{"socketPath":"/tmp/owned.socket"}', b''))
        sock = Socket([])
        with patch('asyncio.create_subprocess_exec', AsyncMock(return_value=process)), \
             patch('websockets.unix_connect', AsyncMock(return_value=sock)):
            start = time.monotonic()
            with self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(Client.connect(), 2.4)
            self.assertLess(time.monotonic()-start, 2.3)
            self.assertTrue(sock.closed)

    async def test_reviewer_timeout_releases_lock_and_connection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);args = argparse.Namespace(handle='owned', brief=None, close=True, timeout=.01, model=None)
            async def hang(*args, **kwargs):
                await asyncio.sleep(10)
            client = AsyncMock()
            with patch.object(Client, 'connect', AsyncMock(return_value=client)), \
                 patch.object(reviewer, 'review', hang):
                for attempt in range(2):
                    start = time.monotonic()
                    with self.assertRaises(asyncio.TimeoutError):
                        await asyncio.wait_for(reviewer.run(args, root), .1)
                    self.assertLess(time.monotonic()-start, .08)
                self.assertEqual(client.close.await_count, 2)
            with patch.object(Client, 'connect', hang):
                start = time.monotonic()
                with self.assertRaises(asyncio.TimeoutError):
                    await asyncio.wait_for(reviewer.run(args, root), .1)
                self.assertLess(time.monotonic()-start, .08)

    async def test_run_locks_handle_reads_brief_and_closes_connection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);brief = root/'brief';brief.write_text('supplied only')
            args = argparse.Namespace(handle='Owned', brief=brief, close=False, timeout=2, model='test-model')
            client = AsyncMock()
            with patch.object(Client, 'connect', AsyncMock(return_value=client)), \
                 patch.object(reviewer, 'review', AsyncMock(return_value='pass')) as perform:
                self.assertEqual(await reviewer.run(args, root), 'pass')
                call = perform.call_args.args
                self.assertEqual(call[0:2], (client, root))
                self.assertEqual(call[3:], ('supplied only', False, 'test-model'))
                self.assertEqual(call[2].parent, root/'.codex/framework/reviewers')
                client.close.assert_awaited_once()
                perform.side_effect = NativeError('failure')
                with self.assertRaises(NativeError):
                    await reviewer.run(args, root)
                self.assertEqual(client.close.await_count, 2)
                args.close = True;args.brief = None;perform.side_effect = None
                await reviewer.run(args, root)
                self.assertEqual(perform.call_args.args[3:5], ('', True))
                args.handle = '../other'
                with self.assertRaises(ValueError):
                    await reviewer.run(args, root)

    async def test_multiple_calls_and_failed_turns(self):
        sock = Socket([{'id': 1, 'result': 'first'}, {'id': 99, 'result': 'unrelated'},
                       {'id': 2, 'result': 'second'}])
        client = Client(sock)
        self.assertEqual(await client.call('first', {}), 'first')
        self.assertEqual(await client.call('second', {}), 'second')
        self.assertEqual([p['id'] for p in sock.sent], [1, 2])
        self.assertEqual(list(client.events), [])
        sock = Socket([{'id': 1, 'result': {'turn': {'id': 't'}}}, {'method': 'notice'},
                       {'method': 'turn/completed', 'params': {'threadId': 'owned',
                        'turn': {'id': 't', 'status': 'failed'}}}, {'id': 2, 'result': {}}])
        with self.assertRaisesRegex(NativeError, 'failed'):
            await Client(sock).turn('owned', 'brief', 'medium')

    async def test_errors_are_not_success(self):
        client = Client(Socket([{'id': 1, 'error': {'code': -1, 'message': 'denied'}}]))
        with self.assertRaisesRegex(NativeError, 'denied'):
            await client.call('query', {})

    async def test_turn_scopes_output_and_completion_and_interrupts_timeout(self):
        def completed(thread, turn, text):
            return {'method': 'item/completed', 'params': {'threadId': thread, 'turnId': turn,
                    'item': {'type': 'agentMessage', 'text': text}}}
        sock = Socket([completed('owned', 'turn', 'before reply'),
                       {'id': 1, 'result': {'turn': {'id': 'turn'}}},
                       completed('other', 'turn', 'not ours'),
                       completed('owned', 'old', 'old reply'),
                       completed('owned', 'turn', 'answer'),
                       {'method': 'turn/completed', 'params': {'threadId': 'owned',
                        'turn': {'id': 'turn', 'status': 'completed'}}}])
        self.assertEqual(await Client(sock).turn('owned', 'brief', 'medium', {'type': 'object'}), 'before reply\nanswer')
        self.assertEqual(sock.sent[0], {'id': 1, 'method': 'turn/start', 'params': {
            'threadId': 'owned', 'input': [{'type': 'text', 'text': 'brief'}], 'effort': 'medium',
            'outputSchema': {'type': 'object'}}})
        sock = Socket([{'id': 1, 'result': {'turn': {'id': 'owned-turn'}}}])
        start = time.monotonic()
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(Client(sock).turn('owned', 'brief', 'medium'), .01)
        self.assertLess(time.monotonic()-start, .5)
        self.assertNotIn('outputSchema', sock.sent[0]['params'])
        self.assertEqual(sock.sent[-1]['method'], 'turn/interrupt')
        self.assertEqual(sock.sent[-1]['params'], {'threadId': 'owned', 'turnId': 'owned-turn'})

    def test_effective_policy_is_checked_not_assumed(self):
        good = {'reasoningEffort': 'medium', 'approvalPolicy': 'never',
                'sandbox': {'type': 'readOnly', 'networkAccess': False}}
        verify_isolation(good, 'medium')
        for field, value in [('reasoningEffort', 'high'), ('approvalPolicy', 'on-request'),
                             ('sandbox', {'type': 'workspaceWrite', 'networkAccess': False}),
                             ('sandbox', {'type': 'readOnly', 'networkAccess': True})]:
            with self.subTest(field=field, value=value), self.assertRaises(NativeError):
                verify_isolation({**good, field: value}, 'medium')
        config = isolated_config('low', tools=False)
        for name in ('hooks','apps','plugins','browser_use','computer_use','shell_tool','unified_exec'):
            self.assertIs(config['features.'+name], False)
        self.assertIs(config['agents.enabled'], False)
        self.assertEqual(config['web_search'], 'disabled')
        self.assertEqual(config['project_doc_max_bytes'], 0)
        self.assertNotIn('features.shell_tool', isolated_config('medium'))
        with self.assertRaises(NativeError):
            verify_isolation({'reasoningEffort': 'medium', 'approvalPolicy': 'never'}, 'medium')

    async def test_isolation_disables_configured_mcp_without_copying_secrets(self):
        client=Client(None)
        client.call=AsyncMock(return_value={'config':{'mcp_servers':{'docs':{'command':'private command','env':{'KEY':'secret'}}}}})
        result=await client.isolation_config('/fixture','low',tools=False)
        client.call.assert_awaited_once_with('config/read',{'cwd':'/fixture','includeLayers':False})
        self.assertEqual(result['mcp_servers'],{'docs':{'enabled':False}})
        self.assertEqual(result['model_reasoning_effort'],'low')
        self.assertFalse(result['features.shell_tool'])
        self.assertNotIn('secret',str(result));self.assertNotIn('private command',str(result))
        client.call.return_value={'config':{'mcp_servers':[]}}
        default=await client.isolation_config('/fixture','medium')
        self.assertEqual(default['mcp_servers'],{})
        self.assertEqual(default['model_reasoning_effort'],'medium')
        self.assertNotIn('features.shell_tool',default)
        client.call.return_value={'config':{'mcp_servers':['bad']}}
        with self.assertRaises(NativeError):await client.isolation_config('/fixture','medium')

    async def test_reviewer_fresh_root_same_handle_and_own_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);source = root/'.claude/agents/medium-reviewer.md'
            source.parent.mkdir(parents=True);source.write_text('---\nname: role\n---\nCanonical brief')
            binding = root/'.codex-session-id';binding.write_text('parent')
            state = root/'review.json'
            response = {'cwd': str(root), 'thread': {'id': '11111111-2222-3333-4444-555555555555'}, 'reasoningEffort': 'medium',
                        'approvalPolicy': 'never', 'sandbox': {'type': 'readOnly', 'networkAccess': False}}
            client = AsyncMock();client.call.return_value = response;client.turn.return_value = 'pass'
            client.isolation_config.return_value = isolated_config('medium')
            self.assertEqual(await reviewer.review(client, root, state, 'supplied excerpts', model='selected'), 'pass')
            method, params = client.call.call_args_list[0].args
            self.assertEqual(method, 'thread/start')
            self.assertEqual(params['baseInstructions'], 'Canonical brief')
            self.assertEqual(params['cwd'], str(root))
            self.assertIs(params['ephemeral'], False)
            self.assertIn('Edit no files', params['developerInstructions'])
            self.assertEqual(params['model'], 'selected')
            self.assertEqual(params['permissions'], ':read-only')
            self.assertNotIn('sandbox', params)
            self.assertEqual(params['approvalPolicy'], 'never')
            self.assertEqual(params['config']['model_reasoning_effort'], 'medium')
            client.turn.assert_awaited_once_with('11111111-2222-3333-4444-555555555555', 'supplied excerpts', 'medium')
            self.assertEqual(json.loads(state.read_text())['thread'], '11111111-2222-3333-4444-555555555555')
            await reviewer.review(client, root, state, 'concrete correction')
            self.assertEqual(client.call.call_args.args, ('thread/resume', {'threadId': '11111111-2222-3333-4444-555555555555', 'excludeTurns': True,
                'approvalPolicy':'never','permissions':':read-only','config':isolated_config('medium')}))
            await reviewer.review(client, root, state, '', close=True)
            self.assertEqual(client.call.call_args.args, ('thread/archive', {'threadId': '11111111-2222-3333-4444-555555555555'}))
            self.assertFalse(state.exists());self.assertEqual(binding.read_text(), 'parent')

    async def test_misconfigured_reviewer_never_receives_brief_and_remains_owned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);state = root/'review.json'
            state.write_text(json.dumps({'root': str(root), 'thread': '11111111-2222-3333-4444-555555555555'}))
            client = AsyncMock();client.call.return_value = {'cwd': str(root), 'thread': {'id': '11111111-2222-3333-4444-555555555555'},
                'reasoningEffort': 'high', 'approvalPolicy': 'never',
                'sandbox': {'type': 'readOnly', 'networkAccess': False}}
            with self.assertRaises(NativeError):
                await reviewer.review(client, root, state, 'secret brief')
            client.turn.assert_not_awaited();self.assertTrue(state.exists())

    async def test_reviewer_rejects_wrong_identity_before_binding_or_brief(self):
        ident='11111111-2222-3333-4444-555555555555'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'.claude/agents/medium-reviewer.md';source.parent.mkdir(parents=True)
            source.write_text('---\nname: role\n---\nReview only the brief')
            state=root/'review.json';client=AsyncMock();client.isolation_config.return_value=isolated_config('medium')
            for response in ({'thread':{'id':'invalid'},'cwd':str(root)},
                             {'thread':{'id':ident},'cwd':'/other'}):
                client.call.return_value=response
                with self.assertRaises((ValueError,NativeError)):
                    await reviewer.review(client,root,state,'secret')
                self.assertFalse(state.exists());client.turn.assert_not_awaited()
            state.write_text(json.dumps({'thread':ident,'root':str(root)}))
            client.call.return_value={'thread':{'id':'11111111-2222-3333-4444-666666666666'},'cwd':str(root)}
            with self.assertRaises(NativeError):await reviewer.review(client,root,state,'secret')
            client.turn.assert_not_awaited()
            self.assertEqual(json.loads(state.read_text())['thread'],ident)


class ReviewerCLITest(unittest.TestCase):
    def test_cli_success_error_and_arguments(self):
        for options, expected in [(['--brief', 'brief.txt'], False), (['--close'], True)]:
            with patch.object(sys, 'argv', ['reviewer', '--handle', 'owned', *options]), \
                 patch.object(reviewer, 'run', AsyncMock(return_value='pass')) as run, \
                 redirect_stdout(io.StringIO()) as output:
                self.assertEqual(reviewer.main(), 0)
                args = run.call_args.args[0]
                self.assertEqual(args.handle, 'owned');self.assertEqual(args.close, expected)
                self.assertEqual(args.timeout, 120);self.assertIsNone(args.model)
                self.assertEqual(args.brief, None if expected else Path('brief.txt'))
                self.assertIn('pass', output.getvalue())
        with patch.object(sys, 'argv', ['reviewer', '--handle', 'owned', '--close', '--timeout', '3.5', '--model', 'selected']), patch.object(reviewer, 'run', AsyncMock(return_value='pass')) as run, redirect_stdout(io.StringIO()):
            reviewer.main()
            self.assertEqual(run.call_args.args[0].timeout, 3.5)
            self.assertEqual(run.call_args.args[0].model, 'selected')
        with patch.object(sys, 'argv', ['reviewer', '--handle', 'owned', '--close']), \
             patch.object(reviewer, 'run', AsyncMock(side_effect=NativeError('actual failure'))), \
             redirect_stderr(io.StringIO()) as output:
            self.assertEqual(reviewer.main(), 1)
            self.assertIn('actual failure', output.getvalue())
        for options in [[], ['--handle', 'x'], ['--close'], ['--handle', 'x', '--brief', 'x', '--close']]:
            with patch.object(sys, 'argv', ['reviewer', *options]), redirect_stderr(io.StringIO()), \
                 self.assertRaises(SystemExit) as error:
                reviewer.main()
            self.assertEqual(error.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
