from datetime import date
import sys
import tempfile
from pathlib import Path
import unittest
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from notebook_context import excerpt


class ReviewTestsTest(unittest.TestCase):
    def test_lists_each_review_with_its_decisive_test(self):
        source = ('<article id="r1" data-kind="review"><p><strong>Decisive test.</strong> Prove the <em>ceiling</em>.</p></article>'
                  '<article id="e1" data-kind="research"><p><strong>Decisive test.</strong> not a review</p></article>'
                  '<article id="r2" data-kind="review"><p>No test here.</p></article>')
        self.assertEqual(excerpt.review_tests(source),
                         'r1\tProve the ceiling.\nr2\t(no Decisive test paragraph)\n')
        self.assertEqual(excerpt.review_tests('<article id="e" data-kind="research"></article>'),
                         '(no review entries)\n')


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

    def test_enclosing_claim_includes_full_proof_only(self):
        article = ('<article id="entry"><h3 id="title">Title</h3>'
                   '<p id="claim">Statement</p><h4>Proof</h4><p>Argument</p></article>')
        source = '<section>' + article + '<article id="next"><p>Next</p></article></section>'
        book = excerpt.Notebook(source, capture_anchors=True)
        for anchor in ('entry', '#claim', 'title'):
            self.assertEqual(book.enclosing_excerpt(anchor), article + '\n')
        with self.assertRaises(ValueError):
            book.excerpt('claim')  # Default structural lookup remains strict.

    def test_enclosing_rejects_ambiguous_or_outside_ids(self):
        for source, anchor in (
            ('<article id="a"><p id="dup"></p><span id="dup"></span></article>', 'dup'),
            ('<article id="dup"><p id="dup"></p></article>', 'dup'),
            ('<section id="living"><p id="outside"></p></section>', 'outside'),
            ('<article id="a"></article>', 'missing'),
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                excerpt.Notebook(source, capture_anchors=True).enclosing_excerpt(anchor)

    def test_enclosing_ignores_math_and_comments(self):
        source = r'''<article id="a"><p id="claim">\(<span id="claim">\)</p>
<!-- <p id="claim"> --> <h4>Proof</h4></article>'''
        self.assertEqual(excerpt.Notebook(source, capture_anchors=True).enclosing_excerpt('claim'),
                         source + '\n')

    def test_enclosing_rejects_incompatible_options(self):
        for args in (['--enclosing'], ['x', '--enclosing', '--current'],
                     ['x', '--enclosing', '--toc'], ['x', '--enclosing', '--backlinks'],
                     ['x', '--enclosing', '--until', 'y']):
            with self.subTest(args=args), patch.object(sys, 'argv', ['notebook-excerpt.py', *args]), \
                    redirect_stderr(StringIO()), self.assertRaises(SystemExit) as failure:
                excerpt.main()
            self.assertEqual(failure.exception.code, 2)

    def test_enclosing_cli_writes_text_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output = Path(temp) / 'notebook.html', Path(temp) / 'excerpt.txt'
            source.write_text('<article id="entry"><p id="claim">Claim</p>'
                              '<h4>Proof</h4><p>Argument</p></article>')
            args = ['notebook-excerpt.py', 'claim', '--enclosing', '--text',
                    '--notebook', 'main', '--out', str(output)]
            with patch.object(sys, 'argv', args), \
                    patch.object(excerpt, 'selected', return_value={'name': 'main', 'source': source}), \
                    patch.object(excerpt, 'observe'):
                excerpt.main()
                self.assertEqual(output.read_text(), 'Claim\nProof\nArgument\n')
                with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as failure:
                    excerpt.main()
                self.assertEqual(failure.exception.code, 2)
                self.assertEqual(output.read_text(), 'Claim\nProof\nArgument\n')

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




class ClaimExcerptsTest(unittest.TestCase):
    def test_named_claims_are_written_with_statement_and_assessment_and_unknown_ones_refused(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('notebook_excerpt_tool', Path(__file__).resolve().parents[1] / 'notebook-excerpt.py')
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        registry = {'claims': [
            {'id': 'lem:first', 'summary': 'First statement.', 'assessment': 'Working proof.',
             'mathematical_status': 'working_proof', 'record': '[Entry](https://example.org/#e1)'},
            {'id': 'prop:second', 'summary': 'Second statement.', 'assessment': 'Conditional.'}]}
        text = tool.claim_excerpts(['prop:second', 'lem:first'], registry)
        self.assertEqual(text.index('prop:second'), 0)                       # in the order asked
        self.assertIn('lem:first\n  Statement: First statement.\n  Assessment: Working proof.\n'
                      '  Status: working_proof\n  Record: [Entry](https://example.org/#e1)\n', text)
        with self.assertRaisesRegex(ValueError, 'not in the registry: lem:absent, thm:gone'):
            tool.claim_excerpts(['lem:first', 'lem:absent', 'thm:gone'], registry)
        registry['claims'].append({'id': 'cor:blank', 'summary': ' '})
        with self.assertRaisesRegex(ValueError, 'registered without a statement: cor:blank'):
            tool.claim_excerpts(['lem:first', 'cor:blank'], registry)


class RecordStatementTest(unittest.TestCase):
    def test_each_claim_carries_its_record_statements_read_once_per_notebook(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('notebook_excerpt_tool', Path(__file__).resolve().parents[1] / 'notebook-excerpt.py')
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'notebook.html').write_text(
                '<article id="e1"><p><strong>Proposition.</strong> There is a placeholder-linear certificate.</p>'
                '<p>Other prose.</p></article><article id="e2"><p>No statement here.</p></article>'
                '<article id="e3"><p><strong>Lemma.</strong> First.</p>'
                '<p id="e3-second"><strong>Theorem.</strong> Second, the claim.</p></article>'
                '<section id="s9"><p>Outside any entry.</p></section>')
            registry = {'claims': [
                {'id': 'prop:w', 'summary': 'There is a certificate.', 'record': '[E](https://x.dev/r/#e1)'},
                {'id': 'lem:v', 'summary': 'Another.', 'record': '[E](https://x.dev/r/#e2)'},
                {'id': 'lem:u', 'summary': 'Unlinked.', 'record': 'Full record'}]}
            text = tool.claim_excerpts(['prop:w', 'lem:v', 'lem:u'], registry, root=root)
            # The record's own wording, which the summary omits, reaches the brief.
            self.assertIn('  Record statement: Proposition. There is a placeholder-linear certificate.\n', text)
            self.assertIn('#e2 has no Lemma, Theorem', text)
            self.assertIn('names no entry anchor', text)
            self.assertIn('read from 1 notebook(s)', text)
            registry['claims'] += [
                {'id': 'thm:t', 'summary': 'Second.', 'record': '[E](https://x.dev/r/#e3-second)'},
                {'id': 'lem:s', 'summary': 'Out.', 'record': '[E](https://x.dev/r/#s9)'}]
            anchored = tool.claim_excerpts(['thm:t', 'lem:s'], registry, root=root)
            self.assertLess(anchored.index('Theorem. Second'), anchored.index('Lemma. First'))
            self.assertIn('#s9 is not inside an entry', anchored)
            # Without a root the excerpt is the registry's alone, as before.
            self.assertNotIn('Record statement', tool.claim_excerpts(['prop:w'], registry))

    def test_claims_sharing_an_entry_each_get_their_own_statement_first(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('notebook_excerpt_tool', Path(__file__).resolve().parents[1] / 'notebook-excerpt.py')
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'notebook.html').write_text(
                '<article id="e1"><p><strong>Lemma (sparse survival).</strong> A weight keeps rank.</p>'
                '<ul><li><strong>Lemma (cut-code classes)</strong> cited in a list.</li></ul>'
                '<p>Setup prose first. <strong>Lemma (cut-code classes).</strong> Classes are cosets.</p>'
                '<p><strong>Theorem.</strong> Conjunction rank equals the coset count of the orbit.</p></article>')
            registry = {'claims': [
                {'id': 'lem:cut-code-classes', 'summary': 'Characters share a coordinate.',
                 'record': '[E](https://x.dev/r/#e1)'},
                {'id': 'thm:conjunction-rank', 'summary': 'Conjunction multiplication rank equals the orbit coset count.',
                 'record': '[E](https://x.dev/r/#e1)'}]}
            first = lambda ident: tool.claim_excerpts([ident], registry, root=root).split('Record statement: ')[1]
            # By the label naming the claim, then by the summary's words.
            self.assertTrue(first('lem:cut-code-classes').startswith('Lemma (cut-code classes).'))
            self.assertTrue(first('thm:conjunction-rank').startswith('Theorem. Conjunction'))
            # The list item's bold reference is not taken for a statement.
            self.assertNotIn('cited in a list', tool.claim_excerpts(['lem:cut-code-classes'], registry, root=root))


class LivingAndTocTest(unittest.TestCase):
    def test_the_tail_parse_agrees_with_the_full_parse(self):
        entries = ''.join(
            f'<article id="entry-2026-10-{day:02d}-e{day}"><h3>{day} October 2026 — Title {day}</h3>'
            f'<p>Body \\(a&lt;b\\) and \\(<article>\\).</p><!-- <article id="fake"> --></article>\n'
            for day in range(1, 15))
        source = ('<section id="where-we-stand"><p>Living.</p></section>\n'
                  f'<section id="research-record">\n{entries}</section>\n')
        book = excerpt.Notebook(source)
        for tail in (1, 3, 10, 14, 20):
            with self.subTest(tail=tail):
                prefix, toc, omitted = excerpt.living_and_toc(source, tail)
                self.assertEqual(prefix, source[:book.anchor('research-record')['start']])
                self.assertEqual((toc, omitted), book.toc(tail=tail))
        with self.assertRaises(ValueError):
            excerpt.living_and_toc('<section id="x"></section>')


class ReadLogTest(unittest.TestCase):
    def test_the_anchors_an_excerpt_prints_are_logged(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            excerpt.log_read(folder, 'main', ['a2', 'a1', 'a2'])
            [row] = [json.loads(line) for line in (Path(folder) / excerpt.READ_LOG).read_text().splitlines()]
            self.assertEqual((row['notebook'], row['anchors']), ('main', ['a1', 'a2']))
            blocker = Path(folder) / 'file'
            blocker.write_text('')
            excerpt.log_read(blocker, 'main', ['a'])        # a log that cannot be written is not an error


if __name__ == '__main__':
    unittest.main()
