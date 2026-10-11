import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('build_entry_citations', ROOT / 'tools' / 'build_entry_citations.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class BuildEntryCitationsTest(unittest.TestCase):
    def test_only_claimless_build_entries_are_listed_with_what_they_cite(self):
        def entry(ident, tags, general):
            return f'<article id="{ident}" data-kind="research" {tags}><p>x</p>{general}</article>'
        cited = '<p><strong>General statement.</strong> None; prop:some-count is cited as the latest, not as related.</p>'
        plain = '<p><strong>General statement.</strong> None: a build has no claim.</p>'
        text = (entry('a', 'data-build="one" data-claims="none"', cited)
                + entry('b', 'data-build="two" data-claims="none"', plain)
                + entry('c', 'data-lead="x:1" data-claims="none"', cited)
                + entry('d', 'data-build="three" data-claims="lem:real"', cited)
                + entry('e', 'data-build="four" data-claims="none"', ''))
        found = tool.build_entries(text)
        self.assertEqual([(ident, claims) for ident, claims, _ in found],
                         [('a', ['prop:some-count']), ('b', []), ('e', [])])
        self.assertIn('not as related', found[0][2])
        self.assertEqual(found[2][2], '')


if __name__ == '__main__':
    unittest.main()
