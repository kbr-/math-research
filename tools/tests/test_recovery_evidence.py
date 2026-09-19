import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from recovery_evidence import Store,observe,snapshot
import test_finish_turn as fixtures


class RecoveryTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.now=[100.,10.,'boot-a']
        self.store=Store(self.root,owner='private-routing-key',clock=lambda:tuple(self.now))
        self.addCleanup(self.store.db.close)

    def tick(self, seconds=1):
        self.now[0]+=seconds;self.now[1]+=seconds

    def test_recovery_repeats_changed_content_and_saved_only(self):
        s=self.store
        with s.db:
            s.bind('turn');s.read('excerpt','claim','old')
            self.tick();s.resume('turn');s.read('excerpt','current','overview')
            self.tick();s.read('excerpt','claim','old')
            s.read('excerpt','claim','changed')
            s.read('excerpt','claim','old',shown=False)
            self.tick(3);s.phase('turn','reading')
            self.assertIsNotNone(s.state()['active'])
            s.phase('turn','mathematics')
        report=s.report('turn');e=report['episodes'][0]
        self.assertEqual(e['elapsed_to_work_s'],4)
        self.assertEqual(e['emitted_reads'],3)
        self.assertEqual(e['unchanged_repeat_reads'],1)
        self.assertEqual(e['reads_seen_before_resume'],1)
        self.assertEqual(e['saved_only_operations'],1)
        for secret in ['private-routing-key','overview','changed','boot-a']:
            self.assertNotIn(json.dumps(secret),json.dumps(report))

    def test_reboot_and_checkpoint_censor_instead_of_inventing_duration(self):
        s=self.store
        with s.db:
            s.bind('turn');s.begin();self.now[2]='boot-b';self.now[1]=0
            s.phase('turn','coding')
            s.begin();s.stop('turn',self.now[0])
        rows=s.report('turn')['episodes']
        self.assertEqual([r['outcome'] for r in rows],['reboot_censored','checkpoint_without_work_phase'])
        self.assertTrue(all(r['elapsed_to_work_s'] is None for r in rows))

    def test_restart_before_timing_binds_later_and_retrigger_is_explicit(self):
        s=self.store
        with s.db:
            s.begin();self.tick();s.begin();s.bind('new');self.tick();s.phase('new','formalization')
        all_rows=s.report()['episodes']
        self.assertEqual(all_rows[0]['outcome'],'superseded_by_resume')
        self.assertIsNone(all_rows[0]['elapsed_to_work_s'])
        self.assertEqual(s.report('new')['episodes'][0]['elapsed_to_work_s'],1)

    def test_identical_command_is_only_a_candidate_after_prior_success(self):
        s=self.store;command=['python','private-script.py','secret-argument']
        with s.db:
            s.job_start('turn','old',command,'local_processing');s.job_end('turn','old',1)
            s.begin();self.tick()
            s.job_start('turn','first',command,'computation');s.job_end('turn','first',0)
            self.tick();s.job_start('turn','repeat',command,'computation');s.job_end('turn','repeat',0)
        report=s.report('turn');e=report['episodes'][0]
        self.assertEqual(e['outcome'],'work_job:computation')
        self.assertEqual([j['same_command_previously_succeeded'] for j in e['jobs_after_resume']],[False,True])
        self.assertNotIn('secret-argument',json.dumps(report))
        self.assertNotIn('private-script.py',json.dumps(report))

    def test_stream_isolation_and_no_identity_no_duration(self):
        a=self.store;b=Store(self.root,owner='different',clock=lambda:tuple(self.now))
        self.addCleanup(b.db.close)
        with a.db:a.bind('a');a.begin();a.read('read','same','text')
        with b.db:b.bind('b');b.begin();b.read('read','same','text');b.phase('b','coding')
        self.assertEqual(b.report('b')['episodes'][0]['unchanged_repeat_reads'],0)
        self.assertEqual(a.report('a')['episodes'][0]['outcome'],'open_at_snapshot')
        with patch.dict(os.environ,{},clear=True):
            c=Store(self.root,clock=lambda:tuple(self.now))
            try:
                with c.db:c.resume('anonymous');c.read('read','same','text')
                episode=c.report('anonymous')['episodes'][0]
                self.assertEqual(episode['outcome'],'unattributed_resume')
                self.assertIsNone(episode['elapsed_to_work_s'])
                self.assertEqual(c.report()['unattributed_reads'],1)
            finally:c.db.close()

    def test_collection_failure_is_nonfatal_and_explicit(self):
        with patch.dict(os.environ,{'MATH_RECOVERY_DISABLED':'0'}),patch('recovery_evidence.Store',side_effect=OSError('secret path')):
            observe('begin',root=self.root)
            report=snapshot(root=self.root)
        self.assertEqual(report['collection'],'unavailable')
        error=(self.root/'research/logs/recovery-errors.jsonl').read_text()
        self.assertNotIn('secret path',error)
        self.assertIn('OSError',error)


