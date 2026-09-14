"""Run via compute.sh with the pinned Lake environment available on PATH."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VerificationCacheTest(unittest.TestCase):
    def test_cached_unfinished_proof_is_rejected_and_changed_proof_rebuilt(self):
        with tempfile.NamedTemporaryFile(prefix='VerificationCacheProbe', suffix='.lean',
                                         dir=ROOT / 'claims', delete=False) as temporary:
            source = Path(temporary.name)
        name = source.stem
        header = (f'/-\nClaim: test:verification-cache\n'
                  f'Source: https://example.invalid/#temporary-negative-fixture\n'
                  f'Scope: Temporary verifier regression fixture, never a research claim.\n'
                  f'Declarations: {name}.proof\n-/\nnamespace {name}\n')
        def run(*args):
            return subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        try:
            source.write_text(header + f'theorem proof : True := by sorry\nend {name}\n')
            built = run('lake', 'build', f'claims.{name}')
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            rejected = run('python3', 'verify.py')
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('FAIL:', rejected.stdout)
            self.assertTrue('sorry' in rejected.stdout.lower() or 'warning' in rejected.stdout.lower())
            source.write_text(header + f'theorem proof : True := True.intro\nend {name}\n')
            for _ in range(2):
                verified = run('python3', 'verify.py')
                self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
                commands = [line for line in verified.stdout.splitlines() if line.startswith('$ ')]
                self.assertEqual(commands[0], '$ lake --wfail build')
                self.assertEqual(len(commands), 2)  # Incremental build + cached declaration reports.
                self.assertNotIn('claims/' + source.name, commands[1])
        finally:
            source.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
