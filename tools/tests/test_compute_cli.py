"""Small integration checks for the combined protected runner/timer."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
import uuid

ROOT = Path(__file__).resolve().parents[2]
CLI = str(ROOT / 'compute.sh')
loader = importlib.machinery.SourceFileLoader('compute_cli', CLI)
spec = importlib.util.spec_from_loader(loader.name, loader)
compute = importlib.util.module_from_spec(spec)
loader.exec_module(compute)


def call(*args, env=None):
    return subprocess.run([CLI, *args], cwd=ROOT, capture_output=True, text=True,
                          timeout=20, env=env)


def eventually(predicate, timeout=6):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError('Timed out waiting for test condition')


def gone_or_dead(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[0] in ('Z', 'X')
    except FileNotFoundError:
        return True


class ArchivedSessionName(unittest.TestCase):
    def test_a_name_whose_evidence_is_archived_is_refused_though_its_log_is_gone(self):
        # 17 October 2026: "route-review" was reused after its log was gone, and the archive refused at the end.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'research/provenance/session-records/old-turn').mkdir(parents=True)
            (root / 'research/logs').mkdir(parents=True)
            with unittest.mock.patch.object(compute, 'ROOT', root), \
                    unittest.mock.patch.object(compute, 'link_user_requests'), \
                    unittest.mock.patch.object(compute, 'link_shared'), \
                    unittest.mock.patch.object(compute, 'session_path', lambda name: root / f'research/logs/{name}.jsonl'), \
                    unittest.mock.patch.dict(sys.modules, {'notebooks': type(sys)('notebooks')}):
                sys.modules['notebooks'].selected = lambda notebook, root: {'name': 'main'}
                with self.assertRaises(ValueError) as raised:
                    compute.start_session('old-turn', agent='unit', model='unit test, none')
                self.assertIn('already archived', str(raised.exception))
                self.assertFalse((root / 'research/logs/old-turn.jsonl').exists())
                (root / 'research/results/table-turn').mkdir(parents=True)
                (root / 'research/results/table-turn/timing.html').write_text('<table></table>')
                with self.assertRaises(ValueError) as raised:
                    compute.start_session('table-turn', agent='unit', model='unit test, none')
                self.assertIn('timing.html', str(raised.exception))
                with unittest.mock.patch.object(compute, 'add_event') as added:
                    compute.start_session('new-turn', agent='unit', model='unit test, none')
                added.assert_called_once()


class InactiveControls(unittest.TestCase):
    """Controls down, as after a reboot: the error names the setup the agent runs itself."""

    def test_both_inactive_states_name_the_setup(self):
        slice_down = subprocess.CompletedProcess([], 0, '\n', '')
        watchdog_down = [subprocess.CompletedProcess([], 0, f'/user.slice/u/{compute.SLICE}\n', ''),
                         subprocess.CompletedProcess([], 0, 'ActiveState=inactive\nSubState=dead\n', '')]
        for answers, state in (([slice_down], 'slice is not active'), (watchdog_down, 'watchdog is not running')):
            with self.subTest(state=state), \
                    unittest.mock.patch.object(compute.subprocess, 'run', side_effect=answers), \
                    unittest.mock.patch.object(compute.Path, 'read_text', return_value='1000\n'):
                with self.assertRaises(RuntimeError) as raised:
                    compute.check_limits()
                self.assertIn(state, str(raised.exception))
                self.assertIn('run python3 resource-controls/setup.py from the repository root, without asking',
                              str(raised.exception))

    def test_session_watchdog_down_names_the_setup_unless_stopped_by_the_user(self):
        runtime = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, runtime)
        down = subprocess.CompletedProcess([], 0, 'ActiveState=inactive\n', '')
        up = subprocess.CompletedProcess([], 0, 'ActiveState=active\n', '')
        with unittest.mock.patch.object(compute, 'runtime_directory', return_value=runtime):
            with unittest.mock.patch.object(compute.subprocess, 'run', return_value=down):
                with self.assertRaises(RuntimeError) as raised:
                    compute.check_session_watchdog()
                self.assertIn('session watchdog is not running', str(raised.exception))
                self.assertIn('run python3 resource-controls/setup.py from the repository root, without asking',
                              str(raised.exception))
                (runtime / compute.SESSION_WATCHDOG_STOPPED).write_text('stopped by the user\n')
                compute.check_session_watchdog()
            (runtime / compute.SESSION_WATCHDOG_STOPPED).unlink()
            with unittest.mock.patch.object(compute.subprocess, 'run', return_value=up):
                compute.check_session_watchdog()

    @unittest.mock.patch.object(compute, 'check_limits')
    def test_protected_job_gets_owned_scratch_without_raw_identity(self, limits):
        from codex_state import scratch_directory
        with unittest.mock.patch.dict(os.environ, {'CODEX_THREAD_ID': 'fixture-owner'}, clear=True):
            args = compute.invocation([sys.executable, '-c', 'pass'], 1, 10, 'fixture.service')
        self.assertIn('--setenv=MATH_CODEX_SCRATCH=' + str(scratch_directory(ROOT, 'fixture-owner')), args)
        self.assertFalse(any('CODEX_THREAD_ID=' in value or 'fixture-owner' in value for value in args))
        for env in ({}, {'CODEX_THREAD_ID': 'fixture-owner', 'CLAUDE_CODE_SESSION_ID': 'claude'}):
            with unittest.mock.patch.dict(os.environ, env, clear=True):
                args = compute.invocation([sys.executable, '-c', 'pass'], 1, 10, 'fixture.service')
            self.assertFalse(any('MATH_CODEX_SCRATCH=' in value for value in args))
        self.assertEqual(limits.call_count, 3)


class GuidanceNote(unittest.TestCase):
    """compute.sh start warns when its turn guidance is slow, and stays quiet otherwise."""

    def test_slow_guidance_is_reported(self):
        note = compute.guidance_note(compute.GUIDANCE_WARN_S + 1.5)
        self.assertIn('Warning: turn guidance took 2.5 s', note)

    def test_fast_guidance_prints_nothing(self):
        self.assertEqual(compute.guidance_note(compute.GUIDANCE_WARN_S / 4), '')


class JobMemory(unittest.TestCase):
    """A job's end says how much memory it held, so that a kill of the whole group names the job that grew."""

    def test_the_last_reading_of_a_job_s_peak_is_kept_and_said_when_it_matters(self):
        with tempfile.TemporaryDirectory() as scratch:
            group = compute.job_group('job-1.service', root=Path(scratch))
            uid = os.getuid()
            self.assertEqual(group, Path(scratch) / 'user.slice' / f'user-{uid}.slice' / f'user@{uid}.service'
                             / 'mathcompute.slice' / 'job-1.service')
            self.assertIsNone(compute.memory_peak(group))
            group.mkdir(parents=True)
            (group / 'memory.peak').write_text('2500000000\n')
            self.assertIsNone(compute.memory_peak(group))          # one of the two files alone is no reading
            (group / 'memory.swap.peak').write_text('500000000\n')
            self.assertEqual(compute.memory_peak(group), (2_500_000_000, 500_000_000))

            class Process:
                polls = 0

                def poll(self):
                    Process.polls += 1
                    if Process.polls == 1:                           # the job grows while it runs
                        (group / 'memory.peak').write_text('3000000000\n')
                    if Process.polls == 2:                           # the job's group is gone when it ends
                        (group / 'memory.peak').unlink()
                    return None if Process.polls < 3 else 9
            watch = compute.PeakWatch(Process(), group, interval=0.001)
            watch.start()
            watch.join(timeout=5)
            self.assertFalse(watch.is_alive())
            self.assertEqual(watch.last, (3_000_000_000, 500_000_000))
            (group / 'memory.swap.peak').write_text('not a number\n')
            (group / 'memory.peak').write_text('1\n')
            self.assertIsNone(compute.memory_peak(group))
        said = ("Memory: this job's own peak was 2.50 GB of RAM and 0.50 GB of swap, at its last reading; every job shares "
                'one budget of 10 GB.')
        self.assertEqual(compute.memory_line((2_500_000_000, 500_000_000), 0), said)
        self.assertEqual(compute.memory_line((2_500_000_000, 500_000_000), 137), said)
        # A small job says nothing when it passes and its peak when it fails; no reading says nothing.
        self.assertIsNone(compute.memory_line((1_600_000_000, 899_999_999), 0))
        self.assertIsNotNone(compute.memory_line((1_600_000_000, 900_000_000), 0))
        self.assertIn('0.09 GB of RAM', compute.memory_line((90_000_000, 0), 3))
        self.assertIsNone(compute.memory_line(None, 3))

    def test_a_job_of_seconds_on_one_cpu_is_called_serial(self):
        with tempfile.TemporaryDirectory() as tmp:
            group = Path(tmp)
            self.assertIsNone(compute.cpu_seconds(group))
            (group / 'cpu.stat').write_text('usage_usec 8250000\nuser_usec 8000000\n')
            self.assertEqual(compute.cpu_seconds(group), 8.25)
            (group / 'cpu.stat').write_text('usage_usec many\n')
            self.assertIsNone(compute.cpu_seconds(group))
        said = compute.serial_line(8.2, 8.0)
        self.assertIn('took 8 s and used 8 s of CPU time, about 1.0 of the 14 CPUs allowed', said)
        self.assertIn('split its independent parts across processes', said)
        self.assertIsNone(compute.serial_line(8.2, 4.9))      # a short job says nothing
        self.assertIsNone(compute.serial_line(12.0, 8.0))     # nor one that used more than one CPU
        self.assertIsNone(compute.serial_line(None, 8.0))     # nor one without a reading
        self.assertIsNone(compute.serial_line(0.5, 30.0))     # nor one that mostly waited

    def test_a_failed_job_s_end_names_its_own_memory(self):
        failed = call('--threads', '1', '--timeout', '20', '--category', 'local_processing', '--', sys.executable, '-c',
                      'import time; x = bytearray(b"x") * 60_000_000; time.sleep(0.5); raise SystemExit(3)')
        self.assertEqual(failed.returncode, 3, failed.stderr)
        line = next(line for line in failed.stdout.splitlines() if line.startswith('Memory: '))
        self.assertGreater(float(line.split('was ')[1].split(' GB')[0]), 0.05)
        passed = call('--threads', '1', '--timeout', '20', '--category', 'local_processing', '--', sys.executable, '-c', 'pass')
        self.assertEqual((passed.returncode, [l for l in passed.stdout.splitlines() if l.startswith('Memory')]), (0, []))


