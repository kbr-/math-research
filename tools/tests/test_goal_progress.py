"""Goal-progress declarations, scheduled architecture reviews, and follow-through."""
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
FT = SourceFileLoader('progress_finisher', str(ROOT / 'tools/finish-turn.py')).load_module()

REPORT = ('<p><strong>New mathematics.</strong> A scoped result was checked; the uniform implication '
          'remains open.</p><p><strong>Goal progress.</strong> The arbitrary-family implication remains '
          'unchanged; no global construction was obtained.</p>')
ARCHITECTURE = FT.ARCHITECTURE_HEADING + ''.join(
    f'<p><strong>{label}.</strong> '
    + ('<a href="review.txt">Blind initial brief and reviewer response</a>. ' if label == 'Independent alternative' else '')
    + 'The requirement and alternative are compared against the actual goal and its full budget.</p>'
    for label in FT.ARCHITECTURE_FIELDS)


def article(ident, kind='research', route='step', obligation='open-target',
            progress='unchanged', content=REPORT, attrs=''):
    return (f'<article id="{ident}" data-kind="{kind}" data-route="{route}" '
            f'data-obligation="{obligation}" data-goal-progress="{progress}" {attrs}>'
            '<p class="entry-meta">Working statement.</p>' + content + '</article>')


def notebook(*entries):
    return ('<section id="remaining-route"><li data-route-item="step">Step</li></section>'
            '<section id="research-record">' + ''.join(entries) + '</section>')


def validate(body):
    start = body.rindex('<article')
    FT.validate_progress(body, start, body.index('</article>', start))


def test_report(target):
    return (f'<p><strong>Architecture test.</strong> The <a href="#{target}">decisive test</a> '
            'failed on the recorded counterexample, so the proposed weakening is rejected.</p>')


class GoalProgressTest(unittest.TestCase):
    def test_separate_reports_and_stable_obligation_required(self):
        validate(notebook(article('a')))
        for body, message in [
            (notebook(article('a', obligation='')), 'stable open-statement'),
            (notebook(article('a', progress='interesting')), 'advanced'),
            (notebook(article('a', content='')), 'New mathematics'),
            (notebook(article('a', content=REPORT.split('<p><strong>Goal progress.')[0])), 'Goal progress'),
        ]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate(body)

    def test_advance_requires_declared_proof_evidence_not_case_count(self):
        body = notebook(article('a', progress='advanced', content=REPORT.replace(
            'remains unchanged', 'is discharged by thm:result'), attrs='data-claims="thm:result"'))
        for status in ('working_proof', 'conditional', 'established', 'refutation'):
            with patch.object(FT, 'registered_status', return_value={'thm:result': status}):
                validate(body)
        for status in ('finite_check', 'conjecture', 'context', None):
            with patch.object(FT, 'registered_status', return_value={'thm:result': status}):
                with self.assertRaisesRegex(ValueError, 'Advanced Goal progress'):
                    validate(body)
        with patch.object(FT, 'registered_status', return_value={'thm:result': 'working_proof'}):
            with self.assertRaisesRegex(ValueError, 'Advanced Goal progress'):
                validate(body.replace('data-claims="thm:result"', 'data-claims="none"'))
            with self.assertRaisesRegex(ValueError, 'Advanced Goal progress'):
                validate(body.replace('by thm:result', 'by thm:result-other'))

    def test_two_unchanged_cycles_warn_without_early_review(self):
        old_review = article('old', kind='review', content=ARCHITECTURE)
        body = notebook(old_review, article('a'), article('b'))
        self.assertEqual(len(FT.progress_warnings(body)), 1)
        self.assertIn('do not add an early review', FT.progress_warnings(body)[0])
        third = notebook(old_review, article('a'), article('b'), article('c'))
        FT.validate_route(third, third.rindex('<article'))
        early = notebook(old_review, article('a'), article('b'), article('too-soon', kind='review'))
        with self.assertRaisesRegex(ValueError, 'Only 2 research entries'):
            FT.validate_route(early, early.rindex('<article'))
        scheduled = notebook(old_review, *(article(f'r{i}') for i in range(6)),
                             article('scheduled', kind='review'))
        FT.validate_route(scheduled, scheduled.rindex('<article'))

    def test_warnings_track_obligation_and_ignore_unrelated_work(self):
        entries = [article('a'), article('other', obligation='different'),
                   article('audit', kind='audit'), article('b')]
        body = notebook(*entries)
        self.assertEqual(len(FT.progress_warnings(body)), 1)
        self.assertIn('open-target', FT.progress_warnings(body)[0])
        for ending in (article('advance', progress='advanced'), article('review', kind='review')):
            self.assertEqual(FT.progress_warnings(notebook(*entries, ending)), [])

    def test_scheduled_review_requires_comparison_and_reviewer_evidence(self):
        valid = notebook(article('review', kind='review', content=REPORT + ARCHITECTURE))
        validate(valid)
        with self.assertRaisesRegex(ValueError, 'Architecture review'):
            validate(notebook(article('review', kind='review')))
        for label in FT.ARCHITECTURE_FIELDS:
            with self.subTest(label=label), self.assertRaises(ValueError):
                validate(valid.replace(f'<strong>{label}.</strong>', '<strong>Omitted.</strong>'))
        with self.assertRaisesRegex(ValueError, 'reviewer evidence'):
            validate(valid.replace('href="review.txt"', 'title="review.txt"'))

    def test_next_cycle_must_test_the_scheduled_decision(self):
        review = article('review', kind='review', content=REPORT + ARCHITECTURE)
        with self.assertRaisesRegex(ValueError, 'Architecture test'):
            validate(notebook(review, article('next')))
        with self.assertRaisesRegex(ValueError, '#review'):
            validate(notebook(review, article('next', content=REPORT + test_report('wrong'))))
        tested = article('test', content=REPORT + test_report('review'))
        validate(notebook(review, tested))
        validate(notebook(review, tested, article('later')))
        self.assertEqual(FT.pending_architecture_test(notebook(review, tested)), {})

    def test_other_routes_and_user_picks_do_not_consume_test(self):
        review = article('review', kind='review', content=REPORT + ARCHITECTURE)
        picked = article('picked', attrs='data-picked="user"')
        validate(notebook(review, picked))
        mention = article('mention', attrs='data-picked="user"', content=REPORT +
                          '<p><strong>Architecture test.</strong> <a href="#review">Later.</a></p>')
        self.assertEqual(FT.pending_architecture_test(notebook(review, mention)), {'step': 'review'})
        body = notebook(review, picked, article('audit', kind='audit'),
                        article('elsewhere', route='different'))
        self.assertEqual(FT.pending_architecture_test(body), {'step': 'review'})
        with self.assertRaisesRegex(ValueError, 'Architecture test'):
            validate(notebook(review, picked, article('ordinary')))

    def test_legacy_and_nonresearch_entries_are_not_rewritten_or_inferred(self):
        legacy = '<article data-kind="research" data-route="step">Legacy result.</article>'
        body = notebook(legacy, legacy, article('new'))
        validate(body)
        self.assertEqual(FT.progress_warnings(body), [])
        for kind in ('audit', 'formalization'):
            validate(notebook(article('entry', kind=kind, obligation='', progress='', content='')))
        FT.validate_progress('<article data-kind="research"></article>', 0, 30)


if __name__ == '__main__':
    unittest.main()
