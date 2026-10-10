import contextlib
import datetime
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import record_audit  # noqa: E402

_spec = importlib.util.spec_from_file_location('record_audit_cli', TOOLS / 'record-audit.py')
CLI = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CLI)


def entry(anchor, body, kind='business'):
    return f'<article class="research-entry" id="{anchor}" data-kind="{kind}">{body}</article>\n'


def follow(kind, key, name, text):
    return f'<li data-{kind}="{key}">{name}. <strong>Follow-up.</strong> {text}</li>'


class CarriedItemsTest(unittest.TestCase):
    def test_earlier_work_shows_behind_a_later_no_work_line(self):
        # The case that prompted it: a lead developed earlier read "no work" in the latest list.
        text = (entry('r1', '<ul>' + follow('lead', 'r0:1', 'Klein', 'Developed: checked the hand test.')
                      + follow('lead', 'r0:2', 'Rogers', 'Continuing: no work on it this cycle.') + '</ul>')
                + entry('r2', '<ul>' + follow('lead', 'r0:1', 'Klein', 'Continuing: no work on it this cycle.')
                        + follow('lead', 'r0:2', 'Rogers', 'Continuing: no work on it this cycle.')
                        + follow('bridge', 'r1:1', 'Edges', 'Developed: one use.') + '</ul>'))
        rows = {key: last for _, key, _, last in record_audit.carried_items(text)}
        self.assertEqual(rows['r0:1'], 'Developed: checked the hand test.')
        self.assertEqual(rows['r0:2'], '')
        self.assertEqual(rows['r1:1'], 'Developed: one use.')

    def test_an_entry_tagged_with_the_lead_counts_as_work(self):
        # Launch-site monitoring was developed by an entry tagged data-lead, not by a follow-up.
        text = (entry('r1', '<ul>' + follow('lead', 'r0:3', 'Monitoring', 'Continuing: no work on it this cycle.') + '</ul>')
                + '<article class="research-entry" id="watch" data-kind="business" data-lead="r0:3"><p>Searched.</p></article>\n'
                + entry('r2', '<ul>' + follow('lead', 'r0:3', 'Monitoring', 'Continuing: no work on it this cycle.') + '</ul>'))
        self.assertEqual(record_audit.carried_items(text)[0][3], 'Developed in watch.')

    def test_items_dropped_from_the_latest_list_are_not_reported(self):
        text = (entry('r1', '<ul>' + follow('lead', 'old:1', 'Closed one', 'Closed: done.') + '</ul>')
                + entry('r2', '<ul>' + follow('lead', 'new:1', 'New', 'Continuing: no work on it this cycle.') + '</ul>'))
        self.assertEqual([key for _, key, _, _ in record_audit.carried_items(text)], ['new:1'])


