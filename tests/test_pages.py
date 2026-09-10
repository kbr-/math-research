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


class PagesBuild(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='math-pages-')
        self.root = Path(self.temp.name)
        (self.root / 'index.html').write_text((ROOT / 'index.html').read_text())
        (self.root / 'notebook.html').write_text('<h1>Example</h1>\\[x^2 + y^2 = z^2\\]')
        (self.root / 'LICENSES').mkdir()
        (self.root / 'LICENSES/MIT.txt').write_text((ROOT / 'LICENSES/MIT.txt').read_text())
        (self.root / 'private').mkdir()
        (self.root / 'private/secret.txt').write_text('must not be published')
        self.out = self.root / 'site'

    def tearDown(self):
        self.temp.cleanup()

    def test_only_rendered_public_files_are_built(self):
        revision = build(self.out, root=self.root)
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
        first = build(self.out, root=self.root)
        self.assertEqual(build(self.out, root=self.root), first)
        (self.root / 'notebook.html').write_text('<h1>New result</h1>')
        self.assertNotEqual(build(self.out, root=self.root), first)

    def test_local_snapshot_keeps_live_configuration(self):
        template, notebook, revision = snapshot(self.root)
        self.assertIn("mode: 'live', revisionUrl: '/revision', pollMs: 1000", template)
        self.assertIn('Example', notebook)
        self.assertEqual(len(revision), 64)

    def test_update_url_works_under_project_subpath(self):
        build(self.out, root=self.root)
        page = (self.out / 'index.html').read_text()
        self.assertIn('"revisionUrl": "./revision.json"', page)
        self.assertEqual(urljoin('https://example.github.io/math-research/', './revision.json'),
                         'https://example.github.io/math-research/revision.json')

    def test_refuses_unexpected_output_files(self):
        self.out.mkdir()
        (self.out / 'private.txt').write_text('do not publish')
        with self.assertRaises(ValueError):
            build(self.out, root=self.root)
        self.assertFalse((self.out / 'index.html').exists())

    def test_requires_template_markers(self):
        (self.root / 'index.html').write_text('<html>unrecognized template</html>')
        with self.assertRaises(ValueError):
            build(self.out, root=self.root)


if __name__ == '__main__':
    unittest.main()
