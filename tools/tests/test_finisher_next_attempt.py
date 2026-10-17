"""The finisher refuses a Record search that reports a search for the next attempt the session never ran."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('finisher_next_attempt_test', ROOT / 'tools/finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)

ENTRY = ('<article><p><strong>Record search.</strong> A search for cylinders returned prop:x. For the next '
         'attempt, errors whose supports contain the empty assignment, the search returned nothing.</p></article>')


class NextAttemptSearchTest(unittest.TestCase):
    def test_a_next_attempt_needs_a_matching_search(self):
        # The case of 16 October 2026: other searches ran, none for the attempt the paragraph names.
        with self.assertRaisesRegex(ValueError, 'names a next attempt that no search of this session matches'):
            FT.validate_next_attempt_search(ENTRY, ['-n 5 least degree vanishing union of cylinders'])
        FT.validate_next_attempt_search(ENTRY, ['-n 4 error support contains empty assignment constant term'])
        # One shared word is not enough; frame words count for nothing.
        with self.assertRaises(ValueError):
            FT.validate_next_attempt_search(ENTRY, ['empty set returned next attempt search'])

    def test_a_record_search_in_a_list_item_ends_at_the_item(self):
        # 17 October 2026: the match ran from a follow-up item's Record search to the Verification gate's </p>.
        entry = ('<ul><li><strong>Record search.</strong> "union of random flats" returned prop:x.</li></ul>'
                 '<p><strong>Verification gate.</strong> The reviewer checked the next attempt\'s Smallest '
                 'case outside its range.</p>')
        FT.validate_next_attempt_search(entry, ['-n 5 union of random flats covering'])
        inside = entry.replace('returned prop:x.', 'returned prop:x. For the next attempt, quadric pencils '
                                                   'over cyclotomic towers, nothing.')
        with self.assertRaises(ValueError):
            FT.validate_next_attempt_search(inside, ['-n 5 union of random flats covering'])

    def test_a_paragraph_without_a_next_attempt_passes(self):
        for entry in ('<p><strong>Record search.</strong> A search for cylinders returned prop:x.</p>',
                      '<p>No record search here; the next attempt is elsewhere.</p>'):
            with self.subTest(entry=entry):
                FT.validate_next_attempt_search(entry, [])


class DraftAssessmentTest(unittest.TestCase):
    def test_a_declared_claim_with_a_draft_assessment_is_refused(self):
        # 16 October 2026: three claims registered before their reviews kept "PENDING".
        import json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / 'index.json'
            index.write_text(json.dumps({'claims': [
                {'id': 'lem:a', 'summary': 's', 'assessment': 'PENDING'},
                {'id': 'lem:b', 'summary': 's', 'assessment': 'Working proof passed by the reviewer.'}]}, indent=1))
            with self.assertRaisesRegex(ValueError, 'lem:a'):
                FT.validate_assessments_filled(index, ['lem:a', 'lem:b'])
            FT.validate_assessments_filled(index, ['lem:b'])


class NextAttemptNeighboursTest(unittest.TestCase):
    def test_recent_claims_sharing_words_with_the_next_attempt_are_listed(self):
        # 16 October 2026: a next attempt at the top degree of the product pigeonhole system was already decided
        # by a transfer lemma registered that day.
        import json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / 'index.json'
            index.write_text(json.dumps({'claims': [
                {'id': 'lem:transfer', 'summary': 'At the top degree of the product pigeonhole system monomial '
                                                  'errors on distinct holes reduce to the domain model.'},
                {'id': 'lem:other', 'summary': 'Curves of positive genus carry locators.'}]}, indent=1))
            body = ('<article id="entry-a" data-claims="lem:transfer"></article>'
                    '<article id="entry-b" data-claims="lem:other"></article>')
            entry = ('<article id="entry-c"><p><strong>Follow-up.</strong> Continuing; the next attempt is the '
                     'block degree at the top degree of the product pigeonhole system, monomial errors on '
                     'distinct holes.</p>')
            lines = FT.next_attempt_neighbours(body + entry, entry, index)
            self.assertEqual(len(lines), 1)
            self.assertIn('lem:transfer', lines[0])
            self.assertNotIn('lem:other', lines[0])
            quiet = entry.replace('the next attempt is', 'nothing is named;')
            self.assertEqual(FT.next_attempt_neighbours(body + quiet, quiet, index), [])


if __name__ == '__main__':
    unittest.main()
