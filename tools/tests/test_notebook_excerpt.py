from datetime import date
import sys
from pathlib import Path
import unittest
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch

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

    def test_backlinks_are_local_ordered_and_bounded(self):
        source = r'''<section id="living"><a href="#target">living</a></section>
<section id="research-record">
<article id="entry-2026-09-01"><h3>Earlier</h3><a href="#target">earlier</a></article>
<article id="entry-2026-09-02"><h3>Target entry</h3><h4 id="target">Claim</h4>
<a href="#target">self</a></article>
<article id="entry-2026-09-03"><h3>Later</h3>
<a href="#target">one</a>
<a href="https://kbr.is-a.dev/math-research/branches/demo/#%74arget">two</a>
<a href="https://kbr-.github.io/math-research/branches/demo/#target">three</a>
<a href="research/branches/demo/notebook.html#target">four</a>
<a href="notebook.html#target">five</a>
<a href="https://kbr.is-a.dev/math-research/#target">different notebook</a>
<a href="other.html#target">different file</a>
<a href="https://example.com/math-research/branches/demo/#target">external</a>
<a href="https://[invalid/#target">invalid URL</a>
<!-- <a href="#target">comment</a> -->
<p>\(<a href="#target">math</a>\)</p>
<pre>&lt;a href="#target"&gt;escaped&lt;/a&gt;</pre></article>
<article id="undated"><h3>Undated</h3><a href="#target">last</a></article>
</section>'''
        book = excerpt.Notebook(source, capture_links=True)
        opts = dict(source_path='research/branches/demo/notebook.html', route='branches/demo/')
        text, omitted = book.backlinks('target', **opts)
        self.assertEqual(omitted, 0)
        self.assertEqual(len(text.splitlines()), 4)
        self.assertIn('entry-2026-09-01\tearlier\t1 link(s)', text)
        self.assertIn('entry-2026-09-02\tself\t1 link(s)', text)
        self.assertIn('entry-2026-09-03\tlater\t5 link(s)', text)
        text, omitted = book.backlinks('#target', tail=1, since=date(2026, 9, 3), **opts)
        self.assertEqual(omitted, 1)
        self.assertTrue(text.startswith('undated\tundated\tlater\t1 link(s)'))
        with self.assertRaises(ValueError):
            book.backlinks('absent', **opts)
        with self.assertRaises(ValueError):
            book.backlinks('target', tail=0, **opts)

    def test_backlink_mode_rejects_incompatible_options(self):
        for args in (['--backlinks'], ['x', '--backlinks', '--toc'],
                     ['x', '--backlinks', '--until', 'y'], ['x', '--backlinks', '--text']):
            with self.subTest(args=args), patch.object(sys, 'argv', ['notebook-excerpt.py', *args]), \
                    redirect_stderr(StringIO()), self.assertRaises(SystemExit) as failure:
                excerpt.main()
            self.assertEqual(failure.exception.code, 2)


if __name__=='__main__':unittest.main()
