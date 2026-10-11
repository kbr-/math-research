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


class ClosureExceptionTest(unittest.TestCase):
    def test_a_closing_paragraph_may_not_except_an_unmade_attempt(self):
        # The wording of the closure drafted and refused on 11 October 2026.
        self.assertTrue(FT.closure_admits_unmade('None is left unmade except the extension of the collapse.'))
        self.assertTrue(FT.closure_admits_unmade('The first is made and the second left undecided, with the reason.'))
        self.assertTrue(FT.closure_admits_unmade('The reading was not made.'))

    def test_a_closing_paragraph_reporting_every_attempt_made_passes(self):
        self.assertFalse(FT.closure_admits_unmade('The reading its last follow-up named was made, with the outcome '
                                                  'above; none is left unmade.'))
        self.assertFalse(FT.closure_admits_unmade('None was named beyond the item\'s own text.'))


class DeclaredLimitsTest(unittest.TestCase):
    def test_a_declared_limit_is_quoted_in_not_examined(self):
        body = '<p>The ceiling is below the threshold by this count; no other example was not sought.</p>'
        self.assertEqual(FT.unlisted_limits(body + '<p><strong>Not examined.</strong> Nothing is left.</p>'),
                         ['by this count', 'not sought'])
        self.assertEqual(FT.unlisted_limits(body + '<p><strong>Not examined.</strong> The reach "by this count" is '
                                            'an upper bound; another frame was not sought.</p>'), [])
        self.assertEqual(FT.unlisted_limits('<p>Every case is proved.</p>'), [])


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

    def test_unmade_with_a_procedural_reason_is_refused(self):
        # Recorded wordings of 11 October 2026 (the first four), a draft's, and the Bearing check's own pattern.
        for text in ('The reading is again not made: the review gave this entry to the screen, since it came first.',
                     'Made or replaced in the entries after each, and one not made, since it was left by the '
                     'seventh review\'s decision to stop the cluster propositions.',
                     'The localization (not made; the review put the one-sided test first), since it waits.',
                     'Not made, because the seventh review replaced it by its decisive test.',
                     'Not made, because the eighth review having put this lemma first, and still owed.',
                     'Not reached, since the last review decided the order.'):
            with self.assertRaisesRegex(ValueError, 'procedural'):
                FT.validate_owed_unmade(*entry(text))
        # A review named beside an attempt that was made is no reason at all, and passes.
        FT.validate_owed_unmade(*entry('Made here, as the review asked: the proof is read whole.'))

    def test_the_reviewer_s_reading_is_not_the_attempt_even_with_a_reason(self):
        # The recorded wording of the entry the queued item was written on.
        with self.assertRaisesRegex(ValueError, 'reviewer\'s reading in place'):
            FT.validate_owed_unmade(*entry('Its own proof I did not read: I chose the induction first because it '
                                           'could be checked completely in one sitting; the reviewer then read the '
                                           'transfer proof.'))
        # An attempt put off with a reason in the mathematics, and no reviewer in its place, passes.
        FT.validate_owed_unmade(*entry('Its own proof I did not read, because the induction that uses it fixes '
                                       'which scales it must return.'))

    def test_attempt_made_passes(self):
        FT.validate_owed_unmade(*entry('Made here: the proof is read whole, with no error found.'))

    def test_earlier_entries_are_exempt(self):
        FT.validate_owed_unmade(*entry('The proof is not reached.', date='2026-10-11'))


if __name__ == '__main__':
    unittest.main()
