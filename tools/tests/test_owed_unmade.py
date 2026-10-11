"""finish-turn.py: an Owed attempt paragraph that reports the attempt unmade gives the reason."""
import importlib.util
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('ft_owed_unmade', TOOLS / 'finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)


def entry(paragraph, date='2026-10-12'):
    body = (f'<section id="research-record"><article id="entry-{date}-x" data-kind="research">'
            f'<p><strong>Owed attempt.</strong> {paragraph}</p></article></section>')
    article = body.rindex('<article')
    return body, article, body.index('</article>', article)


class OwedUnmadeTest(unittest.TestCase):
    def test_not_reached_without_reason_is_refused(self):
        # The wording of the draft of 11 October 2026 that prompted the check.
        with self.assertRaises(ValueError):
            FT.validate_owed_unmade(*entry('The statement is read here; the transfer proposition\'s own proof '
                                           'and the uniformity are not reached.'))

    def test_reviewer_reading_without_reason_is_refused(self):
        with self.assertRaises(ValueError):
            FT.validate_owed_unmade(*entry('The proof was read by the reviewer, whose findings are cited.'))

    def test_unmade_with_reason_passes(self):
        FT.validate_owed_unmade(*entry('The proof is not reached, because the induction that uses it had to be '
                                       'checked first to know which scales it must return.'))

    def test_attempt_made_passes(self):
        FT.validate_owed_unmade(*entry('Made here: the proof is read whole, with no error found.'))

    def test_earlier_entries_are_exempt(self):
        FT.validate_owed_unmade(*entry('The proof is not reached.', date='2026-10-11'))


if __name__ == '__main__':
    unittest.main()
