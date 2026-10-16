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
    + 'The requirement and alternative are compared against the actual goal and its full budget.'
    + (' <strong>Downstream.</strong> Through thm:downstream-transfer the target gives the goal\'s '
       'statement at every parameter; goal: yes.' if label == 'Necessary target' else '')
    + (' <strong>Attempt.</strong> The cited statements were tried on the test and decide it at no reachable size.'
       ' <strong>Test disposition.</strong> New operation. '
       '<strong>Operation.</strong> Contract the two specified maps on the same paid domain. '
       '<strong>Prediction.</strong> Either the contraction is strict or the specified residual survives. '
       ' <strong>Trivial cases.</strong> Adding an implied row changes neither quantity compared. '
       '<strong>Power.</strong> The recorded ceilings leave the outcomes apart at the sizes reachable. '
       '<strong>Record search.</strong> Searched the registry for the terms of the test; no recorded '
       'claim answers it.' if label == 'Decisive test' else '') + '</p>'
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


class NonvacuityTest(unittest.TestCase):
    def test_finite_check_entries_state_nonvacuity(self):
        with self.assertRaisesRegex(ValueError, 'Nonvacuity'):
            FT.validate_nonvacuity('<p>The check ran at three sizes.</p>')
        with self.assertRaisesRegex(ValueError, 'Nonvacuity'):
            FT.validate_nonvacuity('<p><strong>Nonvacuity.</strong> Fine.</p>')
        FT.validate_nonvacuity('<p><strong>Nonvacuity.</strong> The recorded bound is five and the claim predicts '
                               'three at the sizes computed, so the two outcomes differ there.</p>')


