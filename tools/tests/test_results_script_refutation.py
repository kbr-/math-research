"""The launcher's check that a script under research/results names an output that would refute it."""
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CS = SourceFileLoader('compute_sh', str(ROOT / 'compute.sh')).load_module()
BOTH = ('"""Statement.\nRefuted by: a rank above n in any of the nine cases.\n'
        'Possible because: the search for the rank does not use the bound.\n"""\n')


def script(folder, text, name='control.py', where=('research', 'results', 'run_01')):
    path = Path(folder).joinpath(*where, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def check(*paths):
    return dict(CS.scripts_without_refuting_outcome(['python3', *map(str, paths)]))


class ResultsScriptRefutationTest(unittest.TestCase):
    def test_both_labelled_lines_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(check(script(folder, BOTH + 'print(1)\n')), {})

    def test_each_missing_line_is_named(self):
        with tempfile.TemporaryDirectory() as folder:
            neither = script(folder, '"""Expectation: the value is 3."""\nprint(1)\n', 'a.py')
            no_reason = script(folder, '"""Refuted by: a value of four in any case.\n"""\nprint(1)\n', 'b.py')
            found = check(neither, no_reason)
            self.assertEqual(len(found[str(neither)]), 2)
            self.assertEqual(len(found[str(no_reason)]), 1)
            self.assertIn('Possible because:', found[str(no_reason)][0])

    def test_the_subjects_own_words_in_passing_do_not_count(self):
        with tempfile.TemporaryDirectory() as folder:
            passing = script(folder, '"""The refutation degree of H; every refutation of H is replayed.\n'
                                     'Which of the possible values occur?  A degree above six would refute it."""\n')
            self.assertEqual(len(check(passing)[str(passing)]), 2)

    def test_a_label_needs_five_words(self):
        with tempfile.TemporaryDirectory() as folder:
            short = script(folder, '"""Refuted by: failure.\nPossible because: yes.\n"""\n')
            self.assertEqual(len(check(short)[str(short)]), 2)

    def test_a_label_inside_a_line_does_not_count(self):
        with tempfile.TemporaryDirectory() as folder:
            quoted = script(folder, 'print("Refuted by: a rank above n in any case")\n'
                                    'x = "see Possible because: the search does not use it"\n')
            self.assertEqual(len(check(quoted)[str(quoted)]), 2)
            comment = script(folder, '# Refuted by: a rank above n in any case.\n'
                                     '#   Possible because: the search does not use the bound.\n', 'd.py')
            self.assertEqual(check(comment), {})

    def test_a_script_that_tests_nothing_says_so(self):
        with tempfile.TemporaryDirectory() as folder:
            table = script(folder, '"""No statement tested: this script tabulates saved output for the entry.\n"""\n')
            self.assertEqual(check(table), {})
            bare = script(folder, '"""No statement tested: tables.\n"""\n', 'c.py')
            self.assertIn(str(bare), check(bare))

    def test_lines_far_below_the_head_do_not_count(self):
        with tempfile.TemporaryDirectory() as folder:
            late = script(folder, '"""Expectation."""\n' + 'x = 1\n' * CS.REFUTATION_HEAD_LINES + BOTH)
            self.assertEqual(len(check(late)), 1)

    def test_sources_drivers_data_and_scripts_elsewhere_are_not_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            others = [script(folder, 'print(1)\n', where=('scratch',)), script(folder, '{}\n', 'table.json'),
                      script(folder, 'int main(){}\n', 'kernel.c'), script(folder, 'int main(){}\n', 'kernel.cpp'),
                      script(folder, 'echo 1\n', 'drive.sh')]
            self.assertEqual(check(*others), {})

    def test_the_launcher_itself_refuses_the_run(self):
        with tempfile.TemporaryDirectory() as folder:
            path = script(folder, '"""Expectation: the value is 3."""\nprint(1)\n')
            for args in (['git', 'init', '-q'], ['git', 'add', '-A'],
                         ['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 's']):
                subprocess.run(args, cwd=folder, check=True, capture_output=True)
            refused = subprocess.run([str(ROOT / 'compute.sh'), '--timeout', '20', 'python3', str(path)],
                                     capture_output=True, text=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn('Refuted by:', refused.stderr)
            self.assertIn('No statement tested:', refused.stderr)


if __name__ == '__main__':
    unittest.main()
