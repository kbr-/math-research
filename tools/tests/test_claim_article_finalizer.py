"""Real accepted-new-claim finalizer flow with versioned article evidence."""
import copy,hashlib,json,subprocess,sys,unittest
from pathlib import Path
import test_finish_turn as fixtures
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import import_markdown,upgrade,HEADER,render
from claim_reviews import Evidence,FIELDS,make_review,coverage

class ArticleFinalizerTest(unittest.TestCase):
    setUp=fixtures.FinalizationTest.setUp
    command=fixtures.FinalizationTest.command

    def test_complete_article_review_survives_real_finish_but_content_changes_stale(self):
        self.exercise("entry-fixture")

    def test_last_heading_evidence_survives_real_finish_but_content_changes_stale(self):
        self.exercise("last-heading")

    def exercise(self, anchor):
        data=upgrade(import_markdown('# Index\n\n'+HEADER+'| `lem:new` | Fixture | Working proof | [Source](../notebook.html#entry-fixture) |\n'))
        claim=data['claims'][0]
        data['topic_definitions']=[{'id':'fixture','title':'Fixture','description':'Test only'}]
        base=dict(data,claims=[])
        registry=self.root/'research/claims/index.json';view=self.root/'research/CLAIM_INDEX.md';book=self.root/'notebook.html'
        registry.write_text(json.dumps(base));view.write_text(render(base));book.write_text('<section id="research-record"></section>\n')
        subprocess.run(['git','init','-q'],cwd=self.root,check=True)
        subprocess.run(['git','add','research','notebook.html'],cwd=self.root,check=True)
        subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','Baseline'],cwd=self.root,check=True)
        book.write_text('<section id="research-record">\n<article id="entry-fixture" data-kind="research" data-route="side-test" data-claims="lem:new">\n<p class="entry-meta">Working proof.</p>\n<h4 id="last-heading">Claim</h4>\n<p>Exact mathematics.</p>\n<!-- TIMING test_turn -->\n</article>\n</section>\n')
        claim.update(mathematical_status='working_proof',topics=['fixture'],formalization={'status':'not_started','scope':'Test scope.','references':[],'artifacts':[]},significance={'category':'context','rationale':'Software fixture.','novelty':'not_claimed','publication_status':'not_applicable','references':[],'next_action':None})
        target='https://kbr.is-a.dev/math-research/#'+anchor;ev=Evidence(self.root)
        for field in FIELDS:claim['reviews'][field]=make_review(data,claim,field,[target],revision='a'*40,date='2026-09-19',reviewer='Test',note='Inspected source.',evidence=ev)
        registry.write_text(json.dumps(data));view.write_text(render(data));before=registry.read_bytes()
        claim['significance'].update(category='independent_result',novelty='candidate',publication_status='candidate')
        claim['reviews']['significance']=make_review(data,claim,'significance',[target],revision='a'*40,date='2026-09-19',reviewer='Test',note='Candidate worth attention, not novelty approval.',evidence=ev)
        registry.write_text(json.dumps(data));view.write_text(render(data));before=registry.read_bytes()
        output=self.command('tools/finish-turn.py','test_turn')
        self.assertIn('Significance check: 1 changed claim dispositions; 1 new/reopened',output.stdout)
        self.assertIn('lem:new',(self.root/'research/ATTENTION.md').read_text())
        history=json.loads((self.root/'research/claims/attention.json').read_text())
        self.assertEqual(history['events'][0]['state'],'pending')
        from resume import bundle, FILES
        for name in FILES:
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('Fixture rules.\n')
        self.assertTrue(any(label=='Significance attention' and 'lem:new' in body
                            for label,body,_,_ in bundle(self.root)))
        self.assertEqual(registry.read_bytes(),before) # No stored review silently rewritten.
        self.assertTrue(all(v=={'reviewed':1} for v in coverage(data,self.root)['counts'].values()))
        finished=book.read_text();raw=Evidence(self.root).sha256(target)
        excerpt=(finished[finished.index('<article'):finished.index('</article>')+len('</article>')]+'\n'
                 if anchor=='entry-fixture' else finished[finished.index('<h4 id="last-heading"'):finished.index('</article>')].rstrip()+'\n')
        self.assertEqual(raw,hashlib.sha256(excerpt.encode()).hexdigest())
        legacy=copy.deepcopy(data)
        for field in FIELDS:legacy['claims'][0]['reviews'][field]['evidence']=[{'target':target,'sha256':raw}]
        self.assertTrue(all(v=={'reviewed':1} for v in coverage(legacy,self.root)['counts'].values()))
        book.write_text(finished.replace('Produced by Test agent','Produced by Different agent')
                       if anchor=='entry-fixture' else finished.replace('Total instrumented interval','Changed timing total'))
        self.assertTrue(all(v=={'reviewed':1} for v in coverage(data,self.root)['counts'].values()))
        self.assertTrue(all(v=={'stale':1} for v in coverage(legacy,self.root)['counts'].values()))
        substantive=[finished.replace('Exact mathematics.','Changed mathematics.')]
        if anchor=='entry-fixture':substantive.append(finished.replace('Working proof.','Refuted.'))
        for text in substantive:
            book.write_text(text)
            self.assertTrue(all(v=={'stale':1} for v in coverage(data,self.root)['counts'].values()))

if __name__=='__main__':unittest.main()
