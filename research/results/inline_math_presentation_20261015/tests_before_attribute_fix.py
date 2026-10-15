import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('check_append_only', Path(__file__).resolve().parents[1] / 'check-append-only.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def body(cell):
    return f'<section id="research-record"><article id="e1"><table><tr><td>{cell}</td></tr></table></article></section>'


class AppendOnlyTest(unittest.TestCase):
    def test_non_breaking_space_is_presentation(self):
        self.assertEqual(MODULE.violations(body('38 / 527'), body('38&nbsp;/&nbsp;527')), ([], []))
        self.assertEqual(MODULE.violations(body('38 / 527'), body('38 / 527')), ([], []))

    def test_link_repair_is_allowed(self):
        self.assertEqual(MODULE.violations(body('see x'), body('see <a href="#y">x</a>')), ([], []))

    def test_text_change_is_rejected(self):
        self.assertEqual(MODULE.violations(body('38 / 527'), body('38 / 528')), ([], ['e1']))

    def test_inline_math_delimiters_may_be_added_around_unchanged_text(self):
        before = r'(\mathbb F_2), \(x+y\), (O(M(log M)))'
        after = r'\(\mathbb F_2\), \(x+y\), \(O(M(log M))\)'
        self.assertEqual(MODULE.violations(body(before), body(after)), ([], []))
        self.assertEqual(MODULE.inline_math_view(after)[0], r'(\mathbb F_2), (x+y), (O(M(log M)))')
        self.assertEqual(MODULE.inline_math_view(r'prefix \(x\)')[0], 'prefix (x)')

    def test_existing_inline_math_cannot_be_removed_or_moved(self):
        for before, after in [(r'\(x\)', '(x)'), (r'\(x\) (y)', r'(x) \(y\)')]:
            self.assertEqual(MODULE.violations(body(before), body(after)), ([], ['e1']))

    def test_math_repair_does_not_allow_changed_content_or_nested_delimiters(self):
        for before, after in [(r'(\alpha+x)', r'\(\alpha+y\)'), (r'\(f(x)\)', r'\(f\(x\)\)'),
                              ('(x)', r'\(\[(x)\]\)')]:
            self.assertEqual(MODULE.violations(body(before), body(after)), ([], ['e1']))
        self.assertIsNone(MODULE.inline_math_view(r'\(f\(x\)'))
        self.assertIsNone(MODULE.inline_math_view(r'\(\[x\)'))

    def test_code_comments_and_displayed_math_are_not_inline_repairs(self):
        for wrapper in ['<code>{}</code>', '<CODE>{}</CODE>', '<pre>{}</pre>', '<script>{}</script>',
                        '<style>{}</style>', '<!--{}-->', r'\[{}\]', '<i title="{}">']:
            self.assertEqual(MODULE.violations(body(wrapper.format('(x)')),
                                             body(wrapper.format(r'\(x\)'))), ([], ['e1']))
            protected = wrapper.format('(x)\nunchanged')
            self.assertEqual(MODULE.violations(body(protected + ' (y)'),
                                             body(protected + r' \(y\)')), ([], []))
        self.assertIsNone(MODULE.inline_math_view(r'<code>\(x\)'))
        self.assertIsNone(MODULE.inline_math_view(r'<CODE>\(x\)'))
        self.assertIsNone(MODULE.inline_math_view(r'<pre>\(x\)'))

    def test_appended_entries_and_their_neighbours(self):
        base = body('x')
        added = base.replace('</section>', '<article id="e2">new</article></section>')
        self.assertEqual(MODULE.violations(base, added), ([], []))                     # the fast path
        self.assertEqual(MODULE.violations(base, added.replace('<td>x', '<td>y')), ([], ['e1']))
        self.assertEqual(MODULE.violations(added, base), (['e2'], []))                 # a deleted last entry
        empty = '<section id="research-record"></section>'
        self.assertEqual(MODULE.violations(empty, body('first')), ([], []))


if __name__ == '__main__':
    unittest.main()
