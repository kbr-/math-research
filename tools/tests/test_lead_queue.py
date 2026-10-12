import io
import contextlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('lead_queue', ROOT / 'tools/lead_queue.py')
lq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lq)

ROUTE = '<section id="remaining-route"><li data-route-item="step">x</li></section>'
PASS = ' <strong>Answers.</strong> y. <strong>Test.</strong> Passed.'
FAIL = ' <strong>Answers.</strong> y. <strong>Test.</strong> Falsified: no.'


def review(ident, leads, bridges=(FAIL, FAIL)):
    return (f'<article id="{ident}" data-kind="review" data-route="step"><h4>Outside leads</h4><ul>'
            + ''.join(f'<li>L{n}{t}</li>' for n, t in enumerate(leads)) + '</ul><h4>Absurd bridges</h4><ul>'
            + ''.join(f'<li>B{n}{t}</li>' for n, t in enumerate(bridges)) + '</ul></article>')


def research(develops=None, outcome=None):
    tag = f' data-{develops[0]}="{develops[1]}"' if develops else ''
    body = f'<p><strong>Follow-up.</strong> {outcome}: x.</p>' if outcome else ''
    return f'<article data-kind="research" data-route="step"{tag}>{body}</article>'


def subideas(ident, items, kind='task', extra=''):
    """An entry listing sub-ideas: items are (sub kind, text)."""
    return (f'<article id="{ident}" data-kind="{kind}"{extra}>{"" if extra else "<p>work</p>"}<h4>Sub-ideas</h4><ul>'
            + ''.join(f'<li data-sub="{k}">{x}</li>' for k, x in items) + '</ul></article>')


def developing(item, outcome, body=''):
    return (f'<article id="d" data-kind="research" data-route="step" data-{item[0]}="{item[1]}">{body}'
            f'<p><strong>Follow-up.</strong> {outcome}: x.</p></article>')


def line(entry):
    """A queue line: (kind, id), or ((kind, id), [children]) for a parent with sub-ideas."""
    if isinstance(entry[1], list):
        (k, i), children = entry
        return f'<li data-{k}="{i}">{i}<ul>' + ''.join(f'<li data-{ck}="{ci}">{ci}</li>' for ck, ci in children) + '</ul></li>'
    return f'<li data-{entry[0]}="{entry[1]}">{entry[1]}</li>'


def notebook(articles, queue=None, draining=False, attrs='', route=True):
    section = ''
    if queue is not None:
        flag = attrs + (' data-draining="true"' if draining else '')
        section = f'<section id="lead-queue"{flag}><ol>' + ''.join(line(e) for e in queue) + '</ol></section>'
    return (ROUTE if route else '') + section + '<section id="research-record">' + ''.join(articles) + '</section>'