class OpenGapsTest(unittest.TestCase):
    def test_unlinked_gap_is_listed_with_the_later_entry_that_did_it(self):
        # The case that prompted it: practice assurance was done by an entry that never linked back.
        text = (entry('a', '<p><strong>Remaining gap.</strong> Next, accountancy practice assurance reviews.</p>')
                + entry('b', '<h3>Accountancy practice assurance reviews</h3><p>Done.</p>')
                + entry('c', '<p><strong>Remaining gap.</strong> None.</p>'))
        self.assertEqual(record_audit.open_gaps(text), [('a', 'Next, accountancy practice assurance reviews.', 'b')])

    def test_a_gap_linked_by_a_later_entry_is_closed(self):
        text = (entry('a', '<p><strong>Remaining gap.</strong> Next, the radon maps.</p>')
                + entry('b', '<p>Radon, as <a href="#a">asked</a>.</p>'))
        self.assertEqual(record_audit.open_gaps(text), [])

    def test_a_link_from_a_task_entry_closes_a_business_gap(self):
        text = (entry('a', '<p><strong>Remaining gap.</strong> Next, the order fixed.</p>')
                + entry('b', '<p>Fixed, as <a href="#a">found</a>.</p>', kind='task'))
        self.assertEqual(record_audit.open_gaps(text), [])

    def test_not_run_items_are_listed_with_their_reason_and_the_later_entry_on_them(self):
        text = ('<article class="research-entry" id="r1" data-kind="business"><h3>Review</h3>'
                '<h4>Outside leads</h4><ol><li>Kish, the sampling frame. <strong>Answers.</strong> x. '
                '<strong>Test.</strong> Passed: listed.</li>'
                '<li>Sarasvathy, effectuation (2001): means at hand. <strong>Answers.</strong> y. '
                '<strong>Test.</strong> Not run: each pipeline needs a rival read.</li></ol>'
                '<h4>Absurd bridges</h4><ol><li>Aviation, a check. <strong>Test.</strong> Passed.</li></ol></article>'
                '<article class="research-entry" id="e2" data-kind="business"><h3>Effectuation developed</h3>'
                '<p>Sarasvathy\'s effectuation, run.</p></article>')
        rows = record_audit.not_run(text)
        self.assertEqual([(k, s, n, r[:7], later) for k, s, n, r, later, _ in rows],
                         [('r1:2', 'Outside leads', 'Sarasvathy, effectuation', 'Not run', 'e2')])

    def test_a_later_entry_naming_the_items_proper_nouns_is_shown(self):
        # A bridge run on Pocket's shutdown stayed listed as not run, and the ranked match pointed
        # elsewhere; the run named Pocket, which the item's own reason named too.
        text = ('<article class="research-entry" id="r1" data-kind="business"><h3>Review</h3>'
                '<h4>Absurd bridges</h4><ol><li>Ecology, adaptive radiation. <strong>Test.</strong> '
                'Not run: no shutdown followed through, such as Pocket in 2025.</li></ol></article>'
                '<article class="research-entry" id="e2" data-kind="business"><h3>Radiation of species</h3>'
                '<p>Ecology and adaptive radiation in general.</p></article>'
                '<article class="research-entry" id="e3" data-kind="business"><h3>Orphaned readers</h3>'
                '<p>Mozilla closed Pocket; readers moved to Instapaper.</p></article>')
        [row] = record_audit.not_run(text)
        self.assertEqual(row[5], ['e3'])

    def test_a_later_entry_naming_the_items_own_name_is_shown(self):
        # Christaller's bridge was run as "Christaller's lead" and stayed listed: the ranked match
        # pointed elsewhere, and only nouns after the item's name were matched.
        text = ('<article class="research-entry" id="r1" data-kind="business"><h3>Review</h3>'
                '<h4>Absurd bridges</h4><ol><li>Geography, Christaller\'s central place theory: '
                'small towns go without. <strong>Test.</strong> Not run: a cycle\'s work.</li></ol></article>'
                '<article class="research-entry" id="e2" data-kind="business"><h3>Geography of places</h3>'
                '<p>Central places and small towns in general.</p></article>'
                '<article class="research-entry" id="e3" data-kind="business"><h3>Specialists online</h3>'
                '<p>Christaller\'s lead, run on garden design apps.</p></article>')
        [row] = record_audit.not_run(text)
        self.assertEqual(row[5], ['e3'])

    def test_the_first_date_a_reason_names_is_read(self):
        # Items waiting on a date (the FCC docket's comments, the weekly feeds) were found only by
        # reading every reason; their date now lets --due list them on their day.
        self.assertEqual(record_audit.reason_date('Not run: comments are due on 9 October 2026, so none.'),
                         datetime.date(2026, 10, 9))
        self.assertEqual(record_audit.reason_date('Not run: the RCVS has until June 2027 to publish.'),
                         datetime.date(2027, 6, 1))
        self.assertIsNone(record_audit.reason_date('Not run: it needs your approval.'))

    def test_due_lists_only_items_dated_on_or_before_the_day(self):
        review = ('<article class="research-entry" id="r1" data-kind="business"><h3>Review</h3>'
                  '<h4>Outside leads</h4><ol><li>Docket. <strong>Test.</strong> Not run: due on 9 October 2026.</li>'
                  '<li>Format. <strong>Test.</strong> Not run: until June 2027.</li>'
                  '<li>Blank. <strong>Test.</strong> Not run: needs buyers.</li></ol></article>')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'notebook.html'
            path.write_text(review)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                CLI.main(['not-run', '--due', '2026-10-10', '--notebook', str(path)])
        self.assertIn('Docket', out.getvalue())
        self.assertNotIn('Format', out.getvalue())
        self.assertNotIn('Blank', out.getvalue())
        self.assertIn('dated: 2026-10-09', out.getvalue())

    def test_an_item_an_entry_claims_is_no_longer_listed(self):
        # Items run later without a link back stayed listed; an entry's data-lead or data-bridge
        # naming them, one key or several, now closes them.
        review = ('<article class="research-entry" id="r1" data-kind="business"><h3>Review</h3>'
                  '<h4>Outside leads</h4><ol><li>Kish. <strong>Test.</strong> Not run: later.</li>'
                  '<li>Blank. <strong>Test.</strong> Not run: needs buyers.</li></ol>'
                  '<h4>Absurd bridges</h4><ol><li>Aviation. <strong>Test.</strong> Not run: later.</li></ol></article>')
        closing = ('<article class="research-entry" id="e2" data-kind="business" data-lead="r1:1" '
                   'data-bridge="r1:1 r9:4"><h3>Closed</h3><p>Done.</p></article>')
        self.assertEqual([k for k, s, *_ in record_audit.not_run(review + closing)], ['r1:2'])
        self.assertEqual(len(record_audit.not_run(review)), 3)

    def test_an_item_a_later_follow_up_closed_is_no_longer_listed(self):
        # A bridge closed in a later review's follow-up list ("Closed: answered") stayed listed
        # as Not run two days later; a Continuing follow-up leaves it listed.
        review = ('<article class="research-entry" id="r1" data-kind="business"><h3>Review</h3>'
                  '<h4>Outside leads</h4><ol><li>Kish. <strong>Test.</strong> Not run: later.</li></ol>'
                  '<h4>Absurd bridges</h4><ol><li>Seeding. <strong>Test.</strong> Not run: later.</li></ol></article>')
        later = entry('r2', '<ul>' + follow('bridge', 'r1:1', 'Seeding', 'Developed: found. Closed: answered.')
                      + follow('lead', 'r1:1', 'Kish', 'Continuing: no work on it this cycle.') + '</ul>')
        self.assertEqual([(k, s) for k, s, *_ in record_audit.not_run(review + later)],
                         [('r1:1', 'Outside leads')])

    def test_every_kind_is_read_unless_one_is_asked_for(self):
        text = entry('a', '<p><strong>Remaining gap.</strong> A proof step.</p>', kind='research')
        self.assertEqual(record_audit.open_gaps(text), [('a', 'A proof step.', '')])
        self.assertEqual(record_audit.open_gaps(text, kind='research'), [('a', 'A proof step.', '')])
        self.assertEqual(record_audit.open_gaps(text, kind='review'), [])

    def test_an_article_is_found_whatever_stands_before_its_id(self):
        gap = '<p><strong>Remaining gap.</strong> A proof step.</p>'
        text = (f'<article class="research-entry" id="a" data-kind="research">{gap}</article>\n'
                f'<article id="b" data-kind="research" data-route="general">{gap}</article>\n'
                f'<article data-kind="review" id="c" data-lead="r0:1">{gap}'
                + '<ul>' + follow('lead', 'r0:1', 'Kish', 'Ran the check.') + '</ul></article>\n')
        self.assertEqual([anchor for anchor, _ in record_audit.articles(text)], ['a', 'b', 'c'])
        self.assertEqual([anchor for anchor, _ in record_audit.articles(text, kind='review')], ['c'])
        self.assertEqual([anchor for anchor, *_ in record_audit.open_gaps(text)], ['a', 'b', 'c'])
        self.assertEqual(record_audit.carried_items(text), [('lead', 'r0:1', 'Kish.', 'Ran the check.')])
        # Follow-up items outside any article name no review: nothing is carried, and nothing fails.
        self.assertEqual(record_audit.carried_items('<ul>' + follow('lead', 'r0:1', 'Kish', 'Ran.') + '</ul>'), [])


if __name__ == '__main__':
    unittest.main()
