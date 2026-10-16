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


if __name__ == '__main__':
    unittest.main()
