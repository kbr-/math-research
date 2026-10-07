from pathlib import Path
from unittest.mock import patch
import sys,tempfile,unittest
TOOLS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOLS))
from claim_registration import check_entries,article_ids,new_entries,Entries
from claim_registry import import_markdown,upgrade,HEADER


def entry(attrs='',body='',identifier='new'):
    return '<section id="research-record"><article id="'+identifier+'" '+attrs+'>'+body+'</article></section>'

class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.data=upgrade(import_markdown('# Claims\n\n'+HEADER+
            '| `lem:a` | A | Working proof | [Proof](https://kbr.is-a.dev/math-research/#a) |\n'))
    def check(self,text,before='',grandfathered=()):return check_entries(before,text,self.data,self.root,grandfathered)
    def test_explicit_notebook_only_claim_cannot_pass(self):
        report=self.check(entry('data-claims="none" data-claim-note="Tooling only"','<code>lem:missing</code>'))
        self.assertFalse(report['passed']);self.assertIn('unregistered',report['errors'][0])
    def test_missing_inventory_and_unreasoned_none_are_rejected(self):
        self.assertFalse(self.check(entry())['passed'])
        self.assertFalse(self.check(entry('data-claims="none"'))['passed'])
        self.assertTrue(self.check(entry('data-claims="none" data-claim-note="Framework-only update"'))['passed'])
    def test_registered_source_requires_declaration_and_reverse_link(self):
        body='<h4 id="a">Statement</h4>'
        self.assertTrue(self.check(entry('data-claims="lem:a"',body))['passed'])
        self.assertFalse(self.check(entry('data-claims="none" data-claim-note="No new claims"',body))['passed'])
        self.assertFalse(self.check(entry('data-claims="lem:a"'))['passed'])
    def test_historical_and_existing_references_are_not_new_claims(self):
        path=self.root/'php_codex_handoff/manuscript/CLAIM_INDEX.md';path.parent.mkdir(parents=True)
        path.write_text('Old [`lem:old`](old.md)')
        body='<code>lem:old</code> and <code>lem:a</code>'
        self.assertTrue(self.check(entry('data-claims="none" data-claim-note="Discuss existing tools"',body))['passed'])
    def test_old_entries_are_not_rewritten(self):
        old=entry(body='<code>lem:unindexed-historical</code>',identifier='old')
        self.assertTrue(self.check(old,before=old)['passed'])
        self.assertTrue(self.check(old,grandfathered=['old'])['passed'])
        self.assertFalse(self.check(old)['passed'])
    def test_backticks_and_unknown_declared_ids(self):
        self.assertFalse(self.check(entry('data-claims="lem:missing"','`lem:missing`'))['passed'])
    def test_duplicate_entry_ids_fail_closed(self):
        with self.assertRaises(ValueError):self.check(entry()+entry())
    def test_repeated_sources_resolve_each_notebook_once(self):
        labels=[f'lem:a{i}' for i in range(20)]
        rows=''.join(f'| `{label}` | A | Working proof | [Proof](https://kbr.is-a.dev/math-research/#a{i}) |\n'
                     for i,label in enumerate(labels))
        self.data=upgrade(import_markdown('# Claims\n\n'+HEADER+rows))
        body=''.join(f'<h4 id="a{i}">Statement</h4>' for i in range(20))
        notebook=self.root/'notebook.html';calls=[];resolve=Path.resolve
        def counted(path,*args,**kwargs):
            if path==notebook:calls.append(path)
            return resolve(path,*args,**kwargs)
        with patch.object(Path,'resolve',counted):
            report=self.check(entry('data-claims="'+' '.join(labels)+'"',body))
        self.assertTrue(report['passed'],report['errors'])
        self.assertEqual(len(calls),1)
    def test_source_resolution_is_fresh_between_checks(self):
        notebook=self.root/'notebook.html';notebook.write_text('notebook')
        other=self.root/'other.html';other.write_text('other')
        alias=self.root/'alias.html';alias.symlink_to(notebook.name)
        self.data['claims'][0]['record']='[Proof](https://github.com/kbr-/math-research/blob/main/alias.html#a)'
        text=entry('data-claims="lem:a"','<h4 id="a">Statement</h4>')
        self.assertTrue(self.check(text)['passed'])
        alias.unlink();alias.symlink_to(other.name)
        report=self.check(text)
        self.assertFalse(report['passed'])
        self.assertIn('needs a source link',' '.join(report['errors']))
    def test_article_ids_match_the_full_parse(self):
        text=('<article id="before-record"></article><!-- <article id="commented"></article> -->'
              '<section class="x" id="research-record"><article data-id="decoy" class="r" id="a&amp;b">'
              '<h4 id="inner">x</h4></article><article id=\'single\'></article></section>'
              '<article id="after-section"></article>')
        self.assertEqual(article_ids(text),{e['id'] for e in Entries(text).entries})
        self.assertEqual(article_ids(text),{'a&b','single','after-section'})
        self.assertEqual(article_ids('<article id="x"></article>'),set())
    def test_new_entries_match_the_full_parse(self):
        old='<section id="research-record"><article id="o"><p>old</p></article>'
        new='<article id="n" data-claims="lem:a"><h4 id="h">S</h4><!-- </article> --><code>lem:a</code> `x`</article>'
        cur=old+'<!-- </article> -->'+new+'</section>'
        full=[e for e in Entries(cur).entries if e['id']!='o']
        self.assertEqual(new_entries(old+'</section>',cur),full)
        with self.assertRaises(ValueError):new_entries('',cur.replace('id="n" ','',1))
        with self.assertRaises(ValueError):new_entries('',cur.replace('</article>'+'</section>','</section>'))

if __name__=='__main__':unittest.main()
