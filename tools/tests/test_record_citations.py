import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from record_citations import scan_record,select

class RecordCitationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.data={'claims':[{'id':'lem:a','summary':'A','assessment':'Working','record':'[A](https://kbr.is-a.dev/math-research/#a)'},{'id':'lem:b','summary':'B','assessment':'Working','record':'[B](https://kbr.is-a.dev/math-research/#b)'}],'relationships':[]}
        self.text='''<section><p><a href="#b">living</a>lem:outside</p></section>
<section id="research-record"><h2>Record</h2>
<article id="first" data-claims="lem:not-visible"><h4 id="a">A</h4>
<p><a href='#b'>B &amp; comparison</a> <code>lem:b</code>; lem:unknown.</p>
<!-- <a href="#fake">fake</a> lem:comment -->
<script>"lem:script"</script><h4>Unanchored proof</h4>
<p><a href="https://example.org/paper">external</a> lem:b</p></article>
<article id="second"><h4 id="b">B</h4><p>No citation.</p></article>
<article id="unindexed"><h4 id="new">New</h4><p>lem:a <a href="#missing">missing</a></p></article>
</section>'''
        (self.root/'notebook.html').write_text(self.text)

    def test_entire_record_includes_unindexed_articles_and_ignores_attributes_comments(self):
        d=copy.deepcopy(self.data);r=scan_record(d,self.root)
        self.assertEqual(r['counts']['articles'],3);self.assertEqual(r['counts']['hyperlinks'],3)
        labels=[c['target'] for c in r['citations'] if c['kind']=='explicit_claim_label']
        self.assertEqual(labels,['lem:b','lem:unknown','lem:b','lem:a'])
        self.assertEqual(d,self.data);self.assertTrue(all(not c['accepted_relationship'] for c in r['citations']))
        self.assertEqual(len(select(r,article='unindexed')),2)

    def test_unanchored_sibling_does_not_inherit_prior_heading_ownership(self):
        r=scan_record(self.data,self.root);row=next(c for c in r['citations'] if c['target']=='https://example.org/paper')
        self.assertEqual(row['source_ownership'],'unowned');self.assertIsNone(row['heading']['anchor'])
        self.assertEqual(row['heading']['title'],'Unanchored proof');self.assertEqual(row['article_claim_candidates'],['lem:a'])

    def test_shared_and_broad_owners_distinguished(self):
        c=copy.deepcopy(self.data['claims'][0]);c['id']='lem:shared';self.data['claims'].append(c)
        c=copy.deepcopy(c);c['id']='lem:broad';c['record']='[Article](https://kbr.is-a.dev/math-research/#first)';self.data['claims'].append(c)
        r=scan_record(self.data,self.root);link=next(c for c in r['citations'] if c['target']=='#b')
        self.assertEqual(link['source_ownership'],'ambiguous_candidates')
        self.assertEqual(link['source_claim_candidates'],['lem:a','lem:shared'])
        broad=next(c for c in r['citations'] if c['target']=='https://example.org/paper')
        self.assertEqual(broad['source_ownership'],'broad_article_only')

    def test_nonheading_source_bounds_do_not_capture_sibling(self):
        self.data['claims'][0]['record']='[Fragment](https://kbr.is-a.dev/math-research/#fragment)'
        (self.root/'notebook.html').write_text(self.text.replace("<p><a href='#b'>", "<p id='fragment'><a href='#b'>"))
        r=scan_record(self.data,self.root)
        link=next(c for c in r['citations'] if c['target']=='#b')
        self.assertEqual(link['source_claim_candidates'],['lem:a'])
        sibling=next(c for c in r['citations'] if c['target']=='https://example.org/paper')
        self.assertEqual(sibling['source_ownership'],'unowned')

    def test_registry_specific_label_prefix_is_inventoried(self):
        claim=copy.deepcopy(self.data['claims'][0]);claim['id']='special-kind:example'
        self.data['claims'].append(claim)
        (self.root/'notebook.html').write_text(self.text.replace('lem:unknown.','special-kind:example.'))
        report=scan_record(self.data,self.root)
        self.assertTrue(any(c['target']=='special-kind:example' for c in report['citations']))

    def test_target_namespaces_and_missing_anchors(self):
        folder=self.root/'php_codex_handoff/manuscript';folder.mkdir(parents=True);(folder/'CLAIM_INDEX.md').write_text('`lem:b`')
        r=scan_record(self.data,self.root);b=next(c for c in r['citations'] if c['kind']=='explicit_claim_label' and c['target']=='lem:b')
        self.assertEqual(b['target_status'],'current_and_historical')
        self.assertEqual(next(c for c in r['citations'] if c['target']=='#missing')['target_status'],'missing_anchor')

    def test_stable_ids_under_living_section_changes_and_complete_lookup(self):
        r=scan_record(self.data,self.root)
        (self.root/'notebook.html').write_text(self.text.replace('living','changed living introduction'))
        newer=scan_record(self.data,self.root)
        self.assertEqual([c['id'] for c in r['citations']],[c['id'] for c in newer['citations']])
        self.assertNotEqual(r['notebook_sha256'],newer['notebook_sha256'])
        self.assertEqual(len(select(r,claim='lem:b')),3)

if __name__=='__main__':unittest.main()
