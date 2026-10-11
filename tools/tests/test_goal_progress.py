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
    + (' <strong>Trivial cases.</strong> Adding an implied row changes neither quantity compared. '
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
        with self.assertRaisesRegex(ValueError, 'Trivial cases'):
            validate(valid.replace('<strong>Trivial cases.</strong>', ''))
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
        FT.validate_bearing(full, full.rindex('<article'), said, entry + '<p><strong>Best outcome.</strong> A proof '
                            'would give a family at the cutoff the goal needs; a refutation closes the item.</p>')
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


if __name__ == '__main__':
    unittest.main()
