"""notebook-append.py inserts after the last record article and replaces the next step."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('notebook_append', TOOLS / 'notebook-append.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

NOTEBOOK = ('<section id="proposed-next-step">\n<h2>Proposed next step</h2>\n<p>old</p>\n</section>\n'
            '<section id="research-record">\n<h2>Record</h2>\n<article id="a1">one</article>\n'
            '<article id="a2">two</article>\n</section>\n<footer></footer>')

REPORTS = ('<p><strong>New mathematics.</strong> The general statement was checked with its '
           'original hypotheses.</p><p><strong>Goal progress.</strong> The required implication '
           'is still open after the completed test.</p>')
ARCHITECTURE = '<h4>Architecture review</h4>' + ''.join(
    f'<p><strong>{label}.</strong> Core: a substantive comparison of the goal, available '
    'results and their degree budgets. <a href="review.txt">Evidence</a>. '
    '<strong>Downstream.</strong> Through thm:downstream-transfer the target gives the statement wanted '
    'at every parameter. '
    '<strong>Attempt.</strong> The cited statements were tried on the test and decide it at no reachable size. '
    '<strong>Test disposition.</strong> New operation. <strong>Operation.</strong> '
    'Contract the specified maps on their common paid domain. <strong>Prediction.</strong> '
    'A strict loss or surviving residual distinguishes the proposed outcomes. '
    '<strong>Trivial cases.</strong> Adding an implied row changes neither quantity compared. '
    '<strong>Power.</strong> The recorded ceilings leave the outcomes apart at the sizes reachable. '
    '<strong>Record search.</strong> Searched the registry for the terms of the test; no recorded '
    'claim answers it.</p>'
    for label in ('Necessary target', 'Extra requirements', 'Independent alternative',
                  'Rank normalization', 'Decision', 'Decisive test'))


def routed(history=''):
    return ('<li data-route-item="general-step">Route</li>' +
            '<section id="proposed-next-step"><h2>Proposed next step</h2><p>old</p></section>' +
            '<section id="research-record">' + history + '</section>')


def draft(kind='research', extra='', content=''):
    return (f'<article id="new" data-kind="{kind}" data-route="general-step" '
            f'data-obligation="open-goal" data-goal-progress="unchanged" {extra}>' +
            REPORTS + content + '</article>')


def queued(count=1, draining=False):
    items = ''.join(f'<li data-check="item-{n}" data-source="a1">Does the bound hold at width {n}?</li>'
                    for n in range(count))
    flag = ' data-draining="true"' if draining else ''
    return ('<section id="open-statements"><ol><li>Open.</li></ol></section>'
            f'<section id="lead-queue"{flag}><ol>{items}</ol></section>' + NOTEBOOK)


class NextStepItemTests(unittest.TestCase):
    def test_a_next_step_s_items_are_found_by_identifier_or_by_a_link_to_their_development(self):
        source = queued(2).replace('<article id="a2">two</article>',
                                   '<article id="a2" data-kind="research" data-check="item-1">two '
                                   '<p><strong>Follow-up.</strong> Continuing: the width-one case next.</p></article>')
        self.assertEqual(tool.named_items(source, '<p>Develop item-0 further.</p>'),
                         [('item-0', 'Does the bound hold at width 0?', '', '')])
        self.assertEqual(tool.named_items(source, '<p>After <a href="#a2">the last entry</a>.</p>'),
                         [('item-1', 'Does the bound hold at width 1?', 'a2', 'Continuing: the width-one case next.')])
        self.assertEqual(tool.named_items(source, '<p>Something else, not item-10.</p>'), [])
        self.assertEqual(len(tool.named_items(source, '<p>Develop item-0: the width check.</p>')), 1)
        self.assertEqual(tool.named_items(source, '<p>Not item-0:x1, a longer identifier.</p>'), [])
        self.assertIsNone(tool.named_items(NOTEBOOK, '<p>item-0</p>'))
        twice = source.replace('<article id="a1">', '<article id="a1" data-check="item-1"><h3>First look</h3>')
        self.assertEqual([anchor for anchor, _ in tool.item_history(twice, 'item-1')][0], 'a1')
        self.assertEqual(tool.item_history(twice, 'item-1')[0][1], 'First look')
        self.assertEqual(tool.item_history(source, 'item-0'), [])
        elsewhere = source.replace('<article id="a1">', '<article id="a1" data-check="item-1"><h3>Parent</h3>'
                                   '<ul><li data-check="item-0">x <strong>Follow-up.</strong> Reopened: y</li></ul>')
        self.assertEqual(tool.item_history(elsewhere, 'item-0'), [('a1', 'Parent')])     # an outcome given elsewhere

    def test_a_lead_and_a_bridge_of_one_identifier_keep_their_own_text_and_entries(self):
        items = ('<li data-lead="a1:1" data-source="a1">The lead asks about signs.</li>'
                 '<li data-bridge="a1:1" data-source="a1">The bridge asks about sources.</li>')
        source = ('<section id="open-statements"><ol><li>Open.</li></ol></section>'
                  f'<section id="lead-queue"><ol>{items}</ol></section>' + NOTEBOOK)
        source = source.replace('<article id="a2">two</article>',
                                '<article id="a2" data-kind="research" data-lead="a1:1"><h3>On the lead</h3>two '
                                '<p><strong>Follow-up.</strong> Continuing: the cut grid next.</p></article>')
        both = tool.named_items(source, '<p>Take a1:1 next.</p>')                  # no kind said: both are shown
        self.assertEqual([(i.kind, text) for i, text, _, _ in both],
                         [('lead', 'The lead asks about signs.'), ('bridge', 'The bridge asks about sources.')])
        self.assertEqual([(anchor, follow) for _, _, anchor, follow in both],
                         [('a2', 'Continuing: the cut grid next.'), ('', '')])     # the entry is the lead's alone
        lead = tool.named_items(source, '<p>Take the lead a1:1 next.</p>')
        self.assertEqual([(i.kind, text) for i, text, _, _ in lead], [('lead', 'The lead asks about signs.')])
        bridge = tool.named_items(source, '<p>Take the bridge a1:1 next.</p>')
        self.assertEqual([(i.kind, a) for i, _, a, _ in bridge], [('bridge', '')])
        self.assertEqual(tool.item_history(source, lead[0][0]), [('a2', 'On the lead')])
        self.assertEqual(tool.item_history(source, bridge[0][0]), [])
        colon = tool.named_items(source, '<p>Take bridge:a1:1 next.</p>')         # the form the queue tool prints
        self.assertEqual([(i.kind, i.label) for i, *_ in colon], [('bridge', 'bridge:a1:1')])
        self.assertEqual(tool.named_items(source, '<p>Not xbridge:a1:1 or a1:10.</p>'), [])
        # the lead's result files are printed for the lead and not for the bridge
        files = source.replace('two <p>', 'two <a href="research/results/x/run.out.txt">output</a> <p>')
        self.assertIn('research/results/x/run.out.txt', tool.result_files_line(files, lead[0][0]))
        self.assertEqual(tool.result_files_line(files, bridge[0][0]), '')
        self.assertEqual(tool.result_files_line(files, 'a1:1'), '')               # bare and shared: refused, no line
        with self.assertRaisesRegex(ValueError, 'names queue item lead:a1:1 and quotes neither'):
            tool.require_quoted_items(source, '<p>Take the lead a1:1 next, for other reasons entirely.</p>')

    def test_a_draining_queue_refuses_a_next_step_that_names_no_item(self):
        entry = '<article id="a3">three</article>'
        tool.append(queued(2), entry, '<p>Some other work.</p>')                    # not draining
        tool.append(queued(2, draining=True), entry, '<p>Develop item-1.</p>')
        for step in ('<p>Some other work.</p>', '<p>After <a href="#a1">an entry that developed none</a>.</p>'):
            with self.assertRaisesRegex(ValueError, 'names none'):
                tool.append(queued(2, draining=True), entry, step)

    def test_a_next_step_naming_a_developed_item_quotes_its_words(self):
        source = queued(2).replace(
            '<article id="a2">two</article>',
            '<article id="a2" data-kind="research" data-check="item-1">two <p><strong>Follow-up.</strong> '
            'Continuing: compute the degree of the paired class at thirty-two holes and more.</p></article>')
        entry = '<article id="a3">three</article>'
        with self.assertRaisesRegex(ValueError, 'quotes neither'):
            tool.append(source, entry, '<p>Develop item-1 by a different question altogether.</p>')
        tool.append(source, entry, '<p>Develop item-1: "compute the degree of the paired class at thirty-two '
                    'holes", as its follow-up says.</p>')
        longer = source.replace('Does the bound hold at width 1?',
                                'Does the bound hold at width one for every large size?')
        tool.append(longer, entry, '<p>On item-1, which asks whether the bound "hold at width one for every '
                    'large size".</p>')                                # eight words of the queued text
        tool.append(source, entry, '<p>Develop item-0, never developed, in any words.</p>')
        # a quotation must be of the current words: a passage from a superseded draft is refused even when an
        # eight-word run shared by both versions satisfies the quotation requirement
        with self.assertRaisesRegex(ValueError, 'not in the latest follow-up'):
            tool.append(source, entry, '<p>Develop item-1, to compute the degree of the paired class at thirty-two '
                        'holes, that is “the width-two case where the bound is no longer polynomial at all”.</p>')
        tool.append(source, entry, '<p>Develop item-1, to “compute the degree of the paired class at thirty-two '
                    'holes and more”, then “a short aside”.</p>')       # short quotations are not checked
        tool.append(source, entry, '<p>After <a href="#a2">the last entry</a>, something else.</p>')   # by link only
        self.assertTrue(tool.quotes('a b c d e f g h i', 'x a, b c d e f g h. y'))
        self.assertFalse(tool.quotes('a b c d e f g', 'a b c d e f g h'))

    def test_registry_matches_for_an_item_s_text(self):
        claim = lambda ident, summary: {'id': ident, 'summary': summary, 'assessment': 'Working proof.',
                                        'topics': [], 'mathematical_status': 'working_proof',
                                        'formalization': {'status': 'not_started'}}
        data = {'claims': [claim('imp:flow-degree', 'Flow systems on expanders need linear degree.'),
                           claim('lem:other', 'A colouring ceiling on Kneser graphs.')]}
        self.assertEqual(tool.registry_matches('Read the argument for the degree bound for flow systems.', data=data),
                         [('imp:flow-degree', 'Flow systems on expanders need linear degree.')])
        self.assertEqual(tool.registry_matches('Nothing in common here at all.', data=data), [])
        self.assertEqual(len(tool.registry_matches('flow degree colouring Kneser', limit=1, data=data)), 1)
        # A notebook's own claims come before better-scoring claims of other notebooks.
        near, far = claim('lem:own', 'A degree bound.'), claim('imp:other', 'Flow systems need linear degree bound.')
        near['record'] = '[Entry](https://example.org/branches/side-one/#a)'
        far['record'] = '[Entry](https://example.org/branches/side-two/#b)'
        words = 'the degree bound for flow systems of linear size'
        both = {'claims': [far, near]}
        self.assertEqual(tool.registry_matches(words, data=both)[0][0], 'imp:other')
        self.assertEqual(tool.registry_matches(words, data=both, home='branches/side-one/')[0][0], 'lem:own')
        self.assertEqual(tool.home_of('research/branches/side-one/notebook.html'), 'branches/side-one/')
        self.assertIsNone(tool.home_of('notebook.html'))

    def test_a_next_step_may_not_take_only_an_item_with_two_entries_without_bearing(self):
        def tagged(anchor, item, bearing):
            return (f'<article id="{anchor}" data-kind="research" data-route="x" data-check="{item}" '
                    f'data-bearing="{bearing}">t</article>')
        twice = queued(2).replace('<article id="a2">two</article>', tagged('a2', 'item-1', 'none'))
        third = tagged('a3', 'item-1', 'none')
        with self.assertRaisesRegex(ValueError, 'last two entries declared no bearing'):
            tool.refuse_excluded_item(twice.replace('</article>\n</section>', '</article>\n' + third + '\n</section>')
                                      if '</article>\n</section>' in twice else twice + third,
                                      '<p>Develop item-1 again.</p>')
        both = twice + third
        tool.refuse_excluded_item(both, '<p>Develop item-0; item-1 waits.</p>')            # another item is named
        tool.refuse_excluded_item(twice + tagged('a3', 'item-1', 'some'), '<p>Develop item-1 again.</p>')
        tool.refuse_excluded_item(twice + tagged('a3', 'item-0', 'none'), '<p>Develop item-1 again.</p>')
        tool.refuse_excluded_item(twice, '<p>Develop item-1 again.</p>')                    # one entry only
        # 16 October 2026: the last entry is on another route; the item is judged on its own route.
        other = '<article id="a4" data-kind="research" data-route="y" data-check="item-0" data-bearing="none">t</article>'
        with self.assertRaisesRegex(ValueError, 'last two entries declared no bearing'):
            tool.refuse_excluded_item(both + other, '<p>Develop item-1 again.</p>')

    def test_a_next_step_planning_no_bearing_in_such_a_run_is_refused_unless_it_closes(self):
        def tagged(anchor, bearing):
            return f'<article id="{anchor}" data-kind="research" data-route="x" data-bearing="{bearing}">t</article>'
        run = ''.join(tagged(f'a{i}', 'none') for i in range(3))
        nothing = "<p>Evaluate the bound. Best outcome: nothing at the goal's deficit.</p>"
        with self.assertRaisesRegex(ValueError, 'the finisher will refuse the entry it plans'):
            tool.refuse_no_bearing_plan(run, nothing)
        tool.refuse_no_bearing_plan(run, nothing.replace('deficit.', 'deficit; the entry closes its item.'))
        tool.refuse_no_bearing_plan(run, '<p>The entry closes its item. ' + nothing[3:])    # said before the outcome
        tool.refuse_no_bearing_plan(run, '<p>Best outcome: a barrier near half for narrow rows.</p>')
        tool.refuse_no_bearing_plan(tagged('a0', 'none') * 2, nothing)                      # a run of two only
        tool.refuse_no_bearing_plan(run + tagged('a9', 'some'), nothing)                    # the run is broken
        # the next step of 12 October 2026 that was accepted and whose entry was refused
        real = ('<p>read the entry on the immunity budget and evaluate what it gives. Best outcome at the goal\'s '
                'parameters: a proved lower bound, which cannot exceed a quarter; so nothing at the goal\'s '
                'deficit, and the entry is spent to learn whether the item has anything left.</p>')
        with self.assertRaisesRegex(ValueError, 'the finisher will refuse'):
            tool.refuse_no_bearing_plan(run, real)
        # words that do not say the planned entry closes its item
        for words in ('it does not close the item.', 'the other check is closed.'):
            with self.assertRaisesRegex(ValueError, 'the finisher will refuse'):
                tool.refuse_no_bearing_plan(run, nothing.replace('deficit.', 'deficit; ' + words))
        # a sentence about past work, before the best outcome, is not the plan
        tool.refuse_no_bearing_plan(run, "<p>The block gave nothing at the goal's parameters. Best outcome: a "
                                         'barrier near half.</p>')
        # the route review that is due is not a planned research entry
        record = '<section id="research-record">' + ''.join(tagged(f'b{i}', 'none') for i in range(6)) + '</section>'
        tool.refuse_no_bearing_plan(record, nothing)
        with self.assertRaisesRegex(ValueError, 'the finisher will refuse'):
            tool.refuse_no_bearing_plan(record.replace(tagged('b5', 'none'), ''), nothing)

    def test_the_refusal_of_such_a_plan_is_made_by_append(self):
        def tagged(anchor):
            return f'<article id="{anchor}" data-kind="research" data-route="x" data-bearing="none">t</article>'
        source = NOTEBOOK.replace('<article id="a1">one</article>\n<article id="a2">two</article>',
                                  tagged('a1') + '\n' + tagged('a2'))
        nothing = "<p>Evaluate the bound. Best outcome: nothing at the goal's deficit.</p>"
        with self.assertRaisesRegex(ValueError, 'the finisher will refuse the entry it plans'):
            tool.append(source, tagged('a3'), nothing)                     # the appended entry is the third
        tool.append(source, tagged('a3'), nothing.replace('deficit.', 'deficit; the entry closes its item.'))
        tool.append(NOTEBOOK, tagged('a3'), nothing)                       # one entry without bearing only

    def test_a_review_due_next_needs_no_item(self):
        research = [('<article id="r%d" data-kind="research" data-route="x">' % n, '') for n in range(6)]
        self.assertTrue(tool.review_due(research))
        self.assertFalse(tool.review_due(research[:5]))
        self.assertFalse(tool.review_due([('<article id="v" data-kind="review" data-route="x">', '')] + research[:5]))
        self.assertTrue(tool.review_due(research + [('<article id="o" data-kind="research" data-route="y">', '')]
                                        + [research[0]]))
        self.assertFalse(tool.review_due([]))
        mixed = research[:4] + [('<article data-kind="audit" data-route="x">', ''),
                                 ('<article id="legacy" data-route="x">', ''),
                                 ('<article data-kind="formalization" data-route="y">', '')]
        mixed += [('<article id="other%d" data-kind="research" data-route="y">' % n, '')
                  for n in range(2)]
        self.assertTrue(tool.review_due(mixed))
        source = queued(2, draining=True).replace(
            '<article id="a1">one</article>\n<article id="a2">two</article>',
            ''.join(tag + '</article>' for tag, _ in mixed))
        tool.require_named_item(source, '<p>The scheduled route review comes next.</p>')
        with self.assertRaisesRegex(ValueError, 'names none'):
            tool.require_named_item(source.replace('<article id="other1" data-kind="research" '
                                                   'data-route="y"></article>', ''), '<p>Other work.</p>')
        self.assertFalse(tool.review_due(mixed + [('<article data-kind="review" data-route="x">', '')]))


SMALLEST = ('<p><strong>Smallest case.</strong> Width two. Nontrivial because: the input has two variables '
            'of different degrees there.</p>')


class NotebookAppendTests(unittest.TestCase):
    def test_first_article_follows_record_heading_and_introduction(self):
        source = ('<section id="research-record">\n<h2>Research record</h2>\n'
                  '<p>Record introduction.</p>\n</section>\n<footer></footer>')
        out = tool.append(source, '<article id="first">first entry</article>')
        self.assertLess(out.index('</h2>'), out.index('<article'))
        self.assertLess(out.index('Record introduction.'), out.index('<article'))
        self.assertLess(out.index('</article>'), out.index('</section>'))
        self.assertTrue(out.endswith('<footer></footer>'))

    def test_appends_after_last_article_and_replaces_next_step(self):
        out = tool.append(NOTEBOOK, '<article id="a3">three</article>\n', '<p>new</p>')
        self.assertIn('<article id="a2">two</article>\n<article id="a3">three</article>\n</section>', out)
        self.assertIn('<h2>Proposed next step</h2>\n<p>new</p>\n</section>', out)
        self.assertNotIn('<p>old</p>', out)

    def test_accepts_attributes_before_the_anchor(self):
        out = tool.append(NOTEBOOK, '<article class="research-entry" id="a3" data-kind="review">three</article>')
        self.assertIn('<article id="a2">two</article>\n<article class="research-entry" id="a3"', out)
        with self.assertRaisesRegex(ValueError, 'already present'):
            tool.append(NOTEBOOK, '<article class="research-entry" id="a2">dup</article>')

    def test_keeps_next_step_without_option(self):
        out = tool.append(NOTEBOOK, '<article id="a3">three</article>')
        self.assertIn('<p>old</p>', out)

    def test_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'already present'):
            tool.append(NOTEBOOK, '<article id="a2">dup</article>')
        with self.assertRaisesRegex(ValueError, 'one <article'):
            tool.append(NOTEBOOK, '<p>not an article</p>')
        with self.assertRaisesRegex(ValueError, 'research-record'):
            tool.append('<p>none</p>', '<article id="x">x</article>')

    def test_pending_architecture_requires_link_inside_outcome(self):
        source = routed('<article id="review" data-kind="review" data-route="general-step">' +
                        ARCHITECTURE + '</article>')
        outside = '<p>Question: <a href="#review">previous review</a>.</p>'
        outcome = ('<p><strong>Architecture test.</strong> <strong>Decided.</strong> The attempted construction failed '
                   'its stated general test and changes the next action.</p>')
        with self.assertRaisesRegex(ValueError, 'Architecture test must'):
            tool.append(source, draft(content=outside + outcome))
        linked = outcome.replace('The attempted', '<a href="#review">The attempted</a>')
        self.assertIn(linked, tool.append(source, draft(content=linked)))

    def test_goal_review_requires_across_goal_before_append(self):
        history = ''
        for block in range(2):
            history += (f'<article id="r{block}" data-kind="review" '
                        'data-route="general-step" data-open-items="3"></article>')
            history += ''.join(f'<article id="e{block}-{i}" data-kind="research" '
                               'data-route="general-step"></article>' for i in range(6))
        entry = draft('review', 'data-scope="goal" data-open-items="3"', ARCHITECTURE)
        with self.assertRaisesRegex(ValueError, 'Across the goal'):
            tool.append(routed(history), entry)
        across = ('<h4>Across the goal</h4><ul><li>Binary: unchanged, six cycles.</li>'
                  '<li>All-prime: unchanged, zero cycles.</li></ul>')
        self.assertIn(across, tool.append(routed(history), entry.replace('</article>', across + '</article>')))

    def test_registration_waits_but_finalizer_still_checks_it(self):
        entry = draft(extra='data-claims="lem:new-result"').replace(
            'data-goal-progress="unchanged"', 'data-goal-progress="advanced"').replace(
            'The required implication', 'The claim lem:new-result advances the required implication')
        checks = tool.reporting_checks()
        with mock.patch.object(checks, 'registered_status', side_effect=AssertionError('too early')):
            result = tool.append(routed(), entry)
        position = result.index('<article')
        with mock.patch.object(checks, 'registered_status', return_value={}):
            with self.assertRaisesRegex(ValueError, 'Advanced Goal progress'):
                checks.validate_progress(result, position, result.index('</article>', position))

    def test_a_dollar_sign_or_a_character_reference_without_its_ampersand_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'entry contains a dollar sign'):
            tool.append(NOTEBOOK, '<article id="a3">where $x$ is odd</article>')
        self.assertIn(r'where \(x\) is odd', tool.append(NOTEBOOK, r'<article id="a3">where \(x\) is odd</article>'))
        with self.assertRaisesRegex(ValueError, r'entry has character references without their & \(#39;, nbsp;\)'):
            tool.append(NOTEBOOK, '<article id="a3">the budget#39;s share, 2 nbsp;s, 2 nbsp;m</article>')
        self.assertIn('budget&#39;s', tool.append(NOTEBOOK, '<article id="a3">the budget&#39;s share, 2&nbsp;s</article>'))
        with self.assertRaisesRegex(ValueError, r'next step has character references without their & \(quot;\)'):
            tool.append(NOTEBOOK, '<article id="a3">three</article>', '<p>the (quot;new) step</p>')

    def test_an_unverified_suggestion_is_not_named_as_a_next_attempt_without_a_check(self):
        suggestion = ('a core near half extended by variables defined as the products of pairs of its variables, '
                      'whose plateau sits near a quarter')
        listed = ("<h4>Reviewer's suggestions, unverified</h4><ul><li>" + suggestion.capitalize()
                  + '. <strong>Record.</strong> Searched for extension variables defined as products of pairs and '
                  'the closure at twice the cutoff: no match.</li></ul>')

        def entry(follow, extra=''):
            smallest = ('<p><strong>Smallest case.</strong> Width two. Nontrivial because: the input has two '
                        'variables of different degrees there.</p>')
            return f'<article id="a3">{listed}{extra}<p><strong>Follow-up.</strong> {follow}</p>{smallest}</article>'
        said = entry("Continuing: the question is open. Next attempt, the reviewer's candidate, unverified: " + suggestion + '.')
        with self.assertRaisesRegex(ValueError, 'follow-up calls what it names unverified'):
            tool.append(NOTEBOOK, said)
        quoted = entry('Continuing: open. Next attempt: ' + suggestion + ', to prove or refute.')
        with self.assertRaisesRegex(ValueError, "follow-up quotes 8 consecutive words"):
            tool.append(NOTEBOOK, quoted)
        plain_entry = entry('Continuing: open. Next attempt: bound the degree of the input from the width.')
        with self.assertRaisesRegex(ValueError, 'next step quotes 8 consecutive words'):
            tool.append(NOTEBOOK, plain_entry, '<p>The entry takes ' + suggestion + '.</p>')
        # the Record note is the author's search, not the suggestion; and other attempts pass
        self.assertIn('a3', tool.append(NOTEBOOK, plain_entry, '<p>Search for extension variables defined as '
                                        'products of pairs and the closure at twice the cutoff again.</p>'))
        # a sentence before the next attempt may use the word; a short paragraph does not lift the refusal
        before = entry('Continuing: the suggestion stays unverified and is dropped. Next attempt: the width bound.')
        self.assertIn('a3', tool.append(NOTEBOOK, before))
        with self.assertRaisesRegex(ValueError, 'Suggestion checked'):
            tool.append(NOTEBOOK, quoted.replace(listed, listed + '<p><strong>Suggestion checked.</strong> Yes.</p>'))
        checked = ('<p><strong>Suggestion checked.</strong> Its count of the shattered set was computed for four '
                   'variables by hand and agrees with the suggestion.</p>')
        self.assertIn('a3', tool.append(NOTEBOOK, quoted.replace(listed, listed + checked)))
        # the two follow-ups of 12 October 2026 that prompted the check, as recorded, with their lists' items
        pointing = ("<h4 id=\"s\">Reviewer's suggestions, unverified</h4><ol><li>A colon family isolating Q, as in "
                    'the follow-up. <strong>Record.</strong> Searched for a colon family isolating a shattered set: '
                    'no general statement.</li></ol>')
        first = ("Continuing: open. Next attempt, the reviewer's candidate, unverified: a core near half on "
                 'variables q, extended by variables defined as the products.')
        second = ('Continuing: the question is open. Next attempt on its return, toward a proof and not a '
                  "construction: ask whether the engine has a family that removes them; the reviewer's remark is "
                  'that the degree of such an input is about the number of outside variables.')
        for follow, reason in ((first, 'calls what it names unverified'), (second, "names the reviewer's")):
            with self.assertRaisesRegex(ValueError, reason):
                tool.append(NOTEBOOK, f'<article id="a3">{pointing}<p><strong>Follow-up.</strong> {follow}</p></article>')
        own_words = 'Continuing: open. Next attempt: bound the degree of an isolating input from the width.'
        with self.assertRaisesRegex(ValueError, 'as in the follow-up'):
            tool.append(NOTEBOOK, f'<article id="a3">{pointing}<p><strong>Follow-up.</strong> {own_words}</p></article>')
        # a follow-up in a list item is read; with no list and no label nothing is found
        in_item = ('<article id="a3"><ul><li data-check="x:s1">Tried. <strong>Follow-up.</strong> Continuing: next '
                   'attempt, the unverified candidate (cf. the list) again.</li></ul></article>')
        with self.assertRaisesRegex(ValueError, 'calls what it names unverified'):
            tool.append(NOTEBOOK, in_item)
        self.assertIn('a3', tool.append(NOTEBOOK, f'<article id="a3"><p><strong>Follow-up.</strong> {own_words}</p>{SMALLEST}</article>'))
        # a sentence that sets a suggestion aside is not a plan on it, in a follow-up or a next step
        aside = ('Continuing: open. Next attempt: the width bound. A remark on series stays unverified and is '
                 'dropped.')
        self.assertIn('a3', tool.append(NOTEBOOK, f'<article id="a3"><p><strong>Follow-up.</strong> {aside}</p>{SMALLEST}</article>'))
        entry3 = '<article id="a3">three</article>'
        self.assertIn('a3', tool.append(NOTEBOOK, entry3, '<p>The unverified count is withdrawn. Prove the bound.</p>'))
        with self.assertRaisesRegex(ValueError, 'next step calls what it names unverified'):
            tool.append(NOTEBOOK, entry3, "<p>Take the unverified count and build on it.</p>")

    def test_a_next_step_that_parks_an_open_goal_is_refused(self):
        entry, survey = '<article id="a3">three</article>', '<article id="a3" data-kind="survey">three</article>'
        opened = '<section id="open-statements"><ol><li>Statement one is open.</li></ol></section>' + NOTEBOOK
        proved = '<section id="open-statements"><p>The goal is proved.</p></section>' + NOTEBOOK
        waits = '<p>Research <em>waits</em> for your decision on the route.</p>'
        with self.assertRaisesRegex(ValueError, r'the next step parks the goal \("Research  waits"\)'):
            tool.append(opened, entry, waits)
        # A proved goal and a notebook that lists no statements may wait.
        with tempfile.TemporaryDirectory() as tools:
            for source in (proved, NOTEBOOK):
                self.assertIn('waits', tool.append(source, entry, waits, tools=Path(tools)))
            # An entry of another kind may wait only where the branch's own module names its kind.
            with self.assertRaisesRegex(ValueError, 'parks the goal'):
                tool.append(opened, survey, waits, tools=Path(tools))
        with tempfile.TemporaryDirectory() as tools:
            (Path(tools) / 'branch_own.py').write_text("PARKING_KINDS = ('survey', 'audit')\n")
            self.assertIn('waits', tool.append(opened, survey, waits, tools=Path(tools)))
            for other in (entry, survey.replace('survey', 'surveys')):
                with self.assertRaisesRegex(ValueError, 'parks the goal'):
                    tool.append(opened, other, waits, tools=Path(tools))
        # A step that turns to another statement, or names work that waits without being a wait, is research.
        for step in ('<p>Switch to statement two: prove the transfer lemma for odd fields.</p>',
                     '<p>Prove the bound; the write-up can wait until then.</p>'):
            self.assertIn(step, tool.append(opened, entry, step))
        with self.assertRaisesRegex(ValueError, 'next step contains a dollar sign'):
            tool.append(NOTEBOOK, entry, '<p>Costs $5.</p>')

    def test_a_smallest_case_without_its_nontrivial_reason_is_refused(self):
        # 17 October 2026: one cut with no coarser load was taken for the smallest case of a two-level rule.
        draft = ('<article id="a5"><p><strong>Follow-up.</strong> Continuing. Next attempt: the rule over two '
                 'levels. <strong>Smallest case.</strong> One cut of m edges and no coarser load: the even split.'
                 '</p></article>')
        with self.assertRaisesRegex(ValueError, 'Nontrivial because'):
            tool.refuse_trivial_smallest_case(draft)
        tool.refuse_trivial_smallest_case(draft.replace(
            'the even split.', 'the even split. Nontrivial because: the rule reads the coarser load, which '
            'varies along the cut.'))
        tool.refuse_trivial_smallest_case(draft.replace('Continuing. Next attempt: the rule over two levels.',
                                                        'Closed: a restatement.'))

    def test_a_status_line_crediting_a_review_before_the_gate_is_refused(self):
        # 17 October 2026: "with a reviewed correction pass" stood beside a placeholder Verification gate.
        early = ('<article id="a3">\n<p class="entry-meta">Working proof, with a reviewed correction pass.</p>\n'
                 '<p><strong>Verification gate.</strong> [written after the second pass]</p>\n</article>')
        with self.assertRaisesRegex(ValueError, 'credits a review'):
            tool.refuse_early_review_credit(early)
        for entry in (early.replace('[written after the second pass]', 'One reviewer, two passes.'),
                      early.replace('with a reviewed correction pass', 'two-choice routing'),
                      '<article id="a4">\n<p class="entry-meta">Reviewed unsuccessful estimate.</p>\n</article>',
                      # 17 October 2026: the placeholder status line itself was refused.
                      early.replace('Working proof, with a reviewed correction pass.',
                                    '17 October 2026 · [status written after the review] · Two-choice routing.')):
            tool.refuse_early_review_credit(entry)

    def test_an_entry_is_refused_while_where_we_stand_is_as_committed_unless_a_reason_is_given(self):
        def notebook(stand):
            return f'<section id="where-we-stand"><p>{stand}</p></section>' + NOTEBOOK
        entry = '<article id="a3">\n<h3>Three</h3>\n<p class="entry-meta">Status: finite check.</p>\n<p>Body.</p>\n</article>'
        with self.assertRaisesRegex(ValueError, 'Where we stand is unchanged since the last commit'):
            tool.append(notebook('old'), entry, committed=notebook('old'))
        with self.assertRaisesRegex(ValueError, 'Where we stand is unchanged'):
            tool.append(notebook('old'), entry, committed=notebook('old'), reason='  ')
        kept = tool.append(notebook('old'), entry, committed=notebook('old'), reason='a check of <one> case & no more ')
        self.assertIn('<p class="entry-meta">Status: finite check.</p>\n<p><strong>Where we stand.</strong> Unchanged: '
                      'a check of &lt;one&gt; case &amp; no more</p>\n<p>Body.</p>', kept)
        # Without a status line the paragraph ends the entry.
        why = 'a route review that changes no statement of it'
        self.assertIn(f'three\n<p><strong>Where we stand.</strong> Unchanged: {why}</p>\n</article>',
                      tool.append(notebook('old'), '<article id="a3">three</article>', committed=notebook('old'), reason=why))
        # 17 October 2026: a one-letter reason passed and wrote "Unchanged: x" into an entry.
        with self.assertRaisesRegex(ValueError, 'at least 6 words'):
            tool.append(notebook('old'), entry, committed=notebook('old'), reason='x')
        # A changed section, a notebook not yet committed and one without the section take the entry as it is.
        for source, committed in ((notebook('new'), notebook('old')), (notebook('old'), None), (NOTEBOOK, NOTEBOOK)):
            for reason in (None, 'why'):
                self.assertNotIn('Where we stand.</strong>', tool.append(source, entry, committed=committed, reason=reason))

    def test_a_branch_s_own_checks_run_after_the_generic_ones(self):
        entry = '<article id="a3">three</article>'
        with tempfile.TemporaryDirectory() as directory:
            tools = Path(directory)
            self.assertIn(entry, tool.append(NOTEBOOK, entry, tools=tools))
            (tools / 'append_checks.py').write_text(
                'def check(source, entry, next_html):\n'
                '    open(__file__ + ".ran", "a").write(entry + "|" + str(next_html) + "\\n")\n'
                '    if "three" in entry:\n        raise ValueError("this branch takes no entry about three")\n')
            ran = tools / 'append_checks.py.ran'
            with self.assertRaisesRegex(ValueError, 'this branch takes no entry about three'):
                tool.append(NOTEBOOK, entry, '<p>new</p>', tools=tools)
            self.assertEqual(ran.read_text(), entry + '|<p>new</p>\n')
            self.assertIn('four', tool.append(NOTEBOOK, '<article id="a4">four</article>', tools=tools))
            # An entry both would refuse is refused by the generic check, and the module is not asked.
            ran.unlink()
            with self.assertRaisesRegex(ValueError, 'dollar sign'):
                tool.append(NOTEBOOK, '<article id="a3">three for $3</article>', tools=tools)
            self.assertFalse(ran.exists())

    def test_the_command_reads_the_committed_notebook_and_records_the_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = '<section id="where-we-stand"><p>old</p></section>' + NOTEBOOK
            (root / 'notebook.html').write_text(source)
            entry = root / 'draft.html'
            entry.write_text('<article id="a3">three</article>')
            git = lambda *args: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=root,
                                               capture_output=True, text=True, check=True)
            git('init', '-q'); git('add', 'notebook.html'); git('commit', '-qm', 'x')

            def run(*arguments):
                with mock.patch.object(tool, 'ROOT', root), mock.patch.object(tool, 'selected', return_value={'source': 'notebook.html'}), \
                        mock.patch.object(sys, 'argv', ['notebook-append.py', str(entry), *arguments]), \
                        contextlib.redirect_stdout(io.StringIO()):
                    tool.main()
            with self.assertRaisesRegex(SystemExit, 'Where we stand is unchanged since the last commit'):
                run()
            self.assertEqual((root / 'notebook.html').read_text(), source)
            run('--stand-unchanged', 'only a lemma, which changes no statement')
            self.assertIn('three\n<p><strong>Where we stand.</strong> Unchanged: only a lemma, which changes no '
                          'statement</p>\n</article>',
                          (root / 'notebook.html').read_text())

    def test_next_alone_replaces_the_proposed_next_step_and_appends_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notebook, nxt = root / 'notebook.html', root / 'next.html'
            notebook.write_text(NOTEBOOK)
            def run(*arguments):
                with mock.patch.object(tool, 'ROOT', root), \
                     mock.patch.object(tool, 'selected', return_value={'source': 'notebook.html'}), \
                     mock.patch.object(sys, 'argv', ['notebook-append.py', *arguments]), \
                     contextlib.redirect_stdout(io.StringIO()):
                    tool.main()
            nxt.write_text('<section id="x"><p>new</p></section>')
            with self.assertRaisesRegex(SystemExit, 'only the section contents'):
                run('--next', str(nxt))
            self.assertEqual(notebook.read_text(), NOTEBOOK)
            nxt.write_text('<p>replacement step</p>')
            run('--next', str(nxt))
            result = notebook.read_text()
            self.assertIn('<h2>Proposed next step</h2>\n<p>replacement step</p>', result)
            self.assertEqual(result.count('<article'), NOTEBOOK.count('<article'))
            with self.assertRaisesRegex(SystemExit, '2'):
                run()

    def test_cli_reporting_failure_does_not_write_notebook_or_next_step(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = routed()
            notebook = root / 'notebook.html'
            notebook.write_text(source)
            entry = root / 'draft.html'
            entry.write_text('<article id="new" data-kind="research" data-route="general-step">bad</article>')
            nxt = root / 'next.html'
            nxt.write_text('<p>replacement</p>')
            with mock.patch.object(tool, 'ROOT', root), \
                 mock.patch.object(tool, 'selected', return_value={'source': 'notebook.html'}), \
                 mock.patch.object(sys, 'argv', ['notebook-append.py', str(entry), '--next', str(nxt)]):
                with self.assertRaisesRegex(SystemExit, 'data-obligation'):
                    tool.main()
            self.assertEqual(notebook.read_text(), source)

    def test_cli_checks_fragment_and_living_structure_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notebook, entry, nxt = (root / name for name in ('notebook.html', 'draft.html', 'next.html'))
            entry.write_text('<article id="new">A new entry.</article>')
            cases = [
                (NOTEBOOK, '<section id="proposed-next-step"><h2>Proposed next step</h2><p>new</p></section>',
                 'only the section contents'),
                (NOTEBOOK, "<SECTION id='other'><p>new</p></SECTION>", 'only the section contents'),
                (NOTEBOOK, '<h2 class="title">Proposed next step</h2><p>new</p>', 'retained Proposed'),
                (NOTEBOOK, '</section><p>new</p>', 'Unmatched closing tag'),
                ('<section id="duplicate"></section><section id="duplicate"></section>' + NOTEBOOK,
                 '<p>new</p>', 'unique ID'),
            ]
            def run():
                with mock.patch.object(tool, 'ROOT', root), \
                     mock.patch.object(tool, 'selected', return_value={'source': 'notebook.html'}), \
                     mock.patch.object(sys, 'argv', ['notebook-append.py', str(entry), '--next', str(nxt)]), \
                     contextlib.redirect_stdout(io.StringIO()):
                    tool.main()
            for source, fragment, reason in cases:
                with self.subTest(fragment=fragment):
                    notebook.write_text(source)
                    nxt.write_text(fragment)
                    with self.assertRaisesRegex(SystemExit, reason):
                        run()
                    self.assertEqual(notebook.read_text(), source)
                    self.assertEqual(nxt.read_text(), fragment)
            notebook.write_text(NOTEBOOK)
            fragment = r'<h2>Another heading</h2><h3>Experiment</h3><p>\(a<section>b\) and &lt;section&gt;.</p>'
            nxt.write_text(fragment)
            run()
            result = notebook.read_text()
            self.assertIn('<h2>Proposed next step</h2>\n' + fragment, result)
            self.assertIn('<article id="new">A new entry.</article>', result)
            self.assertEqual(result.count('<section id="proposed-next-step">'), 1)

    def test_a_closing_follow_up_quotes_the_listed_text_of_its_item(self):
        source = ('<article id="entry-a" data-kind="research"><p>work</p><h4>Sub-ideas</h4><ul>'
                  '<li data-sub="check">Bound the mean square of the off-axis sum over a short range of scales '
                  'and compare it.</li><li data-sub="check">A second one.</li></ul></article>')
        resembling = ('<article id="new"><ul><li data-check="entry-a:s1">A pointwise bound was found. '
                      '<strong>Follow-up.</strong> Closed: superseded by the pointwise bound.</li></ul></article>')
        with self.assertRaisesRegex(ValueError, 'quotes 8 consecutive words.*check:entry-a:s1, whose text is: '
                                                'Bound the mean square'):
            tool.refuse_unquoted_closures(source, resembling)
        quoting = resembling.replace('A pointwise bound was found.', 'Its text asks to "bound the mean square '
                                     'of the off-axis sum over a short range"; a pointwise bound does not.')
        lines = tool.refuse_unquoted_closures(source, quoting)
        self.assertEqual(lines[0], 'The entry closes check:entry-a:s1. Its listed text, to read beside the '
                                   'follow-up:')
        self.assertIn('Listed text: Bound the mean square', lines[1])
        # a follow-up that keeps the item open, a merge, and an item of another notebook's article ask nothing
        for other in (resembling.replace('Closed: superseded by the pointwise bound', 'Continuing: not attempted'),
                      resembling.replace('Closed: superseded by the pointwise bound', 'Closed: merged into x'),
                      resembling.replace('entry-a:s1', 'entry-zz:s1')):
            tool.refuse_unquoted_closures(source, other)
        self.assertEqual(len(tool.closing_followups(source, resembling.replace('entry-a:s1', 'entry-zz:s1'))), 1)
        self.assertEqual(tool.closing_followups(source, '<article id="n"><p>No list.</p></article>'), [])
        # a listed text of fewer than eight words is quoted whole; a Developed follow-up is held to the same
        short = resembling.replace('entry-a:s1', 'entry-a:s2').replace('Closed: superseded by the pointwise bound',
                                                                       'Developed: by the bound')
        with self.assertRaisesRegex(ValueError, 'check:entry-a:s2, whose text is: A second one'):
            tool.refuse_unquoted_closures(source, short)
        tool.refuse_unquoted_closures(source, short.replace('A pointwise bound was found.', 'It was "a second one".'))
        self.assertTrue(tool.closures_count(source + resembling + quoting.replace('id="new"', 'id="new2"'))
                        .startswith('1\t0\t0\tnew\n1\t1\t0\tnew2\n2 closing follow-ups in 2 entries; 1 quote'))

    def test_an_entry_s_summing_up_sentences_are_answered_before_it_is_appended(self):
        import draft_claim_sentences
        entry = ('<article id="new"><h3>T</h3><p><strong>New mathematics.</strong> No point hides.</p>'
                 '<p>Every other paragraph is not asked about.</p></article>')
        with self.assertRaisesRegex(ValueError, '1 summing-up sentences.*--answers FILE'):
            tool.refuse_unanswered(entry, None)
        form = draft_claim_sentences.answers_template(entry)
        with self.assertRaisesRegex(ValueError, '1 of 1 summing-up sentences are not answered'):
            tool.refuse_unanswered(entry, form)
        tool.refuse_unanswered(entry, form.replace('rests on: \n', 'rests on: part one of lem:the-lemma\n'))
        with self.assertRaisesRegex(ValueError, '(?s)limits them by a word the sentence lacks.*the answer says: only'):
            tool.refuse_unanswered(entry, form.replace('rests on: \n', 'rests on: lem:the-lemma, one side only\n'))
        tool.refuse_unanswered('<article id="new"><p>A sentence with none of it in a body paragraph.</p></article>',
                               None)                                   # nothing to answer, nothing asked




class UnappliedMatchesTest(unittest.TestCase):
    # The exposing case, 17 October 2026: thm:per-level-count-matchings printed beside mixed-level-counts and
    # applied nowhere in the next entry's Own statements (it was named only in its Degenerate cases).
    MATCHES = ['thm:per-level-count-matchings', 'thm:low-level-mixed-counts']

    def test_a_match_named_outside_own_statements_is_listed(self):
        entry = ('<article id="e" data-kind="research" data-claims="thm:windowed-mixed-counts">'
                 '<p><strong>Degenerate cases.</strong> covered already by thm:per-level-count-matchings.</p>'
                 '<p><strong>Own statements.</strong> thm:low-level-mixed-counts is the case m = 3.</p></article>')
        self.assertEqual(tool.unapplied_matches(entry, self.MATCHES), ['thm:per-level-count-matchings'])

    def test_applied_or_declared_matches_pass(self):
        entry = ('<article id="e" data-kind="research" data-claims="thm:low-level-mixed-counts">'
                 '<p><strong>Own statements.</strong> thm:per-level-count-matchings at level t_2 leaves only the '
                 'repair. <strong>Plainest bound.</strong> none.</p></article>')
        self.assertEqual(tool.unapplied_matches(entry, self.MATCHES), [])
        # A longer identifier sharing a prefix does not count as the shorter one.
        entry = '<article id="e"><p><strong>Own statements.</strong> thm:per-level-count-matchings-x.</p></article>'
        self.assertEqual(tool.unapplied_matches(entry, self.MATCHES[:1]), ['thm:per-level-count-matchings'])


class ResultFilesLineTest(unittest.TestCase):
    def test_the_line_lists_an_item_s_result_files_and_is_empty_without_them(self):
        import lead_queue
        with mock.patch.object(lead_queue, 'result_files', return_value=['research/results/a/x.py', 'research/results/a/x.json']):
            self.assertEqual(tool.result_files_line('body', 'item'),
                             '  Result files its entries link (2): research/results/a/x.py, research/results/a/x.json')
        with mock.patch.object(lead_queue, 'result_files', return_value=[]):
            self.assertEqual(tool.result_files_line('body', 'item'), '')
        with mock.patch.object(lead_queue, 'result_files', side_effect=ValueError('no such item')):
            self.assertEqual(tool.result_files_line('body', 'item'), '')


class CadenceLineTest(unittest.TestCase):
    def record(self, *kinds):
        return ('<section id="lead-queue"><article data-kind="research" data-route="r">not the record</article>'
                '</section><section id="research-record">' + ''.join(
                    f'<article id="e{i}" data-kind="{kind.split(":")[0]}" data-route="{kind.split(":")[-1]}">x</article>'
                    for i, kind in enumerate(kinds)) + '</section>')

    def test_the_line_counts_research_entries_since_the_last_review_as_the_finisher_does(self):
        # Every route counts and an audit does not, as in the finisher's own scan.
        line = tool.cadence_line(self.record('research:r', 'review:r', 'research:r', 'research:other', 'audit:r',
                                             'research:r').replace('<section id="research-record">',
                                                                  '<section id="research-record"><article>legacy</article>'))
        self.assertEqual(line, 'Review cadence: 3 research entries since the last route review, this one included; '
                               '3 more, then the review.')
        self.assertIn('the next entry is the review', tool.cadence_line(self.record(*['research:r'] * 6)))
        self.assertIn('0 research entries', tool.cadence_line(self.record('research:r', 'review:r')))
        self.assertIsNone(tool.cadence_line('<section id="research-record"></section>'))

    def test_the_period_is_the_finisher_s(self):
        finisher = importlib.util.spec_from_file_location('finisher_for_cadence', TOOLS / 'finish-turn.py')
        module = importlib.util.module_from_spec(finisher)
        finisher.loader.exec_module(module)
        self.assertEqual(tool.reporting_checks().REVIEW_PERIOD, module.REVIEW_PERIOD)
        six = [('<article data-kind="research" data-route="r">', '')] * 6
        with mock.patch.object(tool.reporting_checks(), 'REVIEW_PERIOD', 7):
            self.assertFalse(tool.review_due(six))
            self.assertIn('1 more, then the review', tool.cadence_line(self.record(*['research:r'] * 6)))


class PublicationCitationTests(unittest.TestCase):
    def test_a_sentence_linking_a_publication_file_without_a_claim_is_refused(self):
        link = '<a href="publications/bit-php-resolution-over-parities/sections/05-affine-exclusion.tex">corollary</a>'
        with self.assertRaises(ValueError) as caught:
            tool.refuse_uncited_publication(f'<p>The bound of Braun\'s {link} applies here.</p>')
        self.assertIn('cite no registered claim', str(caught.exception))
        self.assertIn('audit:ordinary-restriction-affine-family', str(caught.exception))
        # The same link beside the claim's identifier, and a publication named without a link, pass.
        tool.refuse_uncited_publication(f'<p>Braun\'s {link}, audit:ordinary-restriction-affine-family, applies.</p>')
        tool.refuse_uncited_publication('<p>Braun\'s corollary applies.</p>')

    def test_the_lookup_follows_labels_to_claims_through_lean_files(self):
        import publication_claims
        found = publication_claims.lookup(['cor:polylog-exclusion'])
        self.assertEqual(list(found.values()), [['audit:ordinary-restriction-affine-family']])
        self.assertEqual(publication_claims.lookup(['no-such-label']), {})


class PlainestUniformTests(unittest.TestCase):
    def test_a_one_function_witness_names_the_plainest_uniform_bound_tried(self):
        # 17 October 2026: the first draft's sentence, refused; the corrected one, accepted.
        first = ('<p><strong>Nonvacuity.</strong> A chain. <strong>Plainest bound.</strong> This witness is one fixed '
                 'function, so a bound for one function decides it. The lemma\'s content is the uniformity.</p>')
        with self.assertRaisesRegex(ValueError, 'plainest uniform bound'):
            tool.refuse_one_function_plainest(first)
        fixed = first.replace('uniformity.', 'uniformity. The plainest uniform bound, Bernstein per cell with a '
                                             'union over its subsets, loses a factor log N here.')
        tool.refuse_one_function_plainest(fixed)
        tool.refuse_one_function_plainest('<p><strong>Plainest bound.</strong> The bare count gives N.</p>')


class SkeletonCheckTests(unittest.TestCase):
    """--check runs every entry-level check on a draft and lists each that fails, writing nothing."""

    def names(self, entry, source=None):
        return [name for name, _ in tool.skeleton_check(source or routed(), entry)]

    def test_a_skeleton_missing_required_paragraphs_lists_each_failing_check(self):
        bare = ('<article id="new" data-kind="research" data-route="general-step" data-obligation="open-goal" '
                'data-goal-progress="unchanged"><p><strong>Question.</strong> Trial.</p></article>')
        names = self.names(bare)
        self.assertIn('general statement', names)
        self.assertIn('progress and bearing', names)    # the first failure does not hide the later ones

    def test_a_paragraph_added_to_the_skeleton_clears_its_check(self):
        general = ('<p><strong>General statement.</strong> lem:new-result: the bound holds at every width and '
                   'every depth of the source.</p>')
        entry = draft(extra='data-claims="lem:new-result"', content=general)
        self.assertNotIn('general statement', self.names(entry))
        self.assertIn('general statement', self.names(draft(extra='data-claims="lem:new-result"')))

    def test_the_where_we_stand_refusal_does_not_hide_later_refusals(self):
        source = '<section id="where-we-stand"><p>Same.</p></section>' + NOTEBOOK
        failures = dict(tool.skeleton_check(source, '<article id="a2">dup</article>', committed=source))
        self.assertIn('where we stand', failures)
        self.assertIn('already present', failures['append'])
        with mock.patch.object(tool, 'refuse_item_history', side_effect=ValueError('open sub-ideas')):
            self.assertIn('item history', dict(tool.skeleton_check(NOTEBOOK, '<article id="a3">x</article>')))

    def test_a_commit_hash_in_the_draft_is_found_at_drafting(self):
        # 16 October 2026: a commit hash in an entry was found only by the checkpoint's record check.
        failures = dict(tool.skeleton_check(routed(), draft(content='<p>As committed in 0fc5cc0773a.</p>')))
        self.assertIn('commit hash', failures.get('record lines', ''))
        self.assertNotIn('record lines', dict(tool.skeleton_check(routed(), draft())))

    def test_a_draft_that_is_not_an_article_fails_as_append(self):
        self.assertEqual(tool.skeleton_check(routed(), '<p>not an article</p>')[0][0], 'append')

    def test_the_command_writes_nothing_and_fails_while_a_check_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notebook = root / 'notebook.html'
            notebook.write_text(routed())
            entry = root / 'draft.html'
            entry.write_text(draft())       # no General statement
            out = io.StringIO()
            with mock.patch.object(tool, 'ROOT', root), \
                 mock.patch.object(tool, 'selected', return_value={'source': 'notebook.html'}), \
                 mock.patch.object(sys, 'argv', ['notebook-append.py', str(entry), '--check']), \
                 contextlib.redirect_stdout(out):
                with self.assertRaises(SystemExit) as stop:
                    tool.main()
            self.assertEqual(stop.exception.code, 1)
            self.assertIn('FAILS general statement', out.getvalue())
            self.assertEqual(notebook.read_text(), routed())


if __name__ == '__main__':
    unittest.main()
