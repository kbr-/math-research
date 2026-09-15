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
            rejected = run('python3', 'verify.py', '--target', f'claims/{source.name}')
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('FAIL:', rejected.stdout)
            self.assertTrue('sorry' in rejected.stdout.lower() or 'warning' in rejected.stdout.lower())
            source.write_text(header + f'theorem proof : True := True.intro\nend {name}\n')
            for _ in range(2):
                verified = run('python3', 'verify.py', '--target', f'claims.{name}')
                self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
                commands = [line for line in verified.stdout.splitlines() if line.startswith('$ ')]
                self.assertEqual(commands[0], f'$ lake --wfail build claims.{name}')
                self.assertEqual(len(commands), 2)  # Incremental build + cached declaration reports.
                self.assertNotIn('claims/' + source.name, commands[1])
                self.assertIn('PASS: 1 proof files; 0 interface files', verified.stdout)
                self.assertNotIn('Claim file: claims/ModInterpolation.lean', verified.stdout)
            fresh = run('python3', 'verify.py', '--target', f'formalization/claims/{source.name}',
                        '--recheck-sources')
            self.assertEqual(fresh.returncode, 0, fresh.stdout + fresh.stderr)
            commands = [line for line in fresh.stdout.splitlines() if line.startswith('$ ')]
            self.assertEqual(len(commands), 3)
            self.assertTrue(commands[1].endswith('claims/' + source.name))
            for role in ('Kind: interface', 'Status: statement-only'):
                source.write_text(header.replace('Scope:', role + '\nScope:') +
                                  f'def proof : Prop := True\nend {name}\n')
                interface = run('python3', 'verify.py', '--target', f'claims/{source.name}')
                self.assertEqual(interface.returncode, 0, interface.stdout + interface.stderr)
                self.assertIn('PASS: 0 proof files; 1 interface files', interface.stdout)
                self.assertIn(f'def {name}.proof', interface.stdout)
            missing = run('python3', 'verify.py', '--target', 'claims/DoesNotExist.lean')
            self.assertNotEqual(missing.returncode, 0)
            self.assertNotIn('$ lake', missing.stdout)
        finally:
            source.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
