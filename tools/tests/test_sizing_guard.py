import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CS = SourceFileLoader('compute_sh', str(ROOT / 'compute.sh')).load_module()


def run(rid, command, t0, t1, rc=0, **end):
    return [dict(event='run_start', id=rid, command=command, monotonic_s=t0),
            dict(event='run_end', id=rid, returncode=rc, timed_out=False, interrupted=False, monotonic_s=t1, **end)]


class SizingGuardTest(unittest.TestCase):
    CMD = ['python3', 'research/x/check.py', 'out.json', 'N=8']

    def test_completed_run_of_same_program_sizes(self):
        events = run('abc', ['python3', 'research/x/check.py', 'small.json', 'N=6'], 10.0, 70.0)
        self.assertEqual(CS.sizing_error(events, 'abc', self.CMD, 900), (None, 60.0))

    def test_unknown_id_is_refused(self):
        self.assertIn('no run with that id', CS.sizing_error([], 'abc', self.CMD, 900)[0])

    def test_failed_or_timed_out_run_is_refused(self):
        self.assertIn('did not complete', CS.sizing_error(run('a', self.CMD, 0, 5, rc=1), 'a', self.CMD, 900)[0])
        events = run('b', self.CMD, 0, 5)
        events[1]['timed_out'] = True
        self.assertIn('did not complete', CS.sizing_error(events, 'b', self.CMD, 900)[0])

    def test_other_program_is_refused(self):
        events = run('c', ['python3', 'research/x/other.py'], 0, 5)
        self.assertIn('other.py', CS.sizing_error(events, 'c', self.CMD, 900)[0])

    def test_expect_below_measured_time_is_refused(self):
        self.assertIn('below', CS.sizing_error(run('d', self.CMD, 0, 1000), 'd', self.CMD, 900)[0])

    def test_program_key_uses_script_or_executable(self):
        self.assertEqual(CS.program_key(['Singular', '-q', 'a/b.sing']), 'b.sing')
        self.assertEqual(CS.program_key(['gp', '-q', 'c.gp']), 'c.gp')
        self.assertEqual(CS.program_key(['./kernel', '8']), 'kernel')


if __name__ == '__main__':
    unittest.main()