class LeadQueueTest(unittest.TestCase):
    def setUp(self):
        lq.configure('')            # a notebook's section settings stay in force until the next is parsed
        self.rev = review('r1', [PASS, PASS, FAIL])     # two passed leads: r1:1, r1:2
        self.q = [('lead', 'r1:1'), ('lead', 'r1:2')]

    def test_reviews_generate_nothing_while_draining(self):
        big = review('many', [PASS] * lq.CAP)
        queue = [('lead', f'many:{i}') for i in range(1, lq.CAP + 1)]
        head = notebook([big], queue, draining=True)
        plain = '<article id="drain" data-kind="review" data-route="step"><p>Assess existing work.</p></article>'
        lq.check(head, notebook([big, plain], queue, draining=True))
        lq.check(head, head)  # Do not apply the new rule retroactively to historical reviews.
        for heading in ('Outside leads', 'Absurd bridges'):
            extra = plain.replace('</article>', f'<h4>{heading}</h4><ul></ul></article>')
            with self.subTest(heading=heading), self.assertRaisesRegex(ValueError, 'queue is draining'):
                lq.check(head, notebook([big, extra], queue, draining=True))
        # Crossing the floor inside the review does not allow that same review to add leads.
        queue = queue[:lq.FLOOR + 1]
        head = notebook([big], queue, draining=True)
        closes = plain.replace('</article>', '<ul><li data-lead="many:1"><strong>Follow-up.</strong> '
                               'Closed: falsified by the recorded test.</li></ul></article>')
        after = notebook([big, closes], queue[1:])
        lq.check(head, after)
        with self.assertRaisesRegex(ValueError, 'queue is draining'):
            lq.check(head, after.replace('</article></section>',
                '<h4>Outside leads</h4><ul></ul></article></section>'))
        # The following review may generate again, and backpressure-off notebooks are exempt.
        new = review('new', [PASS, FAIL, FAIL])
        lq.check(after, notebook([big, closes, new], queue[1:] + [('lead', 'new:1')]))
        attrs = ' data-backpressure="off"'
        lq.check(notebook([big], queue, attrs=attrs),
                 notebook([big, new], queue + [('lead', 'new:1')], attrs=attrs))

    def test_open_items_and_init_order(self):
        self.assertEqual(lq.open_items(notebook([self.rev])), self.q)
        body = notebook([self.rev])
        rendered = lq.render(body, lq.open_tree(body), False)
        self.assertLess(rendered.index('r1:1'), rendered.index('r1:2'))

    def test_missing_section_and_membership(self):
        with self.assertRaises(ValueError):
            lq.check(None, notebook([self.rev]))
        with self.assertRaises(ValueError):
            lq.check(None, notebook([self.rev], self.q[:1]))           # an open item is missing
        lq.check(None, notebook([self.rev], self.q))

    def test_ordered_lists_keep_picks_and_subideas(self):
        entry = review('ordered', [PASS, FAIL, FAIL], [PASS, FAIL])
        entry = entry.replace('<li>L0', '<li data-pick>L0').replace('<li>B0', '<li data-pick>B0')
        entry += subideas('todo', [('check', 'test the mechanism')])
        entry = entry.replace('<ul>', '<ol>').replace('</ul>', '</ol>')
        expected = [('lead', 'ordered:1'), ('bridge', 'ordered:1'), ('check', 'todo:s1')]
        self.assertEqual(lq.open_items(notebook([entry])), expected)
        with self.assertRaises(ValueError):
            lq.check(None, notebook([entry], []))
        lq.check(None, notebook([entry], expected))

    def test_fifo_and_outcomes(self):
        head = notebook([self.rev], self.q)
        with self.assertRaises(ValueError):                             # not the head
            lq.check(head, notebook([self.rev, research(self.q[1], 'Closed')], self.q[:1]))
        with self.assertRaises(ValueError):                             # no outcome stated
            lq.check(head, notebook([self.rev, research(self.q[0])], self.q))
        lq.check(head, notebook([self.rev, research(self.q[0], 'Closed')], self.q[1:]))
        lq.check(head, notebook([self.rev, research(self.q[0], 'Developed')], self.q[1:]))
        lq.check(head, notebook([self.rev, research(self.q[0], 'Continuing')], self.q))   # keeps the head
        with self.assertRaises(ValueError):                             # not yet to the tail
            lq.check(head, notebook([self.rev, research(self.q[0], 'Continuing')], self.q[::-1]))
        with self.assertRaises(ValueError):                             # Closed but still listed
            lq.check(head, notebook([self.rev, research(self.q[0], 'Closed')], self.q))

    def test_continuing_head_keeps_the_head_for_a_spell(self):
        cont = research(self.q[0], 'Continuing')
        review_between = review('r0', [FAIL])
        for n in range(1, lq.SPELL + 1):
            earlier = [cont] * (n - 1)
            if n > 2:
                earlier.insert(1, review_between)                       # reviews neither count nor break it
            before = notebook([self.rev] + earlier, self.q)
            after_entry = [self.rev] + earlier + [cont]
            want = self.q if n < lq.SPELL else self.q[::-1]
            lq.check(before, notebook(after_entry, want))
            appended = notebook(after_entry[:-1] + [cont.replace('</article>', '<!-- TIMING t --></article>')],
                                self.q)
            self.assertEqual(lq.parse(lq.done(appended, 'Continuing'))[1], want)
        broken = notebook([self.rev, cont, research(self.q[1], 'Closed'), cont, cont], self.q)
        self.assertEqual(lq.spell(broken, self.q[0]), 2)                 # another item's entry ends the run

    def extension_entry(self, number, evidence=None, extension=True, item=None):
        item = item or self.q[0]
        cid = evidence or f'thm:e{number}'
        attrs = ' data-spell-extend="2"' if extension else ''
        note = (f'<p class="spell-extension" data-statement="Stable orders">'
                f'<strong>Progress.</strong> {cid} closes a necessary all-degree family. '
                '<strong>Next.</strong> Apply its same marked-source mechanism to the remaining prime.</p>')
        return (f'<article id="e{number}" data-kind="research" data-route="step" '
                f'data-{item[0]}="{item[1]}" data-claims="thm:e{number}"{attrs}>'
                + (note if extension else '') + '<p><strong>Follow-up.</strong> Continuing: next.</p></article>')

    def extension_registry(self, **changes):
        records = {f'thm:e{n}': {'mathematical_status': 'working_proof',
                                'record': f'[proof](https://example.test/#e{n})'} for n in range(1, 11)}
        records.update(changes)
        return patch.object(lq.Where, 'claim_records', return_value=records)

    def test_earned_extensions_renew_and_expire(self):
        entries = [self.rev] + [self.extension_entry(n, extension=False) for n in range(1, 4)]
        with self.extension_registry():
            for number in range(4, 10):
                before = notebook(entries, self.q)
                entries.append(self.extension_entry(number, extension=number in (4, 6, 8)))
                after = notebook(entries, self.q)
                lq.check(before, after)
                self.assertEqual(lq.parse(lq.done(after, 'Continuing'))[1], self.q)
                self.assertEqual(lq.spell_limit(after, self.q[0]), 2 * (number // 2) + 2)
            before = notebook(entries, self.q)
            entries.append(self.extension_entry(10, extension=False))
            after = notebook(entries, self.q[::-1])
            lq.check(before, after)
            self.assertEqual(lq.parse(lq.done(notebook(entries, self.q), 'Continuing'))[1], self.q[::-1])

    def test_extension_rejects_stale_finite_or_unproved_progress(self):
        entries = [self.rev] + [self.extension_entry(n, extension=n == 4) for n in range(1, 6)]
        before = notebook(entries, self.q)
        with self.extension_registry():
            with self.assertRaisesRegex(ValueError, 'this extension period'):
                lq.check(before, notebook(entries + [self.extension_entry(6, evidence='thm:e4')], self.q))
        for status in ('finite_check', 'conditional', 'conjecture'):
            with self.subTest(status=status), self.extension_registry(**{
                    'thm:e6': {'mathematical_status': status, 'record': '[proof](https://example.test/#e6)'}}):
                with self.assertRaisesRegex(ValueError, 'registered proof'):
                    lq.check(before, notebook(entries + [self.extension_entry(6)], self.q))
        with self.extension_registry(**{'thm:e6': {'mathematical_status': 'working_proof',
                                                  'record': '[old](https://example.test/#e60)'}}):
            with self.assertRaisesRegex(ValueError, 'registered proof'):
                lq.check(before, notebook(entries + [self.extension_entry(6)], self.q))
        refutation = self.extension_entry(6).replace('thm:e6', 'ex:counterexample')
        with self.extension_registry(**{'ex:counterexample': {'mathematical_status': 'refutation',
                                                              'record': '[proof](https://example.test/#e6)'}}):
            lq.check(before, notebook(entries + [refutation], self.q))

    def test_extension_needs_boundary_statement_and_next_attempt(self):
        entries = [self.rev] + [self.extension_entry(n, extension=False) for n in range(1, 4)]
        before = notebook(entries, self.q)
        valid = self.extension_entry(4)
        invalid = [valid.replace('data-spell-extend="2"', 'data-spell-extend="4"'),
                   valid.replace('data-statement="Stable orders"', ''),
                   valid.replace('<strong>Next.</strong>', 'Later:'),
                   valid.replace('Continuing: next.', 'Closed: finished.')]
        with self.extension_registry():
            for entry in invalid:
                with self.subTest(entry=entry), self.assertRaises(ValueError):
                    lq.check(before, notebook(entries + [entry], self.q))
            with self.assertRaisesRegex(ValueError, 'cycle 4, not cycle 3'):
                lq.check(notebook(entries[:-1], self.q), notebook(entries[:-1] + [self.extension_entry(3)], self.q))

    def test_user_unlimited_spell_is_scoped_and_survives_many_cycles(self):
        listing = subideas('inventory', [('check', 'Complete exception sets')])
        item = ('check', 'inventory:s1')
        queue = [item] + self.q
        override = ('<article id="no-limit" data-kind="audit" data-picked="user" '
                    'data-spell-limit="none" data-spell-item="check:inventory:s1">'
                    '<p><strong>Picked.</strong> "This item has no hard cycle limit."</p></article>')
        entries = [self.rev, listing, override]
        current = notebook(entries, queue)
        lq.check(notebook([self.rev, listing], queue), current)
        for _ in range(10):
            entries.append(research(item, 'Continuing'))
            after = lq.done(notebook(entries, queue), 'Continuing')
            lq.check(current, after)
            self.assertEqual(lq.parse(after)[1], queue)
            current = after
        self.assertEqual(lq.spell_limit(current, item), float('inf'))
        self.assertEqual(lq.spell_limit(current, self.q[0]), lq.SPELL)
        self.assertEqual(lq.spell_limit(notebook([self.rev, listing, override], queue), item, end=-1), lq.SPELL)
        closed = lq.done(notebook(entries + [research(item, 'Closed')], queue), 'Closed')
        lq.check(current, closed)
        self.assertEqual(lq.parse(closed)[1], self.q)

    def test_unlimited_spell_requires_quoted_user_and_queued_parent(self):
        base = notebook([self.rev], self.q)
        valid = ('<article id="u" data-kind="audit" data-picked="user" '
                 'data-spell-limit="none" data-spell-item="lead:r1:1">'
                 '<p><strong>Picked.</strong> "No hard cycle limit."</p></article>')
        for invalid in [valid.replace('data-picked="user"', ''),
                        valid.replace('<strong>Picked.</strong>', 'No quote:'),
                        valid.replace('lead:r1:1', 'lead:missing:1'),
                        valid.replace('data-spell-limit="none"', 'data-spell-limit="100"')]:
            with self.assertRaises(ValueError):
                lq.check(base, notebook([self.rev, invalid], self.q))

    def test_user_restores_rotated_head_with_earned_extension(self):
        entries = [self.rev] + [self.extension_entry(n, extension=False) for n in range(1, 5)]
        before = notebook(entries, self.q[::-1])
        note = self.extension_entry(4).split('<p class="spell-extension"', 1)[1].split('</p>', 1)[0]
        audit = ('<article id="return" data-kind="audit" data-picked="user" '
                 'data-spell-extend="2" data-spell-item="lead:r1:1">'
                 '<p><strong>Picked.</strong> "Bring it back to the head."</p>'
                 '<p class="spell-extension"' + note + '</p><h4>Queue order</h4>'
                 '<ol data-move="head"><li data-lead="r1:1"></li></ol></article>')
        with self.extension_registry():
            after, _ = lq.append_new(notebook(entries + [audit], self.q[::-1]))
            lq.check(before, after)
            self.assertEqual(lq.parse(after)[1], self.q)
            self.assertEqual(lq.spell(after, self.q[0]), 4)
            self.assertEqual(lq.spell_limit(after, self.q[0]), 6)
            self.assertEqual(lq.shape(lq.settle(after, lq.parse_tree(after)[1])), lq.shape(lq.parse_tree(after)[1]))
        unquoted = audit.replace('data-picked="user"', '')
        with self.assertRaises(ValueError):
            lq.append_new(notebook(entries + [unquoted], self.q[::-1]))

    def test_completed_child_can_extend_its_continuing_parent(self):
        listing = subideas('sub', [('check', 'question')]).replace('data-sub="check"',
                   'data-sub="check" data-parent="lead:r1:1"')
        entries = [self.rev, listing] + [self.extension_entry(n, extension=False) for n in range(1, 4)]
        queue = [(self.q[0], [('check', 'sub:s1')]), self.q[1]]
        entry = self.extension_entry(4, item=('check', 'sub:s1')).replace('Continuing: next.', 'Developed: thm:e4.')
        with self.extension_registry():
            before = notebook(entries, queue)
            after = lq.done(notebook(entries + [entry], queue), 'Developed')
            lq.check(before, after)
            self.assertEqual(lq.parse_tree(after)[1][0].item, self.q[0])
            self.assertEqual(lq.parse_tree(after)[1][0].children, [])
            self.assertEqual(lq.spell_limit(after, self.q[0]), 6)

    def test_new_items_go_to_the_end(self):
        head = notebook([self.rev], self.q)
        second = review('r2', [PASS, FAIL, FAIL])
        lq.check(head, notebook([self.rev, second], self.q + [('lead', 'r2:1')]))
        with self.assertRaises(ValueError):
            lq.check(head, notebook([self.rev, second], [('lead', 'r2:1')] + self.q))

    def test_backpressure_from_cap_until_floor(self):
        big = review('r1', [PASS] * lq.CAP)
        queue = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
        with self.assertRaises(ValueError):                             # at the cap the flag is required
            lq.check(None, notebook([big], queue))
        head = notebook([big], queue, draining=True)
        lq.check(None, head)
        with self.assertRaises(ValueError):                             # draining: research must take the head
            lq.check(head, notebook([big, research()], queue, draining=True))
        after = notebook([big, research(queue[0], 'Closed')], queue[1:], draining=True)
        lq.check(head, after)
        with self.assertRaises(ValueError):                             # the flag stays until the floor
            lq.check(head, notebook([big, research(queue[0], 'Closed')], queue[1:]))
        # at the floor plus one, closing the head reaches the floor and removes the flag
        small_head = notebook([big] + [research(q, 'Closed') for q in queue[:lq.CAP - lq.FLOOR - 1]],
                              queue[lq.CAP - lq.FLOOR - 1:], draining=True)
        rest = queue[lq.CAP - lq.FLOOR - 1:]
        done = [research(q, 'Closed') for q in queue[:lq.CAP - lq.FLOOR]]
        lq.check(small_head, notebook([big] + done, rest[1:]))
        with self.assertRaises(ValueError):
            lq.check(small_head, notebook([big] + done, rest[1:], draining=True))

    def test_item_text_escapes_entities_once(self):
        listing = subideas('t1', [('check', 'the hook&#x27;s flags &amp; their &lt;precision&gt;')])
        self.assertEqual(lq.item_text(notebook([listing]), 'check', 't1:s1'),
                         "the hook's flags &amp; their &lt;precision&gt;")

    def test_item_text_never_cuts_inline_math(self):
        long = review('r1', [' The ring \\(F[p_2]\\) ' + 'word ' * 40 + '\\(x+y\\) end.' + PASS])
        text = lq.item_text(notebook([long]), 'lead', 'r1:1')
        self.assertEqual(text.count('\\('), text.count('\\)'))

    def test_done_updates_queue_the_way_check_expects(self):
        head = notebook([self.rev], self.q)
        with self.assertRaises(ValueError):                             # the developing entry is appended first
            lq.done(head, 'Closed')
        entry = lambda outcome: notebook([self.rev, research(self.q[0], outcome)], self.q)
        closed = lq.done(entry('Closed'), 'Closed')
        self.assertEqual(lq.parse(closed)[1], self.q[1:])
        with self.assertRaises(ValueError):                             # twice: the item is gone
            lq.done(closed, 'Closed')
        with self.assertRaises(ValueError):                             # the entry states another outcome
            lq.done(entry('Continuing'), 'Closed')
        kept = lq.done(entry('Continuing'), 'Continuing')               # first of its spell: stays
        self.assertEqual(lq.parse(kept)[1], self.q)
        big = review('r1', [PASS] * (lq.FLOOR + 1))
        queue = [('lead', f'r1:{n}') for n in range(1, lq.FLOOR + 2)]
        draining = notebook([big, research(queue[0], 'Closed')], queue, draining=True)
        self.assertFalse(lq.parse(lq.done(draining, 'Closed'))[0])     # at the floor the flag goes
        with self.assertRaises(ValueError):
            lq.done(head, 'Maybe')

    def test_append_new_items_after_a_review(self):
        head = notebook([self.rev], self.q)
        second = review('r2', [PASS, FAIL, PASS])
        body, count = lq.append_new(notebook([self.rev, second], self.q))
        self.assertEqual(count, 2)
        self.assertEqual(lq.parse(body)[1], self.q + [('lead', 'r2:1'), ('lead', 'r2:3')])
        lq.check(head, body)

    def test_reopened_items_go_to_the_tail(self):
        head = notebook([self.rev, research(self.q[0], 'Developed')], self.q[1:])
        reopen = ('<article data-kind="research" data-route="step" data-lead="r1:2"><ul><li data-lead="r1:1">'
                  'still bears on an open statement. <strong>Follow-up.</strong> Reopened: closed too early.</li>'
                  '</ul><p><strong>Follow-up.</strong> Continuing: next attempt.</p></article>')
        after = notebook([self.rev, research(self.q[0], 'Developed'), reopen], self.q[1:])
        self.assertEqual(lq.developed_by(*lq.record_articles(after)[-1]), (self.q[1], 'Continuing'))
        body, count = lq.append_new(lq.done(after, 'Continuing'))
        self.assertEqual(count, 1)
        self.assertEqual(lq.parse(body)[1], [self.q[1], self.q[0]])
        lq.check(head, body)
        with self.assertRaises(ValueError):                             # the reopened item must be appended
            lq.check(head, lq.done(after, 'Continuing'))
        stray = reopen.replace('r1:1">', 'r9:1">')
        with self.assertRaises(ValueError):                             # only passed review items reopen
            lq.check(head, notebook([self.rev, research(self.q[0], 'Developed'), stray],
                                    [self.q[1], ('lead', 'r9:1')]))

    def test_triage_batches_are_retired(self):
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        head = notebook([rev], q)
        careful = ' '.join(['checked'] * 85)
        batch = ('<article id="t" data-kind="research" data-route="step"><h4>Queue triage</h4><ul>'
                 f'<li data-lead="r1:1">{careful} lem:x-y <strong>Follow-up.</strong> Closed: reason.</li></ul></article>')
        with self.assertRaisesRegex(ValueError, 'retired'):        # user, 9 October 2026: one item per entry
            lq.check(head, notebook([rev, batch], q[1:]))
        lq.check(notebook([rev, batch], q[1:]), notebook([rev, batch], q[1:]))   # an older batch is history
        self.assertEqual(lq.main(['lead_queue.py', 'triage', 'nb.html']), 1)

    def test_research_entries_add_passed_items(self):
        head = notebook([self.rev], self.q)
        entry = ('<article id="w" data-kind="research" data-route="step" data-lead="r1:1"><p><strong>Follow-up.'
                 '</strong> Closed: done.</p><h4>Outside leads</h4><ul><li>New lead' + PASS + '</li></ul></article>')
        body, count = lq.append_new(lq.done(notebook([self.rev, entry], self.q), 'Closed'))
        self.assertEqual(count, 1)
        self.assertEqual(lq.parse(body)[1], [self.q[1], ('lead', 'w:1')])
        lq.check(head, body)

    def test_review_report_defects(self):
        """Regression cases of the fresh-context review of 3 October 2026, one per defect."""
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        head = notebook([rev], q)
        cont = research(q[0], 'Continuing')
        idle = '<article id="i" data-kind="research" data-route="step"><p>other work</p></article>'
        with self.subTest(defect=1):
            # 1: a research entry developing nothing does not restart the spell
            self.assertEqual(lq.spell(notebook([rev, cont, cont, cont, idle, cont], q), q[0]), 4)
        with self.subTest(defect=2):
            # 2: Reopened is not an outcome of the developing entry itself
            with self.assertRaises(ValueError):
                lq.check(head, notebook([rev, research(q[0], 'Reopened')], q[1:]))
        with self.subTest(defect=3):
            # 3: the entry's own (last) Follow-up counts, not a quoted earlier one
            quoting = ('<article data-kind="research" data-route="step" data-lead="r1:1"><p>Earlier: <strong>Follow-up.'
                       '</strong> Closed: old.</p><p><strong>Follow-up.</strong> Continuing: now.</p></article>')
            self.assertEqual(lq.developed_by(*lq.record_articles(notebook([rev, quoting], q))[-1])[1], 'Continuing')
        with self.subTest(defect=4):
            # 4: a review's Closed follow-up removes the item, as init counts it
            rv = ('<article id="rv" data-kind="review" data-route="step"><ul><li data-lead="r1:2">x <strong>Follow-up.'
                  '</strong> Closed: gone.</li></ul></article>')
            with self.assertRaises(ValueError):
                lq.check(head, notebook([rev, rv], q))
            lq.check(head, notebook([rev, rv], [q[0], q[2]]))
            self.assertEqual(lq.open_items(notebook([rev, rv])), [q[0], q[2]])
        with self.subTest(defect=5):
            # 5: closing the head and reopening it in the same entry puts it at the tail
            reo = ('<article data-kind="research" data-route="step" data-lead="r1:1"><ul><li data-lead="r1:1">y <strong>'
                   'Follow-up.</strong> Reopened: back.</li></ul><p><strong>Follow-up.</strong> Closed: done.</p></article>')
            lq.check(head, notebook([rev, reo], q[1:] + q[:1]))
        with self.subTest(defect=6):
            # 6: two developed items in one entry are refused
            two = ('<article data-kind="research" data-route="step" data-lead="r1:1" data-bridge="r1:2"><p><strong>'
                   'Follow-up.</strong> Closed: x.</p></article>')
            with self.assertRaises(ValueError):
                lq.check(head, notebook([rev, two], q[1:]))
        with self.subTest(defect=7):
            # 7: two entries in one commit are refused; before, a first entry developing a non-head item went
            # unchecked behind a valid last entry
            with self.assertRaises(ValueError):
                lq.check(head, notebook([rev, research(q[2], 'Closed'), research(q[0], 'Continuing')], q))
        with self.subTest(defect=8):
            # 8: the commit creating the queue may not develop items
            with self.assertRaises(ValueError):
                lq.check(None, notebook([rev, research(q[1], 'Closed')], q))

    def test_history_closes_only_by_closed_follow_ups(self):
        old = ('<article data-kind="review" data-route="step"><ul><li data-lead="r1:1">x <strong>Follow-up.'
               '</strong> Closed: no.</li><li data-lead="r1:2">x <strong>Follow-up.</strong> Continuing.</li>'
               '</ul></article>')
        self.assertEqual(lq.open_items(notebook([self.rev, old])), self.q[1:])

    def test_audit_items_are_all_queued_at_their_source_place(self):
        later = review('r2', [PASS])
        audit = ('<article id="a" data-kind="audit" data-route="step"><h4>Outside leads</h4><ul>'
                 '<li data-source="r2">untested idea</li><li data-source="r1">older idea</li></ul>'
                 '<h4>Absurd bridges</h4><ul><li data-source="r2">bridge</li></ul><ul><li data-lead="r1:2">x '
                 '<strong>Follow-up.</strong> Reopened: closed by one objection.</li></ul></article>')
        closing = ('<article data-kind="research" data-route="step"><ul><li data-lead="r1:2">x <strong>Follow-up.'
                   '</strong> Closed: early.</li></ul></article>')
        body = notebook([self.rev, later, closing, audit])
        self.assertEqual(lq.open_items(body), [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'a:2'),
                                               ('lead', 'r2:1'), ('lead', 'a:1'), ('bridge', 'a:1')])
        lq.check(None, notebook([self.rev, later, closing, audit], lq.open_items(body)))

    def test_subideas_join_the_tail_from_any_entry(self):
        head = notebook([self.rev], self.q)
        listing = subideas('t1', [('check', 'run it on ARM'), ('build', 'the PDF register')])
        want = self.q + [('check', 't1:s1'), ('build', 't1:s2')]
        body, count = lq.append_new(notebook([self.rev, listing], self.q))
        self.assertEqual((count, lq.parse(body)[1]), (2, want))
        lq.check(head, body)
        with self.assertRaises(ValueError):                             # a listed sub-idea must reach the queue
            lq.check(head, notebook([self.rev, listing], self.q))
        self.assertIn('run it on ARM', lq.item_text(body, 'check', 't1:s1'))

    def test_parentless_subideas_wait_for_a_review_to_promote_them(self):
        head = notebook([self.rev], self.q)
        listing = subideas('t1', [('check', 'run it on ARM'), ('build', 'the PDF register')], kind='research')
        body, count = lq.append_new(notebook([self.rev, listing], self.q))
        self.assertEqual((count, lq.parse(body)[1]), (0, self.q))          # route work has no parent: not queued
        lq.check(head, body)
        self.assertEqual(lq.pending_subideas(body), [('check', 't1:s1'), ('build', 't1:s2')])
        promoting = ('<article id="r2" data-kind="review"><ul><li data-check="t1:s1">Worth doing. '
                     '<strong>Follow-up.</strong> Promoted: it bears on the goal.</li></ul></article>')
        body2, count2 = lq.append_new(notebook([self.rev, listing, promoting], self.q))
        self.assertEqual((count2, lq.parse(body2)[1]), (1, self.q + [('check', 't1:s1')]))
        self.assertEqual(lq.pending_subideas(body2), [])                   # a review ends the wait of the rest
        done = notebook([self.rev, listing, developing(('check', 't1:s1'), 'Developed')], self.q)
        self.assertEqual(lq.pending_subideas(done), [('build', 't1:s2')])  # one developed by its own entry waits no more

    def test_near_duplicates_are_shown_and_merged(self):
        a = 'Prove an upper bound for the refutation degree of random products of two affine forms'
        b = 'Prove an upper bound or a lower bound for the refutation degree of random products of affine forms'
        listing = subideas('t1', [('check', a), ('check', b), ('check', 'Read the source on colourings')])
        body, _ = lq.append_new(notebook([self.rev, listing], self.q))
        self.assertEqual([(x, y) for _, x, y in lq.similar_items(lq.parse_tree(body)[1])], [('t1:s1', 't1:s2')])
        merging = ('<article id="m" data-kind="task"><ul><li data-check="t1:s2">Same question. '
                   '<strong>Follow-up.</strong> Closed: merged into t1:s1</li></ul></article>')
        merged, _ = lq.append_new(notebook([self.rev, listing, merging], [*self.q, ('check', 't1:s1'), ('check', 't1:s2'),
                                                                        ('check', 't1:s3')]))
        nodes = lq.parse_tree(merged)[1]
        self.assertEqual([n.ident for n in nodes][-2:], ['t1:s1', 't1:s3'])
        self.assertIn('Merged from t1:s2: Prove an upper bound or a lower bound', nodes[-2].text)
        # an entry that develops the item and closes it as merged, in its own Follow-up, hands the wording over too
        queue = [*self.q, ('check', 't1:s1'), ('check', 't1:s2'), ('check', 't1:s3')]
        own = developing(('check', 't1:s2'), 'Closed').replace('Closed: x.', 'Closed: merged into t1:s1. The rest.')
        after = notebook([self.rev, listing, own], queue)
        tag, text = lq.record_articles(after)[-1]
        left = lq.transition(after, lq.parse_tree(notebook([self.rev, listing], queue))[1], tag, text)
        self.assertEqual([n.ident for n in left][-2:], ['t1:s1', 't1:s3'])
        self.assertIn('Merged from t1:s2: Prove an upper bound or a lower bound', left[-2].text)
        gone = own.replace('merged into t1:s1', 'merged into t9:s9')
        with self.assertRaisesRegex(ValueError, 'not queued'):
            lq.transition(after.replace(own, gone), lq.parse_tree(notebook([self.rev, listing], queue))[1],
                          *lq.record_articles(after.replace(own, gone))[-1])

    def test_claims_of_entries_on_other_items_are_shown_for_an_item(self):
        a = 'Prove an upper bound for the refutation degree of random products of two affine forms'
        listing = subideas('t1', [('check', a), ('check', 'Read the source on colourings of sparse graphs here')])
        queue = self.q                                    # the listed sub-ideas are queued, with their text, by append
        other = developing(self.q[0], 'Continuing').replace('<article id="d"',
                                                             '<article id="o" data-claims="lem:x lem:y"')
        queued, _ = lq.append_new(notebook([self.rev, listing], queue))
        body = queued.replace(listing, listing + other)
        summaries = [{'id': 'lem:x', 'assessment': 'Proof.', 'summary':
                      'An upper bound for the refutation degree of random products of two affine forms holds.'},
                     {'id': 'lem:y', 'assessment': 'Proof.', 'summary': 'Unrelated matter entirely.'},
                     {'id': 'lem:z', 'assessment': 'Proof.', 'summary': 'Random products of affine forms.'}]
        near = lq.claims_elsewhere(body, summaries, 't1:s1')
        self.assertEqual([pair[1:] for pair in near], [('lem:x', 'o')])                     # lem:z: no later entry
        self.assertEqual(lq.claims_elsewhere(body, summaries, 't1:s2'), [])
        self.assertEqual(lq.answered_report(body, summaries), [('t1:s1', near)])
        self.assertIn(f'  {near[0][0]} lem:x in #o', lq.item_status(body, 't1:s1', summaries))
        self.assertIn('Prove an upper bound for the refutation degree', lq.item_status(body, 't1:s1')[1])   # its text
        # ranked best first and cut at the limit; an item of formulas alone has nothing to rank by
        more = other.replace('lem:x lem:y', 'lem:x lem:y lem:z')
        ranked = lq.claims_elsewhere(queued.replace(listing, listing + more), summaries, 't1:s1')
        self.assertEqual([claim for _, claim, _ in ranked], ['lem:x', 'lem:z'])
        self.assertGreater(ranked[0][0], ranked[1][0])
        self.assertEqual(len(lq.claims_elsewhere(queued.replace(listing, listing + more), summaries, 't1:s1', 1)), 1)
        bare = queued.replace(a, r'\(x\)')
        self.assertEqual(lq.claims_elsewhere(bare.replace(listing, listing + other), summaries, 't1:s1'), [])
        # later entries on other items, of any kind, that link the queuing entry: the other signal, a command only
        linking = other.replace('<p><strong>Follow-up', '<p>See <a href="#t1">there</a>.</p><p><strong>Follow-up')
        self.assertEqual(lq.linking_entries(queued.replace(listing, listing + linking), 't1:s1'), ['o'])
        as_review = linking.replace('data-kind="research"', 'data-kind="review"')
        self.assertEqual(lq.linking_entries(queued.replace(listing, listing + as_review), 't1:s1'), ['o'])
        self.assertEqual(lq.linking_entries(body, 't1:s1'), [])                       # the entry does not link it
        self.assertEqual(lq.linking_entries(queued.replace(listing, linking + listing), 't1:s1'), [])     # earlier
        self.assertEqual(lq.linking_entries(queued.replace(listing, listing + linking.replace(
            f'data-{self.q[0][0]}="{self.q[0][1]}"', 'data-check="t1:s1"')), 't1:s1'), [])       # the item's own
        self.assertIsNone(lq.linking_entries(body, 'no-such-item'))                   # not a zero: nothing to look for
        self.assertIsNone(lq.linking_entries(lq.add(body, 'check', 'by-tool', 'a talk', a), 'by-tool'))
        # other entries whose claims cite, by a registry edge, a claim of the queuing entry: the case of
        # 12 October 2026, where the ranking by nearness printed none (lem:y is far from the item's text)
        self.assertIn('<article id="t1"', listing)
        based = body.replace('<article id="t1"', '<article id="t1" data-claims="lem:base"')
        edges = [{'type': 'cites', 'source': {'id': 'lem:y'}, 'target': {'id': 'lem:base'}},
                 {'type': 'depends_on', 'source': {'id': 'lem:y'}, 'target': {'id': 'lem:far'}},
                 {'type': 'cites', 'source': {'id': 'lem:nowhere'}, 'target': {'id': 'lem:base'}},
                 {'type': 'cites', 'source': {'id': 'lem:base'}, 'target': {'id': 'lem:base'}},
                 {'type': 'cites', 'source': {'id': 'lem:x'}, 'target': {'id': 'lem:base', 'namespace': 'historical'}}]
        self.assertNotIn('lem:y', [claim for _, claim, _ in lq.claims_elsewhere(based, summaries, 't1:s1')])
        row = ('o', 'lem:y', 'cites', 'lem:base', True, True)
        self.assertEqual(lq.citing_entries(based, edges, 't1:s1'), [row])     # not the queuing entry, not the historical
        self.assertEqual(lq.citing_entries(based, edges, 't1:s2'), [row])     # the other sub-idea of the same entry
        self.assertEqual(lq.citing_entries(body, edges, 't1:s1'), [])         # the queuing entry declares no claim
        self.assertEqual(lq.citing_entries(based, [], 't1:s1'), [])
        self.assertEqual(lq.citing_entries(based, edges, 'no-such-item'), [])
        as_review = based.replace(other, other.replace('data-kind="research"', 'data-kind="review"'))
        self.assertEqual(lq.citing_entries(as_review, edges, 't1:s1'), [row])           # a review is listed too
        developed = other.replace(f'data-{self.q[0][0]}="{self.q[0][1]}"', 'data-check="t1:s1"')
        own_entry = based.replace(other, developed)
        self.assertEqual(lq.citing_entries(own_entry, edges, 't1:s1'), [])      # the item's own entry is not another's
        # a claim of an entry that developed the item is looked for too, marked apart: a third entry citing lem:x,
        # after the item's latest development, and one from before the queuing entry
        third = other.replace('"o"', '"p"').replace('lem:x lem:y', 'lem:w')
        before = other.replace('"o"', '"b"').replace('lem:x lem:y', 'lem:v')
        refines = [{'type': 'refines', 'source': {'id': 'lem:w'}, 'target': {'id': 'lem:x'}},
                   {'type': 'cites', 'source': {'id': 'lem:v'}, 'target': {'id': 'lem:x'}},
                   {'type': 'cites', 'source': {'id': 'lem:base'}, 'target': {'id': 'lem:x'}}]
        cites_own = based.replace(other, developed + third).replace('<article id="t1"', before + '<article id="t1"')
        self.assertIn('<article id="b"', cites_own)
        found = lq.citing_entries(cites_own.replace('<article id="t1" data-claims="lem:base"', '<article id="t1"'),
                                  refines, 't1:s1')
        self.assertEqual(found, [('b', 'lem:v', 'cites', 'lem:x', False, False),
                                 ('p', 'lem:w', 'refines', 'lem:x', False, True)])
        self.assertEqual(lq.citing_lines(found, False), ['  #b: lem:v cites lem:x', '  #p [later]: lem:w refines lem:x'])
        self.assertEqual(lq.citing_lines(found, True), [])
        # an item added by the tool names no queuing entry: an identifier equal to an entry's anchor does not make
        # that entry's claims the item's (without the guard the entry t1, citing lem:x of #o, would be listed)
        tool = lq.add(based, 'check', 'o', 'a talk', a)
        self.assertIn('data-check="o"', tool)
        self.assertEqual(lq.citing_entries(tool, refines, 'o'), [])
        unstamped = re.sub(r'(<li data-check="o"[^>]*?) data-after="[^"]*"', r'\1', tool)
        self.assertNotEqual(unstamped, tool)
        self.assertEqual(lq.citing_entries(unstamped, refines, 'o'), [('t1', 'lem:base', 'cites', 'lem:x', True, True)])
        status = lq.item_status(based, 't1:s1', summaries, edges)
        self.assertIn('  #o [later]: lem:y cites lem:base', status)
        self.assertEqual(status[-1], '  none')                                  # no claim of its own entries is cited
        self.assertNotIn('whose claims cite', '\n'.join(lq.item_status(based, 't1:s1', summaries)))
        self.assertEqual(lq.item_status(body, 't1:s1', summaries, edges)[-3:-1],
                         ['  none', 'Other entries whose claims cite a claim of its own entries or its group\'s '
                          '([later]: after the latest development):'])
        self.assertEqual(lq.registered(Path('no-such-file')), ([], []))
        # the start of a cycle prints the entries citing the queuing entry for the item the next step names
        import turn_guidance
        named_step = '<section id="proposed-next-step"><p>Take <code>t1:s1</code> next.</p></section>'
        cited_notes = turn_guidance.next_item_notes(based + named_step, [], edges)
        self.assertEqual(len(cited_notes), 1)
        self.assertIn('#o [later]: lem:y cites lem:base', cited_notes[0])
        self.assertEqual(turn_guidance.next_item_notes(based + named_step, [], []), [])
        # the start of a cycle prints them for the item the next step names, and nothing for one it does not
        import turn_guidance
        step = '<section id="proposed-next-step"><p>Take <code>t1:s1</code> next.</p></section>'
        notes = turn_guidance.next_item_notes(body + step, summaries)
        self.assertEqual(len(notes), 1)
        self.assertIn('the next step names t1:s1', notes[0])
        self.assertIn('lem:x in #o', notes[0])
        self.assertEqual(turn_guidance.next_item_notes(body + step.replace('t1:s1', 't1:s2'), summaries), [])
        self.assertEqual(turn_guidance.next_item_notes(body, summaries), [])
        # an item added by the tool is later than the record's last entry at that time, which it names
        added = lq.add(body, 'check', 'new-item', 'a talk', a)
        self.assertEqual(lq.claims_elsewhere(added, summaries, 'new-item'), [])
        self.assertEqual([c for _, c, _ in lq.claims_elsewhere(added.replace(other, other + more.replace('"o"', '"p"')),
                                                               summaries, 'new-item')], ['lem:x', 'lem:z'])
        self.assertNotIn('Claims of later entries', '\n'.join(lq.item_status(body, 't1:s1')))
        # a claim of an entry that developed the item itself, or that came before the item was queued, is not listed
        own = other.replace(f'data-{self.q[0][0]}="{self.q[0][1]}"', 'data-check="t1:s1"')
        self.assertEqual(lq.claims_elsewhere(queued.replace(listing, listing + own), summaries, 't1:s1'), [])
        before = queued.replace(listing, other + listing)
        self.assertEqual(lq.claims_elsewhere(before, summaries, 't1:s1'), [])
        # ... but the status lists it apart, marked as earlier, and the count over the queue sees it
        old = lq.claims_elsewhere(before, summaries, 't1:s1', earlier=True)
        self.assertEqual([pair[1:] for pair in old], [('lem:x', 'o')])
        self.assertIn(f'  {old[0][0]} lem:x in #o [earlier]', lq.item_status(before, 't1:s1', summaries))
        self.assertNotIn('[earlier]', '\n'.join(lq.item_status(body, 't1:s1', summaries)))
        self.assertEqual(lq.claims_elsewhere(body, summaries, 't1:s1', earlier=True), [])
        self.assertEqual(lq.claims_elsewhere(queued.replace(listing, own + listing), summaries, 't1:s1',
                                             earlier=True), [])                       # the item's own entry
        self.assertEqual(lq.older_nearest(body, summaries)[0], 0)
        self.assertEqual(lq.older_nearest(before, summaries)[:2], (1, 1))
        apart = lq.add(before, 'check', 'by-hand', 'a talk', a)
        gone = re.sub(r'(<li data-check="by-hand"[^>]*?) data-after="[^"]*"', r'\1 data-after="no-such-entry"', apart)
        self.assertEqual(lq.older_nearest(gone, summaries)[2], lq.older_nearest(apart, summaries)[2] + 1)
        # both sides in one ranking: the better match after the item wins, and the worse one before it does not
        late = other.replace('"o"', '"p"')            # with lem:y: a word every ranked claim has weighs nothing
        early = other.replace('lem:x lem:y', 'lem:z')
        mixed = queued.replace(listing, early + listing + late)
        self.assertEqual([c for _, c, _ in lq.claims_elsewhere(mixed, summaries, 't1:s1', earlier=None)],
                         ['lem:x', 'lem:z'])
        self.assertEqual(lq.older_nearest(mixed, summaries)[0], 0)
        # another entry's claim between the queuing and the item's own entry is on neither side
        between = queued.replace(listing, listing + early + own)
        self.assertEqual(lq.claims_elsewhere(between, summaries, 't1:s1', earlier=True), [])
        self.assertEqual(lq.claims_elsewhere(between, summaries, 't1:s1'), [])
        # an item whose queuing entry the record does not hold has no earlier side and is counted apart
        self.assertEqual(lq.claims_elsewhere(lq.add(before, 'check', 'by-hand', 'a talk', a).replace(
            ' data-after="o"', '').replace(' data-after="t1"', ''), summaries, 'by-hand', earlier=True), [])
        places = lq.claim_places(before, summaries, 't1:s1', ['lem:x', 'lem:z'])
        self.assertIn('lem:x: place 1 of 1 among the claims of earlier entries', places[0])
        self.assertEqual(places[1], 'lem:z: not among them')
        # the append tool prints them for an item its next step names
        import importlib.util
        spec = importlib.util.spec_from_file_location('notebook_append', Path(lq.__file__).parent / 'notebook-append.py')
        append_tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(append_tool)
        self.assertEqual(append_tool.older_claim_lines(before, 't1:s1', summaries),
                         ['  Claim of an entry up to the one that queued it, nearest to its text [earlier]: lem:x in #o'])
        self.assertEqual(append_tool.older_claim_lines(body, 't1:s1', summaries), [])

    def test_new_review_pick_merged_without_reappearing(self):
        head = notebook([self.rev], self.q)
        entry = review('r2', [PASS, FAIL, FAIL], [PASS, FAIL])
        entry = entry.replace('</article>',
            '<h4>Sub-idea follow-up</h4><ul><li data-lead="r2:1">Same question. '
            '<strong>Follow-up.</strong> Closed: merged into r1:1</li></ul></article>')
        body, count = lq.append_new(notebook([self.rev, entry], self.q))
        self.assertEqual((count, lq.parse(body)[1]), (1, self.q + [('bridge', 'r2:1')]))
        self.assertIn('Merged from r2:1:', lq.parse_tree(body)[1][0].text)
        lq.check(head, body)
        again, added = lq.append_new(body)
        self.assertEqual((added, again), (0, body))

    def test_subideas_arrive_in_their_lists_order(self):
        listing = subideas('t1', [('build', 'b'), ('check', 'c'), ('build', 'd')])
        self.assertEqual(lq.arrivals_of(*lq.record_articles(notebook([listing]))[0]),
                         [('build', 't1:s1'), ('check', 't1:s2'), ('build', 't1:s3')])

    def test_subidea_ids_never_meet_lead_ids(self):
        entry = ('<article id="w" data-kind="review" data-route="step"><h4>Outside leads</h4><ul><li>L' + PASS
                 + '</li></ul><h4>Sub-ideas</h4><ul><li data-sub="check">c</li><li data-sub="build">b</li></ul></article>')
        self.assertEqual(lq.arrivals_of(*lq.record_articles(notebook([entry]))[0]),
                         [('lead', 'w:1'), ('check', 'w:s1'), ('build', 'w:s2')])

    def test_a_review_with_picks_queues_only_its_picks(self):
        entry = ('<article id="w" data-kind="review" data-route="step"><h4>Outside leads</h4><ul><li data-pick>A' + PASS
                 + '</li><li>B' + PASS + '</li><li data-pick>C' + PASS + '</li></ul><h4>Absurd bridges</h4><ul><li>D'
                 + PASS + '</li><li data-pick>E' + PASS + '</li></ul></article>')
        self.assertEqual(lq.arrivals_of(*lq.record_articles(notebook([entry]))[0]),
                         [('lead', 'w:1'), ('lead', 'w:3'), ('bridge', 'w:2')])

    def test_init_seeds_listed_subideas(self):
        listing = subideas('t1', [('check', 'c')])
        self.assertEqual(lq.open_items(notebook([self.rev, listing])), self.q + [('check', 't1:s1')])

    def test_a_side_notebooks_links_resolve_from_the_repository_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'research/results').mkdir(parents=True)
            (root / 'research/results/out.txt').write_text('answer')
            nb = root / 'research/branches/side/notebook.html'
            nb.parent.mkdir(parents=True)
            listing = subideas('t1', [('check', 'c')])
            head = notebook([listing], [('check', 't1:s1')])
            answered = lambda link: notebook([listing, developing(('check', 't1:s1'), 'Developed',
                                                                  f'<a href="{link}">out</a>')], [])
            lq.check(head, answered('research/results/out.txt'), nb, root)
            with self.assertRaisesRegex(ValueError, 'do not resolve'):       # resolves only from its own folder
                lq.check(head, answered('../../results/out.txt'), nb, root)

    def test_a_check_build_or_idea_joins_by_add_alone(self):
        head = notebook([self.rev], self.q)
        body = lq.add(head, 'build', 'port-it', 'user, 7 October 2026', 'Port <this> to main.')
        lq.check(head, body)
        # The item carries the record's last entry at the time, so that a review's period can place it.
        last = re.findall(r'<article id="([^"]+)"', head)[-1]
        self.assertIn(f'<li data-build="port-it" data-source="user, 7 October 2026" data-after="{last}">'
                      'Port &lt;this&gt; to main.</li>', body)
        self.assertEqual(lq.head_lines(body, 3)[3], '3. port-it: Port <this> to main.')
        for kind in ('check', 'idea'):
            body = lq.add(body, kind, f'a-{kind}', 'entry-2026-10-07-x', 'Y.')
            self.assertIn(f'<li data-{kind}="a-{kind}" data-source="entry-2026-10-07-x" data-after="{last}">Y. '
                          '(<a href="#entry-2026-10-07-x">source</a>)</li>', body)
            lq.check(head, body)
        for kind, ident, source, text, error in (
                ('idea', 'port-it', 's', 't', 'already queued'), ('check', 'Port_It', 's', 't', 'check ID .Port_It.'),
                ('build', 'ok', '', 't', 'an added build is .* where it came up'), ('idea', 'ok', 's', ' ', 'came up')):
            with self.subTest(ident=ident, source=source, text=text):
                with self.assertRaisesRegex(ValueError, error):
                    lq.add(body, kind, ident, source, text)
        with self.assertRaisesRegex(ValueError, 'no lead and bridge queue'):
            lq.add(notebook([self.rev]), 'build', 'x', 's', 't')

    def test_a_build_that_claims_a_cost_or_a_saving_says_whether_it_is_measured(self):
        head = notebook([self.rev], self.q)
        claims = ('Share the runs: it saves most of the time.', 'Cache it; the scan is slow.', 'The copy took 27 s each run.',
                  'Skip the copy, which takes several minutes.', 'Make it faster.', 'A change that cost the run 5 s was hidden.')
        for text in claims:
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, r'^a-build: the text claims a cost or a saving \(".+"\) and does '
                                                        'not say what it rests on: name the measurement'):
                    lq.add(head, 'build', 'a-build', 's', text)
                # The word settles it either way, and a check or an idea is a question, not a promise.
                for said in (' Not measured.', ' Measured: 27 s of 30 (research/results/x.txt).', ' No measurement yet.'):
                    lq.add(head, 'build', 'a-build', 's', text + said)
                lq.add(head, 'check', 'a-check', 's', text)
                lq.add(head, 'idea', 'an-idea', 's', text)
        # No claim of a cost: a verb of taking or saving something else, a time that is no duration.
        for text in ('Port it to main.', 'Let the tool take a source that was rewritten.', 'Ask for the saved output of a run.',
                     'A mutant took the group down twice, the first time unseen.', 'It took four calls by hand.'):
            with self.subTest(text=text):
                lq.add(head, 'build', 'a-build', 's', text)
        body = lq.add(head, 'build', 'a-build', 's', 'Port it.')
        with self.assertRaisesRegex(ValueError, 'a-build: the text claims a cost'):
            lq.edit(body, 'a-build', 'Port it: the copy is slow.')
        body = lq.add(body, 'check', 'a-check', 's', 'Why?')
        lq.edit(body, 'a-check', 'Why is the copy slow?')

    def test_a_second_extension_of_a_queued_builds_text_is_found(self):
        base = lq.add(notebook([self.rev], self.q), 'build', 'b1', 'a talk', 'Have the tool print the line.')
        once = base.replace('print the line.', 'print the line. Added 1 May from an entry: also the count.')
        twice = once.replace('also the count.', 'also the count. Added 2 May from another: also the words.')
        self.assertEqual(lq.extended_again(base, once), [])          # a first addition is allowed
        self.assertEqual(lq.extended_again(once, twice), ['build:b1'])
        self.assertEqual(lq.extended_again(once, once), [])
        self.assertEqual(lq.extended_again(None, twice), [])         # no committed notebook to compare with
        other = lq.add(once, 'check', 'c1', 'a talk', 'Read the source. Added 1 May: its second lemma.')
        self.assertEqual(lq.extended_again(other, other.replace('second lemma.', 'second lemma. Added 2 May: more.')),
                         [])                                         # a check's text may be extended

    def test_edit_replaces_an_added_items_text_and_keeps_its_source(self):
        head = notebook([self.rev], self.q)
        body = lq.add(head, 'build', 'port-it', 'entry-2026-10-07-x', 'Port it.')
        edited = lq.edit(body, 'port-it', 'Port it & test it.')
        self.assertRegex(edited, r'<li data-build="port-it" data-source="entry-2026-10-07-x" data-after="[^"]+">'
                                 r'Port it &amp; test it\. \(<a href="#entry-2026-10-07-x">source</a>\)</li>')
        self.assertNotIn('Port it.', edited)
        self.assertEqual(lq.edit(edited, 'port-it', 'Port it & test it.'), edited)
        lq.check(head, edited)
        with self.assertRaisesRegex(ValueError, 'nothing-like-it is not queued'):
            lq.edit(body, 'nothing-like-it', 't')
        with self.assertRaisesRegex(ValueError, 'listed by an entry'):
            lq.edit(body, 'r1:1', 't')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, 'notebook.html')
            path.write_text(body)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(lq.main(['lead_queue.py', 'edit', str(path), 'port-it', 'Ported.']), 0)
                self.assertEqual(lq.main(['lead_queue.py', 'edit', str(path), 'gone', 'x']), 1)
            self.assertIn('Edited port-it.', out.getvalue())
            self.assertIn('gone is not queued', err.getvalue())
            self.assertIn('>Ported. (<a href="#entry-2026-10-07-x">source</a>)</li>', path.read_text())

    def test_add_from_the_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, 'notebook.html')
            path.write_text(notebook([self.rev], self.q))
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(lq.main(['lead_queue.py', 'add', str(path), '--build', 'port-it', 's', 'Port it.']), 0)
                self.assertEqual(lq.main(['lead_queue.py', 'add', str(path), '--check', 'port-it', 's', 'Again.']), 1)
                self.assertEqual(lq.main(['lead_queue.py', 'add', str(path), '--idea', 'weigh-it', 's', 'Weigh it.']), 0)
                self.assertEqual(lq.main(['lead_queue.py', 'add', str(path), 'other', 's', 'No kind.', 'x']), 2)
                self.assertEqual(lq.main(['lead_queue.py', 'add', str(path), '--lead', 'other', 's', 'x']), 2)
            self.assertIn('Appended port-it, a build; 3 items in the queue.', out.getvalue())
            self.assertIn('Appended weigh-it, an idea; 4 items in the queue.', out.getvalue())
            self.assertIn('port-it is already queued', err.getvalue())
            self.assertRegex(path.read_text(), r'<li data-build="port-it" data-source="s" data-after="[^"]+">Port it\.</li>')
            self.assertNotIn('Again.', path.read_text())
            self.assertNotIn('other', path.read_text())

    def test_a_commit_without_an_entry_only_appends_added_items(self):
        head = notebook([self.rev], self.q)
        refused = 'only by appending, at the tail, the checks, builds and ideas lead_queue.py add writes'
        for queue, error in ((self.q + [('lead', 'r1:9')], refused),
                             (self.q + [('check', 'listed-by-no-entry')], refused),
                             (self.q + [(('idea', 'p'), [('check', 'x:s1')])], refused),
                             ([('idea', 'p')] + self.q, refused),
                             (self.q + [('idea', 'No_Source')], 'may not join the queue')):
            with self.subTest(queue=queue):
                with self.assertRaisesRegex(ValueError, error):
                    lq.check(head, notebook([self.rev], queue))
        sourced_lead = notebook([self.rev], self.q + [('lead', 'r1:9')]).replace(
            '<li data-lead="r1:9">', '<li data-lead="r1:9" data-source="s">')       # leads come from reviews only
        with self.assertRaisesRegex(ValueError, refused):
            lq.check(head, sourced_lead)
        body = head
        for n in range(lq.CAP - len(self.q)):
            body = lq.add(body, 'build', f'b-{n}', 's', 't')
        self.assertIn('data-draining="true"', body)
        lq.check(head, body)
        with self.assertRaisesRegex(ValueError, refused):
            lq.check(head, body.replace(' data-draining="true"', ''))

    def test_added_items_are_developed_by_their_kinds_rules(self):
        closed = [self.rev, research(self.q[0], 'Closed'), research(self.q[1], 'Closed')]
        for kind, cited, error in (('build', '<a href="tools/lead_queue.py">ported</a>', 'link the opened task'),
                                   ('check', '<a href="#r1">answered</a>', 'cite the evidence'),
                                   ('idea', '<a href="tools/lead_queue.py">settled</a>', 'cite the evidence')):
            with self.subTest(kind=kind):
                head = lq.add(notebook(closed, []), kind, 'it', 's', 't')
                developed = lambda body: notebook(closed + [developing((kind, 'it'), 'Developed', body)], [])
                lq.check(head, developed(cited), ROOT / 'notebook.html', ROOT)
                with self.assertRaisesRegex(ValueError, error):
                    lq.check(head, developed('<p>done</p>'), ROOT / 'notebook.html', ROOT)
        build_head = lq.add(notebook(closed, []), 'build', 'it', 's', 't')
        with self.assertRaisesRegex(ValueError, 'link the opened task'):          # an anchor is no built thing
            lq.check(build_head, notebook(closed + [developing(('build', 'it'), 'Developed', '<a href="#r1">x</a>')], []),
                     ROOT / 'notebook.html', ROOT)

    def test_check_and_build_need_resolving_evidence_to_be_developed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'research/results').mkdir(parents=True)
            (root / 'research/results/out.txt').write_text('answer')
            (root / 'work/arm-check').mkdir(parents=True)
            (root / 'research/claims').mkdir(parents=True)
            (root / 'research/claims/index.json').write_text(json.dumps({'claims': [{'id': 'lem:known'}]}))
            nb = root / 'notebook.html'
            listing = subideas('t1', [('check', 'c'), ('build', 'b')])
            queue = [('check', 't1:s1'), ('build', 't1:s2')]
            head = notebook([listing], queue)

            def after(item, outcome, body, rest):
                return notebook([listing, developing(item, outcome, body)], rest)
            accepted = [('check', '<a href="research/results/out.txt">out</a>'),
                        ('check', 'see <a href="#t1">the listing</a>'),
                        ('check', 'by lem:known, and prose naming lem:elsewhere'),
                        ('check', '<a href="https://example.org">a page</a> and lem:known'),
                        ('check', 'see <a href="notebook.html#t1">the listing</a>')]     # through the file
            for kind, body in accepted:
                with self.subTest(accepted=body):
                    lq.check(head, after(queue[0], 'Developed', body, queue[1:]), nb, root)
            refused = ['no evidence at all', 'only lem:elsewhere, unregistered',
                       '<a href="research/results/missing.txt">gone</a> and lem:known', '<a href="#nowhere">x</a>',
                       'answered <a href="#d">here</a>',                 # the entry's own anchor
                       'answered <a href="notebook.html#d">here</a>', '<a href="notebook.html#gone">x</a>',
                       'in <a href="notebook.html">this notebook</a>']
            for body in refused:
                with self.subTest(refused=body), self.assertRaises(ValueError):
                    lq.check(head, after(queue[0], 'Developed', body, queue[1:]), nb, root)
            here = os.getcwd()
            os.chdir(ROOT)                  # a link that resolves from the working directory, not from a notebook
            try:
                with self.assertRaises(ValueError):                     # no path: a file link cannot resolve
                    lq.check(head, after(queue[0], 'Developed', '<a href="tools/lead_queue.py">x</a>', queue[1:]),
                             None, root)
            finally:
                os.chdir(here)
            lq.check(head, after(queue[0], 'Closed', 'no evidence needed', queue[1:]), nb, root)
            build_head = notebook([listing, developing(queue[0], 'Closed')], queue[1:])

            def built(body):
                return notebook([listing, developing(queue[0], 'Closed'), developing(queue[1], 'Developed', body)
                                 .replace('id="d"', 'id="e"')], [])
            lq.check(build_head, built('<a href="work/arm-check/">task</a>'), nb, root)
            lq.check(build_head, built('<a href="research/results/out.txt">built</a>'), nb, root)
            github = 'https://github.com/kbr-/math-research/blob/main/'     # the notebooks' file links
            lq.check(build_head, built(f'<a href="{github}research/results/out.txt">built</a>'), nb, root)
            for body in ('<a href="#t1">an anchor is no build</a>', 'lem:known', '<a href="work/none/">x</a>',
                         f'<a href="{github}research/results/none.txt">x</a>', '<a href="https://example.org/a">x</a>'):
                with self.subTest(build_refused=body), self.assertRaises(ValueError):
                    lq.check(build_head, built(body), nb, root)

    def test_subideas_keep_the_head_only_rule_and_reopen(self):
        listing = subideas('t1', [('check', 'c'), ('check', 'd')])
        queue = [('check', 't1:s1'), ('check', 't1:s2')]
        head = notebook([listing], queue)
        with self.assertRaises(ValueError):                             # not the head
            lq.check(head, notebook([listing, developing(queue[1], 'Closed')], queue[:1]))
        closed = notebook([listing, developing(queue[0], 'Closed')], queue[1:])
        reopen = ('<article id="r" data-kind="research" data-route="step"><ul><li data-check="t1:s1">x '
                  '<strong>Follow-up.</strong> Reopened: closed too early.</li></ul></article>')
        body, count = lq.append_new(notebook([listing, developing(queue[0], 'Closed'), reopen], queue[1:]))
        self.assertEqual((count, lq.parse(body)[1]), (1, [queue[1], queue[0]]))
        lq.check(closed, body)

    def test_subideas_nest_under_the_item_they_belong_to(self):
        head = notebook([self.rev], self.q)
        listing = developing(self.q[0], 'Continuing', '<h4>Sub-ideas</h4><ul><li data-sub="check">c</li>'
                             '<li data-sub="build" data-parent="lead:r1:2">b</li></ul>')
        want = [(self.q[0], [('check', 'd:s1')]), (self.q[1], [('build', 'd:s2')])]
        body, count = lq.append_new(notebook([self.rev, listing], self.q))
        self.assertEqual((count, lq.shape(lq.parse_tree(body)[1])), (2, [(i, c) for i, c in want]))
        lq.check(head, body)
        with self.assertRaises(ValueError):                             # flat, not nested
            lq.check(head, notebook([self.rev, listing], self.q + [('check', 'd:s1'), ('build', 'd:s2')]))
        nested = notebook([self.rev], want)
        child = developing(('check', 'd:s1'), 'Continuing', '<h4>Sub-ideas</h4><ul><li data-sub="check">e</li></ul>'
                           ).replace('id="d"', 'id="f"')
        body, _ = lq.append_new(notebook([self.rev, child], want))       # listed while developing a child: its parent
        self.assertEqual(lq.shape(lq.parse_tree(body)[1])[0], (self.q[0], [('check', 'd:s1'), ('check', 'f:s1')]))

    def test_subideas_of_a_developed_subidea_join_its_parent(self):
        listing = developing(self.q[0], 'Continuing', '<h4>Sub-ideas</h4><ul><li data-sub="build">a</li></ul>'
                             ).replace('id="d"', 'id="k"')
        tree = [(self.q[0], [('build', 'k:s1')]), (self.q[1], [])]
        child = developing(('build', 'k:s1'), 'Developed', '<h4>Sub-ideas</h4><ul><li data-sub="build">b</li></ul>'
                           ).replace('id="d"', 'id="f"')
        body = lq.done(notebook([self.rev, listing, child], tree), 'Developed')   # removes k:s1 first
        body, count = lq.append_new(body)
        self.assertEqual((count, lq.shape(lq.parse_tree(body)[1])),
                         (1, [(self.q[0], [('build', 'f:s1')]), (self.q[1], [])]))

    def test_a_named_parent_must_be_queued_except_in_an_audit(self):
        head = notebook([self.rev], self.q)
        stray = subideas('t1', [('check', 'c')]).replace('data-sub="check"', 'data-sub="check" data-parent="lead:r9:1"')
        with self.assertRaises(ValueError):
            lq.append_new(notebook([self.rev, stray], self.q))
        audit = stray.replace('data-kind="task"', 'data-kind="audit"')
        body, _ = lq.append_new(notebook([self.rev, audit], self.q))
        self.assertEqual(lq.parse(body)[1], self.q + [('check', 't1:s1')])
        lq.check(head, body)

    def test_subideas_of_one_parent_may_be_batched(self):
        tree = [(self.q[0], [('check', 'k:s1'), ('check', 'k:s2'), ('check', 'k:s3')]),
                (self.q[1], [('check', 'm:s1')])]
        before = notebook([self.rev], tree)
        done = ('<ul><li data-check="k:s1">Answered in <a href="#r1">the review</a>. '
                '<strong>Follow-up.</strong> Developed: see the link.</li>'
                '<li data-check="k:s3">Same premise. <strong>Follow-up.</strong> Closed: restated.</li></ul>')
        entry = developing(self.q[0], 'Continuing', done)
        left = [(self.q[0], [('check', 'k:s2')]), (self.q[1], [('check', 'm:s1')])]
        lq.check(before, notebook([self.rev, entry], left))
        with self.assertRaises(ValueError):                             # the developed sub-ideas leave the queue
            lq.check(before, notebook([self.rev, entry], tree))
        with self.assertRaises(ValueError):                             # evidence is still required
            lq.check(before, notebook([self.rev, developing(self.q[0], 'Continuing', done.replace(
                'Answered in <a href="#r1">the review</a>. ', 'Answered. '))], left))
        other = ('<ul><li data-check="m:s1">Answered in <a href="#r1">the review</a>. '
                 '<strong>Follow-up.</strong> Developed: see the link.</li></ul>')
        with self.assertRaises(ValueError):                             # another parent's sub-idea is not batched
            lq.check(before, notebook([self.rev, developing(self.q[0], 'Continuing', other)],
                                      [tree[0], (self.q[1], [])]))
        via_child = developing(('check', 'k:s1'), 'Closed', done.replace('k:s1', 'k:s2'))  # from a sibling
        lq.check(before, notebook([self.rev, via_child], [(self.q[0], []), (self.q[1], [('check', 'm:s1')])]))

    def test_the_head_or_its_first_subidea_and_their_spell(self):
        tree = [(self.q[0], [('check', 'k:s1'), ('check', 'k:s2')]), (self.q[1], [])]
        before = notebook([self.rev], tree)
        with self.assertRaises(ValueError):                             # not the first sub-idea
            lq.check(before, notebook([self.rev, developing(('check', 'k:s2'), 'Closed')],
                                      [(self.q[0], [('check', 'k:s1')]), (self.q[1], [])]))
        first = notebook([self.rev, developing(('check', 'k:s1'), 'Closed')], [(self.q[0], [('check', 'k:s2')]), self.q[1]])
        lq.check(before, first)
        self.assertEqual(lq.shape(lq.parse_tree(lq.done(notebook([self.rev, developing(('check', 'k:s1'), 'Closed')],
                                                                     tree), 'Closed'))[1]),
                         lq.shape(lq.parse_tree(first)[1]))
        cont_parent, cont_child = research(self.q[0], 'Continuing'), developing(('check', 'k:s1'), 'Continuing')
        earlier = [cont_parent, cont_child.replace('id="d"', 'id="d1"'), cont_parent]
        self.assertEqual(lq.spell(notebook([self.rev] + earlier + [cont_child], tree), self.q[0]), 4)
        moved = [(self.q[1], []), (self.q[0], [('check', 'k:s1'), ('check', 'k:s2')])]
        lq.check(notebook([self.rev] + earlier, tree), notebook([self.rev] + earlier + [cont_child], moved))
        with self.assertRaises(ValueError):                             # the fourth entry moves the parent
            lq.check(notebook([self.rev] + earlier, tree), notebook([self.rev] + earlier + [cont_child], tree))
        # so does a fourth that closes the sub-idea: the parent goes to the tail with what is left of it
        closing = developing(('check', 'k:s1'), 'Closed')
        left = [(self.q[1], []), (self.q[0], [('check', 'k:s2')])]
        lq.check(notebook([self.rev] + earlier, tree), notebook([self.rev] + earlier + [closing], left))
        with self.assertRaises(ValueError):
            lq.check(notebook([self.rev] + earlier, tree),
                     notebook([self.rev] + earlier + [closing], [(self.q[0], [('check', 'k:s2')]), self.q[1]]))
        self.assertEqual(lq.shape(lq.parse_tree(lq.done(notebook([self.rev] + earlier + [closing], tree),
                                                        'Closed'))[1]), left)
        # a queue committed with the parent still first after that entry owes the move: the next entry develops
        # the item behind it, done and the head shown settle it, and developing the parent instead is refused
        # (as in a real record, the sub-ideas were listed by an entry developing their parent, here with ID k)
        stale = [(self.q[0], [('check', 'k:s2')]), (self.q[1], [])]
        listing = developing(self.q[0], 'Continuing', '<h4>Sub-ideas</h4><ul><li data-sub="check">a</li>'
                             '<li data-sub="check">b</li></ul>').replace('id="d"', 'id="k"')
        settled = [listing, cont_child.replace('id="d"', 'id="d1"'), cont_parent, closing]
        nxt = research(self.q[1], 'Continuing')
        lq.check(notebook([self.rev] + settled, stale), notebook([self.rev] + settled + [nxt], left))
        self.assertEqual(lq.shape(lq.parse_tree(lq.done(notebook([self.rev] + settled + [nxt], stale),
                                                        'Continuing'))[1]), left)
        self.assertIn(self.q[1][1], lq.head_lines(notebook([self.rev] + settled, stale))[1])
        with self.assertRaises(ValueError):
            lq.check(notebook([self.rev] + settled, stale),
                     notebook([self.rev] + settled + [research(self.q[0], 'Continuing')], stale))

    def test_a_parent_with_subideas_is_not_developed_and_closes_them(self):
        tree = [(self.q[0], [('check', 'k:s1'), ('build', 'k:s2')]), (self.q[1], [])]
        before = notebook([self.rev], tree)
        with self.assertRaises(ValueError):
            lq.check(before, notebook([self.rev, research(self.q[0], 'Developed')], [self.q[1]]))
        lq.check(before, notebook([self.rev, research(self.q[0], 'Closed')], [self.q[1]]))
        keep = ('<article data-kind="research" data-route="step" data-lead="r1:1"><ul><li data-build="k:s2">still '
                'useful <strong>Follow-up.</strong> Continuing: on its own.</li></ul><p><strong>Follow-up.</strong> '
                'Closed: falsified.</p></article>')
        # a sub-idea belongs to its item: keeping one open means the parent is not Closed but Continuing
        with self.assertRaises(ValueError):
            lq.check(before, notebook([self.rev, keep], [self.q[1], ('build', 'k:s2')]))
        lq.check(before, notebook([self.rev, keep.replace('Closed: falsified', 'Continuing: its sub-idea')], tree))

    def test_a_reopened_subidea_returns_at_the_top_level(self):
        listing = developing(self.q[0], 'Continuing', '<h4>Sub-ideas</h4><ul><li data-sub="check">c</li></ul>')
        closing = developing(('check', 'd:s1'), 'Closed').replace('id="d"', 'id="e"')
        closed = notebook([self.rev, listing, closing], self.q)
        # the reopening entry develops the head, yet the reopened sub-idea goes to the tail, not under it
        reopen = ('<article id="r" data-kind="research" data-route="step" data-lead="r1:1"><ul><li data-check="d:s1">'
                  'x <strong>Follow-up.</strong> Reopened: too early.</li></ul><p><strong>Follow-up.</strong> Continuing:'
                  ' next.</p></article>')
        body, count = lq.append_new(notebook([self.rev, listing, closing, reopen], self.q))
        self.assertEqual((count, lq.shape(lq.parse_tree(body)[1])),
                         (1, [(self.q[0], []), (self.q[1], []), (('check', 'd:s1'), [])]))
        lq.check(closed, body)

    def test_triage_and_backpressure_count_top_level_items(self):
        rev = review('r1', [PASS] * (lq.CAP - 1))
        queue = [('lead', f'r1:{n}') for n in range(1, lq.CAP)]
        many = [(queue[0], [('check', f'k:s{n}') for n in range(1, 6)])] + queue[1:]
        before = notebook([rev], many)
        self.assertEqual(lq.parse(before)[1], queue)                     # 49 top-level items: not draining
        flat = notebook([rev], queue)                                    # 49 top-level items, no sub-ideas yet
        listing = developing(queue[0], 'Continuing', '<h4>Sub-ideas</h4><ul>' + '<li data-sub="check">c</li>' * 5
                             + '</ul>')
        body, count = lq.append_new(notebook([rev, listing], queue))
        self.assertEqual((count, lq.parse(body)[0]), (5, False))          # 54 items, 49 top-level: no draining
        lq.check(flat, body)

    def test_init_places_subideas_under_their_parents(self):
        listing = developing(self.q[0], 'Continuing', '<h4>Sub-ideas</h4><ul><li data-sub="check">c</li>'
                             '<li data-sub="build" data-parent="lead:r9:9">b</li></ul>')
        tree = lq.open_tree(notebook([self.rev, listing]))
        self.assertEqual(lq.shape(tree), [(self.q[0], [('check', 'd:s1')]), (self.q[1], []), (('build', 'd:s2'), [])])
        plain = '<article id="z" data-kind="review" data-route="step"><p>no queue work</p></article>'
        lq.check(None, notebook([self.rev, listing, plain], lq.shape(tree)[:2] + [('build', 'd:s2')]))

    def test_the_section_nests_one_level_of_checks_and_builds(self):
        deep = ('<section id="lead-queue"><ol><li data-lead="r1:1">a<ul><li data-check="k:s1">b<ul><li data-check="k:s2">'
                'c</li></ul></li></ul></li></ol></section>')
        with self.assertRaises(ValueError):
            lq.parse_tree(deep)
        lead_child = ('<section id="lead-queue"><ol><li data-lead="r1:1">a<ul><li data-lead="r1:2">b</li></ul></li>'
                      '</ol></section>')
        with self.assertRaises(ValueError):
            lq.parse_tree(lead_child)
        lines = lq.head_lines(notebook([self.rev], [(self.q[0], [('check', 'k:s1')]), self.q[1]]))
        self.assertEqual(lines[1:], ['1. r1:1', '   - k:s1', '2. r1:2'])
        waiting = notebook([self.rev], [(self.q[0], [('check', 'k:s1')]), self.q[1]]).replace(
            'data-check="k:s1">', 'data-check="k:s1" data-waits="the licence">')
        self.assertEqual(lq.head_lines(waiting)[2], '   - k:s1 [waiting: the licence]')

    def test_a_notebook_without_route_items_is_checked_once_it_has_a_queue(self):
        lq.check(None, notebook([self.rev], route=False))               # no section: nothing to check
        with self.assertRaises(ValueError):                             # a section: checked, here an item twice
            lq.check(None, notebook([self.rev], self.q + self.q[:1], route=False))
        lq.check(None, notebook([self.rev], self.q, route=False))

    def test_counted_entry_kinds_come_from_the_section(self):
        task = lambda item, outcome: developing(item, outcome).replace('data-kind="research"', 'data-kind="task"')
        attrs = ' data-counted="task"'
        head = notebook([self.rev], self.q, attrs=attrs)
        lq.check(head, notebook([self.rev, task(self.q[0], 'Closed')], self.q[1:], attrs=attrs))
        with self.assertRaises(ValueError):                             # a research entry does not count here
            lq.check(head, notebook([self.rev, research(self.q[0], 'Closed')], self.q[1:], attrs=attrs))
        with self.assertRaises(ValueError):                             # nor does a task entry by default
            lq.check(notebook([self.rev], self.q), notebook([self.rev, task(self.q[0], 'Closed')], self.q[1:]))
        earlier = [task(self.q[0], 'Continuing').replace('id="d"', f'id="d{n}"') for n in range(3)]
        self.assertEqual(lq.spell(notebook([self.rev] + earlier, self.q, attrs=attrs), self.q[0]), 3)

    def test_backpressure_can_be_off(self):
        big = review('r1', [PASS] * lq.CAP)
        queue = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
        attrs = ' data-backpressure="off"'
        head = notebook([big], queue, attrs=attrs)
        lq.check(None, head)                                            # 50 items, no flag
        with self.assertRaises(ValueError):
            lq.check(None, notebook([big], queue, draining=True, attrs=attrs))
        lq.check(head, notebook([big, research()], queue, attrs=attrs))  # nothing must develop the head
        self.assertFalse(lq.parse(lq.done(notebook([big, research(queue[0], 'Continuing')], queue, attrs=attrs),
                                          'Continuing'))[0])

    def test_the_user_may_pick_an_item_out_of_order(self):
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        head = notebook([rev], q)
        quote = '<p><strong>Picked.</strong> The user: \u201ctake r1:3 next, it unblocks the release\u201d.</p>'
        pick = lambda outcome, said=quote: developing(q[2], outcome, said).replace(
            'data-kind="research"', 'data-kind="research" data-picked="user"')
        lq.check(head, notebook([rev, pick('Closed')], q[:2]))
        lq.check(head, notebook([rev, pick('Continuing')], q))           # it stays where it is
        with self.assertRaises(ValueError):                             # no quotation
            lq.check(head, notebook([rev, pick('Closed', '<p><strong>Picked.</strong> by the user.</p>')], q[:2]))
        with self.assertRaises(ValueError):                             # not picked: the head only
            lq.check(head, notebook([rev, developing(q[2], 'Closed')], q[:2]))
        cont = research(q[0], 'Continuing')
        self.assertEqual(lq.spell(notebook([rev, cont, cont, pick('Continuing'), cont], q), q[0]), 3)
        big = review('r1', [PASS] * lq.CAP)
        bq = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
        bpick = developing(bq[5], 'Closed', quote).replace('data-kind="research"', 'data-kind="research" data-picked="user"')
        lq.check(notebook([big], bq, draining=True), notebook([big, bpick], bq[:5] + bq[6:], draining=True))

    def test_the_agent_may_choose_an_item_with_a_stated_reason(self):
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        head = notebook([rev], q)
        why = ('<p><strong>Chosen.</strong> It bears on the open statement on the family more directly than the '
               'head does.</p>')
        lq.check(head, notebook([rev, developing(q[2], 'Closed', why)], q[:2]))
        lq.check(head, notebook([rev, developing(q[2], 'Continuing', why)], q))      # it stays where it is
        with self.assertRaises(ValueError):                             # no reason given: the head only
            lq.check(head, notebook([rev, developing(q[2], 'Closed')], q[:2]))
        with self.assertRaises(ValueError):                             # a reason must say something
            lq.check(head, notebook([rev, developing(q[2], 'Closed', '<p><strong>Chosen.</strong> yes.</p>')], q[:2]))
        cont = developing(q[2], 'Continuing', why)
        spent = [rev] + [cont] * lq.SPELL
        lq.check(notebook(spent[:-1], q), notebook(spent, q))           # the last entry of its spell
        with self.assertRaises(ValueError):                             # beyond the boundary without an extension
            lq.check(notebook(spent, q), notebook(spent + [cont], q))
        big = review('r1', [PASS] * lq.CAP)
        bq = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
        lq.check(notebook([big], bq, draining=True),                    # also while draining
                 notebook([big, developing(bq[5], 'Closed', why)], bq[:5] + bq[6:], draining=True))

    def test_the_user_may_reorder_the_queue(self):
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        quote = '<p><strong>Picked.</strong> The user: \u201cmost promising first\u201d.</p>'

        def order(items, tag='data-kind="audit" data-picked="user"', said=quote, extra=''):
            return (f'<article id="o" {tag} data-route="step">{said}{extra}<h4>Queue order</h4><ol>'
                    + ''.join(f'<li data-{k}="{i}"></li>' for k, i in items) + '</ol></article>')

        new = [q[2], q[0], q[1]]
        head = notebook([rev], q)
        lq.check(head, notebook([rev, order(new)], new))
        with self.assertRaises(ValueError):                             # the order must be applied
            lq.check(head, notebook([rev, order(new)], q))
        body, added = lq.append_new(notebook([rev, order(new)], q))
        self.assertEqual((lq.open_items(body) and [n.item for n in lq.parse_tree(body)[1]], added), (new, 0))
        refused = {
            'not picked': (order(new, tag='data-kind="audit"'), 'is the user'),
            'missing': (order(new[:2]), 'every remaining top-level item'),
            'twice': (order(new + [q[0]]), 'each item once'),
            'not queued': (order(new + [('lead', 'r9:1')]), 'not queued r9:1'),
            'outcome': (order(new).replace('<li data-lead="r1:1"></li>', '<li data-lead="r1:1">x <strong>Follow-up.'
                                          '</strong> Closed: x.</li>'), 'carry no outcome'),
            'develops': (order(new, tag='data-kind="research" data-picked="user" data-lead="r1:3"',
                              extra='<p><strong>Follow-up.</strong> Continuing: x.</p>'), 'develops no item'),
        }
        for why, (entry, message) in refused.items():
            with self.subTest(why), self.assertRaisesRegex(ValueError, message):
                lq.check(head, notebook([rev, entry], new))
        triage = ('<h4>Queue triage</h4><ul><li data-lead="r1:1">' + 'word ' * 85 + ' (<a href="#r1">'
                  'r1</a>) <strong>Follow-up.</strong> Closed: x.</li></ul>')
        with self.assertRaises(ValueError):                             # with a triage batch
            lq.check(head, notebook([rev, order(new[:2], tag='data-kind="research" data-picked="user"',
                                                extra=triage)], [q[2], q[1]]))
        child = ('<article id="t" data-kind="task"><p>work</p><h4>Sub-ideas</h4><ul><li data-sub="check" '
                 'data-parent="lead:r1:1">x</li></ul></article>')
        nested = [(q[0], [('check', 't:s1')]), q[1], q[2]]
        with self.assertRaisesRegex(ValueError, 'sub-ideas keep their place'):   # a sub-idea is not top-level
            lq.check(notebook([rev, child], nested),
                     notebook([rev, child, order([q[2], q[0], q[1], ('check', 't:s1')])],
                              [q[2], (q[0], [('check', 't:s1')]), q[1]]))
        lq.check(notebook([rev, child], nested), notebook([rev, child, order(new)], [q[2], (q[0], [('check', 't:s1')]), q[1]]))
        big = review('r1', [PASS] * lq.CAP)
        bq = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
        flipped = bq[::-1]
        lq.check(notebook([big], bq, draining=True), notebook([big, order(flipped)], flipped, draining=True))
        with self.assertRaises(ValueError):                             # draining: a counted entry develops
            lq.check(notebook([big], bq, draining=True),
                     notebook([big, order(flipped, tag='data-kind="research" data-picked="user"')], flipped,
                              draining=True))

    def test_an_item_waiting_on_the_user_is_passed_over(self):
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        wait = ('<article id="w" data-kind="research" data-route="step"><ul><li data-lead="r1:1">needs a licence '
                '<strong>Follow-up.</strong> Waiting: the user\'s answer on the licence.</li></ul></article>')
        body, _ = lq.append_new(notebook([rev, wait], q))
        self.assertEqual(lq.marks(lq.parse_tree(body)[1]), {q[0]})
        lq.check(notebook([rev], q), body)
        with self.assertRaises(ValueError):                             # a mark needs its follow-up
            lq.check(notebook([rev], q), body.replace('Waiting: the', 'about the'))
        marked = body
        with self.assertRaises(ValueError):                             # the waiting head is passed over
            lq.check(marked, notebook([rev, wait, research(q[0], 'Closed')], q[1:]))
        nxt = marked.replace('</article></section>', '</article>' + research(q[1], 'Closed') + '</section>')
        lq.check(marked, lq.done(nxt, 'Closed'))
        unblock = ('<article id="u" data-kind="research" data-route="step"><ul><li data-lead="r1:1">x <strong>'
                   'Follow-up.</strong> Unblocked: licence granted.</li></ul></article>')
        body2, _ = lq.append_new(marked.replace('</article></section>', '</article>' + unblock + '</section>'))
        self.assertEqual(lq.marks(lq.parse_tree(body2)[1]), set())
        lq.check(marked, body2)
        everyone = notebook([rev], q).replace('data-lead="r1:1">', 'data-lead="r1:1" data-waits="a">').replace(
            'data-lead="r1:2">', 'data-lead="r1:2" data-waits="b">').replace('data-lead="r1:3">', 'data-lead="r1:3" data-waits="c">')
        draining = everyone.replace('<section id="lead-queue">', '<section id="lead-queue" data-draining="true">')
        # every item waits: draining asks nothing of the entry (the flag goes, three items being under the floor)
        lq.check(draining, everyone.replace('</article></section>', '</article>' + research() + '</section>'))

    def test_waiting_subideas_and_triage_items_are_passed_over(self):
        wait_child = notebook([self.rev], [(self.q[0], [('check', 'k:s1'), ('check', 'k:s2')]), self.q[1]]).replace(
            'data-check="k:s1">', 'data-check="k:s1" data-waits="x">')
        ok = lq.done(wait_child.replace('</article></section>', '</article>' + developing(('check', 'k:s2'), 'Closed')
                                        + '</section>'), 'Closed')
        lq.check(wait_child, ok)                                        # the first sub-idea not waiting
        with self.assertRaises(ValueError):
            lq.check(wait_child, lq.done(wait_child.replace('</article></section>', '</article>' + developing(
                ('check', 'k:s1'), 'Closed') + '</section>'), 'Closed'))
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        waiting_head = notebook([rev], q).replace('data-lead="r1:1">', 'data-lead="r1:1" data-waits="x">')
        nameless = ('<article id="w" data-kind="research" data-route="step"><ul><li data-lead="r1:1">x <strong>'
                    'Follow-up.</strong> Waiting:</li></ul></article>')
        with self.assertRaises(ValueError):                             # a Waiting follow-up names its request
            lq.check(notebook([rev], q), lq.append_new(notebook([rev, nameless], q))[0])

    def test_a_branch_s_own_module_reads_and_checks_what_a_waiting_follow_up_names(self):
        def wait(body):
            return ('<article id="w" data-kind="research" data-route="step"><ul><li data-lead="r1:1">x <strong>'
                    f'Follow-up.</strong> Waiting: {body}.</li></ul></article>')
        seen = []
        named = {'wait_reference': lambda rest: 'ledger 3' if 'ledger' in rest else None,
                 'wait_problems': lambda ref, base: seen.append((ref, base)) or (['no such row'] if ref == 'ledger 3' else [])}
        head = notebook([self.rev], self.q)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            check = lambda body: lq.check(head, lq.append_new(notebook([self.rev, wait(body)], self.q))[0],
                                          root / 'notebook.html', root)
            # No module: the reference is the follow-up's plain text, and nothing more is asked of it.
            with patch.object(lq.branch_extension, 'ask', lambda name, default=None, tools=None: default):
                self.assertEqual(lq.wait_changes(wait('the <a href="ledger.md">ledger</a>, row 3')),
                                 {('lead', 'r1:1'): 'the ledger , row 3'})
                check('the <a href="ledger.md">ledger</a>, row 3')
            with patch.object(lq.branch_extension, 'ask', lambda name, default=None, tools=None: named.get(name, default)):
                self.assertEqual(lq.wait_changes(wait('the <a href="ledger.md">ledger</a>, row 3')), {('lead', 'r1:1'): 'ledger 3'})
                self.assertEqual(lq.wait_changes(wait('your answer on the route')), {('lead', 'r1:1'): 'your answer on the route'})
                check('your answer on the route')
                with self.assertRaisesRegex(ValueError, 'r1:1: no such row'):
                    check('the ledger')
            self.assertEqual(seen, [('your answer on the route', root), ('ledger 3', root)])

    def test_a_kind_module_adds_its_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'fake_kinds.py').write_text(
                'def kinds(lq):\n'
                '    def admit(body, head_body, item):\n'
                '        assert "idea" in lq.NAMES          # the live module, not a copy taken before it\n'
                '        return [] if item[1].startswith("ok") else ["not admitted"]\n'
                '    def closed(tag, text, where):\n'
                '        return [] if "Kill criterion" in text else ["no kill criterion"]\n'
                '    return [lq.Kind("idea", admit=admit, rules={"Closed": closed}, reopen=False)]\n')
            sys.path.insert(0, tmp)
            try:
                attrs = ' data-kind-modules="fake_kinds" data-counted="research survey"'
                ideas = [('idea', 'ok-one'), ('idea', 'ok-two')]
                head = notebook([self.rev], [self.q[0]] + ideas, attrs=attrs)
                lq.check(head, notebook([self.rev, research()], [self.q[0]] + ideas + [('idea', 'ok-three')], attrs=attrs))
                with self.assertRaises(ValueError):                     # the module refuses it
                    lq.check(head, notebook([self.rev, research()], [self.q[0]] + ideas + [('idea', 'bad')], attrs=attrs))
                closed = lambda body: notebook([self.rev, research(self.q[0], 'Closed'),
                                                developing(ideas[0], 'Closed', body).replace('data-kind="research"',
                                                                                           'data-kind="survey"')],
                                               ideas[1:], attrs=attrs)
                after_lead = notebook([self.rev, research(self.q[0], 'Closed')], ideas, attrs=attrs)
                lq.check(after_lead, closed('<p>Kill criterion: none sold.</p>'))
                with self.assertRaises(ValueError):                     # its Closed rule
                    lq.check(after_lead, closed('<p>no test</p>'))
                listed = ('<article id="l" data-kind="research" data-route="step"><ul><li data-idea="ok-one">{} '
                          '<strong>Follow-up.</strong> Closed: done.</li></ul></article>')
                lq.check(after_lead, notebook([self.rev, research(self.q[0], 'Closed'),
                                               listed.format('Kill criterion: none.')], ideas[1:], attrs=attrs))
                with self.assertRaises(ValueError):                     # also when a follow-up list closes it
                    lq.check(after_lead, notebook([self.rev, research(self.q[0], 'Closed'), listed.format('no')],
                                                  ideas[1:], attrs=attrs))
                reopen = ('<article id="r" data-kind="research" data-route="step"><ul><li data-idea="ok-one">x '
                          '<strong>Follow-up.</strong> Reopened: early.</li></ul></article>')
                idea_closed = closed('<p>Kill criterion: none sold.</p>')
                reopened = idea_closed.replace('</article></section>', '</article>' + reopen + '</section>').replace(
                    '<li data-idea="ok-two">ok-two</li>', '<li data-idea="ok-two">ok-two</li><li data-idea="ok-one">ok-one</li>')
                with self.assertRaises(ValueError):                     # not reopened by a follow-up
                    lq.check(idea_closed, reopened)
                lq.check(None, notebook([self.rev], self.q))           # the defaults return without the attribute
                self.assertIs(lq.KINDS['idea'], lq.BUILTIN['idea'])
            finally:
                sys.path.remove(tmp)
                sys.modules.pop('fake_kinds', None)

    def test_a_kind_module_may_name_entries_that_do_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'titled_reviews.py').write_text(
                'def kinds(lq):\n    return []\n'
                'def uncounted(tag, text):\n    return "Review:" in text\n')
            sys.path.insert(0, tmp)
            try:
                attrs = ' data-kind-modules="titled_reviews" data-counted="research survey"'
                big = review('r1', [PASS] * lq.CAP)
                queue = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
                head = notebook([big], queue, draining=True, attrs=attrs)
                entry = lambda title: ('<article id="b" data-kind="survey" data-route="step"><h3>3 October 2026 '
                                       f'&mdash; {title}</h3></article>')
                lq.check(head, notebook([big, entry('Review: where things stand')], queue, draining=True,
                                        attrs=attrs))                    # a review need not develop the head
                with self.assertRaises(ValueError):                     # another survey entry must
                    lq.check(head, notebook([big, entry('A cycle')], queue, draining=True, attrs=attrs))
                cont = developing(queue[0], 'Continuing').replace('data-kind="research"', 'data-kind="survey"')
                titled = cont.replace('<p>', '<h3>Review: x</h3><p>', 1)
                self.assertEqual(lq.spell(notebook([big, cont, titled, cont], queue, attrs=attrs), queue[0]), 2)
                lq.configure('')
                self.assertEqual(lq.SETTINGS['uncounted'], [])          # the next notebook starts afresh
            finally:
                sys.path.remove(tmp)
                sys.modules.pop('titled_reviews', None)

    def test_a_commit_changing_the_section_settings_reads_head_under_the_new_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'idea_kinds.py').write_text('def kinds(lq):\n    return [lq.Kind("idea")]\n')
            sys.path.insert(0, tmp)
            try:
                section = '<section id="lead-queue"{}><ol><li data-idea="one">one</li></ol></section>'
                old = ROUTE + section.format(' data-items="ideas"') + '<section id="research-record"></section>'
                new = ROUTE + section.format(' data-kind-modules="idea_kinds"') + '<section id="research-record"></section>'
                lq.check(old, new)
                with self.assertRaises(ValueError):                     # the items themselves may not change
                    lq.check(old, new.replace('data-idea="one">one', 'data-idea="two">two'))
            finally:
                sys.path.remove(tmp)
                sys.modules.pop('idea_kinds', None)

    def test_a_kind_with_its_own_admit_in_a_new_queue_and_its_head_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'own_kinds.py').write_text(
                'def kinds(lq):\n'
                '    return [lq.Kind("idea", admit=lambda body, head, item: [] if item[1] != "bad" else ["no"])]\n')
            sys.path.insert(0, tmp)
            try:
                section = '<section id="lead-queue" data-kind-modules="own_kinds"{}><ol>{}</ol></section>'
                def body(ids, flag=''):
                    return (ROUTE + section.format(flag, ''.join(f'<li data-idea="{i}">Sold to x.</li>' for i in ids))
                            + '<section id="research-record">' + self.rev + '</section>')
                with self.assertRaises(ValueError):                     # init seeds the leads, which are missing
                    lq.check(None, body(['one', 'two']))
                seeded = body(['one', 'two']).replace('</ol>', '<li data-lead="r1:1">r1:1</li><li data-lead="r1:2">'
                                                     'r1:2</li></ol>')
                lq.check(None, seeded)                                  # ideas admitted, leads as init seeds them
                with self.assertRaises(ValueError):
                    lq.check(None, seeded.replace('data-idea="two"', 'data-idea="bad"'))
                full = [f'i{n}' for n in range(lq.CAP - 2)]
                many = lambda flag: body(full, flag).replace('</ol>', '<li data-lead="r1:1">r1:1</li><li '
                                                             'data-lead="r1:2">r1:2</li></ol>')
                with self.assertRaises(ValueError):                     # 50 items with the ideas: draining
                    lq.check(None, many(''))
                lq.check(None, many(' data-draining="true"'))
                self.assertEqual(lq.head_lines(seeded, 3)[1:], ['1. one: Sold to x.', '2. two: Sold to x.',
                                                                 '3. r1:1'])
            finally:
                sys.path.remove(tmp)
                sys.modules.pop('own_kinds', None)

    def test_a_notebook_without_its_queue_is_told_inits_options(self):
        with self.assertRaisesRegex(ValueError, '--kind-modules'):
            lq.check(None, notebook([self.rev]))

    def test_check_command_compares_the_staged_notebook_with_a_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=repo,
                                            check=True, capture_output=True)
            git('init', '-q')
            nb = repo / 'notebook.html'
            nb.write_text(notebook([self.rev], self.q))
            git('add', '.')
            git('commit', '-q', '-m', 'one')
            run = lambda *a: subprocess.run([sys.executable, str(ROOT / 'tools/lead_queue.py'), 'check', str(nb), *a],
                                            capture_output=True, text=True).returncode
            nb.write_text(notebook([self.rev, research(self.q[0], 'Closed')], self.q[1:]))
            git('add', '.')
            self.assertEqual(run(), 0)
            nb.write_text(notebook([self.rev, research(self.q[1], 'Closed')], self.q[:1]))
            self.assertEqual(run(), 0)                                  # the working file is not what is checked
            git('add', '.')
            self.assertEqual(run(), 1)
            nb.write_text(notebook([self.rev, research(self.q[0], 'Closed')], self.q[1:]))
            git('add', '.')
            git('commit', '-q', '-m', 'two')
            git('add', '.')
            self.assertEqual(run(), 0)                                  # against HEAD: no new entry, same queue
            nb.write_text(notebook([self.rev, research(self.q[0], 'Closed')], self.q))
            git('add', '.')
            self.assertEqual(run(), 1)                                  # no new entry may not change the queue
            nb.write_text(notebook([self.rev, research(self.q[0], 'Closed')], self.q[1:]))
            git('add', '.')
            self.assertEqual(run('--base', 'HEAD^'), 0)                 # as an amend sees it: HEAD's parent
            self.assertEqual(run('--base', 'nonsense^^'), 3)            # no such base: the check cannot run
            self.assertEqual(subprocess.run([sys.executable, str(ROOT / 'tools/lead_queue.py'), 'nonsense'],
                                            capture_output=True).returncode, 2)

    def test_check_command_finds_the_notebook_under_a_hooks_git_dir(self):
        # a pre-commit hook runs with GIT_DIR set, where git rev-parse --show-toplevel answers the current directory
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=repo,
                                            check=True, capture_output=True)
            git('init', '-q')
            (repo / 'notebook.html').write_text(notebook([self.rev]))      # a root notebook without a queue
            nb = repo / 'branch' / 'notebook.html'
            nb.parent.mkdir()
            nb.write_text(notebook([self.rev], self.q))
            git('add', '.')
            git('commit', '-q', '-m', 'one')
            nb.write_text(notebook([self.rev, research(self.q[0], 'Closed')], self.q[1:]))
            git('add', '.')
            result = subprocess.run([sys.executable, str(ROOT / 'tools/lead_queue.py'), 'check', str(nb)],
                                    capture_output=True, text=True, cwd=repo,
                                    env=dict(os.environ, GIT_DIR=str(repo / '.git')))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_creating_the_queue_without_an_entry_ignores_the_last_entrys_work(self):
        older = research(self.q[0], 'Continuing')                       # an entry already in HEAD
        lq.check(notebook([self.rev, older]), notebook([self.rev, older], self.q))
        with self.assertRaises(ValueError):                             # a new entry still may not develop items
            lq.check(notebook([self.rev]), notebook([self.rev, older], self.q))

    def test_init_writes_the_section_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            nb = Path(tmp, 'notebook.html')
            nb.write_text(notebook([self.rev], route=False))
            code = subprocess.run([sys.executable, str(ROOT / 'tools/lead_queue.py'), 'init', str(nb), '--counted',
                                   'task', '--backpressure', 'off'], capture_output=True).returncode
            self.assertEqual(code, 0)
            body = nb.read_text()
            self.assertIn('<section id="lead-queue" data-counted="task" data-backpressure="off">', body)
            lq.check(None, body)
            self.assertEqual(subprocess.run([sys.executable, str(ROOT / 'tools/lead_queue.py'), 'init', str(nb),
                                             '--backpressure', 'on'], capture_output=True).returncode, 2)
            # seeding uses the new section's settings: a task entry closing a listed check counts there
            listing = subideas('t1', [('check', 'c'), ('check', 'd')])
            closing = developing(('check', 't1:s1'), 'Closed').replace('data-kind="research"', 'data-kind="task"')
            nb.write_text(notebook([self.rev, listing, closing], route=False))
            subprocess.run([sys.executable, str(ROOT / 'tools/lead_queue.py'), 'init', str(nb), '--counted', 'task'],
                           check=True, capture_output=True)
            self.assertEqual(lq.parse(nb.read_text())[1], self.q + [('check', 't1:s2')])
            lq.check(notebook([self.rev, listing, closing], route=False), nb.read_text())

    def test_kind_rules_apply_to_triage_blocks_and_listed_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            listing = subideas('t1', [('check', 'c'), ('check', 'e')])
            queue = [('check', 't1:s1'), ('check', 't1:s2')]
            careful = ' '.join(['checked'] * 85)
            triage = lambda evidence: ('<article id="t" data-kind="research" data-route="step"><h4>Queue triage</h4>'
                                       f'<ul><li data-check="t1:s1">{careful} {evidence} <strong>Follow-up.</strong> '
                                       'Developed: answered.</li></ul></article>')
            head = notebook([listing], queue)
            with self.assertRaisesRegex(ValueError, 'retired'):
                lq.check(head, notebook([listing, triage('<a href="#t1">the listing</a>')], queue[1:]),
                         root / 'nb.html', root)
            with self.assertRaises(ValueError):                         # a link that does not resolve
                lq.check(head, notebook([listing, triage('<a href="#t1">x</a> <a href="#gone">y</a>')], queue[1:]),
                         root / 'nb.html', root)

    def test_malformed_subideas_are_refused(self):
        head = notebook([self.rev], self.q)
        for item in ('<li data-sub="chek">c</li>', '<li>c</li>', '<li data-sub="check" data-parent="r1:2">c</li>',
                     '<li data-sub="check" data-parent="nokind:r1:2">c</li>'):
            entry = ('<article id="m" data-kind="research" data-route="step"><h4>Sub-ideas</h4><ul>' + item
                     + '</ul></article>')
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    lq.check(head, notebook([self.rev, entry], self.q))
                with self.assertRaises(ValueError):
                    lq.append_new(notebook([self.rev, entry], self.q))
        fine = ('<article id="m" data-kind="research" data-route="step"><h4>Sub-ideas</h4><ul><li data-sub="check" '
                'data-parent="lead:r1:2">c</li></ul></article>')
        lq.check(head, notebook([self.rev, fine], [self.q[0], (self.q[1], [('check', 'm:s1')])]))

    def test_append_runs_after_done(self):
        listing = developing(self.q[0], 'Closed', '<h4>Sub-ideas</h4><ul><li data-sub="check">c</li></ul>')
        body = notebook([self.rev, listing], self.q)
        with self.assertRaises(ValueError):                             # the closed item is still queued
            lq.append_new(body)
        after, _ = lq.append_new(lq.done(body, 'Closed'))
        self.assertEqual(lq.shape(lq.parse_tree(after)[1]), [(self.q[1], []), (('check', 'd:s1'), [])])
        lq.check(notebook([self.rev], self.q), after)

    def test_append_applies_a_follow_up_lists_closures(self):
        tree = [self.q[0], (self.q[1], [('check', 'k:s1'), ('check', 'k:s2')])]
        entry = developing(self.q[0], 'Continuing', '<ul><li data-lead="r1:2">no longer bears on anything '
                           '<strong>Follow-up.</strong> Closed: superseded.</li><li data-check="k:s2">still open '
                           '<strong>Follow-up.</strong> Continuing: on its own.</li></ul><h4>Sub-ideas</h4><ul>'
                           '<li data-sub="check">c</li></ul>')
        body, count = lq.append_new(lq.done(notebook([self.rev, entry], tree), 'Continuing'))
        self.assertEqual((count, lq.shape(lq.parse_tree(body)[1])),
                         (1, [(self.q[0], [('check', 'd:s1')]), (('check', 'k:s2'), [])]))
        lq.check(notebook([self.rev], tree), body)
        big = review('r1', [PASS] * lq.CAP)
        queue = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
        closes = developing(queue[0], 'Continuing', '<ul>' + ''.join(
            f'<li data-lead="r1:{n}">x <strong>Follow-up.</strong> Closed: moot.</li>' for n in range(2, 33))
            + '</ul>')
        body, _ = lq.append_new(lq.done(notebook([big, closes], queue, draining=True), 'Continuing'))
        self.assertFalse(lq.parse(body)[0])                             # down to the floor: the flag goes
        lq.check(notebook([big], queue, draining=True), body)

    def test_a_queue_section_cannot_go_away(self):
        with self.assertRaises(ValueError):
            lq.check(notebook([self.rev], self.q, route=False), notebook([self.rev], route=False))

    def test_a_reopened_subidea_no_longer_counts_toward_its_old_parent(self):
        listing = developing(self.q[0], 'Continuing', '<h4>Sub-ideas</h4><ul><li data-sub="check">c</li></ul>')
        closing = developing(('check', 'd:s1'), 'Closed').replace('id="d"', 'id="e"')
        reopen = ('<article id="r" data-kind="research" data-route="step"><ul><li data-check="d:s1">x <strong>'
                  'Follow-up.</strong> Reopened: too early.</li></ul></article>')
        again = developing(('check', 'd:s1'), 'Closed').replace('id="d"', 'id="f"')
        body = notebook([self.rev, listing, closing, reopen, again], self.q)
        self.assertEqual(lq.spell(body, self.q[0]), 0)                  # its own entry ends the parent's run
        self.assertEqual(lq.spell(notebook([self.rev, listing, closing], self.q), self.q[0]), 2)
        # entries before the reopen still count toward the parent it then had
        later = research(self.q[0], 'Continuing')
        self.assertEqual(lq.spell(notebook([self.rev, listing, closing, reopen, later], self.q + [('check', 'd:s1')]),
                                  self.q[0]), 3)
        self.assertEqual(lq.spell(notebook([self.rev, listing, closing, reopen, later], self.q), self.q[0]), 3)

    def test_a_parent_developed_with_its_last_subideas_closed_in_the_same_entry(self):
        tree = [(self.q[0], [('check', 'k:s1')]), (self.q[1], [])]
        entry = ('<article data-kind="research" data-route="step" data-lead="r1:1"><ul><li data-check="k:s1">done '
                 'with it <strong>Follow-up.</strong> Closed: moot.</li></ul><p><strong>Follow-up.</strong> '
                 'Developed: x.</p></article>')
        lq.check(notebook([self.rev], tree), notebook([self.rev, entry], [self.q[1]]))

    def test_head_lines(self):
        lines = lq.head_lines(notebook([self.rev], self.q))
        self.assertIn('2 items', lines[0])
        self.assertEqual(len(lines), 3)



