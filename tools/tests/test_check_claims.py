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

    def main(self, limit, actions=False):
        slow = lambda base, jobs: time.sleep(0.1) or []
        env = {'GITHUB_ACTIONS': 'true' if actions else ''}
        output = io.StringIO()
        with mock.patch.object(check_claims, 'run', slow), mock.patch.dict(os.environ, env), \
                mock.patch.object(sys, 'argv', ['check-claims.py', '--limit', str(limit)]), \
                contextlib.redirect_stdout(output):
            return check_claims.main(), output.getvalue()

    def test_over_the_limit_fails(self):
        status, output = self.main(0.05)
        self.assertEqual(status, 1)
        self.assertIn('over the 0.05 s limit', output)

    def test_within_the_limit_passes(self):
        self.assertEqual(self.main(5)[0], 0)

    def test_github_actions_has_no_limit(self):
        self.assertEqual(self.main(0.05, actions=True)[0], 0)


if __name__ == '__main__':
    unittest.main()
