"""Shared queue routing, lossless migration, failure recovery and bounded restoration."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_lead_queue import lq, notebook, subideas
import framework_queue as fq
import resume
import notebook_context


class FrameworkQueue(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.main = self.root / 'notebook.html'
        self.side = self.root / 'research/branches/side/notebook.html'
        self.side.parent.mkdir(parents=True)
        (self.side.parent / 'notebook.json').write_text(json.dumps(dict(
            version=1, name='side', title='Side', status='active', parent='main', origin=None)))
        (self.side.parent / 'context-budgets.json').write_text('{}')
        self.main.write_text(notebook([], []))
        self.side.write_text(notebook([], []))
        lq.configure('')

    def cli(self, *args):
        with patch.object(lq, 'ROOT', self.root), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            return lq.main(['lead_queue.py', *map(str, args)])

    def test_direct_classification_routes_and_does_not_infer_from_kind(self):
        old_side = self.side.read_text()
        self.assertEqual(self.cli('add', self.side, '--idea', 'tool', 'user', 'Full framework question',
                                  '--summary', 'Framework idea', '--scope', 'framework'), 0)
        self.assertEqual(self.side.read_text(), old_side)
        shared = fq.parse(self.main.read_text())
        self.assertEqual(fq.key(shared[0]), 'side::idea:tool')
        self.assertEqual(self.cli('add', self.side, '--build', 'proof', 'user', 'Construct the mathematical proof',
                                  '--summary', 'Mathematical construction', '--scope', 'math'), 0)
        self.assertEqual(lq.parse(self.side.read_text())[1], [('build', 'proof')])
        before = self.main.read_text(), self.side.read_text()
        self.assertEqual(self.cli('add', self.side, '--check', 'unspecified', 'user', 'Question', '--summary', 'Short'), 2)
        self.assertEqual((self.main.read_text(), self.side.read_text()), before)
        self.assertEqual(self.cli('add', self.side, '--idea', 'tool', 'user', 'Duplicate',
                                  '--summary', 'Duplicate', '--scope', 'framework'), 1)
        for ident, source, text in [('Bad ID', 'user', 'Question'), ('empty-source', '', 'Question'),
                                     ('empty-text', 'user', ' '), ('bad"id', 'user', 'Question')]:
            with self.assertRaises(ValueError):
                fq.add(self.root, self.side, 'check', ident, source, text, 'Summary')

    def close(self, ident):
        (self.root / 'review.txt').write_text('Reviewed the work and checked its actual outcomes.')
        self.assertEqual(self.cli('framework-close', ident, '--record', 'review.txt', '--path', 'notebook.html',
                                  '--note', 'Completed and reviewed the task with its required checks.'), 0)

    def test_closed_source_is_not_requeued_and_closed_identity_is_not_reused(self):
        entry = subideas('source', [('check', 'Audit the tool')], kind='research').replace(
            'data-queue="math"', 'data-queue="framework"')
        self.side.write_text(notebook([entry], []))
        self.assertEqual(self.cli('append', self.side), 0)
        self.close('side::check:source:s1')
        self.assertEqual(self.cli('append', self.side), 0)
        self.assertEqual(fq.parse(self.main.read_text()), [])
        fq.check_routed(notebook([], []), self.side.read_text(), self.side, self.root, self.main.read_text())
        fq.add(self.root, self.side, 'idea', 'reuse', 'user', 'First question', 'First')
        saved = self.main.read_text()
        self.close('side::idea:reuse')
        with self.assertRaisesRegex(ValueError, 'closed'):
            fq.add(self.root, self.side, 'idea', 'reuse', 'user', 'Different task', 'Second')
        with self.assertRaisesRegex(ValueError, 'cannot be reused'):
            fq.validate(saved, self.main, self.root)

    def test_resolved_source_does_not_enter_framework_queue(self):
        entry = subideas('source', [('check', 'Audit the tool')], kind='research').replace(
            'data-queue="math"', 'data-queue="framework"')
        entry = entry.replace('</article>', '<ul><li data-check="source:s1"><strong>Follow-up.</strong> '
                              'Closed: answered in this entry.</li></ul></article>')
        self.side.write_text(notebook([entry], []))
        self.assertEqual(self.cli('append', self.side), 0)
        self.assertEqual(fq.parse(self.main.read_text()), [])
        fq.check_routed(notebook([], []), self.side.read_text(), self.side, self.root, self.main.read_text())

    def test_legacy_framework_ownership_survives_closure(self):
        original = lq.add(self.side.read_text(), 'build', 'legacy-tool', 'user', 'Build tooling', summary='Tool')
        self.side.write_text(original)
        fq.migrate(self.root, {'items': [{'notebook': 'side', 'qualified_id': 'build:legacy-tool'}]})
        self.close('side::build:legacy-tool')
        with self.assertRaisesRegex(ValueError, 'already owned'):
            fq.check_math_ownership(original, self.side, self.root)
        self.assertEqual(self.cli('add', self.side, '--build', 'legacy-tool', 'user', 'New math guise',
                                  '--summary', 'New', '--scope', 'math'), 1)

    def test_staged_closure_is_independent_of_the_working_ledger(self):
        def git(*args):
            return subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                                   *args], cwd=self.root, capture_output=True, text=True, check=True)
        git('init', '-q')
        fq.add(self.root, self.side, 'check', 'audit', 'user', 'Audit tooling', 'Audit')
        git('add', '.')
        git('commit', '-qm', 'Initial framework item')
        self.close('side::check:audit')
        git('add', 'notebook.html')
        status, message = lq.staged_check(self.main)
        self.assertEqual(status, 1)
        self.assertIn('reviewed framework-close', message)
        git('add', lq.CLOSURES, 'review.txt')
        (self.root / lq.CLOSURES).write_text('')
        self.assertEqual(lq.staged_check(self.main), (0, None))

    def test_listed_framework_item_routes_immediately_while_math_waits(self):
        entry = subideas('new', [('build', 'Improve the queue'), ('check', 'Prove the lemma')], kind='research')
        entry = entry.replace('data-queue="math"', 'data-queue="framework"', 1)
        self.side.write_text(notebook([entry], []))
        original = self.side.read_text()
        self.assertEqual(self.cli('append', self.side), 0)
        self.assertEqual(lq.parse(self.side.read_text())[1], [])
        self.assertEqual(lq.pending_subideas(self.side.read_text()), [('check', 'new:s2')])
        shared = fq.parse(self.main.read_text())
        self.assertEqual([fq.key(n) for n in shared], ['side::build:new:s1'])
        self.assertIn('https://kbr.is-a.dev/math-research/branches/side/#new', shared[0].text)
        self.assertEqual(self.cli('append', self.side), 0)
        self.assertEqual(len(fq.parse(self.main.read_text())), 1)
        with self.assertRaisesRegex(ValueError, 'staged main'):
            fq.check_routed(notebook([], []), original, self.side, self.root, notebook([], []))
        fq.check_routed(notebook([], []), self.side.read_text(), self.side, self.root, self.main.read_text())
        with self.assertRaisesRegex(ValueError, 'differs from its new source'):
            fq.check_routed(notebook([], []), self.side.read_text(), self.side, self.root,
                            self.main.read_text().replace('Improve the queue', 'Different question'))
        missing = entry.replace(' data-queue="framework"', '')
        with self.assertRaisesRegex(ValueError, 'classify'):
            lq.check_source_summaries(*lq.record_articles('<section id="research-record">'+missing+'</section>')[0])

    def test_migration_preserves_children_payload_and_requires_destination(self):
        source = notebook([], [])
        source = lq.add(source, 'check', 'math', 'user', 'Mathematics', summary='Math')
        nodes = lq.parse_tree(source)[1]
        child = lq.Node('build', 'tool', ' data-build="tool" data-summary="Tool question"',
                        '<a href="#source">Full tool description</a> and later notes.')
        nodes[0].children = [child]
        source = lq.rewrite(source, nodes, False)
        self.side.write_text(source)
        spec = {'items': [{'notebook': 'side', 'qualified_id': 'build:tool'}]}
        self.assertEqual(fq.migrate(self.root, spec), (1, 1))
        updated = self.side.read_text()
        moved = fq.parse(self.main.read_text())[0]
        self.assertEqual(fq.attribute(moved.attrs, 'data-framework-parent'), 'check:math')
        self.assertEqual(moved.text, '<a href="https://kbr.is-a.dev/math-research/branches/side/#source">Full tool description</a> and later notes.')
        from notebook_site import source as public_source
        self.assertIn('href="branches/side/#source"', public_source(self.root, 'main'))
        self.assertEqual(lq.shape(lq.parse_tree(updated)[1]), [(('check', 'math'), [])])
        self.assertEqual(lq.SECTION_RE.sub('', updated), lq.SECTION_RE.sub('', source))
        lq.check(source, updated, self.side, self.root)
        with self.assertRaises(ValueError):
            lq.check(source, updated, self.side, self.root, notebook([], []))
        self.assertEqual(fq.migrate(self.root, spec), (0, 1))
        with self.assertRaisesRegex(ValueError, 'already owned'):
            fq.check_math_ownership(source, self.side, self.root)

    def test_interrupted_transfer_is_retryable_and_origin_disambiguates_ids(self):
        self.side.write_text(lq.add(self.side.read_text(), 'idea', 'same', 'user', 'Side idea', summary='Side'))
        self.main.write_text(lq.add(self.main.read_text(), 'idea', 'same', 'user', 'Main idea', summary='Main'))
        spec = {'items': [{'notebook': n, 'qualified_id': 'idea:same'} for n in ('main', 'side')]}
        real_replace = fq.os.replace
        def fail_side(source, destination):
            if Path(destination) == self.side:
                raise OSError('simulated interrupted source write')
            return real_replace(source, destination)
        with patch.object(fq.os, 'replace', side_effect=fail_side), self.assertRaises(OSError):
            fq.migrate(self.root, spec)
        self.assertEqual(len(fq.parse(self.main.read_text())), 2)
        self.assertEqual(lq.parse(self.side.read_text())[1], [('idea', 'same')])
        self.assertEqual(fq.migrate(self.root, spec), (1, 2))
        self.assertEqual({fq.key(n) for n in fq.parse(self.main.read_text())}, {'main::idea:same', 'side::idea:same'})

    def test_only_main_owns_section_and_close_requires_review_evidence(self):
        fq.add(self.root, self.side, 'check', 'audit', 'user', 'Full audit question', 'Audit tooling')
        body = self.main.read_text()
        with self.assertRaisesRegex(ValueError, 'only in the main'):
            fq.validate(body, self.side, self.root)
        with self.assertRaisesRegex(ValueError, 'reviewed'):
            fq.validate(fq.rewrite(body, []), self.main, self.root, body)
        self.assertEqual(self.cli('framework-status', 'side::check:audit'), 0)
        self.assertEqual(self.cli('framework-edit', 'side::check:audit', 'Updated full question', '--summary', 'Updated audit'), 0)
        review = self.root / 'review.txt'
        review.write_text('Reviewed tool and meaningful regression cases.')
        self.assertEqual(self.cli('framework-close', 'side::check:audit', '--record', 'review.txt',
                                  '--path', 'notebook.html', '--note', 'Completed the audit and verified its reported outcomes.'), 0)
        fq.validate(self.main.read_text(), self.main, self.root, body)
        with self.assertRaisesRegex(ValueError, 'reviewed'):
            fq.validate(self.main.read_text(), self.main, self.root, body, ledger={})
        self.assertEqual(fq.parse(self.main.read_text()), [])

    def test_resume_includes_only_count_for_main_and_side_and_budgets_skip_section(self):
        fq.add(self.root, self.side, 'idea', 'private-description', 'user', 'NEVER_IN_RESUME', 'NEITHER_THIS_SUMMARY')
        for relative in resume.FILES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Resume fixture')
        with patch.object(resume, 'run_state', return_value='No grants'):
            for name in ('main', 'side'):
                parts = resume.bundle(self.root, notebook=name)
                text = '\n'.join(part[1] for part in parts)
                self.assertIn('1 framework items', text)
                self.assertNotIn('NEVER_IN_RESUME', text)
                self.assertNotIn('NEITHER_THIS_SUMMARY', text)
        living, _ = notebook_context.living_sections(self.main.read_text())
        self.assertNotIn('framework-queue', living)
