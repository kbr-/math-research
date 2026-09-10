"""Small integration checks for the combined protected runner/timer."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parent.parent
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


class RunnerChecks(unittest.TestCase):
    def setUp(self):
        self.name = 'cli_test_' + uuid.uuid4().hex[:12]
        self.assertEqual(call('start', self.name).returncode, 0)
        self.path = ROOT / 'research/logs' / (self.name + '.jsonl')

    def tearDown(self):
        call('report', self.name, '--stop')

    def events(self):
        return [json.loads(line) for line in self.path.read_text().splitlines()]

    def test_parallel_success_failure_and_stopped_session(self):
        processes = [subprocess.Popen(
            [CLI, 'run', self.name, '--threads', '1', '--', sys.executable, '-c',
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

    def test_guard_failure_is_logged_without_execution(self):
        env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS='unix:path=/tmp/math-no-such-test-bus')
        result = call('run', self.name, '--threads', '1', '--',
                      sys.executable, '-c', 'print("WORKLOAD_EXECUTED")', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('WORKLOAD_EXECUTED', result.stdout)
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
        result = call('--threads', '1', '--tail-bytes', '50', '--', sys.executable, '-c',
                      'import sys; print("z"*100); print(sys.argv[1])', argument)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(argument, result.stdout)
        self.assertIn('full output is saved', result.stdout)
        log = ROOT / result.stdout.rsplit('log: ', 1)[1].strip()
        self.assertIn('z' * 100, log.read_text())

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


if __name__ == '__main__':
    unittest.main(verbosity=1)
