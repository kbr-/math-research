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
    def test_notebook_argument_takes_a_path_or_a_registered_name(self):
        from notebooks import notebook_file
        p=self.side()
        self.assertEqual(notebook_file(str(p/'notebook.html'),self.root),p/'notebook.html')
        self.assertEqual(notebook_file('side',self.root),self.root/'research/branches/side/notebook.html')
        self.assertEqual(notebook_file('main',self.root),self.root/'notebook.html')
        with self.assertRaises(SystemExit):notebook_file('no-such-thread',self.root)
    def test_tools_resolve_notebook_arguments_through_the_shared_helper(self):
        tools=Path(__file__).resolve().parents[1]
        # A tool that reads the path directly must also try the name (notebook_context.py does, keeping its budgets).
        raw=[f.name for f in tools.glob('*.py')
             if 'Path(args.notebook)' in (t:=f.read_text()) and 'selected(args.notebook' not in t]
        self.assertEqual(raw,[],'read --notebook through notebooks.notebook_file, which also takes a thread name')
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