class RunnerChecks(unittest.TestCase):
    def setUp(self):
        self.name = 'cli_test_' + uuid.uuid4().hex[:12]
        self.assertEqual(call('start', self.name, '--model', 'unit test, no reasoning', '--no-guidance').returncode, 0)
        self.path = ROOT / 'research/logs' / (self.name + '.jsonl')

    def tearDown(self):
        call('report', self.name, '--stop')

    def events(self):
        return [json.loads(line) for line in self.path.read_text().splitlines()]

    def test_a_start_without_guidance_prints_only_the_journal(self):
        # Fails if the flag is ignored only while the real repository's turn guidance prints something, which its
        # queue and cadence lines always do.
        name = 'cli_test_' + uuid.uuid4().hex[:12]
        started = call('start', name, '--model', 'unit test, no reasoning', '--no-guidance')
        self.addCleanup(call, 'report', name, '--stop')
        self.assertEqual(started.returncode, 0, started.stderr)
        self.assertEqual(started.stdout.strip(), f'research/logs/{name}.jsonl')

    def test_parallel_success_failure_and_stopped_session(self):
        processes = [subprocess.Popen(
            [CLI, 'run', self.name, '--threads', '1', '--timeout', '20', '--', sys.executable, '-c',
             f'import time; time.sleep(0.3); raise SystemExit({code})'],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for code in (0, 7)]
        eventually(lambda: sum(e['event'] == 'run_start' for e in self.events()) == 2)
        self.assertNotEqual(call('report', self.name, '--stop').returncode, 0)
        returns = []
        for process in processes:
            process.communicate(timeout=10)
            returns.append(process.returncode)
        self.assertEqual(returns, [0, 7])
        report = call('report', self.name, '--stop')
        self.assertEqual(report.returncode, 0, report.stderr)
        summary = json.loads(report.stdout)
        self.assertEqual(summary['command_runs'], 2)
        self.assertEqual(summary['failed_or_timed_out_commands'], 1)
        self.assertEqual(summary['unfinished_commands'], 0)
        self.assertAlmostEqual(sum(summary['exclusive_categories_s'].values()),
                               summary['total_instrumented_s'], places=5)
        self.assertNotEqual(call('phase', self.name, 'reading').returncode, 0)

    def test_a_fifth_argument_list_of_one_program_is_refused_at_the_command_line(self):
        """The series guard through the launcher: its other tests call the function, and a launcher that never
        called it passed them all."""
        with self.path.open('a') as journal:
            for n in range(compute.MAX_SERIES_ARGSETS):
                journal.write(json.dumps({'event': 'run_start', 'command': ['python3', 'scan.py', str(n)]}) + '\n')
        runs = lambda: sum(e['event'] == 'run_start' for e in self.events())
        run = lambda *words: call('run', self.name, '--threads', '1', '--timeout', '20', *words)
        refused = run('--', sys.executable, 'scan.py', 'another')
        self.assertEqual(refused.returncode, 2)
        self.assertIn(f'scan.py already ran with {compute.MAX_SERIES_ARGSETS} different argument lists', refused.stderr)
        self.assertEqual(runs(), compute.MAX_SERIES_ARGSETS)
        # A list run before is run again, and what is no computation is no series; neither script exists, so both end at once.
        for words in (('--', sys.executable, 'scan.py', '0'), ('--category', 'local_processing', '--', sys.executable, 'scan.py', 'more')):
            before = runs()
            self.assertNotIn('already ran', run(*words).stderr)
            self.assertEqual(runs(), before + 1)

    def test_guard_failure_is_logged_without_execution(self):
        env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS='unix:path=/tmp/math-no-such-test-bus')
        result = call('run', self.name, '--threads', '1', '--timeout', '20', '--',
                      sys.executable, '-c', 'print("WORKLOAD_EXECUTED")', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('WORKLOAD_EXECUTED', result.stdout)
        # Computation output is never displayed, so check the saved log as well.
        log = ROOT / result.stdout.rsplit('log: ', 1)[1].strip()
        self.assertNotIn('WORKLOAD_EXECUTED', log.read_text())
        ends = [e for e in self.events() if e['event'] == 'run_end']
        self.assertEqual(len(ends), 1)
        self.assertNotEqual(ends[0]['returncode'], 0)

    def check_descendant_cleanup(self, interrupt):
        with tempfile.TemporaryDirectory(prefix='compute-cleanup-') as directory:
            pidfile = Path(directory) / 'pids.json'
            code = ('import json,os,subprocess,sys,time; '
                    'child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); '
                    f'open({str(pidfile)!r},"w").write(json.dumps([os.getpid(),child.pid])); '
                    'time.sleep(30)')
            process = subprocess.Popen(
                [CLI, 'run', self.name, '--threads', '1', '--timeout',
                 '10' if interrupt else '2', '--', sys.executable, '-c', code],
                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            eventually(lambda: pidfile.exists() and pidfile.stat().st_size > 0)
            pids = json.loads(pidfile.read_text())
            if interrupt:
                process.send_signal(signal.SIGTERM)
            output, errors = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 130 if interrupt else 124, output + errors)
            eventually(lambda: all(gone_or_dead(pid) for pid in pids))
            end = [e for e in self.events() if e['event'] == 'run_end'][-1]
            self.assertEqual(end['interrupted'], interrupt)
            self.assertEqual(end['timed_out'], not interrupt)

    def test_timeout_kills_service_and_child(self):
        self.check_descendant_cleanup(False)

    def test_interrupt_kills_service_and_child(self):
        self.check_descendant_cleanup(True)

    def test_standalone_logging_argument_preservation_and_output_limit(self):
        argument = 'literal spaces; $(not-a-command)'
        code = 'import sys; print("z"*100); print(sys.argv[1])'
        # A tail may be displayed only outside the computation category.
        result = call('--threads', '1', '--timeout', '20', '--category', 'local_processing',
                      '--tail-bytes', '50', '--', sys.executable, '-c', code, argument)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(argument, result.stdout)
        self.assertNotIn('z' * 100, result.stdout)
        self.assertIn('full output is saved', result.stdout)
        log = ROOT / result.stdout.rsplit('log: ', 1)[1].strip()
        self.assertIn('z' * 100, log.read_text())
        self.assertIn(argument, log.read_text())
        # Computation output is saved but never displayed, and a tail request is refused.
        result = call('--threads', '1', '--timeout', '20', '--', sys.executable, '-c', code, argument)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(argument, result.stdout)
        log = ROOT / result.stdout.rsplit('log: ', 1)[1].strip()
        self.assertIn(argument, log.read_text())
        refused = call('--threads', '1', '--timeout', '20', '--tail-bytes', '50', '--',
                       sys.executable, '-c', code, argument)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn('never displayed', refused.stderr)

    def test_overlapping_intervals_are_counted_once(self):
        events = [dict(event='start', monotonic_s=0),
                  dict(event='phase', monotonic_s=0, category='reading'),
                  dict(event='run_start', monotonic_s=2, id='a', category='computation'),
                  dict(event='run_start', monotonic_s=4, id='b', category='computation'),
                  dict(event='run_end', monotonic_s=6, id='a', returncode=0),
                  dict(event='run_end', monotonic_s=8, id='b', returncode=7)]
        data = compute.summary(events, 10)
        self.assertEqual(data['exclusive_categories_s'], {'reading': 4, 'computation': 6})

    def test_timing_table_formats_measured_categories_and_rejects_bad_totals(self):
        data = {'total_instrumented_s': 867.74,
                'exclusive_categories_s': {'reading': 81.85, 'network_tool': 37.28,
                                           'local_processing': 7.29, 'preparation': 741.32},
                'command_runs': 3, 'failed_or_timed_out_commands': 1,
                'unfinished_commands': 0}
        fragment = compute.timing_html(data, '<example>')
        self.assertIn('14 min 27.74 s', fragment)
        self.assertIn('1 min 21.85 s', fragment)
        self.assertIn('12 min 21.32 s', fragment)
        self.assertIn('Failed/timed-out commands: 1.', fragment)
        self.assertIn('&lt;example&gt;', fragment)
        self.assertNotIn('Individually measured computation</td>', fragment)
        with self.assertRaises(ValueError):
            compute.timing_html(dict(data, total_instrumented_s=900), self.name)

    def test_formalization_phase_and_verification_command(self):
        phase = call('phase', self.name, 'formalization')
        self.assertEqual(phase.returncode, 0, phase.stderr)
        result = call('run', self.name, '--threads', '1', '--category',
                      'formal_verification', '--', sys.executable, '-c', 'print("checked")')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = call('report', self.name, '--stop')
        self.assertEqual(report.returncode, 0, report.stderr)
        data = json.loads(report.stdout)
        self.assertIn('formalization', data['exclusive_categories_s'])
        self.assertIn('formal_verification', data['exclusive_categories_s'])
        fragment = compute.timing_html(data, self.name)
        self.assertIn('Formal proof design and coding', fragment)
        self.assertIn('Individually measured formal verification', fragment)

    def test_formalization_overlapping_check_is_exclusive(self):
        events = [dict(event='start', monotonic_s=0),
                  dict(event='phase', monotonic_s=0, category='mathematics'),
                  dict(event='phase', monotonic_s=2, category='formalization'),
                  dict(event='run_start', monotonic_s=3, id='lean', category='formal_verification'),
                  dict(event='run_end', monotonic_s=7, id='lean', returncode=0)]
        data = compute.summary(events, 10)
        self.assertEqual(data['exclusive_categories_s'],
                         {'mathematics': 2, 'formalization': 4, 'formal_verification': 4})

    def test_html_export_requires_a_finalized_session(self):
        with tempfile.TemporaryDirectory(prefix='timing-html-') as directory:
            output = Path(directory) / 'timing.html'
            incomplete = call('report', self.name, '--html-out', str(output))
            self.assertNotEqual(incomplete.returncode, 0)
            self.assertFalse(output.exists())
            completed = call('report', self.name, '--stop', '--html-out', str(output))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('Total instrumented interval', output.read_text())
            self.assertIn('Through final snapshot; overlapping time counted once.', output.read_text())
            self.assertNotIn('Pure reasoning time', output.read_text())


class RecordedKernelReasonTest(unittest.TestCase):
    def test_a_refused_launch_is_shown_the_reason_recorded_for_code_it_shares(self):
        # 17 October 2026: two launches in a row lacked the kernel reason a run of the same imported flows had
        # recorded; a script sharing no code is shown none.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            res = root / 'research/results'
            (res / 'a').mkdir(parents=True)
            (res / 'b').mkdir()
            (res / 'a/rule.py').write_text('x = 1\n')
            (res / 'a/old.py').write_text("RULE = 'rule.py'\n")
            (res / 'b/new.py').write_text("LEVELS = 'mid.py'\n")
            (res / 'b/mid.py').write_text("RULE = 'rule.py'\n")
            (res / 'b/alone.py').write_text('y = 2\n')
            rec = root / 'research/provenance/session-records/s'
            rec.mkdir(parents=True)
            (root / 'research/logs').mkdir(parents=True)
            reason = 'NumPy batched solves per level do the work once'
            (rec / 'session.jsonl').write_text(
                json.dumps({'event': 'run_start', 'unix_s': 5, 'command': ['python3', 'research/results/a/old.py'],
                            'kernel_reason': reason}) + '\n'
                + json.dumps({'event': 'run_start', 'unix_s': 6, 'command': ['python3', 'x.py'],
                              'kernel_reason': ''}) + '\n')
            self.assertEqual(compute.recorded_kernel_reasons(res / 'b/new.py', root), [('old.py', reason)])
            self.assertEqual(compute.recorded_kernel_reasons(res / 'b/alone.py', root), [])


if __name__ == '__main__':
    unittest.main(verbosity=1)
