#!/usr/bin/env python3
"""Real finalizer/timing/archive integration with a fixture-only job launcher."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]



OBSTACLE = ('<h4>Obstacle</h4><p>No recorded degree method handles many adversarial dense '
            'constraints: every method checked is local or symmetric.</p>')

PROGRESS_ATTRS = ' data-obligation="open-goal" data-goal-progress="unchanged"'
PROGRESS_REPORT = ('<p><strong>New mathematics.</strong> A scoped result was checked, without settling '
                   'the required implication.</p><p><strong>Goal progress.</strong> The general '
                   'implication remains unchanged; no uniform proof was found.</p>'
                   '<p><strong>Nonvacuity.</strong> The recorded bound and the claim predict different values '
                   'at the sizes computed, so the check could fail.</p>')
ARCHITECTURE = '<h4>Architecture review</h4>' + ''.join(
    f'<p><strong>{label}.</strong> The target and alternative are compared against all hypotheses '
    'and the goal budget. <a href="review.txt">Reviewer evidence</a>. <strong>Downstream.</strong> Through '
    'thm:downstream-transfer the target gives the statement wanted at every parameter. <strong>Attempt.</strong> '
    'The cited statements were tried on the test and decide it at no reachable size. <strong>Trivial cases.</strong> '
    '<strong>Test disposition.</strong> New operation. <strong>Operation.</strong> '
    'Contract the two specified maps on their shared domain and retain the paid kernel. '
    '<strong>Prediction.</strong> Either the shared contraction is strict or the stated residual survives. '
    'Adding an implied row changes neither quantity compared. <strong>Power.</strong> The recorded '
    'ceilings leave the outcomes apart at the sizes reachable. <strong>Record search.</strong> '
    'Searched the registry for the terms of the test; no recorded claim answers it.</p>'
    for label in ('Necessary target', 'Extra requirements', 'Independent alternative',
                  'Rank normalization', 'Decision', 'Decisive test'))


def reporting(tags):
    attrs = tags + PROGRESS_ATTRS + (' id="current"' if 'id="' not in tags else '')
    text = PROGRESS_REPORT + (ARCHITECTURE if 'data-kind="review"' in tags else '')
    return attrs, text

from importlib.machinery import SourceFileLoader

FT = SourceFileLoader('finish_turn', str(Path(__file__).resolve().parents[2] / 'tools/finish-turn.py')).load_module()


class StaleReviewHint(unittest.TestCase):
    def test_a_stale_review_gets_the_refresh_steps_and_other_errors_do_not(self):
        hint = FT.stale_review_hint(['lem:x: topics is stale', 'lem:x: significance is missing'])
        self.assertIn('tools/claim_refresh.py', hint)
        self.assertEqual(FT.stale_review_hint(['lem:x: significance is missing']), '')


class ArchitectureDisposition(unittest.TestCase):
    def new_test(self):
        return ('<strong>Test disposition.</strong> New operation. '
                '<strong>Operation.</strong> Contract the specified maps on their common paid domain. '
                '<strong>Prediction.</strong> A strict loss or an unchanged residual distinguishes the outcomes. ')

    def validate(self, value, earlier=None):
        if earlier is None:
            earlier = ('<article id="old" data-kind="review"><p><strong>Decisive test.</strong>'
                       'The original complete output cost is still unanswered.</p></article>')
        body = (earlier + '<article id="current" data-kind="review"></article>'
                '<article id="later" data-kind="review"><p><strong>Decisive test.</strong>'
                'The later complete output cost is still unanswered.</p></article>')
        FT.validate_test_disposition(body, body.index('<article id="current"'), value)

    def test_missing_and_unknown_dispositions_are_rejected(self):
        self.validate(self.new_test())
        self.validate(self.new_test().replace('New operation. ', 'New operation.\n'))
        for note in ('', '<strong>Test disposition.</strong> Rewritten question. '):
            value = self.new_test().replace('<strong>Test disposition.</strong> New operation. ', note)
            with self.subTest(note=note), self.assertRaisesRegex(ValueError, 'Test disposition'):
                self.validate(value)

    def test_new_operation_and_prediction_have_the_report_floor(self):
        for label in ('Operation', 'Prediction'):
            start = self.new_test().index(f'<strong>{label}.</strong>')
            end = self.new_test().find('<strong>', start + len(f'<strong>{label}.</strong>'))
            end = len(self.new_test()) if end == -1 else end
            for size in (0, 39, 40):
                value = (self.new_test()[:start] + f'<strong>{label}.</strong>'
                         + 'x' * size + self.new_test()[end:])
                with self.subTest(label=label, size=size):
                    if size == 40:
                        self.validate(value)
                    else:
                        with self.assertRaisesRegex(ValueError, label):
                            self.validate(value)
            without = self.new_test()[:start] + self.new_test()[end:]
            with self.subTest(label=label, missing=True), self.assertRaisesRegex(ValueError, label):
                self.validate(without)
            multiline = (self.new_test()[:start] + f'<strong>{label}.</strong>'
                         + 'x' * 20 + '\n' + 'x' * 20 + self.new_test()[end:])
            self.validate(multiline)
            for size in (39, 40):
                for payload in (f'<span data-padding="long attribute">{"x" * size}</span>', '&#120;' * size):
                    value = (self.new_test()[:start] + f'<strong>{label}.</strong>'
                             + payload + self.new_test()[end:])
                    with self.subTest(label=label, size=size, payload=payload):
                        if size == 40:
                            self.validate(value)
                        else:
                            with self.assertRaisesRegex(ValueError, label):
                                self.validate(value)

    def test_retained_question_links_an_earlier_review_only(self):
        def retained(anchor):
            return (f'<strong>Test disposition.</strong> Retained exploratory: '
                    f'<a href="#{anchor}">Earlier unanswered test</a>.')
        self.validate(retained('old'))
        self.validate(retained('old'), '<article id="old" data-kind="review">\n'
                      '<p><strong>Decisive test.</strong>Earlier unanswered test.</p>\n</article>')
        for anchor, earlier in (('missing', '<article id="old" data-kind="review"></article>'),
                                ('current', '<article id="old" data-kind="review"></article>'),
                                ('old', '<article id="old" data-kind="research"></article>'),
                                ('old', '<article data-kind="review"></article>'),
                                ('later', '<article id="old" data-kind="review"></article>')):
            with self.subTest(anchor=anchor, earlier=earlier), self.assertRaisesRegex(ValueError, 'earlier review'):
                self.validate(retained(anchor), earlier)
        for tag in ('<article id="old" data-kind="review">', '<article data-kind="review">',
                    '<article id="old" data-kind="research">'):
            for content in ('', '<p><strong>Decisive test.</strong>Earlier unanswered test.</p>'):
                if 'id="old"' in tag and 'data-kind="review"' in tag and content:
                    continue
                with self.subTest(tag=tag, content=content), self.assertRaisesRegex(ValueError, 'earlier review'):
                    self.validate(retained('old'), tag + content + '</article>')
        with self.assertRaisesRegex(ValueError, 'earlier review'):
            self.validate('<strong>Test disposition.</strong> Retained exploratory without a link.')

    def test_progress_gate_checks_the_decisive_test_classification(self):
        def body(architecture):
            return ('<li data-route-item="step">step</li><article id="current" '
                    'data-kind="review" data-route="step"' + PROGRESS_ATTRS + '>'
                    + PROGRESS_REPORT + architecture + '</article>')
        valid = body(ARCHITECTURE)
        FT.validate_progress(valid, valid.index('<article'), valid.index('</article>'),
                             check_registered_claims=False)
        invalid = body(ARCHITECTURE.replace('<strong>Test disposition.</strong> New operation. ', ''))
        with self.assertRaisesRegex(ValueError, 'Test disposition'):
            FT.validate_progress(invalid, invalid.index('<article'), invalid.index('</article>'),
                                 check_registered_claims=False)


class ReviewTestContext(unittest.TestCase):
    """The linked review's Decision, Prediction, Power and Attempt, and the claims they cite, are printed."""
    REVIEW = ('<article id="entry-r" data-kind="review"><p><strong>Decision.</strong> Core: test dense components; '
              'lem:sparse-weight-survival already covers the sparse ones.</p>'
              '<p><strong>Decisive test.</strong> <strong>Test disposition.</strong> New operation. '
              '<strong>Operation.</strong> Compare ratios. <strong>Prediction.</strong> Ratios stay canonical. '
              '<strong>Trivial cases.</strong> None. <strong>Power.</strong> The yes outcome is decided for '
              'polynomially many classes by lem:sparse-weight-survival. <strong>Attempt.</strong> It stops at dense '
              'components. <strong>Record search.</strong> Nothing.</p></article>')

    def load(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('ft', Path(__file__).resolve().parents[1] / 'finish-turn.py')
        ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)
        return ft

    def test_the_review_says_what_its_power_paragraph_decides(self):
        ft = self.load()
        lines = ft.review_test_context(self.REVIEW, 'entry-r', {'lem:sparse-weight-survival': 'Rank at least h/s.'})
        joined = '\n'.join(lines)
        self.assertIn('Decision. Core: test dense components', joined)
        self.assertIn('Power. The yes outcome is decided for polynomially many classes', joined)
        self.assertIn('Attempt. It stops at dense components.', joined)
        self.assertIn('Prediction. Ratios stay canonical.', joined)
        self.assertNotIn('Trivial cases', joined)
        self.assertEqual(joined.count('lem:sparse-weight-survival: Rank at least h/s.'), 1)

    def test_an_entry_linking_the_review_gets_its_context_at_the_finisher(self):
        ft = self.load()
        entry = ('<article id="entry-x" data-kind="research"><p><strong>Architecture test.</strong> '
                 '<strong>Not decided.</strong> The <a href="#entry-r">review</a> test is open for dense ones.</p>')
        lines = ft.architecture_context_report(self.REVIEW + entry, entry)
        self.assertTrue(lines and 'entry-r' in lines[0])
        self.assertEqual(ft.review_test_context(self.REVIEW, 'entry-missing', {}), [])

    def test_summaries_are_read_without_parsing_the_whole_registry(self):
        ft = self.load()
        index = Path(tempfile.mkdtemp()) / 'index.json'
        index.write_text(json.dumps({'claims': [{'id': 'lem:a', 'summary': 'First "quoted".'},
                                                {'id': 'lem:b', 'title': 'no summary'},
                                                {'id': 'lem:c', 'summary': 'Third.'}]}, indent=1))
        self.assertEqual(ft.cited_summaries(index, ['lem:a', 'lem:b', 'lem:c', 'lem:z']),
                         {'lem:a': 'First "quoted".', 'lem:c': 'Third.'})


