import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import replace_text  # noqa: E402

PLAN = """- **A question?** Found:
  - first step, wrapped
    across two lines.
  - the alert route: the receiver and
    route are ours.
- **Next question?** Answer.
"""


class ReplaceTextTest(unittest.TestCase):
    def test_a_reflowed_nested_item_keeps_its_level(self):
        updated, line = replace_text.replace(PLAN, '- the alert route: the receiver and route are ours.',
                                             '- the alert route: ours,\n  with a sub-point:\n  - nested.\n')
        self.assertEqual(updated, PLAN.replace('  - the alert route: the receiver and\n    route are ours.',
                                               '  - the alert route: ours,\n    with a sub-point:\n    - nested.'))
        self.assertEqual(line, 4)

    def test_the_replacement_loses_its_own_indentation_for_the_passages(self):
        updated, _ = replace_text.replace(PLAN, '- **Next question?** Answer.', '      - **Next question?** New.\n')
        self.assertTrue(updated.endswith('\n- **Next question?** New.\n'))

    def test_a_replacement_from_a_continuation_line_can_end_with_an_item_one_level_out(self):
        text = '- **Q1?** Answer that\n  wraps here.\n- **Q2?** Two.\n'

        updated, _ = replace_text.replace(text, 'wraps here.', '  wraps here.\n- **Inserted?** New,\n  wrapped.\n')

        self.assertEqual(updated, '- **Q1?** Answer that\n  wraps here.\n- **Inserted?** New,\n  wrapped.\n'
                                  '- **Q2?** Two.\n')

    def test_blank_lines_stay_blank(self):
        updated, _ = replace_text.replace(PLAN, '- first step, wrapped across two lines.', '- one\n\n  more\n')
        self.assertIn('  - one\n\n    more\n', updated)

    def test_refuses_no_match_several_matches_and_a_passage_inside_a_line(self):
        for old, count in (('- missing item.', 0), ('step,', 0), ('are ours.', 0),
                           ('- the alert route: the receiver', 0)):
            with self.subTest(old=old):
                with self.assertRaisesRegex(ValueError, f'matches {count} line-aligned places, not one'):
                    replace_text.replace(PLAN, old, 'x')
        with self.assertRaisesRegex(ValueError, 'matches 2 line-aligned places'):
            replace_text.replace('a b\n  a\n  b\n', 'a b', 'x')
        with self.assertRaisesRegex(ValueError, 'empty'):
            replace_text.replace(PLAN, ' \n', 'x')

    def test_command_line_writes_only_on_success(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / 'plan.md').write_text(PLAN)
        (tmp / 'old').write_text('- **Next question?**\nAnswer.\n')
        (tmp / 'new').write_text('- **Next question?** Settled.\n')
        (tmp / 'bad').write_text('nowhere\n')
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(replace_text.main(['replace_text.py', str(tmp / 'plan.md'), str(tmp / 'bad'),
                                                str(tmp / 'new')]), 1)
            self.assertEqual((tmp / 'plan.md').read_text(), PLAN)
            self.assertEqual(replace_text.main(['replace_text.py', str(tmp / 'plan.md'), str(tmp / 'old'),
                                                str(tmp / 'new')]), 0)
            self.assertEqual(replace_text.main(['replace_text.py', str(tmp / 'plan.md')]), 2)
        self.assertIn('matches 0 line-aligned places', err.getvalue())
        self.assertIn('replaced the passage at line 6', out.getvalue())
        self.assertTrue((tmp / 'plan.md').read_text().endswith('- **Next question?** Settled.\n'))


if __name__ == '__main__':
    unittest.main()