class RecoveryIntegrationTest(unittest.TestCase):
    setUp=fixtures.FinalizationTest.setUp
    command=fixtures.FinalizationTest.command

    def prepare_bundle(self):
        self.command_env.pop('MATH_RECOVERY_DISABLED',None)
        self.command_env['MATH_RECOVERY_STREAM']='fixture-identity'
        self.command('compute.sh','phase','test_turn','reading')
        import shutil
        shutil.copy2(ROOT/'tools/resume.py',self.root/'tools/resume.py')
        for name in ('research/notes/RESUME.md','AGENTS.md','research/AGENTS.md','COMPUTATION_RULES.md'):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('Fixture instructions for '+name+'\n')
        (self.root/'notebook.html').write_text('<p>Overview.</p><section id="research-record">'
            '<article id="entry-2026-09-19-fixture"><h3 id="statement">Source</h3>'
            '<p class="entry-meta">Working fixture.</p><p>Details.</p>'
            '<!-- TIMING test_turn --></article></section>')

    def test_existing_commands_collect_and_archive_without_extra_output(self):
        self.prepare_bundle()
        first=self.command('tools/notebook-excerpt.py','--current')
        second=self.command('tools/notebook-excerpt.py','--current')
        self.assertEqual(first.stdout,second.stdout)
        self.assertEqual(first.stderr,'')
        with patch.dict(os.environ,{'MATH_RECOVERY_DISABLED':'0'}):
            self.assertEqual(snapshot(root=self.root,turn='test_turn')['episodes'],[])
        resumed=self.command('tools/resume.py')  # Finds this stream's active clock.
        manifest=json.loads(resumed.stdout.splitlines()[0])
        self.assertIn('Fixture instructions',resumed.stdout)
        outputs=[self.command('tools/resume.py','--read',manifest['bundle'],'--part',str(i)).stdout
                 for i in range(1,manifest['parts']+1)]
        self.assertEqual(''.join(outputs).count('Fixture instructions for AGENTS.md'),1)
        self.command('tools/resume.py','--session','test_turn')
        self.command('tools/notebook-excerpt.py','--current')
        self.command('tools/notebook-excerpt.py','statement')
        self.command('tools/notebook-excerpt.py','statement')
        self.command('compute.sh','phase','test_turn','coding')
        self.command('tools/finish-turn.py','test_turn')
        summary=self.root/'research/logs/test_turn.summary.json'
        before=summary.read_bytes();data=json.loads(before)
        report=data['recovery_proxy']
        self.assertEqual(len(report['episodes']),2)
        self.assertGreaterEqual(report['episodes'][1]['unchanged_repeat_reads'],2)
        self.assertNotIn('fixture-identity',json.dumps(report))
        self.assertGreater(data['exclusive_categories_s']['restoration'],0)
        self.assertIn('Context restoration',(self.root/'notebook.html').read_text())
        saved=self.root/'research/provenance/session-records/test_turn/summary.json'
        self.assertEqual(saved.read_bytes(),before)
        output=self.command('compute.sh','report','test_turn')
        self.assertNotIn('recovery_proxy',output.stdout)
        self.assertEqual(summary.read_bytes(),before)

    def test_restore_only_starts_no_cycle_and_rejects_explicit_stopped_clock(self):
        self.prepare_bundle()
        self.command('compute.sh','report','test_turn','--stop')
        logs=self.root/'research/logs';before=sorted(p.name for p in logs.glob('*.jsonl'))
        output=self.command('tools/resume.py')
        self.assertGreater(json.loads(output.stdout.splitlines()[0])['parts'],0)
        self.assertEqual(sorted(p.name for p in logs.glob('*.jsonl')),before)
        with patch.dict(os.environ,{'MATH_RECOVERY_DISABLED':'0'}):
            report=snapshot(root=self.root)
        self.assertEqual(len(report['episodes']),1)
        self.assertIsNone(report['episodes'][0]['timing_session'])
        self.assertIsNone(report['episodes'][0]['elapsed_to_work_s'])
        failed=self.command('tools/resume.py','--session','test_turn',check=False)
        self.assertNotEqual(failed.returncode,0)
        self.assertEqual(failed.stdout,'')

    def test_bounded_cached_parts_preserve_unicode_and_retries_do_not_resume(self):
        self.prepare_bundle()
        source=self.root/'AGENTS.md';source.write_text('数学🙂 '*5000)
        result=self.command('tools/resume.py');info=json.loads(result.stdout.splitlines()[0])
        self.assertLess(len(result.stdout.encode()),17000)
        self.assertGreater(info['parts'],2)
        cached=(self.root/info['path']).read_text()
        source.write_text('Changed after preparation')
        pieces=[]
        for i in range(1,info['parts']+1):
            output=self.command('tools/resume.py','--read',info['bundle'],'--part',str(i)).stdout
            body=output.split('\n',1)[1].rsplit('\nEND RESUME PART ',1)[0]
            self.assertLessEqual(len(body.encode()),16000)
            pieces.append(body)
        self.assertEqual(''.join(pieces),cached)
        retry=self.command('tools/resume.py','--read',info['bundle'],'--part','1')
        self.assertIn('RESUME PART 1/',retry.stdout)
        with patch.dict(os.environ,{'MATH_RECOVERY_DISABLED':'0'}):
            report=snapshot(root=self.root,turn='test_turn')
        self.assertEqual(len(report['episodes']),1)
        self.assertGreater(report['episodes'][0]['unchanged_repeat_reads'],0)
        corrupted=self.root/info['path'];raw=bytearray(corrupted.read_bytes());raw[0]^=1;corrupted.write_bytes(raw)
        failed=self.command('tools/resume.py','--read',info['bundle'],'--part','1',check=False)
        self.assertNotEqual(failed.returncode,0)
        self.assertEqual(failed.stdout,'')

    def test_switching_cycles_does_not_reassign_an_earlier_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            store=Store(Path(temp),owner='shared-stream')
            try:
                with store.db:
                    store.resume('first');store.phase('second','coding')
                first=store.report('first')['episodes'][0]
                self.assertEqual(first['outcome'],'timing_session_changed')
                self.assertIsNone(first['elapsed_to_work_s'])
                self.assertEqual(store.report('second')['episodes'],[])
            finally:store.db.close()

    def test_untracked_historical_summary_is_not_retrofitted(self):
        self.command_env['MATH_RECOVERY_DISABLED']='1'
        self.command('compute.sh','start','historical','--agent','Test','--model','Test')
        self.command('compute.sh','report','historical','--stop')
        path=self.root/'research/logs/historical.summary.json'
        # This matches the old schema, before the collector existed.
        data=json.loads(path.read_text());data.pop('recovery_proxy',None)
        path.write_text(json.dumps(data,indent=2)+'\n');before=path.read_bytes()
        self.command_env.pop('MATH_RECOVERY_DISABLED')
        self.command('compute.sh','report','historical')
        self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main()
