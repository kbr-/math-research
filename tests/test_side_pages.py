import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from branch import create,SECTIONS
from tools.build_pages import build
from server import snapshot

ROOT=Path(__file__).resolve().parents[1]
class SidePages(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        for name in ['index.html','notebook.html','LICENSES/MIT.txt','research/context-budgets.json']:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
        self.ctx={k:'<p>Side content \\(\\alpha\\).</p>' for k in SECTIONS};self.ctx['goal']='Side goal';self.ctx['remaining-route']='<li data-route-item="side-test">Test</li>'
        create('alpha','Alpha',self.ctx,self.root)
    def test_nested_routes_and_no_private_payload(self):
        out=self.root/'site';build(out,self.root)
        side=(out/'branches/alpha/index.html').read_text()
        self.assertIn('"catalogue": "../../notebooks.json"',side)
        self.assertIn('href="../../"',side)
        self.assertIn('"revisionUrl": "./revision.json"',side)
        self.assertNotIn('<!-- THREAD',side)
        self.assertEqual({p.name for p in (out/'branches/alpha').iterdir()},{'index.html','revision.json','notebook-source.html'})
        self.assertEqual(len(json.loads((out/'notebooks.json').read_text())),2)
    def test_live_refresh_is_scoped(self):
        main=snapshot(self.root)[2];side=snapshot(self.root,'alpha')[2]
        p=self.root/'research/branches/alpha/notebook.html';p.write_text(p.read_text().replace('Side content','Edited content'))
        self.assertEqual(snapshot(self.root)[2],main)
        self.assertNotEqual(snapshot(self.root,'alpha')[2],side)
    def test_independent_setup_and_status_preserve_record(self):
        create('beta','Beta',self.ctx,self.root)
        before=(self.root/'research/branches/alpha/notebook.html').read_bytes()
        self.assertEqual(before,(self.root/'research/branches/alpha/notebook.html').read_bytes())
        meta=self.root/'research/branches/alpha/notebook.json';data=json.loads(meta.read_text());data['status']='completed';meta.write_text(json.dumps(data))
        self.assertIn('completed',snapshot(self.root,'alpha')[0])
        self.assertEqual(before,(self.root/'research/branches/alpha/notebook.html').read_bytes())

if __name__=='__main__':unittest.main()
