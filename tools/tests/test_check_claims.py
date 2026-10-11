import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import time
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location(
    'check_claims', Path(__file__).resolve().parents[1] / 'check-claims.py')
check_claims = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_claims)


class TimeLimit(unittest.TestCase):
    """check-claims.py fails a passing run that exceeds its wall-time limit, except in GitHub Actions."""

    def main(self, limit, actions=False, warn=False):
        slow = lambda base, jobs: time.sleep(0.1) or []
        env = {'GITHUB_ACTIONS': 'true' if actions else ''}
        output = io.StringIO()
        with mock.patch.object(check_claims, 'run', slow), mock.patch.dict(os.environ, env), \
                mock.patch.object(sys, 'argv', ['check-claims.py', '--limit', str(limit)]
                                  + (['--warn-over-limit'] if warn else [])), \
                contextlib.redirect_stdout(output):
            return check_claims.main(), output.getvalue()

    def test_over_the_limit_fails(self):
        status, output = self.main(0.05)
        self.assertEqual(status, 1)
        self.assertIn('over the 0.05 s limit', output)

    def test_within_the_limit_passes(self):
        self.assertEqual(self.main(5)[0], 0)

    def test_a_push_gets_a_note_not_a_failure(self):
        status, output = self.main(0.05, warn=True)
        self.assertEqual(status, 0)
        self.assertIn('Note: took', output)

    def test_the_limit_grows_with_the_changed_scope(self):
        report = 'note\n{"passed": true, "required_reviews": [{"id": "a"}, {"id": "b"}]}\n'
        self.assertEqual(check_claims.changed_claims(report), 2)
        self.assertEqual(check_claims.changed_claims('no report'), 0)
        times = [('other check', 0.01, 0.01), ('contract', 0.1, 0.1)]
        with mock.patch.dict(check_claims.SCOPE, {'claims': 1000, 'times': times}):
            status, output = self.main(0.05)
        self.assertEqual(status, 0)
        self.assertIn('Changed scope: 1000 claims', output)
        with mock.patch.dict(check_claims.SCOPE, {'claims': 1, 'times': times}):
            self.assertEqual(self.main(0.05)[0], 1)
        # The allowance is the contract's alone: another check over the fixed limit still fails.
        slow_other = [('other check', 0.1, 0.1), ('contract', 0.1, 0.1)]
        with mock.patch.dict(check_claims.SCOPE, {'claims': 1000, 'times': slow_other}):
            self.assertEqual(self.main(0.05)[0], 1)

    def test_a_busy_machine_is_a_note_and_a_slow_check_is_not(self):
        # Over in wall time, within the limit in CPU time: the machine was busy.
        busy = [('other check', 0.1, 0.01), ('contract', 0.01, 0.01)]
        with mock.patch.dict(check_claims.SCOPE, {'claims': 0, 'times': busy}):
            status, output = self.main(0.05)
        self.assertEqual(status, 0)
        self.assertIn('the machine was busy', output)
        # Over in both: the check itself is slow.
        slow = [('other check', 0.1, 0.09), ('contract', 0.01, 0.01)]
        with mock.patch.dict(check_claims.SCOPE, {'claims': 0, 'times': slow}):
            self.assertEqual(self.main(0.05)[0], 1)

    def test_run_reads_scope_and_times_from_the_checks(self):
        report = '{"passed": true, "required_reviews": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}'
        def fake(command):
            contract = 'changed' in command
            return mock.Mock(returncode=0, stdout=report if contract else 'ok', stderr=''), 0.02, 0.01
        with mock.patch.object(check_claims, 'measured', fake), \
                mock.patch.dict(check_claims.SCOPE), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_claims.run('BASE'), [])
            self.assertEqual(check_claims.SCOPE['claims'], 3)
            self.assertEqual(len(check_claims.SCOPE['times']), 6)
            self.assertEqual(check_claims.SCOPE['times'][-1][1:], (0.02, 0.01))

    def test_measured_reports_output_status_and_cpu_time(self):
        result, seconds, cpu = check_claims.measured(
            [sys.executable, '-c', 'import sys; print("out"); print("err", file=sys.stderr); sys.exit(3)'])
        self.assertEqual((result.returncode, result.stdout.strip(), result.stderr.strip()), (3, 'out', 'err'))
        self.assertGreater(seconds, 0)
        self.assertGreaterEqual(cpu, 0)

    def test_github_actions_has_no_limit(self):
        self.assertEqual(self.main(0.05, actions=True)[0], 0)


if __name__ == '__main__':
    unittest.main()
