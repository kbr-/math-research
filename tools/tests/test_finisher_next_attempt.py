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

    def test_a_paragraph_without_a_next_attempt_passes(self):
        for entry in ('<p><strong>Record search.</strong> A search for cylinders returned prop:x.</p>',
                      '<p>No record search here; the next attempt is elsewhere.</p>'):
            with self.subTest(entry=entry):
                FT.validate_next_attempt_search(entry, [])


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