class LinkEarlierWorkTest(unittest.TestCase):
    """An entry on a queue item links the latest earlier entry on that item's group."""

    def setUp(self):
        lq.configure('')    # the module's settings are whatever the worker's last test left: start from the defaults

    def entry(self, ident, item, body=''):
        return (f'<article id="{ident}" data-kind="research" data-route="step" data-{item[0]}="{item[1]}">{body}'
                '<p><strong>Follow-up.</strong> Continuing: x.</p></article>')

    def unlinked(self, articles, queue, item):
        body = notebook(articles, queue)
        return lq.unlinked_earlier_entry(body, lq.parse_tree(body)[1], lq.record_articles(body), item)

    def test_status_lists_every_attempt_the_item_s_follow_ups_named(self):
        item = ('lead', 'r:1')
        first = ('<article id="entry-2026-10-09-a" data-kind="research" data-route="step" data-lead="r:1">'
                 '<p><strong>Follow-up.</strong> Continuing. Next attempt on it: read the proof of the bound.</p>'
                 '</article>')
        second = ('<article id="entry-2026-10-11-b" data-kind="research" data-route="step" data-lead="r:1">'
                  '<p><strong>Owed attempt.</strong> The construction came first, for the reason given below.</p>'
                  '<p><strong>Follow-up.</strong> Continuing: a count. Next attempt: the complex. Still owed '
                  'from 9 October: the proof of the bound.</p></article>')
        third = self.entry('entry-2026-10-11-c', item)
        body = notebook([first, second, third], [item])
        rows = lq.named_attempts(body, 'r:1')
        self.assertEqual([(anchor, owed) for anchor, _said, owed in rows],         # b answers a; nothing answers b
                         [('entry-2026-10-09-a', True), ('entry-2026-10-11-b', False)])
        self.assertEqual(rows[1][1], ['Next attempt: the complex.', 'Still owed from 9 October: the proof of '
                                      'the bound.'])
        status = '\n'.join(lq.item_status(body, 'r:1'))
        self.assertIn('#entry-2026-10-09-a: Next attempt on it: read the proof', status)
        self.assertIn('#entry-2026-10-11-b [no later entry has an Owed attempt paragraph]: Next attempt: the '
                      'complex. Still owed', status)
        self.assertIn('  none', '\n'.join(lq.item_status(notebook([third], [item]), 'r:1')))

    def test_survey_gives_one_row_for_each_top_level_item(self):
        worked, idle = ('lead', 'r:1'), ('lead', 'r:2')
        named = ('<article id="entry-2026-10-11-a" data-kind="research" data-route="step" data-lead="r:1">'
                 '<p><strong>Follow-up.</strong> Continuing. Next attempt: read the source.</p></article>')
        body = notebook([named], [worked, idle])
        self.assertEqual(lq.survey(body), [('lead', 'r:1', 1, 0, 'Continuing', True, 1),
                                           ('lead', 'r:2', 0, 0, 'none', False, 0)])
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'n.html'
            path.write_text(body)
            with contextlib.redirect_stdout(output):
                self.assertEqual(lq.main(['lead_queue.py', 'survey', str(path)]), 0)
        self.assertIn('2 items: 1 with no entry; 0 with entries, no open sub-idea and no attempt named',
                      output.getvalue())

    def test_an_entry_accounts_for_the_attempt_its_item_s_last_entry_named(self):
        item, other = ('check', 'e:s1'), ('lead', 'r:2')
        named = ('<article id="entry-2026-10-11-a" data-kind="research" data-check="e:s1"><p><strong>Follow-up.'
                 '</strong> Continuing. Next attempt on the item: read the source.</p></article>')
        said = '<p><strong>Owed attempt.</strong> The reading was made; its outcome is the table above.</p>'
        late = lambda body='': self.entry('entry-2026-10-11-b', item, body)
        articles = lambda *entries: lq.record_articles(notebook(list(entries), [item, other]))
        self.assertEqual(lq.unaccounted_attempt(articles(named, late()), item), 'entry-2026-10-11-a')
        self.assertIsNone(lq.unaccounted_attempt(articles(named, late(said)), item))
        self.assertEqual(lq.unaccounted_attempt(
            articles(named, late('<p><strong>Owed attempt.</strong> None.</p>')), item), 'entry-2026-10-11-a')
        quiet = self.entry('entry-2026-10-11-a', item)                   # its follow-up names no attempt
        self.assertIsNone(lq.unaccounted_attempt(articles(quiet, late()), item))
        self.assertIsNone(lq.unaccounted_attempt(articles(named, late()), other))        # another item's entry
        old = self.entry('entry-2026-10-10-b', item)                     # older entries are not retrofitted
        self.assertIsNone(lq.unaccounted_attempt(articles(named, old), item))

    def test_an_entry_on_an_item_the_last_review_left_says_why_it_returns(self):
        item, other = ('check', 'e:s1'), ('lead', 'r:2')
        review = lambda left: (f'<article id="entry-2026-10-11-r" data-kind="review" data-route="step"'
                               f' data-left-items="{left}"><p>Decision.</p></article>')
        late = lambda body='': self.entry('entry-2026-10-11-b', item, body)
        said = '<p><strong>Returns.</strong> The review left it for a block; the block has ended and it is owed.</p>'
        run = lambda *entries: lq.left_by_last_review(
            *(lambda body: (body, lq.parse_tree(body)[1], lq.record_articles(body)))(
                notebook(list(entries), [item, other])), item)
        self.assertEqual(run(review('e:s1 x:s2'), late()), 'entry-2026-10-11-r')
        self.assertIsNone(run(review('e:s1 x:s2'), late(said)))
        self.assertEqual(run(review('e:s1'), late('<p><strong>Returns.</strong> Owed.</p>')), 'entry-2026-10-11-r')
        self.assertIsNone(run(review('x:s2'), late()))                    # the review left another item
        self.assertIsNone(run(late()))                                     # no review before the entry
        self.assertIsNone(run(review('e:s1'), review(''), late()))         # only the last review counts
        elsewhere = review('e:s1').replace('data-route="step"', 'data-route="other"')
        self.assertIsNone(run(elsewhere, late()))                          # a review of another route
        head = notebook([review('e:s1')], [item, other])
        with self.assertRaisesRegex(ValueError, 'data-left-items'):
            lq.check(head, notebook([review('e:s1'), late()], [item, other]))
        lq.check(head, notebook([review('e:s1'), late(said)], [item, other]))      # the exemption, through check
        parent, child = ('lead', 'r:1'), ('check', 'e:s1')                 # a sub-idea of a left item
        nested = [(parent, [child]), other]
        on_child = lambda body='': self.entry('entry-2026-10-11-b', child, body)
        tree = notebook([review('r:1'), on_child()], nested)
        self.assertEqual(lq.left_by_last_review(tree, lq.parse_tree(tree)[1], lq.record_articles(tree), child),
                         'entry-2026-10-11-r')
        with self.assertRaisesRegex(ValueError, 'not queued: r:9'):        # a mistyped identifier leaves nothing
            lq.check(None, notebook([review('e:s1 r:9')], [item, other]))

    def test_status_uses_latest_group_entry_and_resets_only_after_other_work(self):
        parent, child, other = ('lead', 'r:1'), ('check', 'e:s1'), ('lead', 'r:2')
        queue = [(parent, [child]), other]
        entries = [self.entry(f'entry-2026-10-10-{i}', parent) for i in range(3)]
        entries += [self.entry('entry-2026-10-10-later', child)]
        body = notebook(entries, queue)
        status = '\n'.join(lq.item_status(body, child[1]))
        self.assertIn('group: lead:r:1', status)
        self.assertIn('Latest development: #entry-2026-10-10-later (Continuing)', status)
        self.assertIn('Current spell: 4; boundary: 4.', status)
        self.assertNotIn('the spell restarted', status)
        self.assertIn('Boundary reached:', status)
        self.assertIn('Open sub-ideas: e:s1', status)
        self.assertIn('Result files its entries link (read what was computed before computing again): none', status)
        linked = [self.entry('entry-2026-10-10-0', parent,
                             '<a href="research/results/a/control.py">script</a> <a href="research/results/a/out.txt">'
                             'output</a> <a href="research/results/a/review.txt">review</a> '
                             '<a href="research/results/a/timing.html">timing</a>'),
                  self.entry('entry-2026-10-10-x', other, '<a href="research/results/b/other.py">another item</a>'),
                  self.entry('entry-2026-10-10-later', child, '<a href="research/results/a/control.py">again</a>')]
        self.assertEqual(lq.result_files(notebook(linked, queue), child[1]),
                         ['research/results/a/control.py', 'research/results/a/out.txt'])
        extended = entries[:-1] + [entries[-1].replace('<article ', '<article data-spell-extend="2" ')]
        status = '\n'.join(lq.item_status(notebook(extended, queue), child[1]))
        self.assertIn('Current spell: 4; boundary: 6.', status)
        self.assertIn('Next development would be entry 5.', status)
        override = ('<article id="override" data-kind="audit" data-picked="user" '
                    'data-spell-limit="none" data-spell-item="lead:r:1">'
                    '<p><strong>Picked.</strong> "No hard cycle limit."</p></article>')
        self.assertIn('boundary: unlimited.', '\n'.join(lq.item_status(
            notebook(entries + [override], queue), parent[1])))
        entries += [review('review', [PASS]), self.entry('entry-2026-10-11-other', other)]
        status = '\n'.join(lq.item_status(notebook(entries, queue), parent[1]))
        self.assertIn('Latest development: #entry-2026-10-10-later', status)
        self.assertIn('Current spell: 0; boundary: 4.', status)
        self.assertIn('the spell restarted after entries on other items', status)   # the lifetime count shows it
        self.assertIn('Next development would be entry 1.', status)
        entries += [self.entry('entry-2026-10-11-return', parent)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'notebook.html'
            path.write_text(notebook(entries, queue))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(lq.main(['lead_queue.py', 'history', str(path), child[1], '--status']), 0)
            self.assertIn('Latest development: #entry-2026-10-11-return', output.getvalue())
            self.assertIn('Current spell: 1; boundary: 4.', output.getvalue())

    def test_status_requires_queued_item_and_reports_an_unused_one(self):
        body = notebook([], [('lead', 'r:1')])
        status = '\n'.join(lq.item_status(body, 'r:1'))
        self.assertIn('Latest development: none', status)
        self.assertIn('Open sub-ideas: none', status)
        one = notebook([self.entry('entry-2026-10-11-only', ('lead', 'r:1'))], [('lead', 'r:1')])
        self.assertIn('Latest development: #entry-2026-10-11-only (Continuing)',
                      '\n'.join(lq.item_status(one, 'r:1')))
        with self.assertRaisesRegex(ValueError, 'Expected one queued item r:1; found 0'):
            lq.item_status(notebook([], None), 'r:1')
        with self.assertRaisesRegex(ValueError, 'Expected one queued item missing; found 0'):
            lq.item_status(body, 'missing')

    def test_a_lead_and_a_bridge_of_one_identifier_are_told_apart_by_kind(self):
        entries = [self.entry('entry-2026-10-11-on-lead', ('lead', 'r:1')),
                   self.entry('entry-2026-10-11-on-bridge', ('bridge', 'r:1'))]
        both = notebook(entries, [('lead', 'r:1'), ('bridge', 'r:1')])
        with self.assertRaisesRegex(ValueError, '2 queued items share the identifier r:1; name one by its kind: '
                                                'lead:r:1, bridge:r:1'):
            lq.item_status(both, 'r:1')
        lead, bridge = '\n'.join(lq.item_status(both, 'lead:r:1')), '\n'.join(lq.item_status(both, 'bridge:r:1'))
        self.assertIn('Item: lead:r:1', lead)
        self.assertIn('Latest development: #entry-2026-10-11-on-lead', lead)
        self.assertIn('Item: bridge:r:1', bridge)
        self.assertIn('Latest development: #entry-2026-10-11-on-bridge', bridge)
        self.assertIn('Entries on it in all: 1.', bridge)             # not the lead's count: 13 for 1 on the real queue
        self.assertEqual([anchor for anchor, _, _ in lq.history(both, 'bridge:r:1')], ['entry-2026-10-11-on-bridge'])
        with self.assertRaisesRegex(ValueError, '2 queued items share the identifier r:1'):
            lq.history(both, 'r:1')                                   # never the first match unsaid
        self.assertEqual([(kind, count) for kind, _, count, *_ in lq.survey(both)], [('lead', 1), ('bridge', 1)])
        # An unshared identifier takes the prefix too, and the bare form still works.
        one = notebook(entries[:1], [('lead', 'r:1')])
        self.assertEqual(lq.item_status(one, 'lead:r:1'), lq.item_status(one, 'r:1'))

    def test_the_latest_earlier_entry_of_the_group_is_linked(self):
        parent, child, sibling, other = ('lead', 'r:1'), ('check', 'e:s1'), ('check', 'e:s2'), ('lead', 'r:2')
        queue = [(parent, [child, sibling]), other]
        between = [self.entry('entry-2026-10-10-old', parent), self.entry('entry-2026-10-10-sib', sibling)]
        self.assertEqual(self.unlinked(between + [self.entry('entry-2026-10-11-new', child)], queue, child),
                         'entry-2026-10-10-old')                                   # a sibling's entry is not it
        old = self.entry('entry-2026-10-10-old', parent)
        self.assertEqual(self.unlinked([old, self.entry('entry-2026-10-11-new', child)], queue, child),
                         'entry-2026-10-10-old')                                   # the child's group is the parent's
        linked = self.entry('entry-2026-10-11-new', child, '<a href="#entry-2026-10-10-old">earlier</a>')
        self.assertIsNone(self.unlinked([old, linked], queue, child))
        self.assertIsNone(self.unlinked([old, self.entry('entry-2026-10-11-new', other)], queue, other))
        self.assertIsNone(self.unlinked([old, self.entry('entry-2026-10-10-late', child)], queue, child))  # older date
        self.assertEqual([r[:2] for r in lq.history(notebook(between, queue), 'e:s1')],          # the whole group
                         [('entry-2026-10-10-old', 'r:1'), ('entry-2026-10-10-sib', 'e:s2')])
        self.assertEqual(lq.history(notebook(between, queue), 'r:2'), [])
        with self.assertRaisesRegex(ValueError, 'link that entry'):
            lq.check(None, notebook([old, self.entry('entry-2026-10-11-new', child)], queue))


class OpenSubideaOutcomesTest(unittest.TestCase):
    """An entry on an item gives an outcome for every other open sub-idea of that item's parent."""

    def entry(self, ident, item, body=''):
        return (f'<article id="{ident}" data-kind="research" data-route="step" data-{item[0]}="{item[1]}">{body}'
                '<p><strong>Follow-up.</strong> Continuing: x.</p></article>')

    def test_silent_subideas_are_named(self):
        parent, one, two = ('lead', 'r:1'), ('check', 'e:s1'), ('check', 'e:s2')
        nodes = lq.parse_tree(notebook([], [(parent, [one, two])]))[1]
        tag = '<article id="entry-2026-10-11-new" data-kind="research" data-check="e:s1">'
        self.assertEqual(lq.unstated_subideas(tag, tag + 'text', one, nodes), ['e:s2'])
        self.assertEqual(lq.unstated_subideas(tag, tag + 'text', parent, nodes), ['e:s1', 'e:s2'])
        said = tag + '<ul><li data-check="e:s2">The other. <strong>Follow-up.</strong> Continuing: waits.</li></ul>'
        self.assertEqual(lq.unstated_subideas(tag, said, one, nodes), [])
        quoted = tag + '<ul><li data-check="e:s2">The other, no outcome.</li></ul>'
        self.assertEqual(lq.unstated_subideas(tag, quoted, one, nodes), ['e:s2'])
        old = tag.replace('2026-10-11', '2026-10-10')                              # older entries are not retrofitted
        self.assertEqual(lq.unstated_subideas(old, old + 'text', one, nodes), [])
        self.assertEqual(lq.unstated_subideas(tag, tag + 'text', ('lead', 'r:9'), nodes), [])

    def test_the_check_refuses_a_silent_entry(self):
        parent, one, two = ('lead', 'r:1'), ('check', 'e:s1'), ('check', 'e:s2')
        queue = [(parent, [one, two])]
        head = notebook([], queue)
        with self.assertRaisesRegex(ValueError, 'e:s2'):
            lq.check(head, notebook([self.entry('entry-2026-10-11-new', one)], queue))


class QueueTrendTest(unittest.TestCase):
    """A review of a draining queue records its count; the guidance shows the trend and the run without bearing."""

    def review(self, ident, count=None):
        attr = '' if count is None else f' data-queue-items="{count}"'
        return f'<article id="{ident}" data-kind="review" data-route="step"{attr}><p>Assess.</p></article>'

    def test_a_draining_review_declares_the_count(self):
        queue = [('lead', 'r:1'), ('lead', 'r:2')]
        nodes = lq.parse_tree(notebook([], queue, draining=True))[1]
        tag = '<article id="entry-2026-10-12-review" data-kind="review">'
        self.assertEqual(lq.undeclared_review_count(tag, True, nodes), 2)
        self.assertEqual(lq.undeclared_review_count(tag.replace('>', ' data-queue-items="3">'), True, nodes), 2)
        self.assertIsNone(lq.undeclared_review_count(tag.replace('>', ' data-queue-items="2">'), True, nodes))
        self.assertIsNone(lq.undeclared_review_count(tag, False, nodes))                      # not draining
        self.assertIsNone(lq.undeclared_review_count(tag.replace('review"', 'research"'), True, nodes))
        self.assertIsNone(lq.undeclared_review_count('<article id="old" data-kind="review">', True, nodes))
        with self.assertRaisesRegex(ValueError, 'data-queue-items="2"'):
            lq.check(notebook([], queue, draining=True),
                     notebook([self.review('entry-2026-10-12-review')], queue, draining=True))

    def test_guidance_prints_the_trend_and_the_run(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('turn_guidance', ROOT / 'tools/turn_guidance.py')
        guide = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guide)
        queue = [('lead', 'r:1'), ('lead', 'r:2')]
        self.assertIn('no review has recorded', guide.queue_trend_notes(notebook([], queue, draining=True))[0])
        self.assertEqual(guide.queue_trend_notes(notebook([], queue)), [])                      # not draining
        body = notebook([self.review('entry-a', 5), self.review('entry-b', 2)], queue, draining=True)
        note = guide.queue_trend_notes(body)[0]
        self.assertIn('5 at #entry-a, 2 at #entry-b', note)
        self.assertIn('not shrunk', note)
        self.assertIn('shrinking', guide.queue_trend_notes(notebook([self.review('entry-a', 5)], queue, draining=True))[0])
        none = '<article id="e{}" data-kind="research" data-route="step" data-bearing="none"></article>'
        some = '<article id="s" data-kind="research" data-route="step" data-bearing="some"></article>'
        run = [some] + [none.format(i) for i in range(2)] + [self.review('entry-r')] + [none.format(2)]
        self.assertIn('last 3 research entries', guide.bearing_run_notes(notebook(run, queue))[0])
        self.assertEqual(guide.bearing_run_notes(notebook(run[:3], queue)), [])               # two is below the mark
        self.assertEqual(guide.bearing_run_notes(notebook(run + [some], queue)), [])


class LastItemGuidanceTest(unittest.TestCase):
    def test_start_guidance_counts_the_chosen_items_spell(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('tg', Path(__file__).resolve().parents[1] / 'turn_guidance.py')
        tg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tg)
        lq.configure('')
        rev = review('r1', [PASS, PASS, FAIL])
        queue = [('lead', 'r1:1'), ('lead', 'r1:2')]
        chosen = developing(('lead', 'r1:2'), 'Continuing')
        self.assertEqual(tg.last_item_notes(notebook([rev], queue)), [])
        one = ' '.join(tg.last_item_notes(notebook([rev, chosen], queue)))
        self.assertIn('r1:2, which has had 1 consecutive entries', one)
        full = ' '.join(tg.last_item_notes(notebook([rev] + [chosen] * lq.SPELL, queue)))
        self.assertIn('at its boundary', full)
        head = developing(('lead', 'r1:1'), 'Continuing')
        self.assertEqual(tg.last_item_notes(notebook([rev, head], queue)), [])       # the head has its own line



class BuiltItemsTest(unittest.TestCase):
    ITEM = ('<a href="#x">suite-over-limit</a> (build): Framework: the whole suite ran over its limit with browser '
            'cases slow; find whether the time is the suite own work or other jobs, and fix the measurement.')

    def test_a_commit_message_is_compared_with_the_queued_build_items(self):
        nodes = [lq.Node('build', 'suite-over-limit', '', self.ITEM),
                 lq.Node('lead', 'r:1', '', self.ITEM),                    # the same words in a lead: not a build
                 lq.Node('build', 'other', '', 'x (build): Refuse an entry whose closing paragraph disclaims a part '
                                               'that its reason names, with a count on recorded entries.')]
        message = ('Test runner: measure the suite own work apart from other jobs\n\nA whole suite over its limit '
                   'with slow browser cases says whether the time was other jobs.\ntools/tests/run.py')
        self.assertEqual([ident for _, ident in lq.built_items(nodes, message)], ['suite-over-limit'])
        self.assertEqual(lq.built_items(nodes, 'Riemann notebook: a range bound for clusters'), [])

    def test_the_command_reads_a_framework_commit_and_every_notebook_s_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = lambda *args: subprocess.run(['git', '-C', tmp, *args], check=True, capture_output=True)
            run('init', '-q')
            (root / 'research/branches/side').mkdir(parents=True)
            (root / 'tools').mkdir()
            (root / 'research/branches/side/notebook.html').write_text(
                f'<section id="lead-queue"><ol><li data-build="suite-over-limit">{self.ITEM}</li></ol></section>')
            commit = ['-c', 'user.name=t', '-c', 'user.email=t@example.org', 'commit', '-qm']
            run('add', '-A')
            run(*commit, 'Queue an item')
            (root / 'tools/run.py').write_text('pass\n')
            run('add', '-A')
            run(*commit, 'Test runner: the whole suite over its limit says whether the time is other jobs or the '
                         'suite own work, with the slow browser cases')
            lines = lq.built(root)
            self.assertEqual(len(lines), 1, lines)
            self.assertIn('suite-over-limit of research/branches/side/notebook.html', lines[0])
            (root / 'notes.txt').write_text('the whole suite over its limit: other jobs, slow browser cases, own work\n')
            run('add', '-A')
            run(*commit, 'Notes: the whole suite over its limit, other jobs or the suite own work, browser cases')
            self.assertEqual(lq.built(root), [])                           # not a framework commit
            queued = ('<a href="#y">refuse-unsized</a> (build): Launcher: refuse a long computation that names no '
                      'sizing run, with a measured estimate from a smaller completed case.')
            (root / 'research/branches/side/notebook.html').write_text(
                f'<section id="lead-queue"><ol><li data-build="refuse-unsized">{queued}</li></ol></section>')
            (root / 'tools/run.py').write_text('pass  # edited\n')
            run('add', '-A')
            run(*commit, 'Queue: the launcher should refuse a long computation that names no sizing run, with a '
                         'measured estimate from a smaller completed case')
            self.assertEqual(lq.built(root), [])                           # the commit queued the item itself


if __name__ == '__main__':
    unittest.main()