class ChecksNote(unittest.TestCase):
    """The finisher warns when its checks are slow, and stays quiet otherwise."""

    def test_slow_checks_are_reported(self):
        self.assertIn('Warning: the finisher\'s checks took 6.5 s', FT.checks_note(FT.CHECKS_WARN_S + 1.5))

    def test_fast_checks_print_nothing(self):
        self.assertEqual(FT.checks_note(FT.CHECKS_WARN_S / 4), '')



class DrainingReviewsTest(unittest.TestCase):
    def body(self, text, attrs=' data-draining="true"'):
        queue = '<section id="lead-queue"' + attrs + '><ol>' + ''.join(
            f'<li data-lead="r:{i}">item</li>' for i in range(21)) + '</ol></section>'
        return ('<li data-route-item="step">step</li>' + queue
                + '<article data-kind="review">' + text + '</article>')

    def validate(self, body, **kwargs):
        FT.validate_leads(body, body.index('<article'), body.index('</article>'), **kwargs)

    def test_draining_review_omits_both_sections_but_keeps_obstacle(self):
        self.validate(self.body(OBSTACLE))
        with self.assertRaisesRegex(ValueError, 'Obstacle'):
            self.validate(self.body('<p>Review without its obstacle.</p>'))
        for heading in ('Outside leads', 'Absurd bridges'):
            with self.subTest(heading=heading), self.assertRaisesRegex(ValueError, 'queue is draining'):
                self.validate(self.body(OBSTACLE + f'<h4>{heading}</h4><ol><li>New item</li></ol>'))

    def test_non_draining_review_still_requires_leads(self):
        for attrs in ('', ' data-backpressure="off"'):
            with self.subTest(attrs=attrs), self.assertRaisesRegex(ValueError, 'Outside leads'):
                self.validate(self.body(OBSTACLE, attrs))

    def test_ordered_review_lists_enforce_picks(self):
        item = ('<li data-pick>Mechanism. <strong>Answers.</strong> The obstacle. <strong>Break point.</strong> None '
                'found. <strong>Test.</strong> Passed.</li>')
        text = OBSTACLE + '<h4>Outside leads</h4><ol>' + item * 3 + '</ol>'
        text += '<h4>Absurd bridges</h4><ol>' + item * 2 + '</ol>'
        self.validate(self.body(text, ''), draining=False)
        with self.assertRaisesRegex(ValueError, 'most promising'):
            self.validate(self.body(text.replace(' data-pick', '', 1), ''), draining=False)

    def test_pre_entry_state_controls_review_that_finishes_draining(self):
        body = self.body(OBSTACLE, '')
        self.validate(body, draining=True)
        with self.assertRaisesRegex(ValueError, 'Outside leads'):
            self.validate(body, draining=False)


