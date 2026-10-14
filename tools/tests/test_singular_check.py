"""Real Singular output/exit controls for assertion-script validation."""
import contextlib
import io
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

TOOLS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import singular_check as tool


class SingularCheckTest(unittest.TestCase):
    def run_script(self, body, mode='direct'):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'check.sing'
            path.write_text('ring guardRing=2,(guardX),dp;\n' + body + '\nquit;\n')
            if mode == 'cli':
                python_runtime_env = os.environ.copy()
                python_runtime_env['PYTHONPATH'] = os.pathsep.join(sys.path)
                result = subprocess.run([sys.executable, tool.__file__, str(path)],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        env=python_runtime_env)
                return result.returncode, result.stdout
            output = io.BytesIO()
            if mode == 'default':
                stream = io.TextIOWrapper(output, encoding='utf-8', write_through=True)
                with contextlib.redirect_stdout(stream):
                    status = tool.main([str(path)])
            else:
                status = tool.main([str(path)], output=output)
            return status, output.getvalue()

    def test_complete_clean_output_is_preserved(self):
        for mode in ('direct', 'default', 'cli'):
            with self.subTest(mode=mode):
                status, output = self.run_script('print("data before completion"); print("PASS calculation"); print("");', mode=mode)
                self.assertEqual(status, 0)
                self.assertEqual(output, b'data before completion\nPASS calculation\n\n')
        error_output = io.BytesIO()
        self.assertEqual(tool.run_script('--invalid-singular-check-option', error_output), 1)
        self.assertIn(b'invalid-singular-check-option', error_output.getvalue())
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'check.sing'
            path.write_text('print("data before completion"); print("PASS calculation"); quit;\n')
            raw = io.BytesIO()
            buffered = io.BufferedWriter(raw, buffer_size=4096)
            self.assertEqual(tool.main([str(path)], output=buffered), 0)
            self.assertEqual(raw.getvalue(), b'data before completion\nPASS calculation\n')

    def test_parser_errors_cannot_be_hidden_by_a_later_pass(self):
        cases = [('poly minor; print("PASS calculation");', b'last reserved name'),
                 ("system(\"sh\", \"echo '  ? stderr diagnostic' >&2\"); print(\"PASS calculation\");", b'stderr diagnostic')]
        for body, marker in cases:
            with self.subTest(marker=marker):
                status, output = self.run_script(body)
                self.assertEqual(status, 1)
                self.assertIn(b'?', output)
                self.assertIn(marker, output)
                self.assertTrue(output.rstrip().endswith(b'PASS calculation'))

    def test_failed_assertion_cannot_be_hidden_by_a_later_pass(self):
        status, output = self.run_script('print("FAILED: polynomial mismatch"); print("PASS calculation");')
        self.assertEqual(status, 1)
        self.assertIn(b'FAILED: polynomial mismatch', output)
        self.assertTrue(output.rstrip().endswith(b'PASS calculation'))

    def test_completion_is_a_final_token_not_a_prefix_or_earlier_line(self):
        for body in ('print("PASSage is data");',
                     'print("PASS calculation"); print("unfinished output");',
                     'print("");'):
            with self.subTest(body=body):
                status, _ = self.run_script(body)
                self.assertEqual(status, 1)

    def test_nonzero_exit_cannot_be_a_successful_completion(self):
        self.assertTrue(tool.acceptable(0, False, b'PASS calculation'))
        self.assertFalse(tool.acceptable(7, False, b'PASS calculation'))


if __name__ == '__main__':
    unittest.main()
