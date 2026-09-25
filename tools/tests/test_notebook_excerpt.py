from datetime import date
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from notebook_context import excerpt


class ExcerptTest(unittest.TestCase):
    def book(self):
        return excerpt.Notebook('<section id="research-record">'+''.join(
            f'<article id="entry-2026-09-{i:02}"><h3>19 September 2026 — Title {i}</h3><p>body</p></article>'
            for i in range(1,13))+'</section>')

    def test_toc_default_and_date_filter(self):
        text,omitted=self.book().toc()
        self.assertEqual(len(text.splitlines()),10);self.assertEqual(omitted,2)
        text,omitted=self.book().toc(tail=2,since=date(2026,9,10))
        self.assertEqual(len(text.splitlines()),2);self.assertEqual(omitted,1)
        self.assertIn('2026-09-11\tentry-2026-09-11\tTitle 11',text)

    def test_titles_are_bounded_and_undated_retained(self):
        book=excerpt.Notebook('<section id="research-record"><article id="undated-entry"><h3>'+('title '*20)+'</h3></article></section>')
        text,_=book.toc(since=date(2026,9,19))
        self.assertTrue(text.startswith('undated\tundated-entry\t'))
        self.assertEqual(text.count('title'),10);self.assertIn('…',text)

    def test_exact_boundaries_and_math(self):
        source=r'<section id="x"><h3 id="a">One</h3><p>\(a<h3>b\)</p><h3 id="b">Two</h3></section>'
        book=excerpt.Notebook(source)
        self.assertIn(r'\(a<h3>b\)',book.excerpt('a'))
        self.assertNotIn('Two',book.excerpt('a'))
        self.assertEqual(book.excerpt('a'),book.excerpt('a','b'))
        with self.assertRaises(ValueError):book.excerpt('missing')
        with self.assertRaises(ValueError):book.excerpt('b','a')
        with self.assertRaises(ValueError):book.toc(tail=0)

    def test_readable_text(self):
        source=('<article id="e"><h3>Title</h3><p>A <strong>bold</strong>\nclaim \\(a<b &amp; c\\) \\(k&lt;2\\).</p>'
                '<ol><li>one</li><li>two</li></ol><div class="timing-report"><table><tr><td>x</td></tr>'
                '</table>\n<p class="timing-note">note</p>\n</div></article>')
        self.assertEqual(excerpt.readable_text(source),
                         'Title\nA bold claim \\(a<b & c\\) \\(k<2\\).\none\ntwo\n')
        self.assertEqual(excerpt.readable_text('<table><tr><th>k</th><td>v  w</td></tr></table>'),'\tk\tv w\n')

    def test_duplicate_and_unclosed_anchors_fail(self):
        book=excerpt.Notebook('<section id="x"></section><section id="x"></section>')
        with self.assertRaises(ValueError):book.anchor('x')
        with self.assertRaises(ValueError):excerpt.Notebook('<section id="x">')


if __name__=='__main__':unittest.main()
