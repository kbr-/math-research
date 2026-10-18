"""Full canonical queue text and bounded, agent-authored metadata are separate contracts."""
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from test_lead_queue import lq, notebook, subideas, review


class QueueText(unittest.TestCase):
    def test_waiting_sources_require_summaries_before_later_promotion(self):
        base = notebook([], [])
        entry = subideas('waiting', [('check', 'Investigate the full question.')], kind='research')
        missing = entry.replace(' data-summary="Listed fixture item"', '')
        for operation in (lambda: lq.append_new(notebook([missing], [])),
                          lambda: lq.check(base, notebook([missing], []))):
            with self.assertRaisesRegex(ValueError, 'agent-written summary'):
                operation()
        waiting, added = lq.append_new(notebook([entry], []))
        self.assertEqual(added, 0)
        lq.check(base, waiting)
        promotion = ('<article id="promote" data-kind="review"><ul><li data-check="waiting:s1">'
                     '<strong>Follow-up.</strong> Promoted: bears on the goal.</li></ul></article>')
        at = waiting.rfind('</section>')
        promoted, added = lq.append_new(waiting[:at] + promotion + waiting[at:])
        self.assertEqual(added, 1)
        self.assertEqual(lq.item_preview(lq.parse_tree(promoted)[1][0]), 'Listed fixture item')

    def test_first_queue_validates_direct_items_but_seeds_historical_text(self):
        base = notebook([], None)
        current = lq.add(notebook([], []), 'check', 'direct', 'user', 'Full question', summary='Short question')
        lq.check(base, current)
        missing = current.replace(' data-summary="Short question"', '')
        with self.assertRaisesRegex(ValueError, 'agent-written summary'):
            lq.check(base, missing)
        historical = subideas('old', [('check', 'Historical question')]).replace(' data-summary="Listed fixture item"', '')
        source = notebook([historical], None)
        seeded = lq.rewrite(notebook([historical], []), lq.open_tree(source), False)
        lq.check(source, seeded)
        self.assertIsNone(lq.item_summary(lq.parse_tree(seeded)[1][0].attrs))

    def test_merges_preserve_full_directly_added_text_and_later_notes(self):
        full = 'A directly queued question with its full scope. ' * 8 + 'Final restriction.'
        body = lq.add(notebook([], []), 'check', 'source', 'user', full, summary='Source question')
        body = lq.add(body, 'check', 'target', 'user', 'Target question.', summary='Target question')
        nodes = lq.parse_tree(body)[1]
        nodes[0].text += ' Later note retained.'
        follow = '<li data-check="source"><strong>Follow-up.</strong> Closed: merged into target.</li>'
        lq.apply_merges(body, nodes, follow)
        self.assertIn(full + ' Later note retained.', nodes[1].text)
        saved = nodes[1].text
        lq.apply_merges(body, nodes, follow)
        self.assertEqual(nodes[1].text, saved)
        at = body.rfind('</section>')
        entry = ('<article id="merge" data-kind="research" data-route="step" data-check="source">'
                 '<p><strong>Follow-up.</strong> Closed: merged into target.</p></article>')
        current = body[:at] + entry + body[at:]
        merged, _ = lq.append_new(lq.done(current, 'Closed'))
        self.assertEqual(lq.parse(merged)[1], [('check', 'target')])
        self.assertIn(full, lq.parse_tree(merged)[1][0].text)

    def test_bulk_summaries_change_only_metadata_and_refuse_unknown_or_duplicate_items(self):
        body = notebook([subideas('old', [('check', 'Keep the full question.')])], [('check', 'old:s1')])
        rows = [{'item': 'check:old:s1', 'summary': 'Test the original question.'}]
        updated = lq.apply_summaries(body, rows)
        old_node, new_node = lq.parse_tree(body)[1][0], lq.parse_tree(updated)[1][0]
        self.assertEqual(old_node.text, new_node.text)
        self.assertEqual(lq.item_preview(new_node), rows[0]['summary'])
        self.assertEqual(lq.apply_summaries(updated, rows), updated)
        for invalid in (rows * 2, [{'item': 'check:missing', 'summary': 'Missing item'}],
                        [{'item': 'check:old:s1', 'summary': 'x' * 161}]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                lq.apply_summaries(body, invalid)
        with tempfile.TemporaryDirectory() as directory:
            path, spec = Path(directory) / 'notebook.html', Path(directory) / 'summaries.json'
            path.write_text(body)
            spec.write_text(json.dumps(rows))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lq.main(['lead_queue.py', 'summarize', str(path), str(spec)]), 0)
            self.assertEqual(path.read_text(), updated)
            spec.write_text(json.dumps(rows * 2))
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(lq.main(['lead_queue.py', 'summarize', str(path), str(spec)]), 1)
            self.assertEqual(path.read_text(), updated)

    def test_restoration_handles_renamed_sources_cross_kind_merges_and_literal_ellipsis(self):
        question = 'Question with all hypotheses. ' * 15 + 'Final clause.'
        body = notebook([subideas('renamed', [('check', question)]),
                         review('mix', ['Lead ' + question], bridges=['Bridge ' + question])], [])
        node = lq.Node('check', 'old:s1', ' data-check="old:s1"',
                       '<a href="#renamed">old:s1</a> (check): ' + lq.legacy_item_text(question))
        for kind in ('lead', 'bridge'):
            node.text += ' Merged from mix:1: ' + lq.legacy_item_text(lq.item_text(body, kind, 'mix:1'))
        before = lq.rewrite(body, [node], False)
        after, changed = lq.restore_text(before)
        self.assertEqual(changed, ['check:old:s1'])
        for kind in ('lead', 'bridge'):
            self.assertIn('Merged from mix:1: ' + lq.item_text(body, kind, 'mix:1'), after)
        self.assertIn('(check): ' + question, after)
        self.assertEqual(lq.restore_text(after), (after, []))
        # A literal ellipsis at the old cutoff is not a truncation on a second pass.
        full = 'x' * 220 + '… followed by the rest.'
        source = notebook([subideas('literal', [('check', full)])], [])
        complete = lq.rewrite(source, [lq.new_node(source, ('check', 'literal:s1'))], False)
        self.assertEqual(lq.restore_text(complete), (complete, []))
        mismatched = before.replace('(check): Question', '(check): Changed question')
        restored, _ = lq.restore_text(mismatched)
        self.assertIn('(check): Changed question', restored)

    def test_add_requires_summary_and_previews_never_replace_full_status(self):
        body = notebook([], [])
        full = 'Read the complete construction. ' * 20 + 'The final obligation is still here.'
        summary = 'Compare "A & B" and test the missing implication.'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'notebook.html'
            path.write_text(body)
            argv = ['lead_queue.py', 'add', str(path), '--check', 'compare', 'user', full, '--scope', 'math']
            missing = io.StringIO()
            with contextlib.redirect_stderr(missing):
                self.assertEqual(lq.main(argv), 2)
            self.assertIn('--summary', missing.getvalue())
            self.assertEqual(path.read_text(), body)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lq.main([*argv, '--summary', summary]), 0)
            updated = path.read_text()
            node = lq.parse_tree(updated)[1][0]
            self.assertEqual(lq.item_summary(node.attrs), summary)
            self.assertEqual(lq.item_preview(node), summary)
            self.assertTrue(lq.listing(updated)[0].endswith('\t' + summary))
            self.assertIn(summary, '\n'.join(lq.head_lines(updated)))
            self.assertNotIn('final obligation', '\n'.join(lq.head_lines(updated)))
            self.assertIn(full, lq.item_status(updated, 'compare')[1])
            output = io.StringIO()
            with patch.object(lq, 'registered', return_value=([], [])), contextlib.redirect_stdout(output):
                self.assertEqual(lq.main(['lead_queue.py', 'history', str(path), 'compare', '--status']), 0)
            self.assertIn(full, output.getvalue())
            legacy = updated.replace(lq.summary_attribute(summary), '')
            for preview in (lambda: lq.item_preview(lq.parse_tree(legacy)[1][0]),
                            lambda: lq.head_lines(legacy), lambda: lq.listing(legacy)):
                with self.assertRaisesRegex(ValueError, 'missing agent-written summary'):
                    preview()
            self.assertIn(full, lq.item_status(legacy, 'compare')[1])
            for bad in ('', ' ', 'x' * 161):
                with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'agent-written summary'):
                    lq.add(body, 'check', 'bad', 'user', full, summary=bad)
            self.assertIn('x' * 160, lq.add(body, 'check', 'limit', 'user', full, summary='x' * 160))

    def test_new_sources_require_metadata_and_legacy_storage_needs_preview_repair(self):
        full = 'Preserve the entire source question with its hypotheses. ' * 8
        entry = subideas('new', [('check', full)])
        base = notebook([], [])
        missing = entry.replace(' data-summary="Listed fixture item"', '')
        with self.assertRaisesRegex(ValueError, 'agent-written summary'):
            lq.append_new(notebook([missing], []))
        updated, count = lq.append_new(notebook([entry], []))
        self.assertEqual(count, 1)
        lq.check(base, updated)
        self.assertIn(full.strip(), lq.item_status(updated, 'new:s1')[1])
        self.assertEqual(lq.item_preview(lq.parse_tree(updated)[1][0]), 'Listed fixture item')
        # A hand-written queue line cannot bypass the admission requirement.
        bad = updated.replace(' data-summary="Listed fixture item"', '', 1)
        with self.assertRaisesRegex(ValueError, 'agent-written summary'):
            lq.check(base, bad)
        old = notebook([missing], [('check', 'new:s1')]).replace(' data-summary="new:s1"', '')
        lq.check(old, old)
        with self.assertRaisesRegex(ValueError, 'missing agent-written summary'):
            lq.item_preview(lq.parse_tree(old)[1][0])

    def test_restore_recovers_complete_text_without_losing_notes_children_or_order(self):
        text = 'A &amp; B with \\(x&lt;y\\). ' + 'Long question ' * 30 + 'complete final clause.'
        entries = [subideas('old', [('check', text), ('check', 'Child ' + text)])]
        body = notebook(entries, [])
        parent = lq.new_node(body, ('check', 'old:s1'))
        child = lq.new_node(body, ('check', 'old:s2'))
        for node in (parent, child):
            node.attrs = re.sub(r' data-summary="[^"]*"', '', node.attrs)
            full = lq.item_text(body, node.kind, node.ident)
            node.text = node.text.replace(full, lq.legacy_item_text(full))
        parent.text += ' Extra plan retained. Merged from old:s2: ' + lq.legacy_item_text(lq.item_text(body, 'check', 'old:s2'))
        parent.children = [child]
        old = lq.rewrite(body, [parent], False)
        restored, changed = lq.restore_text(old)
        self.assertEqual(changed, ['check:old:s1', 'check:old:s2'])
        actual = lq.parse_tree(restored)[1]
        self.assertEqual(lq.shape(actual), lq.shape([parent]))
        self.assertIn('complete final clause.', actual[0].text)
        self.assertIn('Extra plan retained.', actual[0].text)
        self.assertIn('Merged from old:s2: ' + lq.item_text(body, 'check', 'old:s2'), actual[0].text)
        self.assertIn('complete final clause.', actual[0].children[0].text)
        self.assertIsNone(lq.item_summary(actual[0].attrs))
        self.assertEqual(lq.SECTION_RE.sub('', old), lq.SECTION_RE.sub('', restored))
        self.assertEqual(lq.restore_text(restored), (restored, []))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'notebook.html'
            path.write_text(old)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(lq.main(['lead_queue.py', 'restore-text', str(path)]), 0)
            self.assertEqual(json.loads(output.getvalue())['count'], 2)
            self.assertEqual(path.read_text(), restored)
