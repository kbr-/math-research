import argparse
from contextlib import redirect_stdout
import fcntl
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import watch_run as watch
from codex_state import atomic_json

RUN='a'*32


class NativeMonitorTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.logs=self.root/'research/logs';self.logs.mkdir(parents=True)
        self.path=watch.native_path(self.root,RUN)
        self.env=patch.dict(os.environ,{'CODEX_THREAD_ID':'owner','CLAUDE_CODE_SESSION_ID':''});self.env.start();self.addCleanup(self.env.stop)

    def test_readiness_requires_live_lock_owner_session_and_no_cancel(self):
        atomic_json(self.path,{'owner':'owner','session':'fixture'})
        with self.path.with_suffix('.lock').open('a') as lock:
            self.assertFalse(watch.native_ready(self.root,'fixture',RUN,'owner'))
            fcntl.flock(lock,fcntl.LOCK_EX)
            self.assertTrue(watch.native_ready(self.root,'fixture',RUN,'owner'))
            self.assertFalse(watch.native_ready(self.root,'other',RUN,'owner'))
            self.assertFalse(watch.native_ready(self.root,'fixture',RUN,'other'))
            self.path.with_suffix('.cancel').touch()
            self.assertFalse(watch.native_ready(self.root,'fixture',RUN,'owner'))
        self.path.with_suffix('.cancel').unlink()
        self.assertFalse(watch.native_ready(self.root,'fixture',RUN,'owner'))
        self.path.write_text('broken')
        self.assertFalse(watch.native_ready(self.root,'fixture',RUN,'owner'))

    def test_arm_acknowledges_before_run_and_handles_fast_completion(self):
        out=io.StringIO();journal=self.logs/'fixture.jsonl'
        def release(_):
            run=json.loads(out.getvalue().split('WATCH_READY ')[1].splitlines()[0])['run_id']
            self.assertTrue(watch.native_ready(self.root,'fixture',run,'owner'))
            journal.write_text(json.dumps({'event':'run_start','id':run,'unix_s':1,'output':'logs/test'})+'\n'
                               +json.dumps({'event':'run_end','id':run,'unix_s':2,'returncode':0})+'\n')
        with patch.object(watch,'ROOT',self.root),patch.object(watch,'LOGS',self.logs), \
             patch.object(watch.time,'sleep',release),redirect_stdout(out):
            self.assertEqual(watch.arm('fixture',poll=0),0)
        run=json.loads(out.getvalue().split('WATCH_READY ')[1].splitlines()[0])['run_id']
        self.assertIn('ended after 1 s: exit 0',out.getvalue())
        self.assertFalse(watch.native_ready(self.root,'fixture',run,'owner'))

    def test_arm_failure_and_cancel_never_leave_readiness(self):
        out=io.StringIO()
        with patch.object(watch,'ROOT',self.root),patch.object(watch,'LOGS',self.logs),redirect_stdout(out):
            self.assertEqual(watch.arm('fixture',wait=0),1)
            for at in (0,301):
                with self.assertRaises(ValueError):watch.arm('fixture',at=at)
        run=json.loads(out.getvalue().split('WATCH_READY ')[1].splitlines()[0])['run_id']
        self.assertFalse(watch.native_ready(self.root,'fixture',run,'owner'))
        atomic_json(self.path,{'owner':'owner','session':'fixture'})
        (self.logs/'fixture.jsonl').write_text(json.dumps({'event':'run_start','id':RUN,'systemd_unit':'mathcompute-job-'+RUN+'.service'})+'\n')
        with patch.object(watch,'ROOT',self.root),patch.object(watch,'LOGS',self.logs), \
             patch.object(watch.subprocess,'run') as stop,redirect_stdout(io.StringIO()):
            self.assertEqual(watch.cancel(RUN),0)
            stop.assert_called_once_with(['systemctl','--user','stop','mathcompute-job-'+RUN+'.service'],check=True,timeout=10)
        self.assertTrue(self.path.with_suffix('.cancel').exists())
        with patch.object(watch,'ROOT',self.root),patch.dict(os.environ,{'CODEX_THREAD_ID':'other'}),self.assertRaises(ValueError):
            watch.cancel(RUN)

    def test_arm_rejects_missing_owner_and_unsafe_sessions(self):
        with patch.object(watch,'ROOT',self.root),patch.object(watch,'LOGS',self.logs):
            for session in ('', '.', '..', '../escape', 'white space'):
                with self.assertRaises(ValueError):watch.arm(session,wait=0)
            with patch.dict(os.environ,{'CODEX_THREAD_ID':''}),self.assertRaises(ValueError):
                watch.arm('fixture',wait=0)
        self.assertEqual(self.path,self.logs/'codex-watchers'/(RUN+'.json'))
        with self.assertRaises(ValueError):watch.native_path(self.root,'bad')

    def test_arm_waits_for_start_not_end_and_preserves_watch_options(self):
        out=io.StringIO();journal=self.logs/'Fixture.jsonl'
        def release(delay):
            self.assertEqual(delay,.1)
            run=json.loads(out.getvalue().split('WATCH_READY ')[1].splitlines()[0])['run_id']
            journal.write_text(json.dumps({'event':'run_start','id':run})+'\n')
        with patch.object(watch,'ROOT',self.root),patch.object(watch,'LOGS',self.logs), \
             patch.object(watch.time,'sleep',release),patch.object(watch,'watch',return_value=7) as observed,redirect_stdout(out):
            self.assertEqual(watch.arm('Fixture',at=1,poll=.4),7)
            run=json.loads(out.getvalue().split('WATCH_READY ')[1].splitlines()[0])['run_id']
            observed.assert_called_once_with('Fixture',1,.4,out=out,grace=0,expected=run)

    def test_prestart_cancellation_and_completed_run_are_safe(self):
        out=io.StringIO()
        def cancel_before_start(_):
            run=json.loads(out.getvalue().split('WATCH_READY ')[1].splitlines()[0])['run_id']
            watch.native_path(self.root,run).with_suffix('.cancel').touch()
        with patch.object(watch,'ROOT',self.root),patch.object(watch,'LOGS',self.logs), \
             patch.object(watch.time,'sleep',cancel_before_start),redirect_stdout(out):
            self.assertEqual(watch.arm('fixture'),1)
            self.assertIn('cancelled before run start',out.getvalue())
            self.assertEqual(watch.cancel(RUN),0)
            atomic_json(self.path,{'owner':'owner','session':'fixture'})
            journal=self.logs/'fixture.jsonl'
            journal.write_text(json.dumps({'event':'run_start','id':RUN,'systemd_unit':'invalid'})+'\n')
            with self.assertRaises(ValueError):watch.cancel(RUN)
            with journal.open('a') as file:file.write(json.dumps({'event':'run_end','id':RUN})+'\n')
            with patch.object(watch.subprocess,'run') as stop:
                self.assertEqual(watch.cancel(RUN),0)
                stop.assert_not_called()

    def test_owned_watch_ignores_other_runs_and_announces_once(self):
        out=io.StringIO();journal=self.logs/'fixture.jsonl';output=self.logs/'job.txt'
        output.write_text('first\nlast\n')
        start={'event':'run_start','id':RUN,'unix_s':100,'output':'logs/job.txt','systemd_unit':'u.service'}
        journal.write_text(json.dumps(start)+'\n'+json.dumps({**start,'id':'other'})+'\n')
        steps=[]
        def advance(delay):
            self.assertEqual(delay,.1);steps.append(1)
            if len(steps)==2:
                with journal.open('a') as file:file.write(json.dumps({'event':'run_end','id':RUN,'unix_s':403,'timed_out':True})+'\n')
            if len(steps)>3:raise AssertionError('Watched unrelated run or failed completion')
        with patch.object(watch,'ROOT',self.root),patch.object(watch,'LOGS',self.logs):
            self.assertEqual(watch.last_line(start),'last')
            self.assertEqual(watch.watch('fixture',at=300,poll=.1,clock=lambda:400,sleep=advance,out=out,grace=0,expected=RUN),0)
        self.assertEqual(out.getvalue().count('(decision point)'),1)
        self.assertIn('Last output: last',out.getvalue())
        self.assertIn('timed out',out.getvalue())
        self.assertNotIn('Run other',out.getvalue())

    def test_cli_routes_native_modes_and_reports_failures(self):
        with patch.object(watch,'arm',return_value=0) as arm:
            self.assertEqual(watch.main(['fixture','--arm']),0)
            arm.assert_called_once_with('fixture',300,2)
        with patch.object(watch,'watch',return_value=0) as normal:
            self.assertEqual(watch.main(['fixture','--grace','4']),0)
            normal.assert_called_once_with('fixture',300,2,grace=4)
        with patch.object(watch,'arm',return_value=4) as arm:
            self.assertEqual(watch.main(['fixture','--arm','--at','3','--poll','.1']),4)
            arm.assert_called_once_with('fixture',3,.1)
        with patch.object(watch,'cancel',return_value=2) as cancel:
            self.assertEqual(watch.main(['--cancel',RUN]),2)
            cancel.assert_called_once_with(RUN)
        with patch.object(watch,'arm',side_effect=ValueError('bad')),patch('sys.stderr',new_callable=io.StringIO) as out:
            self.assertEqual(watch.main(['fixture','--arm']),1)
            self.assertIn('bad',out.getvalue())

    def test_compute_refuses_unarmed_or_duplicate_native_identity(self):
        loader=importlib.machinery.SourceFileLoader('compute_native_watch',str(ROOT/'compute.sh'))
        spec=importlib.util.spec_from_loader(loader.name,loader);compute=importlib.util.module_from_spec(spec);loader.exec_module(compute)
        journal=self.logs/'fixture.jsonl';journal.write_text('{"event":"start"}\n')
        args=argparse.Namespace(session='fixture',run_id=RUN,category='local_processing',threads=1,timeout=30,expect=None,tail_bytes=0)
        with patch.object(compute,'ROOT',self.root),patch.object(compute,'LOGS',self.logs), \
             patch.object(compute,'recovery_observe'),patch.object(compute,'invocation',side_effect=RuntimeError('fixture refusal')) as invoke,redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError,'armed'):compute.run_job(args,['true'])
            invoke.assert_not_called()
            atomic_json(self.path,{'owner':'owner','session':'fixture'})
            with self.path.with_suffix('.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                self.assertEqual(compute.run_job(args,['true']),1)
                with self.assertRaisesRegex(ValueError,'duplicate'):compute.run_job(args,['true'])
            args.run_id=None;args.timeout=181
            with self.assertRaisesRegex(ValueError,'armed'):compute.run_job(args,['true'])

    def test_harness_bridge_yields_forwards_milestones_and_cancels_failure(self):
        script=r'''
const fs=require('fs'),assert=require('assert');
const run=eval(fs.readFileSync(process.argv[1],'utf8'));
async function scenario(failure) {
  const calls=[],notes=[],order=[];let watcherPolls=0;
  const tools={
    exec_command:async o=>{calls.push(o);if(o.cmd.includes('--cancel'))return {exit_code:0,output:'cancelled'};
      if(o.cmd.startsWith('python3'))return {session_id:1,output:'WATCH_READY {"run_id":"'+'a'.repeat(32)+'"}\n'};
      return {session_id:2,output:''};},
    write_stdin:async o=>{order.push('poll');if(o.session_id===2)return {exit_code:failure?1:0,output:'full controller output'};
      if(++watcherPolls===1)return {session_id:1,output:'decision point'};
      return {exit_code:0,output:'completion'};}
  };
  const action=()=>run({tools,notify:s=>notes.push(s),yield_control:async()=>order.push('yield'),root:'/fixture',session:'turn',args:['--','echo',"a'$(touch BAD)"]});
  if(failure)await assert.rejects(action);else assert.equal((await action()).exit_code,0);
  assert.equal(order[0],'yield');assert(notes.includes('decision point'));assert(notes.includes('completion'));assert(notes.includes('full controller output'));
  assert(calls[0].cmd.includes('--arm'));assert(calls[1].cmd.includes('--run-id '+'a'.repeat(32)));
  assert(calls[1].cmd.includes("'a'\\''$(touch BAD)'"));
  assert.equal(calls.filter(c=>c.cmd.includes('--cancel')).length,failure?1:0);
}
(async()=>{await scenario(false);await scenario(true);console.log('native bridge controls passed')})().catch(e=>{console.error(e);process.exit(1)});
'''
        result=subprocess.run(['node','-e',script,str(ROOT/'tools/codex_monitor.js')],capture_output=True,text=True,timeout=3)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':
    unittest.main()
