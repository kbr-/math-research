import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from notebooks import catalogue, selected, public_target, resolve_anchor
from claim_registry import local_target

class NotebooksTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'notebook.html').write_text('<section id="shared"></section>')
    def side(self,name='side'):
        p=self.root/'research/branches'/name;p.mkdir(parents=True)
        (p/'notebook.json').write_text(json.dumps(dict(version=1,name=name,title='Side',status='active',parent='main',origin=None)))
        (p/'notebook.html').write_text('<section id="shared"></section><article id="side-only"></article>')
        (p/'context-budgets.json').write_text('{}')
        return p
    def test_main_compatibility(self):
        self.assertEqual(catalogue(self.root)['main']['source'],'notebook.html')
        self.assertEqual(local_target('https://kbr.is-a.dev/math-research/#shared',self.root),(self.root/'notebook.html','shared'))
    def test_qualified_and_ambiguous(self):
        p=self.side()
        self.assertEqual(local_target('https://kbr.is-a.dev/math-research/branches/side/#side-only',self.root),(p/'notebook.html','side-only'))
        self.assertEqual(resolve_anchor('side-only',root=self.root)['name'],'side')
        with self.assertRaises(ValueError):resolve_anchor('shared',root=self.root)
        self.assertEqual(resolve_anchor('shared','side',self.root)['name'],'side')
    def test_bad_names_missing_and_cycles(self):
        self.side('../escape')
        with self.assertRaises(ValueError):selected('../escape',self.root)
        p=self.side();m=json.loads((p/'notebook.json').read_text());m['parent']='side';(p/'notebook.json').write_text(json.dumps(m))
        with self.assertRaises(ValueError):catalogue(self.root)
    def test_missing_file_fails(self):
        p=self.side();(p/'notebook.html').unlink()
        with self.assertRaises(ValueError):catalogue(self.root)
    def test_symlink_rejected(self):
        p=self.side();(p/'notebook.html').unlink();(p/'notebook.html').symlink_to(self.root/'notebook.html')
        with self.assertRaises(ValueError):catalogue(self.root)

if __name__=='__main__':unittest.main()
