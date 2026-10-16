import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

TOOLS =pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import test_can_fail  # noqa: E402


class TestCanFailTest(unittest.TestCase):
    def test_a_test_whose_assertion_ignores_the_tool_is_flagged_and_a_real_one_is_not(self):
        # 16 October 2026: a skeleton-check test called the tool and then compared an immutable string with
        # itself. The fixture tool sits in scratch, named as the tools root, not inside tools/ where tests running
        # in parallel would see it.
        folder = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        self.addCleanup(lambda: [sys.modules.pop(name, None) for name in ('fixture_tool', 'test_fixture')])
        self.addCleanup(lambda: sys.path.remove(str(folder)) if str(folder) in sys.path else None)
        (folder / 'fixture_tool.py').write_text(
            'def skeleton(text):\n    return ["general statement"]\n\n'
            'def validate(text):\n    if "bad" in text:\n        raise ValueError(text)\n')
        test_file = folder / 'test_fixture.py'
        test_file.write_text(textwrap.dedent('''
            import unittest
            import fixture_tool as tool

            class Fixture(unittest.TestCase):
                def test_cannot_fail(self):
                    expected = 'general statement'
                    tool.skeleton('<p>draft</p>')
                    self.assertEqual(expected, 'general statement')

                def test_can_fail(self):
                    self.assertIn('general statement', tool.skeleton('<p>draft</p>'))

                def test_truthy_result(self):
                    self.assertTrue(tool.skeleton('<p>draft</p>'))

                def test_passing_path_of_a_validator(self):
                    tool.validate('<p>good</p>')

                def test_not_judged(self):
                    self.assertEqual(len('ab'), 2)
        '''))
        check = lambda name: test_can_fail.check(test_file, f'Fixture.{name}', tools=folder)
        self.assertEqual(check('test_cannot_fail'), (True, ['fixture_tool.skeleton']))
        self.assertEqual(check('test_can_fail'), (False, ['fixture_tool.skeleton']))
        # A truthy assertion fails on the falsy wrong value, and a validator's passing path on the refusal.
        self.assertEqual(check('test_truthy_result'), (False, ['fixture_tool.skeleton']))
        self.assertEqual(check('test_passing_path_of_a_validator'), (False, ['fixture_tool.validate']))
        self.assertEqual(check('test_not_judged'), (False, []))

    def test_tests_are_placed_by_their_definition_line_even_when_two_classes_share_a_name(self):
        text = textwrap.dedent('''
            class A:
                def test_main(self):
                    pass

            class B:
                def helper(self):
                    pass

                def test_main(self):
                    pass
        ''')
        self.assertEqual(test_can_fail.enclosing_tests(text), {3: 'A.test_main', 10: 'B.test_main'})

    def test_staged_mode_reads_the_staged_file_whose_lines_the_diff_numbers(self):
        repo = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, repo, True)
        git = lambda *args: subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)
        git('init', '-q')
        git('config', 'user.email', 't@t')
        git('config', 'user.name', 't')
        tests = repo / 'tools' / 'tests'
        tests.mkdir(parents=True)
        path = tests / 'test_x.py'
        path.write_text('class A:\n    def test_old(self):\n        pass\n')
        git('add', '.')
        git('commit', '-qm', 'one')
        path.write_text('class A:\n    def test_old(self):\n        pass\n\n    def test_new(self):\n        pass\n')
        git('add', '.')
        # An unstaged edit above the new test moves its working-tree line.
        path.write_text('class A:\n    def test_inserted(self):\n        pass\n\n    def test_old(self):\n        pass\n\n'
                        '    def test_new(self):\n        pass\n')
        with mock.patch.object(test_can_fail, 'ROOT', repo):
            self.assertEqual(test_can_fail.added_tests(staged=True), ['tools/tests/test_x.py::A.test_new'])


if __name__ == '__main__':
    unittest.main()
