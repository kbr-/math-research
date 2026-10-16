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

    def test_refuses_no_match_several_matches_and_a_split_passage_inside_lines(self):
        with self.assertRaisesRegex(ValueError, 'no line-aligned place and 0 places within or across lines'):
            replace_text.replace(PLAN, '- missing item.', 'x')
        with self.assertRaisesRegex(ValueError, 'no line-aligned place and 2 places within or across lines'):
            replace_text.replace('x a b y\nz a b w\n', 'a b', 'c')
        # A passage that crosses a line break but starts mid-line is still refused.
        with self.assertRaisesRegex(ValueError, 'matches 0 line-aligned places'):
            replace_text.replace(PLAN, 'step, wrapped\nacross', 'x')
        with self.assertRaisesRegex(ValueError, 'matches 2 line-aligned places'):
            replace_text.replace('a b\n  a\n  b\n', 'a b', 'x')

    def test_a_one_line_passage_inside_a_longer_line_is_replaced_there(self):
        # 16 October 2026: a notebook paragraph kept on one line held the passage mid-line.
        text = '<p>One <a href="#x">old link</a>. More.</p>\nnext\n'
        updated, line = replace_text.replace(text, '<a href="#x">old link</a>.', '<a href="#y">new link</a>.')
        self.assertEqual((updated, line), ('<p>One <a href="#y">new link</a>. More.</p>\nnext\n', 1))
        updated, _ = replace_text.replace(PLAN, 'step,', 'stage,')
        self.assertEqual(updated, PLAN.replace('first step,', 'first stage,'))
        # The old refusals of passages inside a line now replace them, on a continuation line too.
        updated, line = replace_text.replace(PLAN, 'are ours.', 'are theirs.')
        self.assertEqual((updated, line), (PLAN.replace('route are ours.', 'route are theirs.'), 5))
        updated, _ = replace_text.replace(PLAN, '- the alert route: the receiver', '- the alert path: the receiver')
        self.assertEqual(updated, PLAN.replace('alert route', 'alert path'))

    def test_an_inline_passage_neither_starts_inside_a_word_nor_hides_an_overlap(self):
        with self.assertRaisesRegex(ValueError, '0 places within or across lines'):
            replace_text.replace('a misstep, here\n', 'step,', 'stage,')
        with self.assertRaisesRegex(ValueError, '2 places within or across lines'):
            replace_text.replace('x a a a y\n', 'a a', 'b')
        # A passage starting mid-line and crossing a line break takes a one-line replacement over its whole span.
        updated, line = replace_text.replace('the wrapped\nstep, here and\nthere.\n', 'step, here and there', 'stage')
        self.assertEqual((updated, line), ('the wrapped\nstage.\n', 2))
        # It never crosses a blank line, which would merge two paragraphs.
        with self.assertRaisesRegex(ValueError, '0 places within or across lines'):
            replace_text.replace('one step, here\n\nand there.\n', 'step, here and there', 'stage')
        # A multi-line replacement of a passage found only inside a line is refused.
        with self.assertRaisesRegex(ValueError, 'matches 0 line-aligned places'):
            replace_text.replace('x step, y\n', 'step,', 'one\ntwo')
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
        self.assertIn('matches no line-aligned place and 0 places within or across lines', err.getvalue())
        self.assertIn('replaced the passage at line 6', out.getvalue())
        self.assertTrue((tmp / 'plan.md').read_text().endswith('- **Next question?** Settled.\n'))

    def test_new_text_older_than_the_old_text_is_refused(self):
        # 16 October 2026: a failed write left an earlier edit's new-text file, which then replaced a passage.
        import os
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / 'plan.md').write_text(PLAN)
            (tmp / 'new').write_text('Settled.')
            (tmp / 'old').write_text('Answer.')
            os.utime(tmp / 'new', (1000, 1000))
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(replace_text.main(['replace_text.py', str(tmp / 'plan.md'), str(tmp / 'old'),
                                                    str(tmp / 'new')]), 1)
            self.assertIn('written before', err.getvalue())
            self.assertEqual((tmp / 'plan.md').read_text(), PLAN)

    def test_new_text_ending_inside_a_tag_is_refused(self):
        # 16 October 2026: a cut byte left "</p" at the end of the new text.
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / 'page.html').write_text('<p>Answer.</p>\n')
            (tmp / 'old').write_text('<p>Answer.</p>')
            (tmp / 'new').write_text('<p>Settled.</p')
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(replace_text.main(['replace_text.py', str(tmp / 'page.html'), str(tmp / 'old'),
                                                    str(tmp / 'new')]), 1)
            self.assertIn('ends inside a tag', err.getvalue())
            (tmp / 'new').write_text('Settled: 1 < 2 and a<b')     # a comparison, not a tag, passes
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(replace_text.main(['replace_text.py', str(tmp / 'page.html'), str(tmp / 'old'),
                                                    str(tmp / 'new')]), 0)


if __name__ == '__main__':
    unittest.main()
