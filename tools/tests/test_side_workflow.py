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
        (d/'notebook.html').write_text('<section id="research-record"><article id="side-entry" data-kind="review" data-route="side-test" data-claims="none" data-claim-note="Fixture"><p class="entry-meta">Test.</p><!-- TIMING side_turn --></article></section>')
        self.command('compute.sh','start','side_turn','--model','Test model, high','--notebook','test')
        result=self.command('tools/finish-turn.py','side_turn','--notebook','test')
        self.assertIn('in test:',result.stdout)
        self.assertEqual(main.read_bytes(),before)
        self.assertIn('timing-table',(d/'notebook.html').read_text())

if __name__=='__main__':unittest.main()

class SideIntegration(SideWorkflow):
    def test_resume_only_selected_context(self):
        create('test','Test',self.ctx,self.root)
        resume=module('resume')
        for file in resume.FILES:
            p=self.root/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('Rule fixture')
        parts=resume.bundle(self.root,notebook='test')
        content=''.join(body for _,body,_,_ in parts)
        self.assertIn('Test side goal',content)
        self.assertNotIn('id="origin"',content)
    def test_independent_git_branch_merge(self):
        subprocess.run(['git','add','.'],cwd=self.root,check=True)
        def git(*args):return subprocess.check_output(['git',*args],cwd=self.root,text=True,stderr=subprocess.DEVNULL)
        git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','base')
        base=git('rev-parse','HEAD').strip()
        git('switch','-qc','left');create('alpha','Alpha',self.ctx,self.root);git('add','research')
        git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','alpha')
        git('switch','-qc','right',base);create('beta','Beta',self.ctx,self.root);git('add','research')
        git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','beta')
        git('-c','user.name=Test','-c','user.email=test@example.invalid','merge','--no-edit','left')
        self.assertTrue((self.root/'research/branches/alpha/notebook.html').exists())
        self.assertTrue((self.root/'research/branches/beta/notebook.html').exists())
    def test_failed_and_interrupted_setup_is_recoverable(self):
        import copy
        from notebooks import catalogue
        bad=copy.deepcopy(self.ctx);bad['goal']='word '*1000
        with self.assertRaises(ValueError):create('too-big','Too big',bad,self.root)
        self.assertNotIn('too-big',catalogue(self.root))
        interrupted=self.root/'research/branches/.creating-interrupted'
        interrupted.mkdir(parents=True);(interrupted/'notebook.json').write_text('incomplete')
        create('recovered','Recovered',self.ctx,self.root)
        self.assertIn('recovered',catalogue(self.root))
        with self.assertRaises(ValueError):create('recovered','Recovered',self.ctx,self.root)

    def test_cross_notebook_claim_packet_and_citations(self):
        from claim_registry import HEADER,upgrade,import_markdown
        from record_citations import scan_record
        from claim_reviews import Evidence
        create('test','Test',self.ctx,self.root)
        p=self.root/'research/branches/test/notebook.html'
        p.write_text(p.read_text().replace('<h2>Research record</h2>', '<h2>Research record</h2><article id="side-entry"><h4 id="result">Result</h4><p>Working proof uses <a href="https://kbr.is-a.dev/math-research/#origin">original</a>.</p></article>'))
        d=upgrade(import_markdown('# Index\n\n'+HEADER+'| `lem:a` | A | Working | [Proof](https://kbr.is-a.dev/math-research/branches/test/#result) |\n| `lem:b` | B | Working | [Proof](https://kbr.is-a.dev/math-research/#origin) |\n'))
        dependencies=module('claim-dependencies')
        packet=dependencies.metadata_packet(d,'lem:a',self.root)
        self.assertIn('/branches/test/',str(packet))
        report=scan_record(d,self.root)
        self.assertTrue(any(c['target_claim_candidates']==['lem:b'] for c in report['citations']))
        report=dependencies.scan(d,self.root)
        self.assertTrue(any(c['source']=='lem:a' and 'lem:b' in c['targets'] for c in report['candidates']))
        self.assertTrue(Evidence(self.root).sha256('https://kbr.is-a.dev/math-research/branches/test/#result'))
