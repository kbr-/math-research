import importlib.util
import json
import os
import subprocess
import sys
import tempfile
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

    def test_check_and_build_need_resolving_evidence_to_be_developed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'research/results').mkdir(parents=True)
            (root / 'research/results/out.txt').write_text('answer')
            (root / 'tasks/arm-check').mkdir(parents=True)
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
            lq.check(build_head, built('<a href="tasks/arm-check/">task</a>'), nb, root)
            lq.check(build_head, built('<a href="research/results/out.txt">built</a>'), nb, root)
            github = 'https://github.com/kbr-/math-research/blob/main/'     # the notebooks' file links
            lq.check(build_head, built(f'<a href="{github}research/results/out.txt">built</a>'), nb, root)
            for body in ('<a href="#t1">an anchor is no build</a>', 'lem:known', '<a href="tasks/none/">x</a>',
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
        after = notebook([self.rev, keep], [self.q[1], ('build', 'k:s2')])
        lq.check(before, after)
        self.assertEqual(lq.parse(lq.done(notebook([self.rev, keep], tree), 'Closed'))[1], [self.q[1], ('build', 'k:s2')])

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

    def test_a_waiting_task_request_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tasks/x').mkdir(parents=True)
            (root / 'tasks/x/task.json').write_text(json.dumps({'requests': [{'number': 3}]}))
            (root / 'tasks/x/USER_REQUESTS.md').write_text('3. a request')
            (root / 'tasks/z').mkdir()
            (root / 'tasks/z/task.json').write_text(json.dumps({'requests': [{'number': 3}]}))

            def wait(n):
                return (f'<article id="w" data-kind="research" data-route="step"><ul><li data-lead="r1:1">x <strong>'
                        f'Follow-up.</strong> Waiting: <a href="tasks/x/USER_REQUESTS.md">item {n}</a>.</li></ul>'
                        '</article>')
            head = notebook([self.rev], self.q)
            body, _ = lq.append_new(notebook([self.rev, wait(3)], self.q))
            lq.check(head, body, root / 'notebook.html', root)
            body, _ = lq.append_new(notebook([self.rev, wait(4)], self.q))
            with self.assertRaises(ValueError):
                lq.check(head, body, root / 'notebook.html', root)
            for broken in (wait(3).replace('item 3', 'request 3'),                     # no "item N"
                           wait(3).replace('tasks/x/', 'tasks/z/')):                   # the link does not resolve
                with self.subTest(broken=broken), self.assertRaises(ValueError):
                    lq.check(head, lq.append_new(notebook([self.rev, broken], self.q))[0], root / 'notebook.html',
                             root)

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
                attrs = ' data-kind-modules="fake_kinds" data-counted="research business"'
                ideas = [('idea', 'ok-one'), ('idea', 'ok-two')]
                head = notebook([self.rev], [self.q[0]] + ideas, attrs=attrs)
                lq.check(head, notebook([self.rev, research()], [self.q[0]] + ideas + [('idea', 'ok-three')], attrs=attrs))
                with self.assertRaises(ValueError):                     # the module refuses it
                    lq.check(head, notebook([self.rev, research()], [self.q[0]] + ideas + [('idea', 'bad')], attrs=attrs))
                closed = lambda body: notebook([self.rev, research(self.q[0], 'Closed'),
                                                developing(ideas[0], 'Closed', body).replace('data-kind="research"',
                                                                                           'data-kind="business"')],
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
                self.assertNotIn('idea', lq.KINDS)
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
                attrs = ' data-kind-modules="titled_reviews" data-counted="research business"'
                big = review('r1', [PASS] * lq.CAP)
                queue = [('lead', f'r1:{n}') for n in range(1, lq.CAP + 1)]
                head = notebook([big], queue, draining=True, attrs=attrs)
                entry = lambda title: ('<article id="b" data-kind="business" data-route="step"><h3>3 October 2026 '
                                       f'&mdash; {title}</h3></article>')
                lq.check(head, notebook([big, entry('Review: where things stand')], queue, draining=True,
                                        attrs=attrs))                    # a review need not develop the head
                with self.assertRaises(ValueError):                     # another business entry must
                    lq.check(head, notebook([big, entry('A cycle')], queue, draining=True, attrs=attrs))
                cont = developing(queue[0], 'Continuing').replace('data-kind="research"', 'data-kind="business"')
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


if __name__ == '__main__':
    unittest.main()
