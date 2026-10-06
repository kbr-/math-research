import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
TOOLS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOLS))
from claim_registry import import_markdown, upgrade, HEADER
from claim_reviews import make_review, Evidence, FIELDS
from claim_maintenance import maintenance


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'research').mkdir()
        (self.root/'research/source.md').write_text('Precise source statement and proof.')
        self.data=upgrade(import_markdown('# Index\n\n'+HEADER+
            '| `lem:a` | A | Working proof | [Proof](source.md) |\n'))
        self.data['topic_definitions']=[{'id':'pc','title':'PC','description':'Polynomial calculus.'}]
        self.empty=copy.deepcopy(self.data);self.empty['claims']=[]

    def complete(self,data,claim,fields=FIELDS):
        if 'mathematical_status' in fields:claim['mathematical_status']='working_proof'
        if 'topics' in fields:claim['topics']=['pc']
        if 'formalization' in fields:
            claim['formalization']={'status':'not_started','scope':'Not assigned for this new result.',
                                    'references':['source.md'],'artifacts':[]}
        if 'significance' in fields:
            claim['significance']={'category':'route_specific','rationale':'Local bridge for the recorded method.',
                                  'novelty':'not_claimed','publication_status':'not_applicable',
                                  'references':['source.md'],'next_action':None}
        for field in fields:
            claim['reviews'][field]=make_review(data,claim,field,['source.md'],revision='a'*40,
                date='2026-09-19',reviewer='Test',note='Source reviewed with the recorded scope.',
                evidence=Evidence(self.root))

    def check(self,before,after,changed=()):return maintenance(before,after,self.root,changed)

    def test_new_claim_requires_every_field_but_backlog_is_not_blocked(self):
        self.assertTrue(self.check(self.data,self.data)['passed'])
        self.assertFalse(self.check(self.empty,self.data)['passed'])
        self.complete(self.data,self.data['claims'][0])
        self.assertTrue(self.check(self.empty,self.data)['passed'])

    def test_enrichment_checks_touched_field_without_requiring_backlog(self):
        before=copy.deepcopy(self.data);c=self.data['claims'][0]
        self.complete(self.data,c,['topics'])
        self.assertTrue(self.check(before,self.data)['passed'])
        c['reviews']['topics']['value_sha256']='0'*64
        self.assertFalse(self.check(before,self.data)['passed'])

    def test_changed_statement_requires_fresh_complete_dispositions(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        self.data['claims'][0]['summary']='Corrected statement'
        self.assertFalse(self.check(before,self.data)['passed'])
        self.complete(self.data,self.data['claims'][0])
        self.assertTrue(self.check(before,self.data)['passed'])

    def test_formalization_update_needs_its_review(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        c=self.data['claims'][0];c['formalization']['scope']='Verified special case, full claim still open.'
        self.assertFalse(self.check(before,self.data)['passed'])
        c['reviews']['formalization']=make_review(self.data,c,'formalization',['source.md'],
            revision='b'*40,date='2026-09-19',reviewer='Test',note='Scope update reviewed.',evidence=Evidence(self.root))
        self.assertTrue(self.check(before,self.data)['passed'])

    def test_correction_requires_target_status_acknowledgment(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        c=copy.deepcopy(self.data['claims'][0]);c['id']='lem:correction';self.data['claims'].append(c)
        self.data['relationships']=[{'id':'fix','source':{'namespace':'current','id':c['id'],'locator':None},
            'target':{'namespace':'current','id':'lem:a','locator':None},'type':'corrects','scope':'Bound only.',
            'evidence':['source.md'],'review_status':'reviewed','review':{'note':'Corrected bound.'}}]
        self.complete(self.data,c)
        self.complete(self.data,self.data['claims'][0],['relationships'])
        self.assertFalse(self.check(before,self.data)['passed'])
        self.data['claims'][0]['reviews']['mathematical_status']['note']='Old scope remains working with the separately recorded correction.'
        self.assertFalse(self.check(before,self.data)['passed'])
        self.data['claims'][0]['reviews']['significance']['note']='Significance reconsidered under the corrected bound.'
        self.assertTrue(self.check(before,self.data)['passed'])

    def test_pending_question_is_explicit_not_fake_completion(self):
        c=self.data['claims'][0];self.complete(self.data,c)
        c['significance']=None
        c['reviews']['significance']=make_review(self.data,c,'significance',['source.md'],
            revision='a'*40,date='2026-09-19',reviewer='Test',state='pending',
            note='Possible independent finite-field theorem; novelty not resolved.',
            next_action='Compare the stated field hypotheses with the cited theorem.',evidence=Evidence(self.root))
        self.assertTrue(self.check(self.empty,self.data)['passed'])
        self.assertEqual(self.check(self.empty,self.data)['coverage']['significance']['pending'],1)

    def test_reviewed_null_significance_is_not_a_completed_check(self):
        c=self.data['claims'][0];self.complete(self.data,c)
        c['significance']=None
        c['reviews']['significance']=make_review(self.data,c,'significance',['source.md'],
            revision='a'*40,date='2026-09-19',reviewer='Test',note='Looks reviewed.',evidence=Evidence(self.root))
        self.assertFalse(self.check(self.empty,self.data)['passed'])

    def test_changed_source_detected_without_index_edit(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        (self.root/'research/source.md').write_text('Changed scope.')
        self.assertFalse(self.check(before,self.data,['research/source.md'])['passed'])
        self.assertTrue(self.check(before,self.data)['passed']) # old stale backlog remains reported

    NOTEBOOK=('<section id="research-record"><h2>Record</h2>\n'
              '<article id="a1"><h3>One</h3><h4 id="a1-part">Part</h4><p>x \\(a&lt;b\\)</p></article>\n'
              '<article id="a2"><h3>Two</h3><p>y</p></article>\n</section>\n')

    def test_article_excerpts_skip_the_parse_and_match_it(self):
        path=self.root/'research/nb.html';path.write_text(self.NOTEBOOK)
        spec=importlib.util.spec_from_file_location('ne',TOOLS/'notebook-excerpt.py')
        ne=importlib.util.module_from_spec(spec);spec.loader.exec_module(ne)
        parsed=ne.Notebook(self.NOTEBOOK);evidence=Evidence(self.root)
        for anchor in ('a1','a2'):
            self.assertEqual(evidence.article(path,anchor),parsed.excerpt(anchor))
        self.assertEqual(evidence.notebooks,{})                         # no whole-notebook parse
        self.assertIsNone(evidence.article(path,'a1-part'))           # an inner anchor is parsed
        self.assertEqual(evidence.excerpt(path,'a1-part'),parsed.excerpt('a1-part'))

    def test_internal_fragments_match_full_reader_without_parsing_later_articles(self):
        source = (r"""<section id="record"><h2 id="outside">Record</h2>
<article id="first"><h3>First</h3><h4 id='part'>Part</h4>
<p>\(a<b\)</p><h5 id="child">Child</h5><p>Child proof.</p>
<section id="nested"><h4 id="inside">Inside</h4><p>Nested proof.</p></section>
<h4 id=last>Last</h4><p>Final proof.</p></article>
<article id="later"><h3>Later</h3><h4 id="later-part">Later part</h4><p>Unrelated record.</p></article></section>""")
        path = self.root/'research/nb.html'; path.write_text(source)
        spec = importlib.util.spec_from_file_location('ne', TOOLS/'notebook-excerpt.py')
        ne = importlib.util.module_from_spec(spec); spec.loader.exec_module(ne)
        full, evidence = ne.Notebook(source), Evidence(self.root)
        for name in ('part', 'child', 'nested', 'inside', 'last'):
            self.assertEqual(evidence.excerpt(path, name), full.excerpt(name))
        self.assertEqual(evidence.notebooks, {})
        self.assertEqual(len(evidence.partial_notebooks), 1)
        parsed = next(iter(evidence.partial_notebooks.values()))
        self.assertNotIn('later', [node['anchor'] for node in parsed.nodes])
        self.assertEqual(evidence.excerpt(path, 'later-part'), full.excerpt('later-part'))
        self.assertIs(evidence.partial_notebooks[path], parsed)  # extend, never reparse earlier input
        self.assertEqual(evidence.excerpt(path, 'part'), full.excerpt('part'))
        self.assertEqual(evidence.excerpt(path, 'outside'), full.excerpt('outside'))
        self.assertIn(path, evidence.notebooks)
        with self.assertRaises(ValueError):
            ne.Notebook(source, end=source.index('<h4'))
        with self.assertRaises(ValueError):
            ne.Notebook(source[:source.index('<article id="later">')])

    def test_fragment_duplicate_ids_retain_full_reader_errors(self):
        for attribute in ('id="dup"', "ID='dup'", 'id=dup', 'id="d&#117;p"'):
            with self.subTest(attribute=attribute):
                source = ('<section id="record"><article id="a"><h4 id="dup">First</h4>'
                          '</article><article id="b"><h4 '+attribute+'>Second</h4>'
                          '</article></section>')
                path = self.root/'research/nb.html'; path.write_text(source)
                with self.assertRaisesRegex(ValueError, 'found 2'):
                    Evidence(self.root).excerpt(path, 'dup')

    def test_fragment_ignores_article_text_inside_comments_scripts_and_attributes(self):
        fake = '<article id="fake"><h4 id="phantom">Not a heading</h4></article>'
        for wrapper in ('<!--'+fake+'-->', '<script>const x = \''+fake+'\';</script>',
                        "<div title='"+fake+"'></div>", r"\("+fake+r"\)"):
            with self.subTest(wrapper=wrapper):
                path = self.root/'research/nb.html'
                path.write_text('<section id="record">'+wrapper+'</section>')
                with self.assertRaisesRegex(ValueError, 'found 0'):
                    Evidence(self.root).excerpt(path, 'phantom')

    def test_fragment_decodes_unique_ids_and_falls_back_for_nested_articles(self):
        spec = importlib.util.spec_from_file_location('ne', TOOLS/'notebook-excerpt.py')
        ne = importlib.util.module_from_spec(spec); spec.loader.exec_module(ne)
        for source in (
            '<article id="a"><h4 id="p&#97;rt">Proof</h4><p>x</p></article>',
            '<article id="a"><article id="b"><h4 id="part">Proof</h4></article></article>',
        ):
            path = self.root/'research/nb.html'; path.write_text(source)
            self.assertEqual(Evidence(self.root).excerpt(path, 'part'),
                             ne.Notebook(source).excerpt('part'))

    def test_only_articles_changed_since_the_base_are_rehashed(self):
        import subprocess
        from claim_maintenance import UnchangedArticles
        git=lambda *a:subprocess.run(['git','-c','user.name=t','-c','user.email=t@t',*a],cwd=self.root,
                                     check=True,capture_output=True)
        path=self.root/'research/nb.html';path.write_text(self.NOTEBOOK)
        git('init','-q');git('add','.');git('commit','-q','-m','base')
        path.write_text(self.NOTEBOOK.replace('<p>y</p>','<p>y, corrected</p>').replace(
            '</section>','<article id="a3"><p>new</p></article>\n</section>'))
        unchanged=UnchangedArticles(self.root,'HEAD')
        self.assertTrue(unchanged(path,'a1'))
        self.assertTrue(unchanged(path,'a1-part'))                     # inside an unchanged article
        self.assertFalse(unchanged(path,'a2'))                         # changed
        self.assertFalse(unchanged(path,'a3'))                         # new
        self.assertFalse(unchanged(path,None))
        self.assertFalse(unchanged(self.root/'research/source.md','a1'))

    def test_parallel_complete_additions_keep_the_contract(self):
        spec=importlib.util.spec_from_file_location('merge',TOOLS/'merge-formalization-appends.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        a=copy.deepcopy(self.data);b=copy.deepcopy(self.data);b['claims'][0]['id']='lem:b'
        self.complete(a,a['claims'][0]);self.complete(b,b['claims'][0])
        import json
        merged=module.merge_registry(*(json.dumps(d) for d in (self.empty,a,b)))
        if isinstance(merged,str):merged=json.loads(merged)
        self.assertTrue(self.check(self.empty,merged)['passed'])

if __name__=='__main__':unittest.main()
