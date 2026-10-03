import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = load('monitor_gate', TOOLS / 'hooks' / 'monitor-gate.py')
watch_run = load('watch_run', TOOLS / 'watch_run.py')


def payload(tool, background=False, **tool_input):
    if background:
        tool_input['run_in_background'] = True
    return {'session_id': 's1', 'tool_name': tool, 'tool_input': tool_input}


class MonitorGateTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def test_long_background_run_requires_the_monitor_next(self):
        long_run = './compute.sh run t1 --threads 1 --timeout 900 --expect 300 -- M2 --script x.m2'
        self.assertEqual(gate.long_run_session(long_run), 't1')
        self.assertEqual(gate.long_run_session('./compute.sh --session t2 --timeout 900 python3 x.py'), 't2')
        self.assertIsNone(gate.long_run_session('./compute.sh run t1 --timeout 120 --expect 5 -- ./k'))
        self.assertIsNone(gate.long_run_session('./compute.sh phase t1 coding'))
        gate.post(payload('Bash', command=long_run), self.root)                 # foreground: no mark
        self.assertEqual(gate.pre(payload('Read', file_path='x'), self.root), 0)
        gate.post(payload('Bash', True, command=long_run), self.root)
        self.assertEqual(gate.pre(payload('Read', file_path='x'), self.root), 2)
        self.assertEqual(gate.pre(payload('Bash', command='ls'), self.root), 2)
        self.assertEqual(gate.pre(payload('Monitor', command='tail -f x'), self.root), 2)
        self.assertEqual(gate.pre(payload('ToolSearch', query='select:Monitor'), self.root), 0)
        self.assertEqual(gate.pre(payload('Monitor', command='python3 tools/watch_run.py t1'), self.root), 0)
        self.assertEqual(gate.pre(payload('Read', file_path='x'), self.root), 0)   # cleared

    def test_short_background_run_needs_no_monitor(self):
        gate.post(payload('Bash', True, command='./compute.sh run t1 --timeout 60 -- ./k'), self.root)
        self.assertEqual(gate.pre(payload('Read', file_path='x'), self.root), 0)


class WatchRunTest(unittest.TestCase):
    def journal(self, events):
        directory = Path(tempfile.mkdtemp())
        path = directory / 't1.jsonl'
        path.write_text(''.join(json.dumps(e) + '\n' for e in events))
        return directory, path

    def test_decision_point_and_end(self):
        directory, path = self.journal([{'event': 'run_start', 'id': 'r1', 'unix_s': 0.0, 'output': 'logs/none.txt',
                                         'systemd_unit': 'u.service'}])
        old = watch_run.LOGS
        watch_run.LOGS = directory
        times = [10.0, 400.0, 500.0, 600.0]
        out = io.StringIO()

        def clock():
            return times.pop(0) if len(times) > 1 else times[0]

        def sleep(_):
            if next(iter([0])) == 0 and 'decision point' in out.getvalue() and 'r1' not in path.read_text()[60:]:
                with path.open('a') as handle:
                    handle.write(json.dumps({'event': 'run_end', 'id': 'r1', 'unix_s': 550.0, 'returncode': 0}) + '\n')
        try:
            watch_run.watch("t1", at=300, poll=0, clock=clock, sleep=sleep, out=out, grace=0)
        finally:
            watch_run.LOGS = old
        text = out.getvalue()
        self.assertIn('still running after 400 s (decision point)', text)
        self.assertIn('systemctl --user stop u.service', text)
        self.assertIn('Run r1 ended after 550 s: exit 0', text)

    def test_a_chained_run_is_picked_up(self):
        directory, path = self.journal([{'event': 'run_start', 'id': 'r1', 'unix_s': 0.0, 'output': 'x'}])
        steps = []

        def sleep(_):   # first sleep: r1 ends and r2 starts a moment later; later: r2 ends
            steps.append(1)
            with path.open('a') as handle:
                if len(steps) == 1:
                    handle.write(json.dumps({'event': 'run_end', 'id': 'r1', 'unix_s': 5.0, 'returncode': 0}) + '\n')
                elif len(steps) == 2:
                    handle.write(json.dumps({'event': 'run_start', 'id': 'r2', 'unix_s': 6.0, 'output': 'x'}) + '\n')
                elif len(steps) == 3:
                    handle.write(json.dumps({'event': 'run_end', 'id': 'r2', 'unix_s': 9.0, 'returncode': 0}) + '\n')
        old = watch_run.LOGS
        watch_run.LOGS = directory
        out = io.StringIO()
        try:
            ticks = iter(range(7, 10**6))
            watch_run.watch('t1', at=300, poll=0, clock=lambda: float(next(ticks)), sleep=sleep, out=out, grace=15)
        finally:
            watch_run.LOGS = old
        self.assertIn('Run r1 ended', out.getvalue())
        self.assertIn('Run r2 ended', out.getvalue())

    def test_nothing_to_watch(self):
        directory, _ = self.journal([])
        old = watch_run.LOGS
        watch_run.LOGS = directory
        out = io.StringIO()
        try:
            self.assertEqual(watch_run.watch('t1', out=out), 0)
        finally:
            watch_run.LOGS = old
        self.assertIn('No unfinished', out.getvalue())


if __name__ == '__main__':
    unittest.main()
