from pathlib import Path
import sys,tempfile,unittest
TOOLS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOLS))
from claim_registration import check_entries
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

if __name__=='__main__':unittest.main()