class FinalizationTest(unittest.TestCase):
    def fixture_finisher(self):
        """The fixture's finish-turn.py loaded in process, so its ROOT is the fixture root (as in a subprocess)
        without paying a Python start per case."""
        import importlib.util
        before = list(sys.path)
        spec = importlib.util.spec_from_file_location('ft_fixture', self.root / 'tools/finish-turn.py')
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path[:] = before
        return module

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='math-finish-turn-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'tools').mkdir()
        shutil.copy2(ROOT / 'tools/notebook_context.py', self.root / 'tools/notebook_context.py')
        shutil.copy2(ROOT / 'tools/recovery_evidence.py', self.root / 'tools/recovery_evidence.py')
        shutil.copy2(ROOT / 'tools/notebook_math.py', self.root / 'tools/notebook_math.py')
        shutil.copy2(ROOT / 'tools/claim_attention.py', self.root / 'tools/claim_attention.py')
        shutil.copy2(ROOT / 'tools/bearing_ledger.py', self.root / 'tools/bearing_ledger.py')
        for name in ('tools/notebooks.py', 'tools/codex_state.py', 'tools/finish-turn.py', 'tools/lead_queue.py', 'tools/branch_extension.py','tools/result_names.py', 'tools/archive-session.py', 'tools/claim_registry.py', 'tools/claim_notices.py', 'tools/claim_maintenance.py', 'tools/claim_reviews.py', 'tools/claim_evidence.py', 'tools/notebook-excerpt.py', 'tools/claim_registration.py'):
            shutil.copy2(ROOT / name, self.root / name)
        # Exercise real metadata, report generation and archival without requiring
        # this laptop's systemd slice on CI. Only the tiny fixture archiver may
        # use this test double; production compute.sh is never changed.
        shutil.copy2(ROOT / 'compute.sh', self.root / 'compute_fixture.py')
        launcher = self.root / 'compute.sh'
        launcher.write_text('''#!/usr/bin/env python3
import sys
from pathlib import Path
import compute_fixture as compute

def archive_invocation(command, threads, timeout, unit):
    expected = Path(__file__).parent / 'tools/archive-session.py'
    if len(command) != 3 or command[:2] != [sys.executable, str(expected)]:
        raise AssertionError('Unexpected fixture workload: ' + repr(command))
    return command

compute.invocation = archive_invocation
sys.exit(compute.main())
''')
        launcher.chmod(0o755)
        # Make accidental host-service access fail even on a configured laptop.
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        for name in ('systemctl', 'systemd-run'):
            guard = bin_dir / name
            guard.write_text('#!/bin/sh\necho "Unexpected host-service access in fixture" >&2\nexit 99\n')
            guard.chmod(0o755)
        self.command_env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ.get('PATH', ''))
        # a real session's scratchpad must not decide fixture runs (in process or in a subprocess)
        self.command_env.pop('CLAUDE_CODE_SESSION_ID', None)
        self.command_env.pop('CODEX_THREAD_ID', None)
        scrub = mock.patch.dict(os.environ)
        scrub.start()
        self.addCleanup(scrub.stop)
        os.environ.pop('CLAUDE_CODE_SESSION_ID', None)
        os.environ.pop('CODEX_THREAD_ID', None)
        (self.root / 'research/claims').mkdir(parents=True)
        (self.root / 'research/context-budgets.json').write_text(json.dumps({
            'version': 1, 'hard_multiplier': 1.5, 'characters_per_word': 12,
            'total_soft_words': 100, 'regions': {'@intro': 100}}))
        for schema in ('schema.json', 'schema-v1.json'):
            shutil.copy2(ROOT / 'research/claims' / schema, self.root / 'research/claims' / schema)
        self.command('compute.sh', 'start', 'test_turn', '--agent', 'Test agent',
                     '--model', 'Test model, high')

    def command(self, script, *args, check=True):
        result = subprocess.run([sys.executable, str(self.root / script), *args],
                                cwd=self.root, env=self.command_env, text=True, capture_output=True)
        if check and result.returncode:
            self.fail(f'{script} exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}')
        return result

    def events(self, name):
        return [json.loads(line) for line in
                (self.root / 'research/logs' / f'{name}.jsonl').read_text().splitlines()]

    def test_complete_and_start_next(self):
        notebook = self.root / 'notebook.html'
        content = ('<section id="research-record">\nearlier record\n'
                   '<article id="new-entry">\n<p class="entry-meta">Status: test.</p>\n'
                   '<!-- TIMING test_turn -->\n'
                   '</article>\nappend here\n</section>\n')
        notebook.write_text(content)
        self.command('tools/finish-turn.py', 'test_turn', '--next', 'next_turn')
        table = (self.root / 'research/results/test_turn/timing.html').read_text().strip()
        table = table.replace('<div class="timing-report"', '<div data-generated="finish-turn-timing-v1" class="timing-report"', 1)
        expected = content.replace('<!-- TIMING test_turn -->', table).replace(
            'Status: test.</p>', 'Status: test. <span data-generated="finish-turn-producer-v1">Produced by Test agent (Test model, high).</span></p>')
        self.assertEqual(notebook.read_text(), expected)
        archive = self.root / 'research/provenance/session-records/test_turn'
        self.assertEqual((archive / 'session.jsonl').read_bytes(),
                         (self.root / 'research/logs/test_turn.jsonl').read_bytes())
        stop = next(e for e in self.events('test_turn') if e['event'] == 'stop')
        following = self.events('next_turn')
        self.assertGreaterEqual(following[0]['monotonic_s'], stop['monotonic_s'])
        self.assertTrue(any(e.get('category') == 'preparation' for e in following))
        self.assertFalse(any(e['event'] == 'stop' for e in following))
        self.assertEqual((following[0]['agent'], following[0]['model']),
                         ('Test agent', 'Test model, high'))
        repeated = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(repeated.returncode, 0)
        self.assertEqual(notebook.read_text(), expected)

    def test_an_unanswered_stand_in_review_is_answered_in_the_entry_being_finished(self):
        (self.root / 'tools/hooks').mkdir()
        for name in ('tools/stand_in_review.py', 'tools/haiku_judge.py', 'tools/hooks/stop_checks.py'):
            shutil.copy2(ROOT / name, self.root / name)
        state = self.root / 'research/logs/stand-in-review'
        state.mkdir(parents=True)
        (state / 'r.json').write_text('{}')
        (state / 'state.json').write_text(json.dumps({'fired': '2026-01-01T00:00:00+00:00', 'unanswered': 'research/logs/stand-in-review/r.json'}))
        notebook = self.root / 'notebook.html'
        entry = ('<section id="research-record">\n<article id="old"><p><strong>Review.</strong> An earlier entry answered an earlier '
                 'review, at length enough.</p></article>\n<article id="new-entry">\n<p class="entry-meta">Status: test.</p>\n{}'
                 '<!-- TIMING test_turn -->\n</article>\n</section>\n')
        for answer in ('', '<p><strong>Review.</strong> Noted.</p>\n'):
            notebook.write_text(entry.format(answer))
            refused = self.command('tools/finish-turn.py', 'test_turn', check=False)
            self.assertEqual(refused.returncode, 1)
            self.assertIn('The stand-in review in research/logs/stand-in-review/r.json is unanswered', refused.stderr)
            self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))
        review = ('<p><strong>Review.</strong> The first objection was right and is fixed; the second misread '
                  'the text.</p>\n')
        # The Review paragraph alone still leaves the meta-question for the right objection unanswered.
        notebook.write_text(entry.format(review))
        refused = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertEqual(refused.returncode, 1)
        self.assertIn('is answered without its meta-question', refused.stderr)
        notebook.write_text(entry.format(review + '<p><strong>Meta.</strong> The habit of reporting before checking '
                                         'the record; AGENTS.md now asks for the check first.</p>\n'))
        done = self.command('tools/finish-turn.py', 'test_turn')
        # The answered review is settled, and the review that is due says why it did not run here.
        self.assertIsNone(json.loads((state / 'state.json').read_text())['unanswered'])
        self.assertIn('Stand-in review not run: no transcript of this session was found.', done.stdout)

    def test_review_crossing_queue_threshold_keeps_pre_entry_state_after_archive(self):
        import lead_queue
        notebook = self.root / 'notebook.html'
        queue = '<section id="lead-queue"><ol>' + ''.join(
            f'<li data-idea="old-{i}" data-source="old">Existing research question {i}.</li>'
            for i in range(lead_queue.CAP - 1)) + '</ol></section>'
        earlier = ''.join(
            f'<article id="old-{i}" data-kind="research" data-route="general-step">'
            '<p class="entry-meta">Earlier research.</p></article>' for i in range(6))
        base = ('<section id="remaining-route"><li data-route-item="general-step">step</li></section>'
                + queue + '<section id="research-record">' + earlier + '</section>')
        notebook.write_text(base)
        subprocess.run(['git', 'init', '-q'], cwd=self.root, check=True)
        subprocess.run(['git', 'add', 'notebook.html'], cwd=self.root, check=True)
        subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'Before review'], cwd=self.root, check=True)
        passed = ('<li data-pick>A concrete continuation. <strong>Answers.</strong> The open obstacle. '
                  '<strong>Test.</strong> Passed. <strong>Break point.</strong> The full source bound '
                  'still requires a proved compatibility statement.</li>')
        rejected = ('<li>A rejected shortcut. <strong>Answers.</strong> The same open obstacle. '
                    '<strong>Test.</strong> Falsified: this proposed transfer fails its control.</li>')
        tags, report = reporting('id="current" data-kind="review" data-route="general-step" '
                                 'data-open-items="3"')
        entry = (f'<article {tags}><p class="entry-meta">Reviewed route assessment.</p>'
                 '<p><strong>General statement.</strong> The recorded conjecture remains open '
                 '(conj:fixture-general); this review does not promote it.</p>' + report + OBSTACLE
                 + '<h4>Outside leads</h4><ul>' + passed + rejected * 2 + '</ul>'
                 + '<h4>Absurd bridges</h4><ul>' + rejected * 2 + '</ul>'
                 + '<!-- TIMING test_turn --></article>')
        current = base
        at = current.rindex('</section>')
        current = current[:at] + entry + current[at:]
        current, added = lead_queue.append_new(current)
        self.assertEqual(added, 1)
        self.assertFalse(lead_queue.is_draining(base))
        self.assertTrue(lead_queue.is_draining(current))
        budget_path = self.root / 'research/context-budgets.json'
        budget = json.loads(budget_path.read_text())
        budget['regions']['remaining-route'] = 100
        budget_path.write_text(json.dumps(budget))
        notebook.write_text(current)
        (self.root / 'research/logs/claim-searches.jsonl').write_text(json.dumps({
            'unix_s': self.events('test_turn')[0]['unix_s'], 'query': 'fixture compatibility'}) + '\n')
        self.fixture_finisher().finish(self.root, 'test_turn', next_turn='next_turn')
        self.assertNotIn('<!-- TIMING test_turn -->', notebook.read_text())
        self.assertIn('data-generated="finish-turn-timing-v1"', notebook.read_text())
        self.assertTrue((self.root / 'research/provenance/session-records/test_turn/manifest.json').exists())
        self.assertTrue(any(e['event'] == 'stop' for e in self.events('test_turn')))
        self.assertFalse(any(e['event'] == 'stop' for e in self.events('next_turn')))

    def test_incomplete_new_claim_is_rejected_before_clock_stops(self):
        sys.path.insert(0,str(ROOT/'tools'))
        import claim_registry as cr
        data=cr.upgrade(cr.import_markdown('# Index\n\n'+cr.HEADER+
            '| `lem:new` | New statement | Working proof | [Proof](source.md) |\n'))
        complete_path=self.root/'research/claims/index.json'
        empty=dict(data,claims=[])
        complete_path.write_text(json.dumps(empty))
        (self.root/'research/CLAIM_INDEX.md').write_text(cr.render(empty))
        (self.root/'research/source.md').write_text('Source')
        subprocess.run(['git','init','-q'],cwd=self.root,check=True)
        subprocess.run(['git','add','research'],cwd=self.root,check=True)
        subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid',
                        'commit','-qm','Baseline'],cwd=self.root,check=True)
        complete_path.write_text(json.dumps(data))
        (self.root/'research/CLAIM_INDEX.md').write_text(cr.render(data))
        notebook=self.root/'notebook.html'
        notebook.write_text('<section id="research-record"><article id="new-entry">'
            '<p class="entry-meta">Status: test.</p><!-- TIMING test_turn --></article></section>')
        result=self.command('tools/finish-turn.py','test_turn',check=False)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Changed-claim metadata incomplete',result.stderr)
        self.assertFalse(any(e['event']=='stop' for e in self.events('test_turn')))
        complete_path.write_text(json.dumps(empty))
        (self.root/'research/CLAIM_INDEX.md').write_text(cr.render(empty))
        notebook.write_text('<section id="research-record"><article id="new-entry" '
            'data-claims="none" data-claim-note="Framework-only">'
            '<p class="entry-meta">Status: test.</p><code>lem:forgotten</code>'
            '<!-- TIMING test_turn --></article></section>')
        result=self.command('tools/finish-turn.py','test_turn',check=False)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('explicit claim label is unregistered',result.stderr)
        self.assertFalse(any(e['event']=='stop' for e in self.events('test_turn')))


    def test_misplaced_marker_does_not_stop_session(self):
        notebook = self.root / 'notebook.html'
        marker = '<!-- TIMING test_turn -->'
        cases = [
            '<section id="overview"><article>' + marker + '</article></section>'
            '<section id="research-record"></section>',
            '<section id="research-record">' + marker + '</section>',
            '<section id="research-record"><article></article></section>' + marker,
            '<section id="research-record"><article>' + marker + '</article></section>',
            '<section id="research-record"><article><p class="entry-meta">Status.</p>'
            'It cost $5.' + marker + '</article></section>',
        ]
        for content in cases:
            with self.subTest(content=content):
                notebook.write_text(content)
                result = self.command('tools/finish-turn.py', 'test_turn', check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(notebook.read_text(), content)
                self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))

    def test_passed_bridges_need_follow_up(self):
        notebook = self.root / 'notebook.html'
        marker = '<!-- TIMING test_turn -->'
        route = '<section id="remaining-route"><li data-route-item="general-step">x</li></section>'
        general = ('<p><strong>General statement.</strong> For every level the kernel is spanned by '
                   'short elements (conj:fixture-general).</p>')
        ok = ' <strong>Answers.</strong> It would resolve it. <strong>Break point.</strong> None found. <strong>Test.</strong> Passed.'
        leads = (OBSTACLE + f'<h4>Outside leads</h4><ul><li data-pick>a{ok}</li><li data-pick>b{ok}</li><li data-pick>c{ok}</li></ul>'
                 f'<h4>Absurd bridges</h4><ul><li data-pick>d{ok}</li><li>e <strong>Answers.</strong> y. '
                 '<strong>Test.</strong> Falsified: x.</li></ul>')
        old_review = ('<article id="rev1" data-kind="review" data-route="general-step">'
                      '<p class="entry-meta">Review.</p>' + general + leads + '</article>')
        research = '<article data-kind="research" data-route="general-step"{}><p class="entry-meta">S.</p></article>'
        def record(earlier, tags, extra=''):
            tags, report = reporting(tags)
            return (route + '<section id="research-record">' + old_review + earlier + f'<article {tags}>'
                    '<p class="entry-meta">Status.</p>' + general + extra + report + marker + '</article></section>')
        tagged = 'data-kind="research" data-route="general-step"'
        reviewed = 'id="rev2" data-kind="review" data-route="general-step" data-open-items="2"'
        follow = '<h4>Bridge follow-up</h4><ul><li data-bridge="rev1:1">Tried it. <strong>Follow-up.</strong> {}</li></ul>'
        lead_follow = ('<h4>Lead follow-up</h4><ul>' + ''.join(
            f'<li data-lead="rev1:{n}">Worked on it. <strong>Follow-up.</strong> Continuing: next.</li>'
            for n in (1, 2, 3)) + '</ul>')
        # Open items wait in the lead queue (test_lead_queue.py); a review lists only changed follow-ups.
        rejected = [
            record(research.format('') * 6, reviewed, leads + follow.format('Pending.') + lead_follow),  # no outcome
            record(research.format('') * 6, reviewed, leads + follow.format('Continuing: x.')
                   + lead_follow.replace('Continuing: next.', 'Pending.')),      # lead follow-up without outcome
        ]
        accepted = [
            record(research.format('') * 6, reviewed, leads),                  # no follow-ups: nothing changed
            record(research.format('') * 6, reviewed, leads + follow.format('Continuing: x.')),   # one change only
            record(research.format('') * 2, tagged),
            record(research.format(' data-bridge="rev1:1"') + research.format(''), tagged),
            record(research.format('') * 2, tagged + ' data-bridge="rev1:1"'),
            record(research.format('') * 6, reviewed, leads + follow.format('Continuing: next cycle.') + lead_follow),
            record(research.format('') * 6, reviewed, leads + follow.format('Closed: the translation fails.')
                   + lead_follow),
            record(research.format(' data-lead="rev1:2"') + research.format(''), tagged),
        ]
        import contextlib, io
        ft = self.fixture_finisher()   # in process: these cases exercise validate_marker only
        with contextlib.redirect_stderr(io.StringIO()):   # the bridge reminder is expected output
            for content in rejected:
                with self.subTest(content=content[-400:]):
                    with self.assertRaises(ValueError):
                        ft.validate_marker(content, marker)
            for content in accepted:
                with self.subTest(content=content[-400:]):
                    ft.validate_marker(content, marker)

    def test_route_review_and_status_length_are_enforced(self):
        notebook = self.root / 'notebook.html'
        marker = '<!-- TIMING test_turn -->'
        route = '<section id="remaining-route"><li data-route-item="general-step">x</li></section>'
        general = ('<p><strong>General statement.</strong> For every level the kernel is spanned by '
                   'short elements (conj:fixture-general).</p>')
        def record(earlier, tags, status='Status.', general=general, earlier_status='Status.', earlier_claims=None):
            tags, report = reporting(tags)
            claims = earlier_claims or [''] * len(earlier)
            entries = ''.join(f'<article data-kind="{kind.split(":")[0]}" data-route="general-step"'
                              + (f' data-open-items="{kind.split(":")[1]}"' if ':' in kind else '')
                              + (f' data-claims="{cl}"' if cl else '') + '>'
                              f'<p class="entry-meta">{earlier_status}</p></article>' for kind, cl in zip(earlier, claims))
            return (route + '<section id="research-record">' + entries + f'<article {tags}>'
                    f'<p class="entry-meta">{status}</p>' + general + report + marker + '</article></section>')
        tagged = 'data-kind="research" data-route="general-step"'
        reviewed = 'data-kind="review" data-route="general-step" data-open-items="3"'
        goal_review = reviewed + ' data-scope="goal"'
        across = ('<h4>Across the goal</h4><ul><li>Statement 1: unchanged, ten cycles.</li>'
                  '<li>Statement 2: unchanged, none.</li></ul><p><strong>Decision.</strong> Core: the window.</p>')
        ok = ' <strong>Answers.</strong> It would resolve it. <strong>Break point.</strong> None found. <strong>Test.</strong> Passed.'
        leads = (OBSTACLE + f'<h4>Outside leads</h4><ul><li data-pick>a{ok}</li><li>b <strong>Answers.</strong> y. '
                 '<strong>Test.</strong> Falsified: x.</li>'
                 f'<li data-pick>c{ok}</li></ul><h4>Absurd bridges</h4><ul><li data-pick>d{ok}</li>'
                 '<li>e <strong>Answers.</strong> y. <strong>Test.</strong> Not run: needs a kernel.</li></ul>')
        rejected = [
            record(['research'] * 6, reviewed),                       # a review without outside leads
            record(['research'] * 6, reviewed.replace(' data-open-items="3"', ''),
                   general=general + leads),                          # no open-item count
            record(['review:3'] + ['research'] * 10, reviewed, general=general + leads),  # count not dropped
            record(['review:3'] + ['research'] * 10, goal_review, general=general + leads),  # no Across the goal
            record(['review:3'] + ['research'] * 10, goal_review,
                   general=general + leads + across.replace('Core', 'Maybe')),  # no decision
            record(['research'] * 6, reviewed, general=general + leads.replace(f'<li data-pick>c{ok}</li>', '')),  # two leads
            record(['research'] * 6, reviewed, general=general + leads.replace(
                '<li>e <strong>Answers.</strong> y. <strong>Test.</strong> Not run: needs a kernel.</li>', '')),  # one bridge
            record(['research'] * 6, reviewed, general=general + leads.replace(f'<li data-pick>d{ok}</li>', '<li data-pick>d</li>')),  # untested
            record(['research'] * 6, reviewed, general=general + leads.replace(OBSTACLE, '')),  # no obstacle
            record(['research'] * 6, reviewed, general=general + leads.replace(
                f'<li data-pick>a{ok}</li>', '<li data-pick>a <strong>Test.</strong> Passed.</li>')),  # item not aimed at the obstacle
            record(['research'] * 6, reviewed, general=general + leads.replace(
                f'<li data-pick>a{ok}</li>',
                f'<li data-pick>a{ok.replace("<strong>Break point.</strong> None found. ", "")}</li>')),  # passed, break point unevaluated
            record(['research'] * 6, reviewed, general=general + leads.replace(
                f'<li data-pick>a{ok}</li>',
                f'<li data-pick>a{ok.replace("Passed", "Passed for the quadratic cost")}</li>')),  # passed on another object
            record(['research'] * 6, reviewed, general=general + leads.replace(
                f'<li data-pick>a{ok}</li>',
                f'<li data-pick>a{ok.replace("None found. <strong>Test.</strong> Passed.", "Seen. <strong>Test.</strong> Passed. <strong>Break point.</strong> It is the coupling in another form.")}</li>')),  # restatement found after the test
            record(['research'] * 6, reviewed, general=general + leads.replace(
                'Not run: needs a kernel.', 'Not run: the theorem was recalled, not read.')),  # unread, no retrieval named
            record(['research'] * 6, reviewed, general=general + leads.replace(
                'Not run: needs a kernel.', 'Not run: Recalled. <strong>Retrieval.</strong> None tried.')),  # upper case, none named
            record(['research'] * 6, reviewed, general=general + leads.replace(
                '<li>e <strong>Answers.</strong>', '<li>e (a theorem recalled) <strong>Answers.</strong>')),  # unread in the citation
            record([], ''),                                           # untagged entry
            record([], 'data-kind="research" data-route="sub-gap"'),  # not a declared route item
            record(['research'] * 6, tagged),                         # seventh research entry in a row
            record(['review'] + ['research', 'formalization'] * 6, tagged),
            record([], tagged, status='S' * 301),
            record([], tagged, general=''),                           # no General statement
            record([], tagged, general='<p><strong>General statement.</strong> A claim for all '
                   'parameters without any registered identifier.</p>'),
            record(['research'], tagged + ' data-claims="ex:b"', status='Finite check.',
                   earlier_status='Finite check.'),                   # two finite checks in a row
            record(['research'], tagged + ' data-claims="ex:b"', status='Finite check and a failed proof route.',
                   earlier_status='Finite check.'),                   # status words do not escape the rule
            record(['research'] * 4, tagged + ' data-claims="ex:e lem:f"',
                   earlier_claims=['conj:a', 'ex:b lem:x', 'ex:c prop:y', 'ex:d']),   # fourth of five entries with cases
            record(['research', 'review', 'research', 'research', 'research'], tagged + ' data-claims="ex:e"', status='Proof sketch.',
                   earlier_claims=['ex:a', 'ex:r', 'ex:b', 'conj:c', 'ex:d lem:z']),  # reviews neither count nor reset
        ]
        # One rejection through the real command shows that a refused entry leaves the session running; the
        # other cases exercise validate_marker only and run in process.
        notebook.write_text(rejected[0])
        result = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))
        ft = self.fixture_finisher()
        for number, content in enumerate(rejected[1:], 1):
            with self.subTest(case=number):
                with self.assertRaises(ValueError):
                    ft.validate_marker(content, marker)
        accepted = [
            record(['research'] * 6, reviewed, general=general + leads),
            record(['research'] * 6, reviewed, general=general + leads.replace(
                'Not run: needs a kernel.', 'Not run: recalled, not read. <strong>Retrieval.</strong> '
                'tools/held_sources.py found no copy; the publisher copy is restricted.')),  # retrieval named
            record(['research'] * 6, reviewed, general=general + leads.replace(
                f'<li data-pick>a{ok}</li>',
                f'<li data-pick>a{ok.replace("None found.", "The transfer to the continuous class was not checked.")}</li>')),  # a limit, not another object
            record(['research'] * 6, reviewed, general=general + leads.replace(
                f'<li data-pick>a{ok}</li>',
                f'<li data-pick>a{ok.replace("Passed.", "Passed on all three instances; the bound does not transfer beyond p = 2.")}</li>')),  # ordinary qualifiers
            record(['research'] * 6, reviewed, general=general + leads.replace(
                f'<li data-pick>a{ok}</li>',
                f'<li data-pick>a (it may return in another form){ok}</li>')),  # the words before the test
            record(['review:4'] + ['research'] * 10, reviewed, general=general + leads),  # count dropped
            record(['review:3'] + ['research'] * 9, reviewed, general=general + leads),   # span not reached
            record(['review'] + ['research'] * 10, reviewed, general=general + leads),    # no earlier count
            record(['review:3'] + ['research'] * 10, goal_review, general=general + leads + across),
            record(['research'] * 6 + ['review'] + ['research'] * 5, tagged),
            record(['research'] * 9, 'data-kind="formalization"'),
            record(['research'] * 3, 'data-kind="research" data-route="side-preprint"'),
            record(['research'], tagged + ' data-claims="ex:b"', status='Finite check.'),
            record(['research', 'review'], tagged + ' data-claims="ex:b"', status='Finite check.',
                   earlier_status='Finite check.'),                   # a review resets the streak
            record(['research'], tagged + ' data-claims="none"', status='Literature step.',
                   earlier_status='Literature step.'),
            record(['research'] * 4, tagged + ' data-claims="ex:e lem:f"',
                   earlier_claims=['ex:a', 'conj:b', 'ex:c', 'lem:d']),   # three of five entries with cases
            record(['research', 'research', 'research'], tagged + ' data-claims="thm:e"',
                   earlier_claims=['ex:a', 'ex:b lem:x', 'ex:c prop:y']),  # a general entry is always allowed
        ]
        for content in accepted:
            with self.subTest(content=content[:160]):
                ft.validate_marker(content, marker)
        # an entry edited after it was appended is held to the rule on unverified suggestions here
        plan = ("<p><strong>Follow-up.</strong> Continuing: open. Next attempt, the reviewer's candidate, "
                'unverified: an extension by products.</p>')
        with self.assertRaisesRegex(ValueError, 'follow-up calls what it names unverified'):
            ft.validate_marker(record(['research'], tagged, general=general + plan), marker)
        # a follow-up that closes its item plans nothing, whatever it reports of a past attempt
        past = ("<p><strong>Follow-up.</strong> Closed: restatement. <strong>Not examined.</strong> What the item's "
                "last entry named as its next attempt; this is the reviewer's argument.</p>")
        self.assertEqual(ft.unverified_attempts(f'<article>{past}</article>'), [])
        self.assertTrue(ft.unverified_attempts(f'<article>{past.replace("Closed: restatement.", "Continuing.")}</article>'))

    def test_scratchpad_cap(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('ft', Path(__file__).resolve().parents[1] / 'finish-turn.py')
        ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)
        home = self.root / 'home'
        pad = home / '.claude/jobs/abcdef12/tmp'
        pad.mkdir(parents=True)
        (pad / 'big.json').write_bytes(b'x' * 3000)
        env = {'CLAUDE_CODE_SESSION_ID': 'abcdef12-3456'}
        self.assertEqual(ft.scratchpad(env, home), pad)
        with self.assertRaises(ValueError) as caught:
            ft.check_scratch(env, home, cap=2000)
        self.assertIn('big.json', str(caught.exception))
        ft.check_scratch(env, home, cap=5000)
        ft.check_scratch({}, home, cap=1)   # no session id: nothing to check
        self.assertTrue((pad / 'big.json').exists())   # never deletes

    def test_codex_scratch_cap_in_real_finisher(self):
        import codex_state
        ft = self.fixture_finisher()
        pad = codex_state.scratch_directory(self.root, 'fixture-thread', create=True)
        (pad/'large.txt').write_bytes(b'x' * 3000)
        env = {'CODEX_THREAD_ID': 'fixture-thread'}
        with self.assertRaisesRegex(ValueError, 'Codex scratch'):
            ft.check_scratch(env, cap=2000)
        ft.check_scratch(env, cap=3000)
        ft.check_scratch({'CODEX_THREAD_ID': 'other'}, cap=1)
        self.assertEqual((pad/'large.txt').stat().st_size, 3000)

    def test_review_cadence_and_goal_level_scope(self):
        # In process: one route review in seven entries, and goal-level reviews only when the line stalled.
        import importlib.util
        spec = importlib.util.spec_from_file_location('ft', Path(__file__).resolve().parents[1] / 'finish-turn.py')
        ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)
        marker = '<!-- TIMING test_turn -->'
        ok = ' <strong>Answers.</strong> It would resolve it. <strong>Break point.</strong> None found. <strong>Test.</strong> Passed.'
        body = ('<p><strong>General statement.</strong> For every level the kernel is spanned by short elements '
                '(conj:fixture-general).</p>' + OBSTACLE
                + f'<h4>Outside leads</h4><ul><li data-pick>a{ok}</li><li data-pick>b{ok}</li><li data-pick>c{ok}</li></ul>'
                f'<h4>Absurd bridges</h4><ul><li data-pick>d{ok}</li><li data-pick>e{ok}</li></ul>')
        across = ('<h4>Across the goal</h4><ul><li>Statement 1: unchanged.</li><li>Statement 2: unchanged.</li>'
                  '</ul><p><strong>Decision.</strong> Core: the window.</p>')
        def record(earlier, scope='', extra=''):
            entries = ''.join(f'<article data-kind="{k.split(":")[0]}" data-route="general-step"'
                              + (f' data-open-items="{k.split(":")[1]}"' if ':' in k else '')
                              + '><p class="entry-meta">S.</p></article>' for k in earlier)
            return ('<section id="remaining-route"><li data-route-item="general-step">x</li></section>'
                    '<section id="research-record">' + entries + '<article data-kind="review" data-route='
                    f'"general-step" data-open-items="3"{scope}{PROGRESS_ATTRS} id="current">'
                    '<p class="entry-meta">Review.</p>' + body + extra + PROGRESS_REPORT + ARCHITECTURE
                    + marker + '</article></section>')
        goal = ' data-scope="goal"'
        for earlier, scope, extra in [(['review'] + ['research'] * 5, '', ''),            # too soon
                                      (['review:4'] + ['research'] * 10, goal, across),   # not stalled
                                      (['research'] * 6, goal, across)]:                  # nothing to compare
            with self.subTest(earlier=earlier, scope=scope):
                with self.assertRaises(ValueError):
                    ft.validate_marker(record(earlier, scope, extra), marker)
        for earlier, scope, extra in [(['research'] * 3, '', ''),                         # first review
                                      (['review'] + ['research'] * 6, '', ''),
                                      (['review:3'] + ['research'] * 10, goal, across)]:  # stalled
            with self.subTest(earlier=earlier, scope=scope):
                ft.validate_marker(record(earlier, scope, extra), marker)

    def test_refutation_checks_do_not_count_as_cases(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('ft', Path(__file__).resolve().parents[1] / 'finish-turn.py')
        ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)
        body = '<article data-kind="research" data-claims="ex:r"><p class="entry-meta">x</p></article>'
        self.assertFalse(ft.registers_cases(body, 0, {'ex:r': 'refutation'}))
        self.assertTrue(ft.registers_cases(body, 0, {'ex:r': 'finite_check'}))
        self.assertFalse(ft.cases_only(body, 0, {'ex:r': 'refutation'}))

    def test_append_only_check_flags_edits_but_not_link_repairs(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('cao', ROOT / 'tools/check-append-only.py')
        cao = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cao)
        base = ('<section id="research-record"><article id="a"><p>Claim one.</p></article>'
                '<article id="b"><p>See the lemma.</p></article></section>')
        appended = base.replace('</section>', '<article id="c"><p>New.</p></article></section>')
        linked = base.replace('the lemma', '<a href="#x">the lemma</a>')
        self.assertEqual(cao.violations(base, appended), ([], []))
        self.assertEqual(cao.violations(base, linked), ([], []))
        self.assertEqual(cao.violations(base, base.replace('Claim one.', 'Claim 1.')), ([], ['a']))
        self.assertEqual(cao.violations(base, base.replace('<article id="b"><p>See the lemma.</p></article>', '')),
                         (['b'], []))

    def test_duplicate_marker_does_not_stop_session(self):
        notebook = self.root / 'notebook.html'
        content = '<!-- TIMING test_turn -->\n' * 2
        notebook.write_text(content)
        result = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(notebook.read_text(), content)
        self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))

    def test_stale_claim_view_does_not_stop_session(self):
        data = {'schema_version': 1, 'preamble': '# Index\n\n', 'claims': [], 'relationships': []}
        (self.root / 'research/claims/index.json').write_text(json.dumps(data))
        (self.root / 'research/CLAIM_INDEX.md').write_text('stale view\n')
        (self.root / 'notebook.html').write_text(
            '<section id="research-record"><article><p class="entry-meta">Status.</p>'
            '<!-- TIMING test_turn --></article></section>')
        result = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('claim index is stale', result.stderr)
        self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))

    def test_context_overflow_leaves_clock_and_evidence_untouched(self):
        notebook = self.root / 'notebook.html'
        content = ('<p>' + 'word ' * 151 + '</p><section id="research-record">'
                   '<article><p class="entry-meta">Status.</p><!-- TIMING test_turn -->'
                   '</article></section>')
        notebook.write_text(content)
        before = (self.root / 'research/logs/test_turn.jsonl').read_bytes()
        result = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Notebook context hard limit exceeded', result.stderr)
        self.assertEqual(notebook.read_text(), content)
        self.assertEqual((self.root / 'research/logs/test_turn.jsonl').read_bytes(), before)
        self.assertFalse((self.root / 'research/results').exists())
        self.assertFalse((self.root / 'research/provenance').exists())


if __name__ == '__main__':
    unittest.main()
