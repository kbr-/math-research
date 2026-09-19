import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import claim_registry as cr
from claim_notices import START, END, render_notices, strip_notices


def fixture():
    data = cr.upgrade(cr.import_markdown('# Index\n\n' + cr.HEADER +
        '| `thm:old` | Original theorem | Working proof | [Proof](../notebook.html#old) |\n' +
        '| `audit:fix` | Correction of application only | Correction | [Dated correction](../notebook.html#fix) |\n' +
        '| `obs:counterexample` | Counterexample to stronger claim | Established result | [Proof](../notebook.html#counter) |\n'))
    data['claims'][0]['mathematical_status'] = 'conditional'
    data['claims'][1]['mathematical_status'] = 'context'
    data['claims'][2]['mathematical_status'] = 'refutation'
    data['relationships'] = [{'id': 'fix-old', 'type': 'corrects',
        'source': {'namespace': 'current', 'id': 'audit:fix', 'locator': None},
        'target': {'namespace': 'current', 'id': 'thm:old', 'locator': None},
        'scope': 'Only the proposed application is withdrawn; the algebraic theorem remains valid.',
        'review_status': 'reviewed', 'evidence': ['../notebook.html#fix'],
        'review': {'revision': 'a' * 40, 'date': '2026-09-20', 'reviewer': 'Test', 'note': 'Scope checked.'}}]
    return data


class ClaimNoticesTest(unittest.TestCase):
    def test_scoped_correction_conditional_and_counterexample_not_conflated(self):
        data = fixture(); before = copy.deepcopy(data)
        result = render_notices(data)
        self.assertIn('Conditional result', result)
        self.assertIn('Only the proposed application is withdrawn', result)
        self.assertIn('../notebook.html#fix', result)
        self.assertIn('Refutation / counterexample result', result)
        self.assertIn('does not mean this record is false', result)
        self.assertNotIn('Retracted claim', result)
        self.assertEqual(data, before)
        self.assertEqual(result, render_notices(data))

    def test_explicit_retraction_and_unreviewed_supersession(self):
        data = fixture()
        data['claims'][0]['mathematical_status'] = 'retracted'
        edge = data['relationships'][0]
        edge['type'] = 'supersedes'; edge['review_status'] = 'unreviewed'
        result = render_notices(data)
        self.assertIn('Retracted claim', result)
        self.assertIn('Dated record:', result)
        self.assertIn('Scoped supersession', result)
        self.assertIn('(unreviewed;', result)

    def test_strip_preserves_legacy_import_and_reconciliation(self):
        data = fixture()
        original = data['preamble'] + cr.HEADER + ''.join('| `' + c['id'] + '` | ' +
                    ' | '.join(c[f] for f in cr.TEXT_FIELDS) + ' |\n' for c in data['claims'])
        decorated = original.replace(cr.HEADER, render_notices(data) + cr.HEADER, 1)
        self.assertEqual(strip_notices(decorated), original)
        self.assertEqual(cr.import_markdown(strip_notices(decorated)), cr.import_markdown(original))
        self.assertTrue(cr.reconcile(strip_notices(decorated), data)['passed'])
        self.assertEqual(strip_notices(original), original)
        # Exercise the integrated real renderer/importer, not only helper calls.
        regenerated = cr.render(data)
        self.assertIn(START, regenerated)
        imported = cr.import_markdown(regenerated)
        for old, new in zip(data['claims'], imported['claims']):
            self.assertEqual([old[k] for k in cr.TEXT_FIELDS], [new[k] for k in cr.TEXT_FIELDS])
        self.assertNotIn(START, imported['preamble'])
        self.assertTrue(cr.reconcile(regenerated, data)['passed'])

    def test_marker_errors_fail_closed(self):
        for text in [START, END, END + START, START + START + END, START + END + END]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                strip_notices(text)

    def test_no_notice_for_ordinary_or_unclassified_claim_without_correction(self):
        data = fixture(); data['relationships'] = []
        for claim in data['claims']:
            claim['mathematical_status'] = 'working_proof'
        self.assertEqual(render_notices(data), '')
        data['claims'][0]['mathematical_status'] = None
        self.assertEqual(render_notices(data), '')


if __name__ == '__main__':
    unittest.main()