def test_report(target):
    return (f'<p><strong>Architecture test.</strong> <strong>Decided.</strong> The '
            f'<a href="#{target}">decisive test</a> '
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
        with patch.object(FT, 'registered_status', return_value={'thm:result': 'working_proof'}):
            with self.assertRaisesRegex(ValueError, 'Degenerate cases'):      # a proof is tried on trivial inputs
                validate(body)
        body = body.replace('</article>', '<p><strong>Degenerate cases.</strong> A satisfiable system is excluded by '
                            'hypothesis, and with no rows the statement is vacuous.</p></article>')
        with patch.object(FT, 'registered_status', return_value={'thm:result': 'working_proof'}):
            with self.assertRaisesRegex(ValueError, 'Nonvacuity'):            # and has an instance written down
                validate(body)
        body = body.replace('</article>', '<p><strong>Nonvacuity.</strong> The system of three rows on four '
                            'variables recorded with the witness satisfies every hypothesis.</p></article>')
        with patch.object(FT, 'registered_status', return_value={'thm:result': 'working_proof'}):
            with self.assertRaisesRegex(ValueError, 'Hypotheses, each with its step'):   # and names each step
                validate(body)
        body = body.replace('</article>', '<p><strong>Hypotheses, each with its step.</strong> Unsatisfiability '
                            'is used in the counting step and nowhere else; the rows need only be distinct.</p>'
                            '</article>')
        for status in ('working_proof', 'conditional', 'established'):
            with patch.object(FT, 'registered_status', return_value={'thm:result': status}):
                validate(body)
        with patch.object(FT, 'registered_status', return_value={'thm:result': 'refutation'}):
            with self.assertRaisesRegex(ValueError, 'Structural reason'):     # a refutation says why it works
                validate(body)
            validate(body.replace('</article>', '<p><strong>Structural reason.</strong> The hypothesis fails because '
                                  'one is a constant combination of the rows, as for every such family.</p></article>'))
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
        with self.assertRaisesRegex(ValueError, 'Record search'):
            validate(valid.replace('<strong>Record search.</strong>', ''))
        with self.assertRaisesRegex(ValueError, 'Power'):
            validate(valid.replace('<strong>Power.</strong>', ''))
        # From 16 October 2026 Power says where the test's instance stands against the goal's window.
        dated = valid.replace('id="review"', 'id="entry-2026-10-17-review"')
        with self.assertRaisesRegex(ValueError, "parameter window"):
            validate(dated)
        stated = dated.replace('at the sizes reachable.', 'at the sizes reachable, inside the goal\'s window.')
        with patch.object(FT, 'attempt_checked', return_value=True):
            try:
                validate(stated)
            except ValueError as error:
                self.assertNotIn('parameter window', str(error))
        with self.assertRaisesRegex(ValueError, 'Trivial cases'):
            validate(valid.replace('<strong>Trivial cases.</strong>', ''))
        with self.assertRaisesRegex(ValueError, 'Attempt'):
            validate(valid.replace('<strong>Attempt.</strong>', ''))
        with self.assertRaisesRegex(ValueError, 'Downstream'):
            validate(valid.replace('<strong>Downstream.</strong>', ''))
        with self.assertRaisesRegex(ValueError, 'Downstream'):
            validate(valid.replace('thm:downstream-transfer', 'the transfer'))
        with self.assertRaisesRegex(ValueError, 'reviewer evidence'):
            validate(valid.replace('href="review.txt"', 'title="review.txt"'))

    def test_next_cycle_must_test_the_scheduled_decision(self):
        review = article('review', kind='review', content=REPORT + ARCHITECTURE)
        with self.assertRaisesRegex(ValueError, 'Architecture test'):
            validate(notebook(review, article('next')))
        with self.assertRaisesRegex(ValueError, '#review'):
            validate(notebook(review, article('next', content=REPORT + test_report('wrong'))))
        tested = article('test', content=REPORT + test_report('review'))
        with self.assertRaisesRegex(ValueError, 'Not decided'):
            validate(notebook(review, article('vague', content=REPORT + test_report('review').replace(
                '<strong>Decided.</strong> ', ''))))
        validate(notebook(review, article('open', content=REPORT + test_report('review').replace(
            '<strong>Decided.</strong>', '<strong>Not decided.</strong>'))))
        validate(notebook(review, tested))
        validate(notebook(review, tested, article('later')))
        self.assertEqual(FT.pending_architecture_test(notebook(review, tested)), {})

    def test_start_guidance_prints_what_the_review_says_of_its_test(self):
        import sys
        sys.path.insert(0, str(ROOT / 'tools'))
        import turn_guidance
        review = article('review', kind='review', content=REPORT + ARCHITECTURE)
        notes = turn_guidance.guidance(notebook(review), FT, which=lambda name: None, has=lambda header: False)
        at = next(i for i, note in enumerate(notes) if 'must perform the decisive Architecture test' in note)
        self.assertIn('What #review already says about its test', notes[at + 1])
        self.assertTrue(any(note.startswith('  Decision') for note in notes[at + 2:]))

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
        # A review can deliberately select another route's research mechanism.
        # Only its explicit outcome and exact review link discharge that test.
        for kind in ('audit', 'formalization'):
            self.assertEqual(FT.pending_architecture_test(notebook(
                review, article('not-research', kind=kind, route='different',
                                content=REPORT + test_report('review')))), {'step': 'review'})
        for content in (test_report('wrong'),
                        test_report('review').replace('<strong>Decided.</strong>', ''),
                        '<p><strong>Architecture test.</strong> <strong>Decided.</strong>'
                        '<a href="#review">Done.</a></p>'):
            self.assertEqual(FT.pending_architecture_test(notebook(
                review, article('not-tested', route='different', content=content))), {'step': 'review'})
        for legacy in (article('legacy', kind='review'),
                       article('', kind='review', content=REPORT + ARCHITECTURE)):
            self.assertEqual(FT.pending_architecture_test(notebook(legacy)), {})
            self.assertEqual(FT.pending_architecture_test(notebook(review, legacy)), {})
        self.assertEqual(FT.pending_architecture_test(notebook(
            review, article('legacy-other', kind='review', route='unseen'))), {'step': 'review'})
        # report_paragraph excludes its label. Closing/opening tags contribute
        # the two spaces here, so this outcome is at the existing character floor.
        self.assertEqual(len('Decided.  ' + 'abcdefghij' * 3), 40)
        for label, expected in ((('abcdefghij' * 3)[:-1], {'step': 'review'}),
                                ('abcdefghij' * 3, {})):
            boundary = ('<p><strong>Architecture test.</strong><strong>Decided.</strong>'
                        f'<a href="#review">{label}</a></p>')
            self.assertEqual(FT.pending_architecture_test(notebook(
                review, article('boundary', route='different', content=boundary))), expected)
        other_review = article('other-review', kind='review', route='different', content=REPORT + ARCHITECTURE)
        for outcome in ('Decided', 'Not decided'):
            tested = article('tested', route='different', content=REPORT + test_report('review').replace(
                '<strong>Decided.</strong>', f'<strong>{outcome}.</strong>'))
            body = notebook(review, other_review, tested)
            self.assertEqual(FT.pending_architecture_test(body), {'different': 'other-review'})
            self.assertEqual(FT.pending_architecture_test(body, body.index(tested)),
                             {'step': 'review', 'different': 'other-review'})
            both = notebook(review, other_review, tested,
                            article('second-test', route='step', content=REPORT + test_report('other-review')))
            self.assertEqual(FT.pending_architecture_test(both), {})

    def test_legacy_and_nonresearch_entries_are_not_rewritten_or_inferred(self):
        legacy = '<article data-kind="research" data-route="step">Legacy result.</article>'
        body = notebook(legacy, legacy, article('new'))
        validate(body)
        self.assertEqual(FT.progress_warnings(body), [])
        for kind in ('audit', 'formalization'):
            validate(notebook(article('entry', kind=kind, obligation='', progress='', content='')))
        FT.validate_progress('<article data-kind="research"></article>', 0, 30)



class ClosureStakesTest(unittest.TestCase):
    CLOSE = '<p><strong>Follow-up.</strong> Closed: superseded.</p>'
    STAKES = ('<p><strong>Stakes.</strong> A yes would add a clause to the specification on row width; a no would '
              'name the structure a candidate needs. <strong>Follow-up.</strong> Closed: superseded.</p>')
    RECORD = '<p>Record: <a href="https://example.org/results/x/review.txt">review.txt</a>.</p>'
    READ = '<p><strong>Sources read.</strong> None: the closure relies on recorded results only.</p>'
    LEFT = '<p><strong>Not examined.</strong> Nothing the item names is left: its one object is the bound closed here.</p>'
    OWED = ('<p><strong>Owed attempt.</strong> The run its last follow-up named was made in this entry; its '
            'outcome is the table above.</p>')
    LINK = RECORD + READ + LEFT + OWED

    def test_a_closure_needs_stakes_and_a_reviewer_record(self):
        FT.validate_closures('<p><strong>Follow-up.</strong> Continuing: next.</p>')      # nothing closed
        with self.assertRaises(ValueError):
            FT.validate_closures(self.CLOSE + self.LINK)                                   # no stakes
        with self.assertRaises(ValueError):
            FT.validate_closures(self.STAKES)                                              # no reviewer record
        FT.validate_closures(self.STAKES + self.LINK)
        two = self.STAKES + '<ul><li data-check="a:s1">x <strong>Follow-up.</strong> Closed: same.</li></ul>'
        with self.assertRaises(ValueError):
            FT.validate_closures(two + self.LINK)                                          # one closure lacks stakes
        with self.assertRaisesRegex(ValueError, 'Sources read'):
            FT.validate_closures(self.STAKES + self.RECORD)                                # no reading stated
        with self.assertRaisesRegex(ValueError, 'abstract'):
            FT.validate_closures(self.STAKES + self.RECORD + '<p><strong>Sources read.</strong> The capacity '
                                 'paper, abstract only; the testing paper likewise.</p>')
        with self.assertRaises(ValueError):                                                # too short to say anything
            FT.validate_closures('<p><strong>Stakes.</strong> none. <strong>Follow-up.</strong> Closed: x.</p>'
                                 + self.LINK)
        with self.assertRaisesRegex(ValueError, 'Not examined'):                           # the remainder unlisted
            FT.validate_closures(self.STAKES + self.RECORD + self.READ)
        with self.assertRaisesRegex(ValueError, 'Owed attempt'):                           # the named attempt
            FT.validate_closures(self.STAKES + self.RECORD + self.READ + self.LEFT)
        FT.validate_closures(self.STAKES.replace('Closed: superseded', 'Closed: merged into other-item')
                             + self.RECORD + self.READ)                                    # a merge names no remainder


class ProvedInstanceTest(unittest.TestCase):
    def test_a_registered_proof_exhibits_an_input_meeting_its_hypotheses(self):
        plain = '<p>The proposition holds for every graph of the class.</p>'
        FT.validate_proved_instance(plain)
        FT.validate_proved_instance(plain, {'finite_check', 'conjecture', None})
        for status in ('working_proof', 'conditional'):
            with self.assertRaisesRegex(ValueError, 'Nonvacuity'):
                FT.validate_proved_instance(plain, {status})
        with self.assertRaisesRegex(ValueError, 'Nonvacuity'):
            FT.validate_proved_instance(plain + '<p><strong>Nonvacuity.</strong> Yes.</p>', {'working_proof'})
        FT.validate_proved_instance(plain + '<p><strong>Nonvacuity.</strong> Seven left vertices of degree six and '
                                    'six right vertices of degree seven form an instance.</p>', {'working_proof'})


class DegenerateCasesTest(unittest.TestCase):
    def test_a_registered_proof_says_what_it_gives_on_degenerate_inputs(self):
        plain = '<h3>A bound</h3><p><strong>New mathematics.</strong> A ceiling for systems of rows.</p>'
        FT.validate_degenerate_cases(plain)
        FT.validate_degenerate_cases(plain, {'finite_check', 'conjecture', None})
        for status in ('working_proof', 'conditional'):
            with self.assertRaisesRegex(ValueError, 'Degenerate cases'):
                FT.validate_degenerate_cases(plain, {status})
        with self.assertRaises(ValueError):
            FT.validate_degenerate_cases(plain + '<p><strong>Degenerate cases.</strong> None.</p>', {'working_proof'})
        FT.validate_degenerate_cases(plain + '<p><strong>Degenerate cases.</strong> A satisfiable system is excluded '
                                     'by hypothesis; with no rows the bound is vacuous; blocks must be multilinear.</p>',
                                     {'working_proof'})


class BaselineTest(unittest.TestCase):
    def test_a_registered_proof_names_the_trivial_baseline(self):
        # 16 October 2026: a comparison omitted the multiplier that survived every choice.
        plain = '<article id="entry-2026-10-17-bound"><p><strong>New mathematics.</strong> A degree.</p>'
        FT.validate_baseline(plain, {'finite_check'})
        FT.validate_baseline(plain.replace('2026-10-17', '2026-10-15'), {'working_proof'})
        with self.assertRaisesRegex(ValueError, 'Baseline'):
            FT.validate_baseline(plain, {'working_proof'})
        FT.validate_baseline(plain + '<p><strong>Baseline.</strong> The indicator of the origin survives at '
                             'degree n; the lemma saves t degrees.</p>', {'working_proof'})


class PlainestBoundTest(unittest.TestCase):
    def test_smallest_case_and_witness_name_the_plainest_bound(self):
        # 16 October 2026: a next attempt and a witness that bare per-cell counts already decided.
        smallest = ('<article id="entry-2026-10-16-x"><p><strong>Smallest case.</strong> One band along a '
                    'horizontal line: the chaining gives a bounded factor.</p>')
        with self.assertRaisesRegex(ValueError, 'Smallest case paragraph needs'):
            FT.validate_plainest(smallest)
        FT.validate_plainest(smallest.replace('2026-10-16', '2026-10-15'))
        FT.validate_plainest(smallest.replace('</p>', ' <strong>Plainest bound.</strong> The per-cell counts give '
                                              'the same order, so the instance decides nothing.</p>'))
        witness = '<article id="entry-2026-10-16-y"><p><strong>Nonvacuity.</strong> The band with a = 1.</p>'
        FT.validate_plainest(witness, {'finite_check'})
        with self.assertRaisesRegex(ValueError, 'Nonvacuity paragraph needs'):
            FT.validate_plainest(witness, {'working_proof'})
        FT.validate_plainest(witness.replace('</p>', ' <strong>Plainest bound.</strong> None applies: the '
                                             'statement is an identity of formal series.</p>'), {'working_proof'})

    def test_a_draft_with_a_proof_counts_as_proved_before_registration(self):
        # 16 October 2026: a Nonvacuity without its Plainest bound passed the skeleton check twice, the draft's
        # claims being unregistered, and was refused only at the finisher after the append.
        self.assertEqual(FT.draft_statuses('<p><strong>Proof.</strong> Direct.</p>'), {'working_proof'})
        self.assertEqual(FT.draft_statuses('<p><strong>Proof of (b).</strong> Direct.</p>'), {'working_proof'})
        self.assertEqual(FT.draft_statuses('<p><strong>Full proof.</strong> Direct.</p>'), {'working_proof'})
        self.assertEqual(FT.draft_statuses('<p><strong>Proof sketch.</strong> Roughly.</p>'), set())
        self.assertEqual(FT.draft_statuses('<p><strong>Nonvacuity.</strong> One case.</p>'), set())
        # Not counted as proved where the registry path would not count it (the reviewer's one case in 241).
        proof = '<p><strong>Proof.</strong> Direct.</p>'
        self.assertEqual(FT.draft_statuses('<article data-claims="none">' + proof), set())
        self.assertEqual(FT.draft_statuses('<p class="entry-meta">Refutation, by one case.</p>' + proof), set())
        self.assertEqual(FT.draft_statuses('<article data-claims="ex:c">' + proof), set())
        self.assertEqual(FT.draft_statuses('<article data-claims="ex:c">' + proof, {'ex:c': 'finite_check'}),
                         set())
        witness = ('<article id="entry-2026-10-16-y"><p><strong>Proof.</strong> Direct.</p>'
                   '<p><strong>Nonvacuity.</strong> The band with a = 1.</p>')
        with self.assertRaisesRegex(ValueError, 'Nonvacuity paragraph needs'):
            FT.validate_plainest(witness, FT.draft_statuses(witness))

    def test_the_draft_branch_runs_the_other_checks_of_proved_statements(self):
        draft = ('<article id="entry-2026-10-17-y"><p><strong>Proof.</strong> Direct.</p>'
                 '<p><strong>Nonvacuity.</strong> The band with a = 1. <strong>Plainest bound.</strong> The bare '
                 'count gives the same order, so it decides nothing.</p>')
        with self.assertRaisesRegex(ValueError, 'Degenerate|Hypotheses|Baseline'):
            FT.validate_drafted_proofs(draft, FT.draft_statuses(draft))
        FT.validate_drafted_proofs(draft, set())

    def test_smallest_case_says_what_the_entry_s_own_statements_give(self):
        # 16 October 2026: three named next attempts in a row were decided by their entries' own statements.
        plain = (' <strong>Plainest bound.</strong> The per-cell counts give the same order, so they decide '
                 'nothing.</p>')
        later = ('<article id="entry-2026-10-17-x"><p><strong>Smallest case.</strong> Two twists in two '
                 'holes on three pigeons:<ul><li>window two.</li></ul>' + plain)
        with self.assertRaisesRegex(ValueError, 'Own statements'):
            FT.validate_plainest(later)
        FT.validate_plainest(later.replace('</p>', ' <strong>Own statements.</strong> Part (a) splits both '
                                           'twists to window zero, so it gives nothing here.</p>'))
        FT.validate_plainest(later.replace('2026-10-17', '2026-10-16'))


class UnboundedWitnessTest(unittest.TestCase):
    def test_a_witness_bounding_n_from_above_is_refused(self):
        # 16 October 2026: a cost at most 2 only "for N with 4 log log N <= 4096".
        bounded = (r'<p><strong>Nonvacuity.</strong> The cost is at most \(2\) when \(\log(1+y_0)\le8^4\), true '
                   r'for \(N\) with \(4\log\log N\le4096\).</p>')
        with self.assertRaisesRegex(ValueError, 'bounds N from above'):
            FT.validate_unbounded_witness(bounded)
        for fine in (r'<p><strong>Nonvacuity.</strong> \(w&lt;m\) when \(\log N&gt;12^4\); \(j\le\ell_1\).</p>',
                     r'<p><strong>Nonvacuity.</strong> \(\log y\le\log N\) and \(2^{-j}\le w\) for large \(N\).</p>'):
            FT.validate_unbounded_witness(fine)


class UnlistedSuggestionTest(unittest.TestCase):
    def test_a_gate_reporting_a_suggestion_needs_the_list(self):
        # 16 October 2026: a next attempt taken from a reviewer's suggestion in the author's words, with no list.
        body = ('<article id="entry-2026-10-17-x"><p><strong>Verification gate.</strong> The reviewer suggested a '
                'matching upper bound, adopted as the next attempt.</p>')
        with self.assertRaisesRegex(ValueError, 'no <h4>Reviewer'):
            FT.refuse_unlisted_suggestions(body)
        FT.refuse_unlisted_suggestions(body + "<h4>Reviewer's suggestions, unverified</h4><ul><li>A bound. "
                                              '<strong>Record.</strong> none.</li></ul>')
        FT.refuse_unlisted_suggestions(body.replace('2026-10-17', '2026-10-15'))


class ScopeDirectionTest(unittest.TestCase):
    def test_a_reported_change_of_scope_says_which_way(self):
        # 16 October 2026: "weakened" hypotheses read as a generalization thrown away.
        gate = ('<article id="entry-2026-10-17-x"><p><strong>Verification gate.</strong> The reviewer passed it; '
                'soundness and killing were weakened to the downstream form.</p>')
        with self.assertRaisesRegex(ValueError, 'without its direction'):
            FT.validate_scope_direction(gate)
        FT.validate_scope_direction(gate.replace('downstream form', 'downstream form, so the lemma assumes less '
                                                 'and is more general'))
        FT.validate_scope_direction(gate.replace('2026-10-17', '2026-10-15'))


class HypothesisPartsTest(unittest.TestCase):
    def test_each_statement_part_is_named_in_the_hypotheses(self):
        # 16 October 2026: a part added after review was missing from the Hypotheses paragraph.
        body = ('<article id="entry-2026-10-17-x"><p><strong>Statement.</strong> (a) One thing. (b) Another thing. '
                '(c) A third.</p><p><strong>Hypotheses, each with its step.</strong> The field is used in (a) and '
                'the axiom in (b); nothing else is used anywhere in the proof at all.</p>')
        with self.assertRaisesRegex(ValueError, r'names none of \(c\)'):
            FT.validate_hypothesis_steps(body, {'working_proof'})
        FT.validate_hypothesis_steps(body.replace('in (b);', 'in (b) and (c);'), {'working_proof'})
        FT.validate_hypothesis_steps(body.replace('2026-10-17', '2026-10-15'), {'working_proof'})
        # parts named in later items of a list inside the paragraph count too
        listed = body.replace('The field is used in (a) and the axiom in (b);',
                              '<ul><li>Part (a): the field is used throughout the whole proof.</li>'
                              '<li>Part (b): the axiom.</li><li>Part (c): nothing else.</li></ul>')
        FT.validate_hypothesis_steps(listed, {'working_proof'})

    def test_a_hypothesis_bullet_names_a_step_not_a_source(self):
        # 16 October 2026: "m > N: the system of Theorem 2.9" kept a hypothesis no step used.
        body = ('<article id="entry-2026-10-17-x"><p><strong>Hypotheses, each with its step.</strong><ul>'
                '<li>\\(D\\le n\\): Proposition 2.8 at degree \\(D\\), the basis step of the proof.</li>'
                '<li>\\(m&gt;N\\): the system of Theorem 2.9.</li></ul></p>')
        with self.assertRaisesRegex(ValueError, "names a source's setting"):
            FT.validate_hypothesis_steps(body, {'working_proof'})
        for phrase in ('the setting of', 'the statement of', 'the hypotheses of', 'the assumptions in'):
            with self.assertRaisesRegex(ValueError, "names a source's setting"):
                FT.validate_hypothesis_steps(body.replace('the system of', phrase), {'working_proof'})
        # the same words inside a named step are a step
        FT.validate_hypothesis_steps(body.replace('the system of Theorem 2.9', 'the free-hole step, which counts '
                                                  'holes in the system of Theorem 2.9'), {'working_proof'})
        FT.validate_hypothesis_steps(body.replace('2026-10-17', '2026-10-15'), {'working_proof'})


class SmallestCaseTest(unittest.TestCase):
    def test_a_named_next_attempt_reports_its_smallest_case(self):
        # 16 October 2026: four next attempts in a row were decided in a few lines at their smallest case.
        body = ('<article id="entry-2026-10-17-x"><p><strong>Follow-up.</strong> Continuing. The next attempt is '
                'the twisted case.</p>')
        with self.assertRaisesRegex(ValueError, 'Smallest case'):
            FT.validate_smallest_case(body)
        FT.validate_smallest_case(body + '<p><strong>Smallest case.</strong> At k=2, n=1 the matrix is '
                                  'conjugate to a diagonal one only when its trace is a polynomial.</p>')
        FT.validate_smallest_case(body.replace('2026-10-17', '2026-10-15'))
        FT.validate_smallest_case(body.replace('Continuing', 'Closed: superseded'))


class SearchesRunTest(unittest.TestCase):
    def test_a_record_search_paragraph_needs_a_logged_search(self):
        import json, tempfile
        entry = '<article><p><strong>Record search.</strong> Searched the registry for cut ceilings: nothing.</p>'
        with self.assertRaisesRegex(ValueError, 'was not run'):
            FT.validate_searches_run(entry, [])
        self.assertEqual(FT.validate_searches_run(entry, ['cut ceiling']), ['cut ceiling'])
        self.assertEqual(FT.validate_searches_run('<article><p>No such paragraph.</p>', []), [])
        with tempfile.TemporaryDirectory() as root:
            logs = Path(root) / 'research/logs'
            logs.mkdir(parents=True)
            (logs / 'claim-searches.jsonl').write_text(
                json.dumps({'unix_s': 10.0, 'query': 'old'}) + '\nnot json\n'
                + json.dumps({'unix_s': 30.0, 'query': 'cut ceiling'}) + '\n')
            self.assertEqual(FT.logged_searches(root, 20.0), ['cut ceiling'])
            self.assertEqual(FT.logged_searches(Path(root) / 'absent', 0), [])


class ResemblanceRunTest(unittest.TestCase):
    def test_declared_claims_need_a_logged_resemblance_run(self):
        entry = '<article id="e" data-claims="prop:one cor:two"><p>Text.</p>'
        with self.assertRaisesRegex(ValueError, 'prop:one, cor:two'):
            FT.validate_resemblance_run(entry, ['cut ceiling'])
        with self.assertRaisesRegex(ValueError, 'not run on in its session: cor:two'):
            FT.validate_resemblance_run(entry, ['claim_resemblance prop:one'])
        FT.validate_resemblance_run(entry, ['claim_resemblance prop:one cor:two'])
        FT.validate_resemblance_run('<article id="e" data-claims="none"><p>Text.</p>', [])
        FT.validate_resemblance_run('<article id="e"><p>Text.</p>', [])


class StructuralReasonTest(unittest.TestCase):
    REASON = ('<p><strong>Structural reason.</strong> One is a combination of the rows with constant coefficients; '
              'random rows of width three are not expected to have one.</p>')

    def test_a_counterexample_or_registered_refutation_needs_its_reason(self):
        plain = '<h3>A bound</h3><p><strong>New mathematics.</strong> A PC refutation of degree three exists.</p>'
        FT.validate_structural_reason(plain)                                        # "refutation" alone: a proof
        told = '<h3>A counterexample to independence</h3><p><strong>New mathematics.</strong> Rows.</p>'
        with self.assertRaisesRegex(ValueError, 'Structural reason'):
            FT.validate_structural_reason(told)
        FT.validate_structural_reason(told + self.REASON)
        inside = '<h3>Rows</h3><p><strong>New mathematics.</strong> Two counterexamples below a threshold.</p>'
        with self.assertRaises(ValueError):
            FT.validate_structural_reason(inside + '<p><strong>Structural reason.</strong> Short.</p>')
        with self.assertRaises(ValueError):
            FT.validate_structural_reason(plain, {'refutation', 'working_proof'})
        FT.validate_structural_reason(plain + self.REASON, {'refutation'})
        with self.assertRaisesRegex(ValueError, 'Structural reason'):                # an obstruction's identifier
            FT.validate_structural_reason(plain, {'working_proof'}, ['obs:dense-pinning'])
        FT.validate_structural_reason(plain + self.REASON, {'working_proof'}, ['obs:dense-pinning'])
        FT.validate_structural_reason(plain, {'working_proof'}, ['prop:observed-bound'])     # not the prefix
        FT.validate_structural_reason(plain, {'working_proof', None})


class DevelopedRemovalTest(unittest.TestCase):
    DONE = '<p><strong>Follow-up.</strong> Developed: the bound is proved and nothing of the item remains.</p>'
    LEFT = ClosureStakesTest.LEFT
    OWED = ClosureStakesTest.OWED
    RECORD = ClosureStakesTest.RECORD

    def test_a_developed_follow_up_accounts_for_unexamined_parts_and_the_owed_attempt(self):
        FT.validate_developed_removals('<p><strong>Follow-up.</strong> Continuing: next.</p>')   # nothing removed
        with self.assertRaisesRegex(ValueError, 'Not examined'):
            FT.validate_developed_removals(self.DONE + self.OWED + self.RECORD)
        with self.assertRaisesRegex(ValueError, 'Owed attempt'):
            FT.validate_developed_removals(self.DONE + self.LEFT + self.RECORD)
        with self.assertRaisesRegex(ValueError, 'review.txt'):
            FT.validate_developed_removals(self.DONE + self.LEFT + self.OWED)
        FT.validate_developed_removals(self.DONE + self.LEFT + self.OWED + self.RECORD)
        item = ('<ul><li data-check="a:s1">A sub-idea. <strong>Follow-up.</strong> Developed: done.</li></ul>')
        with self.assertRaisesRegex(ValueError, 'Not examined'):
            FT.validate_developed_removals(item)


class DevelopedReadingTest(unittest.TestCase):
    ASK = '<li data-check="a:s1">Read the statement of the threshold theorem with its window. '
    READ = ('<strong>Sources read.</strong> Theorem 3.2 of the paper, in its text, with the definition of a '
            'symmetric property. ')

    def test_a_developed_reading_check_states_what_was_read(self):
        done = '<strong>Follow-up.</strong> Developed: the window is of the order of the density.</li>'
        FT.validate_developed_readings('<ul>' + self.ASK + self.READ + done + '</ul>')
        FT.validate_developed_readings('<ul>' + self.ASK + done[:-5] + ' ' + self.READ + '</li></ul>')   # after it
        with self.assertRaisesRegex(ValueError, 'Sources read'):
            FT.validate_developed_readings('<ul>' + self.ASK + done + '</ul>')
        with self.assertRaisesRegex(ValueError, 'memory'):
            FT.validate_developed_readings('<ul>' + self.ASK + '<strong>Sources read.</strong> The form of the '
                                           'theorem as recalled from memory of an earlier reading. ' + done + '</ul>')

    def test_other_items_are_left_alone(self):
        FT.validate_developed_readings('<ul>' + self.ASK + '<strong>Follow-up.</strong> Continuing: unread.</li></ul>')
        FT.validate_developed_readings('<ul><li data-check="a:s2">Prove the bound for relation blocks. '
                                       '<strong>Follow-up.</strong> Developed: prop:x proves it.</li></ul>')
        FT.validate_developed_readings('<ul><li data-check="a:s3">Prove it. <strong>Follow-up.</strong> Developed: '
                                       'done.</li>' + self.ASK + '<strong>Follow-up.</strong> Continuing.</li></ul>')


class PreventionTest(unittest.TestCase):
    def test_a_process_assessment_names_its_prevention(self):
        FT.validate_prevention('<p><strong>Question.</strong> No assessment here.</p>')
        with self.assertRaises(ValueError):
            FT.validate_prevention('<p><strong>Process assessment.</strong> I closed an item wrongly.</p>')
        with self.assertRaises(ValueError):
            FT.validate_prevention('<p><strong>Process assessment.</strong> x <strong>Prevention.</strong> ok.</p>')
        FT.validate_prevention('<p><strong>Process assessment.</strong> I closed an item wrongly. <strong>Prevention.'
                               '</strong> The finisher now requires stakes on every closure (commit abc).</p>')


class UnreviewedDerivationsTest(unittest.TestCase):
    NONE = '<p><strong>Verification gate.</strong> No new lemma is stated, so no reviewer was used.</p>'

    def test_an_entry_without_reviewer_may_quote_and_may_not_extrapolate(self):
        FT.validate_unreviewed_derivations('<p>The source states the bound for X at most T.</p>' + self.NONE)
        for derived in ('This is an extrapolation from the two stages.', 'A what-if with 3/4 in its place.',
                        'The derived relations are checked at both stages.'):
            with self.assertRaises(ValueError):
                FT.validate_unreviewed_derivations(f'<p>{derived}</p>' + self.NONE)
        # With a reviewer the same text passes, and the gate's own wording is not searched.
        FT.validate_unreviewed_derivations('<p>An extrapolation from the two stages.</p><p><strong>Verification '
                                           'gate.</strong> One medium reviewer checked the relations.</p>')
        FT.validate_unreviewed_derivations('<p>Quoted only.</p><p><strong>Verification gate.</strong> No reviewer '
                                           'was used; nothing here is an extrapolation.</p>')

    def test_a_build_entry_without_claims_may_say_that_no_claim_applies(self):
        general = '<p><strong>General statement.</strong> None: a framework build has no all-parameter claim.</p>'
        def body(tags):
            return ('<section id="remaining-route"><li data-route-item="step">x</li></section>'
                    f'<section id="research-record"><article data-kind="research" data-route="step" {tags}>'
                    + general + '</article></section>')
        def check(tags):
            text = body(tags)
            FT.validate_general(text, text.index('<article'), text.index('</article>'))
        check('data-build="some-item" data-claims="none"')
        check('data-claims="none" data-claim-note="A build." data-build="some-item"')
        for tags in ('data-claims="none"', 'data-build="some-item" data-claims="lem:fixture"',
                     'data-build="" data-claims="none"', 'data-lead="some-item" data-claims="none"'):
            with self.subTest(tags=tags), self.assertRaisesRegex(ValueError, 'must cite the registered claim'):
                check(tags)
        # The paragraph itself is still required of a build entry.
        text = body('data-build="some-item" data-claims="none"').replace(general, '')
        with self.assertRaisesRegex(ValueError, 'needs a <p><strong>General statement'):
            FT.validate_general(text, text.index('<article'), text.index('</article>'))

    def test_a_third_deferral_in_a_row_of_an_owed_attempt_on_one_item_is_printed(self):
        def entry(ident, owed, item='the-idea'):
            return (f'<article id="entry-{ident}" data-kind="research" data-idea="{item}">'
                    f'<p><strong>Owed attempt.</strong> {owed}</p></article>')
        later = 'The reading named is made. The attempt on the twist is again not made, since room comes first.'
        made = 'The attempt on the twist is made here, with its outcome below.'
        dropped = 'The attempt on the twist is not made and is dropped: the proof it audits is no longer used.'
        def line(last, *before):
            body = '<section id="research-record">' + ''.join(before) + last + '</section>'
            return FT.third_deferral_line(body, body.rindex('<article'), body.rindex('</article>'))
        two = (entry('a', later), entry('b', later))
        self.assertIn('#entry-a, #entry-b', line(entry('c', later), *two))
        self.assertIsNone(line(entry('c', made), *two))
        self.assertIsNone(line(entry('c', dropped), *two))
        self.assertIsNone(line(entry('c', later, item='another'), *two))              # another item's run
        self.assertIsNone(line(entry('c', later), entry('a', later), entry('b', made)))   # made in between
        # Why it prints and does not refuse: an entry that makes the attempt deferred twice is still reported.
        self.assertIsNotNone(line(entry('c', 'The attempt deferred twice is made here, with its outcome.'), *two))

    def test_a_removal_whose_corrections_the_reviewer_did_not_read_is_refused(self):
        gate = '<p><strong>Verification gate.</strong> One reviewer: pass with corrections. {}</p>'
        removal = '<p><strong>Follow-up.</strong> Developed: the build exists.</p>'
        unread = gate.format('It did not read the corrections.')
        with self.assertRaisesRegex(ValueError, 'same reviewer'):
            FT.validate_corrections_read(unread + removal)
        with self.assertRaisesRegex(ValueError, 'same reviewer'):
            FT.validate_corrections_read(gate.format('The reviewer has not read the code as changed.')
                                         + '<p><strong>Follow-up.</strong> Closed: superseded.</p>')
        # The same admission in other words: edits made after the follow-up, however small the entry calls them.
        with self.assertRaisesRegex(ValueError, 'not shown to it again'):
            FT.validate_corrections_read(gate.format('Two optional points, both taken after it and not shown to it '
                                                     'again.') + removal)
        FT.validate_corrections_read(unread + '<p><strong>Follow-up.</strong> Continuing: the attempt is named.</p>')
        FT.validate_corrections_read(gate.format('In a follow-up it read the corrections and found them right.')
                                     + removal)

    def test_an_entry_without_claim_or_reviewer_may_not_display_formulas_of_its_own(self):
        shown = '<p>So the boundary is \\[\\beta=\\tfrac{11}{12}-\\tfrac{\\ell}4.\\]</p>'
        with self.assertRaisesRegex(ValueError, 'displays formulas'):
            FT.validate_unreviewed_derivations(shown + self.NONE, [])
        # A registered claim has its own review duty; an unknown claim list and an inline formula are left alone.
        FT.validate_unreviewed_derivations(shown + self.NONE, ['lem:boundary'])
        FT.validate_unreviewed_derivations(shown + self.NONE)
        FT.validate_unreviewed_derivations('<p>Inline \\(x\\) only.</p>' + self.NONE, [])
        # With a reviewer, or with the gate saying the formulas are the source's, it passes.
        FT.validate_unreviewed_derivations(shown + '<p><strong>Verification gate.</strong> One medium reviewer '
                                                   'checked the relation.</p>', [])
        FT.validate_unreviewed_derivations(shown + '<p><strong>Verification gate.</strong> No reviewer was used: '
                                                   'every displayed relation is quoted from the source, its '
                                                   'equation (3.2).</p>', [])


class ProcessAuditTest(unittest.TestCase):
    GATE = '<p><strong>Verification gate.</strong> One reviewer. Record: <a href="r/review.txt">review.txt</a>.%s</p>'

    def test_a_reviewed_entry_reports_the_process_audit(self):
        FT.validate_process_audit('<p><strong>Verification gate.</strong> No reviewer in this cycle.</p>')
        with self.assertRaises(ValueError):
            FT.validate_process_audit(self.GATE % '')
        FT.validate_process_audit(self.GATE % ' <strong>Process audit.</strong> The title claimed more than '
                                  'the data showed and was narrowed.')
        with self.assertRaisesRegex(ValueError, 'title'):                 # the audit compares title and body
            FT.validate_process_audit(self.GATE % ' <strong>Process audit.</strong> The reviewer found a '
                                      'search made after the draft and nothing else.')


class BearingLedgerIntegrationTest(unittest.TestCase):
    def test_first_application_also_requires_a_matched_ledger(self):
        body = notebook(article('first', attrs='data-bearing="some"'))
        start = body.index('<article')
        with self.assertRaisesRegex(ValueError, 'data-ledger'):
            FT.validate_progress(body, start, body.index('</article>'), check_registered_claims=False)


class BearingTest(unittest.TestCase):
    def test_a_bearing_that_claims_something_ends_with_what_is_not_covered(self):
        unchanged = ('research', 'unchanged')
        said = 'Unchanged. <strong>Bearing.</strong> At cutoffs within the range the levels are too large for the endpoint.'
        with self.assertRaisesRegex(ValueError, 'Not covered'):
            self.check([unchanged, unchanged], said, last='data-bearing="some"')
        with self.assertRaisesRegex(ValueError, 'Not covered'):
            self.check([unchanged, unchanged], said + ' <strong>Not covered.</strong> More.', last='data-bearing="some"')
        self.check([unchanged, unchanged], said + ' <strong>Not covered.</strong> Cutoffs above the range, wide '
                   'windows and rows of unbounded overlap.', last='data-bearing="some"')
        self.check([unchanged, unchanged], said)                                    # declares none

    def check(self, earlier, progress, last='data-bearing="none"'):
        body = ''.join(f'<article data-kind="{row[0]}" data-route="r" data-goal-progress="{row[1]}" '
                       f'{row[2] if len(row) > 2 else ""}></article>' for row in earlier)
        body += '<article data-kind="research" data-route="r" data-goal-progress="unchanged" ' + last + '>'
        FT.validate_bearing(body, body.rindex('<article'), progress)

    def test_a_bearing_of_some_does_not_rest_on_something_unchecked(self):
        unchanged = ('research', 'unchanged')
        said = ('Unchanged. <strong>Bearing.</strong> At the goal\'s parameters the count is automatic for pairs. '
                '<strong>Not covered.</strong> Any system reaching these degrees; ')
        for tail in ('the remaining hypotheses of the transfer, which I did not check.',
                     'the envelope, whose clauses were not yet verified for this class.',
                     'the transfer for such a system, its hypotheses unchecked.'):
            with self.assertRaisesRegex(ValueError, 'was not checked'):
                self.check([unchanged, unchanged], said + tail, last='data-bearing="some"')
        self.check([unchanged, unchanged], said + 'groups of four or more, where the count leaves no room.',
                   last='data-bearing="some"')
        self.check([unchanged, unchanged], 'Unchanged. <strong>Bearing.</strong> Nothing at the goal\'s parameters: '
                   'a class could have followed, and its hypotheses were not checked.')

    def test_a_bearing_of_none_gives_no_procedural_reason(self):
        unchanged = ('research', 'unchanged')
        for reason in ('spent on it because the review decided that the item be attempted before the block ends.',
                       'the cycle was spent because the last entry left this owed and nothing else was named.',
                       'spent on it because the item had been queued for two days without an entry.'):
            with self.assertRaisesRegex(ValueError, 'procedural reason'):
                self.check([unchanged, unchanged], 'Unchanged. <strong>Bearing.</strong> Nothing at the goal\'s '
                           'parameters; ' + reason)
        self.check([unchanged, unchanged], 'Unchanged. <strong>Bearing.</strong> Nothing at the goal\'s parameters: '
                   'a proof would have excluded the family at four levels, and the attempt found no proof.')

    def test_a_third_unchanged_entry_states_its_bearing(self):
        unchanged = ('research', 'unchanged')
        self.check([unchanged], 'Unchanged.')
        self.check([unchanged, ('research', 'advanced'), unchanged], 'Unchanged.')
        with self.assertRaisesRegex(ValueError, 'Bearing'):
            self.check([unchanged, ('review', 'unchanged'), unchanged], 'Unchanged.')
        with self.assertRaisesRegex(ValueError, 'Bearing'):
            self.check([unchanged, unchanged], 'Unchanged. <strong>Bearing.</strong> none.')
        self.check([unchanged, unchanged], 'Unchanged. <strong>Bearing.</strong> At the degree the goal needs '
                   'this gives nothing; it was spent to decide whether the item continues.')

    def test_two_entries_without_bearing_end_an_items_turn(self):
        said = 'Unchanged. <strong>Bearing.</strong> ' + 'Nothing at the degree the goal needs; spent to decide the item.'
        none = ('research', 'unchanged', 'data-check="a:1" data-bearing="none"')
        with self.assertRaisesRegex(ValueError, 'data-bearing'):
            self.check([none, none], said, last='data-check="b:1"')                 # no declaration
        self.check([none, none], said, last='data-check="b:1" data-bearing="none"')  # a different item
        with self.assertRaisesRegex(ValueError, 'different queue item'):
            self.check([none, none], said, last='data-check="a:1" data-bearing="none"')
        some = ('research', 'unchanged', 'data-check="a:1" data-bearing="some"')
        self.check([none, some], said, last='data-check="a:1" data-bearing="none"')
        # An item queued as an idea or a build is held to the same rule: on 11 October 2026 a third entry
        # without bearing on a data-idea item was drafted and the check, which knew only three kinds, let it by.
        for kind in ('idea', 'build'):
            row = ('research', 'unchanged', f'data-{kind}="x" data-bearing="none"')
            with self.assertRaisesRegex(ValueError, 'different queue item'):
                self.check([row, row], said, last=f'data-{kind}="x" data-bearing="none"')
            self.check([row, row], said, last=f'data-{kind}="y" data-bearing="none"')

    def test_after_three_entries_without_bearing_the_next_states_its_best_outcome(self):
        said = 'Unchanged. <strong>Bearing.</strong> ' + 'Nothing at the degree the goal needs; spent to decide the item.'
        rows = [('a:1', 'none'), ('b:1', 'none'), ('c:1', 'none')]
        def body(earlier):
            text = ''.join(f'<article data-kind="research" data-route="r" data-goal-progress="unchanged" '
                           f'data-check="{item}" data-bearing="{bearing}"></article>' for item, bearing in earlier)
            return text + ('<article data-kind="research" data-route="r" data-goal-progress="unchanged" '
                           'data-check="d:1" data-bearing="none">')
        entry = '<p><strong>Follow-up.</strong> Closed: answered.</p>'
        full = body(rows)
        with self.assertRaisesRegex(ValueError, 'Best outcome'):
            FT.validate_bearing(full, full.rindex('<article'), said, entry)
        with self.assertRaisesRegex(ValueError, 'Best outcome'):
            FT.validate_bearing(full, full.rindex('<article'), said, entry + '<p><strong>Best outcome.</strong> Some.</p>')
        # A Best outcome that names no recorded result to beat is refused (16 October 2026).
        with self.assertRaisesRegex(ValueError, 'by its claim ID, the recorded result'):
            FT.validate_bearing(full, full.rindex('<article'), said, entry + '<p><strong>Best outcome.</strong> A '
                                'proof would give a family at the cutoff the goal needs; a refutation closes it.</p>')
        FT.validate_bearing(full, full.rindex('<article'), said, entry + '<p><strong>Best outcome.</strong> A proof '
                            'would give a family at the cutoff the goal needs, below lem:cylinder-killer-degree; a '
                            'refutation closes the item.</p>')
        nothing = ('<p><strong>Best outcome.</strong> Nothing at the goal\'s parameters; a family on which the frame '
                   'provably halves a degree beyond cor:frame-ratio-half, which settles one point.</p>')
        with self.assertRaisesRegex(ValueError, 'closes no queue item'):    # nothing to gain and nothing closed
            FT.validate_bearing(full, full.rindex('<article'), said,
                                '<p><strong>Follow-up.</strong> Continuing: open.</p><p><strong>Record '
                                'search.</strong> Searched the registry for the next attempt: no statement.</p>'
                                + nothing)
        FT.validate_bearing(full, full.rindex('<article'), said, entry + nothing)   # the entry closes an item
        FT.validate_bearing(full, full.rindex('<article'), said,                    # or removes it as developed
                            '<p><strong>Follow-up.</strong> Developed: built.</p>' + nothing)
        fewer = body(rows[1:])                                             # two such entries: not yet asked
        FT.validate_bearing(fewer, fewer.rindex('<article'), said, entry)
        broken = body([rows[0], ('b:1', 'some'), rows[2]])                 # a run broken by a bearing
        FT.validate_bearing(broken, broken.rindex('<article'), said, entry)

    def test_a_continuing_entry_in_such_a_run_states_its_record_search(self):
        said = 'Unchanged. <strong>Bearing.</strong> ' + 'Nothing at the degree the goal needs; spent to decide the item.'
        unchanged = ('research', 'unchanged')
        body = ''.join(f'<article data-kind="{k}" data-route="r" data-goal-progress="{g}"></article>'
                       for k, g in [unchanged, unchanged])
        body += '<article data-kind="research" data-route="r" data-goal-progress="unchanged" data-bearing="none">'
        follow = '<p><strong>Follow-up.</strong> Continuing. Next attempt: the count by supports.</p>'
        with self.assertRaisesRegex(ValueError, 'Record search'):
            FT.validate_bearing(body, body.rindex('<article'), said, follow)
        FT.validate_bearing(body, body.rindex('<article'), said, follow + '<p><strong>Record search.</strong> '
                            'Searched the registry for supports and circuits; nothing recorded answers it.</p>')
        FT.validate_bearing(body, body.rindex('<article'), said, '<p><strong>Follow-up.</strong> Developed: x.</p>')




class AttemptCheckedTest(unittest.TestCase):
    GATE = ('<p><strong>Verification gate.</strong> One reviewer. <strong>Attempt checked.</strong> The reviewer '
            'tried the step at which the attempt stops and did not close it either.</p>')

    def test_a_review_says_what_its_reviewer_found_at_the_step_where_the_attempt_stops(self):
        dated = 'entry-2026-10-12-review'
        with self.assertRaisesRegex(ValueError, 'Attempt checked'):
            validate(notebook(article(dated, kind='review', content=REPORT + ARCHITECTURE)))
        validate(notebook(article(dated, kind='review', content=REPORT + ARCHITECTURE + self.GATE)))
        with self.assertRaisesRegex(ValueError, 'Attempt checked'):    # the marker alone says nothing
            validate(notebook(article(dated, kind='review', content=REPORT + ARCHITECTURE
                                      + self.GATE.split('The reviewer')[0] + '</p>')))
        # Markup at the sentence's start does not hide it; the marker in another paragraph does not count.
        tagged = self.GATE.replace('The reviewer tried', '<a href="r.txt">The reviewer</a> tried')
        validate(notebook(article(dated, kind='review', content=REPORT + ARCHITECTURE + tagged)))
        elsewhere = self.GATE.replace('<strong>Verification gate.</strong>', '<strong>Remark.</strong>')
        with self.assertRaisesRegex(ValueError, 'Attempt checked'):
            validate(notebook(article(dated, kind='review', content=REPORT + ARCHITECTURE + elsewhere)))
        # Reviews recorded before the rule are left alone.
        validate(notebook(article('entry-2026-10-11-review', kind='review', content=REPORT + ARCHITECTURE)))


class InstanceCheckTest(unittest.TestCase):
    def test_a_review_s_decisive_test_evaluates_its_inequalities_at_the_instance(self):
        # 16 October 2026: a third review's test was decided by its own Trivial cases (room 2 < 3, called tight).
        dated = 'entry-2026-10-17-review'
        gate = AttemptCheckedTest.GATE
        base = ARCHITECTURE.replace('<strong>Power.</strong>', "<strong>Power.</strong> The instance lies outside the goal's window. ", 1)
        with self.assertRaisesRegex(ValueError, 'Instance check'):
            validate(notebook(article(dated, kind='review', content=REPORT + base + gate)))
        words = base.replace('<strong>Record search.</strong>',
                                     '<strong>Instance check.</strong> The room is tight. <strong>Record search.</strong>', 1)
        with self.assertRaisesRegex(ValueError, 'Instance check'):         # the label without numbers
            validate(notebook(article(dated, kind='review', content=REPORT + words + gate)))
        numbers = base.replace('<strong>Record search.</strong>',
                                       '<strong>Instance check.</strong> The room is \\(2+1=3\\le3\\), tight. '
                                       '<strong>Record search.</strong>', 1)
        validate(notebook(article(dated, kind='review', content=REPORT + numbers + gate)))


class CountListingReportTest(unittest.TestCase):
    ENTRY = '<article id="entry-2026-10-12-x" data-kind="research"><p><strong>Checks.</strong> It ran 12 tests.</p>'

    def test_an_entry_with_counts_and_no_logged_listing_is_reported_and_not_refused(self):
        line = FT.count_listing_report(self.ENTRY, ['-n 3 some search', 'draft_counts entry-2026-10-12-other 4'])
        self.assertIn('logged no run on this entry', line)
        self.assertIn('1 of its sentences hold a count', line)
        self.assertIsNone(FT.count_listing_report(self.ENTRY, ['draft_counts entry-2026-10-12-x 1']))
        # A run on an earlier draft that listed fewer sentences than the entry now holds is reported.
        grown = self.ENTRY + '<p><strong>Limit.</strong> Only 3 of them.</p>'
        self.assertIn('last listed 1 sentences with a count for this entry and it now holds 2',
                      FT.count_listing_report(grown, ['draft_counts entry-2026-10-12-x 1']))
        self.assertIsNone(FT.count_listing_report(grown, ['draft_counts entry-2026-10-12-x 1',
                                                           'draft_counts entry-2026-10-12-x 2']))
        # An entry without a count, and text without an article, have nothing to report.
        self.assertIsNone(FT.count_listing_report('<article id="e"><p><strong>Checks.</strong> None.</p>', []))
        self.assertIsNone(FT.count_listing_report('<p>loose text with 3 numbers</p>', []))

    def test_a_test_reported_decided_is_printed_beside_the_entry_s_hedges(self):
        def entry(test, body):
            return ('<article id="e" data-kind="research"><p class="entry-meta">Working proof. Label.</p>'
                    f'<p><strong>Architecture test.</strong> {test}</p>{body}')
        hedged = '<p>Steps two to four of the outline are not verified.</p>'
        lines = FT.decided_report(entry('<strong>Decided.</strong> The third outcome.', hedged))
        self.assertIn('Decided and hedged', lines[0])
        self.assertEqual(lines[1:], ['  firm: Architecture test. Decided. The third outcome.',
                                     '  hedge: Steps two to four of the outline are not verified.'])
        # A firm status line alone, a test not decided, and a decided test with nothing hedged print nothing.
        self.assertEqual(FT.decided_report(entry('<strong>Not decided.</strong> None occurred.', hedged)), [])
        self.assertEqual(FT.decided_report(entry('<strong>Decided.</strong> The third outcome.', '<p>Shown.</p>')), [])

    def test_a_closing_entry_s_absence_claims_are_printed(self):
        def entry(follow):
            return ('<article id="e" data-kind="research"><p>The scratch file is gone.</p>'
                    f'<p><strong>Follow-up.</strong> {follow}</p>')
        lines = FT.absence_report(entry('Closed: inapplicable.'))
        self.assertIn('Absence claims', lines[0])
        self.assertEqual(lines[1:], ['  absence: The scratch file is gone.'])
        self.assertEqual(FT.absence_report(entry('Continuing: one more attempt.')), [])


if __name__ == '__main__':
    unittest.main()
