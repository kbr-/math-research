import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from branch import create, SECTIONS
from notebooks import selected, select
from notebook_context import check
from test_finish_turn import FinalizationTest
TOOLS=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,TOOLS/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class SideWorkflow(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        (self.root/'research').mkdir();(self.root/'research/context-budgets.json').write_bytes((TOOLS.parent/'research/context-budgets.json').read_bytes())
        self.ctx={key:'<p>Initial context, no result.</p>' for key in SECTIONS};self.ctx['goal']='Test side goal'
        self.ctx['remaining-route']='<ol><li data-route-item="side-test">Test obligation</li></ol>'
        (self.root/'notebook.html').write_text('<section id="research-record"><article id="origin">old</article></section>')
        subprocess.run(['git','init','-q'],cwd=self.root,check=True)
    def test_create_selection_budgets_and_origin(self):
        create('test','Test',self.ctx,self.root,origin='https://kbr.is-a.dev/math-research/#origin')
        self.assertTrue(check(self.root,'test')['passed'])
        text=(self.root/'research/branches/test/notebook.html').read_text()
        self.assertNotIn('<article',text)
        select('test',self.root);self.assertEqual(selected(root=self.root)['name'],'test')
        self.assertEqual(selected('main',self.root)['name'],'main')
        with self.assertRaises(ValueError):create('test','Test',self.ctx,self.root)
        with self.assertRaises(ValueError):create('other','Test',self.ctx,self.root,origin='https://kbr.is-a.dev/math-research/#missing')
    def test_append_guard_deletion_and_mutation(self):
        create('test','Test',self.ctx,self.root)
        p=self.root/'research/branches/test/notebook.html';p.write_text(p.read_text().replace('</section>\n','</section>\n',1).replace('<h2>Research record</h2>','<h2>Research record</h2><article id="a">original</article>'))
        subprocess.run(['git','add','.'],cwd=self.root,check=True)
        subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','base'],cwd=self.root,check=True)
        guard=module('check-append-only')
        self.assertEqual(guard.check(self.root,'HEAD'),([],[]))
        p.write_text(p.read_text().replace('original','changed'))
        self.assertTrue(guard.check(self.root,'HEAD')[1])
        import shutil
        shutil.rmtree(p.parent)
        self.assertTrue(guard.check(self.root,'HEAD')[0])

class SideFinalization(FinalizationTest):
    def test_side_finish_does_not_touch_main(self):
        # Fixture has permissive budget regions, so initialize a registered notebook
        # manually to exercise the actual finalizer with independent content.
        d=self.root/'research/branches/test';d.mkdir(parents=True)
        (d/'notebook.json').write_text(json.dumps(dict(version=1,name='test',title='Test',status='active',parent='main',origin=None)))
        (d/'context-budgets.json').write_bytes((self.root/'research/context-budgets.json').read_bytes())
        main=self.root/'notebook.html';before=main.read_bytes() if main.exists() else b''
        if not main.exists():main.write_text('<section id="research-record"></section>');before=main.read_bytes()
        (d/'notebook.html').write_text('<section id="research-record"><article id="side-entry" data-kind="review" data-route="side-test" data-claims="none" data-claim-note="Fixture"><p class="entry-meta">Test.</p><!-- TIMING test_turn --></article></section>')
        result=self.command('tools/finish-turn.py','test_turn','--notebook','test')
        self.assertIn('in test:',result.stdout)
        self.assertEqual(main.read_bytes(),before)
        self.assertIn('timing-table',(d/'notebook.html').read_text())

if __name__=='__main__':unittest.main()
