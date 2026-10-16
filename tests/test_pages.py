import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server import snapshot
from tools.build_pages import build, OUTPUT_FILES

SITE = 'https://example.github.io/math-research/'


class PagesBuild(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='math-pages-')
        self.root = Path(self.temp.name)
        (self.root / 'index.html').write_text((ROOT / 'index.html').read_text())
        (self.root / 'notebook.html').write_text('<h1>Example</h1>\\[x^2 + y^2 = z^2\\]')
        (self.root / 'LICENSES').mkdir()
        (self.root / 'LICENSES/MIT.txt').write_text((ROOT / 'LICENSES/MIT.txt').read_text())
        (self.root / 'CITATION.cff').write_text((ROOT / 'CITATION.cff').read_text())
        (self.root / 'private').mkdir()
        (self.root / 'private/secret.txt').write_text('must not be published')
        self.out = self.root / 'site'

    def tearDown(self):
        self.temp.cleanup()

    def test_only_rendered_public_files_are_built(self):
        revision = build(self.out, SITE, root=self.root)
        page = (self.out / 'index.html').read_text()
        self.assertEqual({p.name for p in self.out.iterdir()}, OUTPUT_FILES)
        self.assertIn('<h1>Example</h1>', page)
        self.assertIn('\\[x^2 + y^2 = z^2\\]', page)
        self.assertIn('tex-svg.js', page)
        self.assertNotIn('<!-- NOTEBOOK -->', page)
        self.assertNotIn('__REVISION__', page)
        self.assertNotIn('must not be published', page)
        self.assertIn('"mode": "published"', page)
        self.assertIn('Kamil Braun', page)
        self.assertIn('CC BY 4.0', page)
        self.assertIn('Permission is hereby granted', page)
        self.assertEqual(json.loads((self.out / 'revision.json').read_text())['revision'], revision)

    def test_revision_is_repeatable_and_changes_with_notebook(self):
        first = build(self.out, SITE, root=self.root)
        self.assertEqual(build(self.out, SITE, root=self.root), first)
        (self.root / 'notebook.html').write_text('<h1>New result</h1>')
        self.assertNotEqual(build(self.out, SITE, root=self.root), first)

    def test_local_snapshot_keeps_live_configuration(self):
        template, notebook, revision = snapshot(self.root)
        self.assertIn("mode: 'live', revisionUrl: '/revision', pollMs: 1000", template)
        self.assertIn('Example', notebook)
        self.assertEqual(len(revision), 64)

    def test_update_url_works_under_project_subpath(self):
        build(self.out, SITE, root=self.root)
        page = (self.out / 'index.html').read_text()
        self.assertIn('"revisionUrl": "./revision.json"', page)
        self.assertEqual(urljoin('https://example.github.io/math-research/', './revision.json'),
                         'https://example.github.io/math-research/revision.json')

    def test_citations_follow_the_introduction_and_every_entry(self):
        (self.root / 'notebook.html').write_text(
            '<h1>Goal</h1><p class="intro">The target.</p><section id="where-we-stand"><p>Open.</p></section>'
            '<article class="research-entry" id="entry-2026-09-26-first" data-kind="research">\n'
            '<h3>26 September 2026 — A <em>first</em> result</h3>\n'
            '<p class="entry-meta"><strong>Status:</strong> proved.</p><p>Body one.</p></article>'
            '<article id="entry-2026-10-05-second" data-claim-note="k > 2, no claim."> <h3>5 October 2026 — '
            'Second \\(q<h\\) <em>bound</em></h3><p>Body two.</p></article>'
            '<article data-note="a > b" id="entry-setup"><h3>Setup</h3></article><article id="other"><h3>Not an entry</h3></article>')
        build(self.out, SITE, root=self.root)
        page = (self.out / 'index.html').read_text()
        url = SITE + '#entry-2026-09-26-first'
        self.assertLess(page.index('The target.</p>'), page.index('id="cite-this-notebook"'))
        self.assertLess(page.index('id="cite-this-notebook"'), page.index('id="where-we-stand"'))
        self.assertIn(f'<strong>Cite as:</strong> Kamil Braun, <cite>Main research notebook</cite>, '
                      f'Noemesis research notebooks, <a href="{SITE}">{SITE}</a>', page)
        self.assertIn('<p class="entry-meta"><strong>Status:</strong> proved.</p>\n<p class="entry-cite">Cite as: '
                      'Kamil Braun, “A first result”, Main research notebook, Noemesis research notebooks, '
                      f'26 September 2026, <a href="{url}">{url}</a>.</p><p>Body one.', page)
        self.assertIn('bound</em></h3>\n<p class="entry-cite">Cite as: Kamil Braun, “Second \\(q&lt;h\\) bound”, '
                      'Main research notebook, '
                      'Noemesis research notebooks, 5 October 2026, ', page)
        self.assertIn('Setup</h3>\n<p class="entry-cite">Cite as: Kamil Braun, “Setup”, Main research notebook, '
                      f'Noemesis research notebooks, <a href="{SITE}#entry-setup">', page)
        self.assertEqual(page.count('class="entry-cite"'), 3)
        source = (self.out / 'notebook-source.html').read_text()
        self.assertEqual(source.count('class="entry-cite"'), 3)
        self.assertIn('id="cite-this-notebook"', source)

    def test_author_is_read_from_the_citation_file(self):
        citation = self.root / 'CITATION.cff'
        citation.write_text(citation.read_text().replace('given-names: Kamil', 'given-names: Ada'))
        build(self.out, SITE, root=self.root)
        page = (self.out / 'index.html').read_text()
        self.assertIn('<strong>Author:</strong> Ada Braun.', page)
        self.assertIn('<footer id="notebook-footer">Ada Braun · ', page)
        citation.write_text('cff-version: 1.2.0\ntitle: "No authors"\n')
        with self.assertRaises(ValueError):
            build(self.out, SITE, root=self.root)

    def test_head_names_the_notebook_and_carries_citation_metadata(self):
        (self.root / 'notebook.html').write_text(
            '<h1>Goal</h1><article id="entry-2026-10-05-later"><h3>5 October 2026 — Later</h3></article>'
            '<article id="entry-2026-09-21-first"><h3>21 September 2026 — First</h3></article>'
            '<p>Not an entry: id="entry-2027-01-01-quoted"</p>')
        build(self.out, SITE, root=self.root)
        page = (self.out / 'index.html').read_text()
        head = page[:page.index('</head>')]
        self.assertIn('<title>Main research notebook · Noemesis</title>', head)
        for tag in ('<meta name="citation_title" content="Main research notebook">',
                    '<meta name="citation_author" content="Kamil Braun">',
                    '<meta name="citation_publication_date" content="2026/09/21">',
                    f'<meta name="citation_public_url" content="{SITE}">',
                    f'<link rel="canonical" href="{SITE}">',
                    '<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">'):
            self.assertIn(tag, head)
        record = json.loads(head.split('<script type="application/ld+json">', 1)[1].split('</script>', 1)[0])
        self.assertEqual(record['@type'], 'ScholarlyArticle')
        self.assertEqual(record['author'], [{'@type': 'Person', 'name': 'Kamil Braun'}])
        self.assertEqual((record['datePublished'], record['dateModified']), ('2026-09-21', '2026-10-05'))
        self.assertEqual(record['url'], SITE)
        self.assertEqual(page.count('<title>'), 1)

    def test_head_metadata_escapes_the_title(self):
        (self.root / 'research/branches/alpha').mkdir(parents=True)
        (self.root / 'research/branches/alpha/notebook.html').write_text('<h1>Alpha</h1>')
        (self.root / 'research/branches/alpha/context-budgets.json').write_text('{}')
        (self.root / 'research/branches/alpha/notebook.json').write_text(json.dumps(dict(
            version=1, name='alpha', title='Bounds for x < y & "z"', status='active', parent='main', origin=None)))
        build(self.out, SITE, root=self.root)
        head = (self.out / 'branches/alpha/index.html').read_text().split('</head>', 1)[0]
        self.assertIn('<title>Bounds for x &lt; y &amp; "z" · Noemesis</title>', head)
        self.assertIn('<meta name="citation_title" content="Bounds for x &lt; y &amp; &quot;z&quot;">', head)
        self.assertIn('"headline": "Bounds for x \\u003c y & \\"z\\""', head)
        self.assertIn(f'<link rel="canonical" href="{SITE}branches/alpha/">', head)

    def test_refuses_a_site_url_without_https(self):
        with self.assertRaises(ValueError):
            build(self.out, 'http://example.github.io/math-research/', root=self.root)
        with self.assertRaises(ValueError):
            build(self.out, 'https:///', root=self.root)
        self.assertFalse((self.out / 'index.html').exists())

    def test_refuses_unexpected_output_files(self):
        self.out.mkdir()
        (self.out / 'private.txt').write_text('do not publish')
        with self.assertRaises(ValueError):
            build(self.out, SITE, root=self.root)
        self.assertFalse((self.out / 'index.html').exists())

    def test_requires_template_markers(self):
        (self.root / 'index.html').write_text('<html>unrecognized template</html>')
        with self.assertRaises(ValueError):
            build(self.out, SITE, root=self.root)


if __name__ == '__main__':
    unittest.main()
