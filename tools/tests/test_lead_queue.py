import importlib.util
import unittest
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


def notebook(articles, queue=None, draining=False):
    section = ''
    if queue is not None:
        flag = ' data-draining="true"' if draining else ''
        section = (f'<section id="lead-queue"{flag}><ol>'
                   + ''.join(f'<li data-{k}="{i}">{i}</li>' for k, i in queue) + '</ol></section>')
    return ROUTE + section + '<section id="research-record">' + ''.join(articles) + '</section>'


class LeadQueueTest(unittest.TestCase):
    def setUp(self):
        self.rev = review('r1', [PASS, PASS, FAIL])     # two passed leads: r1:1, r1:2
        self.q = [('lead', 'r1:1'), ('lead', 'r1:2')]

    def test_open_items_and_init_order(self):
        self.assertEqual(lq.open_items(notebook([self.rev])), self.q)
        body = notebook([self.rev])
        rendered = lq.render(body, self.q, False)
        self.assertLess(rendered.index('r1:1'), rendered.index('r1:2'))

    def test_missing_section_and_membership(self):
        with self.assertRaises(ValueError):
            lq.check(None, notebook([self.rev]))
        with self.assertRaises(ValueError):
            lq.check(None, notebook([self.rev], self.q[:1]))           # an open item is missing
        lq.check(None, notebook([self.rev], self.q))

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
            self.assertEqual(lq.parse(lq.done(before, 'Continuing'))[1], want)                    # before append
            appended = notebook(after_entry[:-1] + [cont.replace('</article>', '<!-- TIMING t --></article>')],
                                self.q)
            self.assertEqual(lq.parse(lq.done(appended, 'Continuing'))[1], want)                  # after append
        broken = notebook([self.rev, cont, research(self.q[1], 'Closed'), cont, cont], self.q)
        self.assertEqual(lq.spell(broken, self.q[0]), 2)                 # another item's entry ends the run

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

    def test_item_text_never_cuts_inline_math(self):
        long = review('r1', [' The ring \\(F[p_2]\\) ' + 'word ' * 40 + '\\(x+y\\) end.' + PASS])
        text = lq.item_text(notebook([long]), 'lead', 'r1:1')
        self.assertEqual(text.count('\\('), text.count('\\)'))

    def test_done_updates_queue_the_way_check_expects(self):
        head = notebook([self.rev], self.q)
        closed = lq.done(head, 'Closed')
        self.assertEqual(lq.parse(closed)[1], self.q[1:])
        kept = lq.done(head, 'Continuing')                              # first of its spell: stays
        self.assertEqual(lq.parse(kept)[1], self.q)
        big = review('r1', [PASS] * (lq.FLOOR + 1))
        queue = [('lead', f'r1:{n}') for n in range(1, lq.FLOOR + 2)]
        draining = notebook([big], queue, draining=True)
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

    def test_triage_batch_settles_a_prefix_with_full_care(self):
        rev = review('r1', [PASS, PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2'), ('lead', 'r1:3')]
        head = notebook([rev], q)
        careful = ' '.join(['checked'] * 85)

        def batch(*items):
            body = ''.join(f'<li data-lead="{i}">{text} <strong>Follow-up.</strong> {outcome}: reason.</li>'
                           for i, outcome, text in items)
            return f'<article id="t" data-kind="research" data-route="step"><h4>Queue triage</h4><ul>{body}</ul></article>'
        good = batch(('r1:1', 'Closed', careful + ' lem:x-y'), ('r1:2', 'Developed', careful + ' <a href="#e">e</a>'))
        after = notebook([rev, good], q)
        body, count = lq.settle_triage(after)
        self.assertEqual((count, lq.parse(body)[1]), (2, q[2:]))
        lq.check(head, body)
        for bad, why in [(batch(('r1:2', 'Closed', careful + ' lem:x-y')), 'not the head'),
                         (batch(('r1:1', 'Continuing', careful + ' lem:x-y')), 'Continuing is not batched'),
                         (batch(('r1:1', 'Closed', 'too short lem:x-y')), 'too short'),
                         (batch(('r1:1', 'Closed', careful)), 'no evidence')]:
            with self.subTest(why=why), self.assertRaises(ValueError):
                lq.check(head, notebook([rev, bad], q[1:]))

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

    def test_head_lines(self):
        lines = lq.head_lines(notebook([self.rev], self.q))
        self.assertIn('2 items', lines[0])
        self.assertEqual(len(lines), 3)


if __name__ == '__main__':
    unittest.main()
