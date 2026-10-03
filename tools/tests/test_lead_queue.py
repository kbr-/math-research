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
        lq.check(head, notebook([self.rev, research(self.q[0], 'Continuing')], self.q[::-1]))   # to the tail
        with self.assertRaises(ValueError):                             # Continuing stays at the head
            lq.check(head, notebook([self.rev, research(self.q[0], 'Continuing')], self.q))
        with self.assertRaises(ValueError):                             # Closed but still listed
            lq.check(head, notebook([self.rev, research(self.q[0], 'Closed')], self.q))

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
        moved = lq.done(head, 'Continuing')
        self.assertEqual(lq.parse(moved)[1], self.q[::-1])
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

    def test_head_lines(self):
        lines = lq.head_lines(notebook([self.rev], self.q))
        self.assertIn('2 items', lines[0])
        self.assertEqual(len(lines), 3)


if __name__ == '__main__':
    unittest.main()
