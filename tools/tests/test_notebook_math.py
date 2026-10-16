"""Math delimiters protect comparisons without escaping notebook markup twice."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notebook_math import protect_math


class MathMarkup(unittest.TestCase):
    def test_math_angles_and_existing_entities(self):
        source = r'<p title="keep">\(a<b>c\), \[P_{<a}\n>0\], $$u<v>w$$; \(x&lt;y&gt;z\). $5 to $6.</p>'
        expected = r'<p title="keep">\(a&lt;b&gt;c\), \[P_{&lt;a}\n&gt;0\], $$u&lt;v&gt;w$$; \(x&lt;y&gt;z\). $5 to $6.</p>'
        self.assertEqual(protect_math(source), expected)
        self.assertEqual(protect_math(expected), expected)

    def test_tag_stripping_keeps_the_text_after_a_raw_comparison(self):
        from notebook_math import strip_tags, strip_tags_tight
        import re
        source = r'<p>Prove \(q<h\) for every edge set of bounded incidence <strong>now</strong>.</p>'
        self.assertNotIn('bounded incidence', re.sub(r'<[^>]*>', ' ', source))     # the loss reproduced
        self.assertIn('for every edge set of bounded incidence', strip_tags(source))
        self.assertIn(r'\(q&lt;h\)', strip_tags(source))
        self.assertEqual(strip_tags_tight('<b>a</b>b'), 'ab')

    def test_the_tools_that_read_notebook_prose_keep_it(self):
        import importlib.util
        tools = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('notebook_append', tools / 'notebook-append.py')
        append = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(append)
        follow = r'Continuing: prove \(q<h\) for every edge set of bounded incidence in the window <em>now</em>.'
        self.assertTrue(append.quotes('<p>Next: for every edge set of bounded incidence in the window.</p>', follow))
        import record_search
        self.assertIn('bounded incidence', record_search.plain(follow))
        import lead_queue
        self.assertIn('incidence', lead_queue.content_words('x): ' + follow))
        from record_citations import CitationHTML
        parsed = CitationHTML(r'<p>\(q<h\) and <a href="#x">a link</a></p>')
        self.assertEqual(len(parsed.links), 1)


if __name__ == '__main__':
    unittest.main()
