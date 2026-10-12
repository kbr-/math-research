"""Sentences of a draft that cite a claim are listed beside the claim's registered statement."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import draft_claim_sentences as dcs

REGISTRY = {'claims': [
    {'id': 'lem:first', 'summary': 'First lemma: holds for original instances only.'},
    {'id': 'prop:second', 'summary': 'Second proposition, for balanced profiles.'},
]}

DRAFT = '''<article id="entry-x" data-claims="lem:new-one">
<h3>Title</h3>
<p><strong>New mathematics.</strong> <code>lem:new-one</code>: a bound \\(s&lt;n/2.5\\) holds. By <code>lem:first</code> every core is excluded. Nothing else.</p>
<h4>The count</h4>
<p>With <code>prop:second</code> and <code>lem:first</code> the budget is two-sided. See <code>cor:missing</code>.</p>
<ul><li>An item citing <code>lem:first</code> twice, <code>lem:first</code> again.</li></ul>
</article>'''


class DraftClaimSentences(unittest.TestCase):
    def test_sentences_are_listed_under_their_claim_with_labels(self):
        out, unregistered = dcs.report(DRAFT, REGISTRY, 0)
        self.assertIn('lem:first\n  REGISTERED: First lemma: holds for original instances only.', out)
        self.assertIn('  [New mathematics] By lem:first every core is excluded.', out)
        self.assertIn('  [The count] With prop:second and lem:first the budget is two-sided.', out)
        self.assertEqual(out.count('An item citing lem:first twice'), 1)
        self.assertEqual(unregistered, {'cor:missing'})

    def test_a_full_stop_inside_tex_does_not_split_a_sentence(self):
        found = dcs.citations(DRAFT)
        self.assertIn(('lem:new-one', 'New mathematics', 'New mathematics. lem:new-one: a bound \\(s<n/2.5\\) holds.'),
                      found)

    def test_declared_and_unregistered_claims_are_told_apart(self):
        out, _ = dcs.report(DRAFT, REGISTRY, 0)
        self.assertIn('lem:new-one\n  REGISTERED: (declared by this draft; not yet registered)', out)
        self.assertIn('cor:missing\n  REGISTERED: (NOT IN THE REGISTRY)', out)
        self.assertTrue(out.endswith('6 citing sentences, 4 claims, 1 unregistered.'))
        # identifiers of every kind the registry holds are found, an imported statement among them
        more = ('<article><p>By <code>imp:a-source</code> and <code>third-party:b</code>, and <code>check:c</code>; '
                'a path <code>tools/x.py</code> and a queue item <code>entry-2026-10-09-x:s2</code> are not claims.</p>'
                '</article>')
        listed, missing = dcs.report(more, REGISTRY, 0)
        self.assertEqual(missing, {'imp:a-source', 'third-party:b', 'check:c'})
        self.assertNotIn('tools/x.py\n', listed)
        self.assertNotIn('entry-2026-10-09-x:s2\n', listed)
        # a kind of identifier the list does not hold is reported, not passed over in silence
        self.assertNotIn('WARNING', listed)
        newer = {'claims': REGISTRY['claims'] + [{'id': 'newkind:a', 'summary': 'A statement.'}]}
        self.assertIn('prefixes this tool does not look for', dcs.report(more, newer, 0)[0])
        self.assertIn(': newkind.', dcs.report(more, newer, 0)[0])

    def test_sentences_linking_an_entry_stand_beside_its_title_and_status(self):
        notebook = ('<article id="entry-old" data-kind="research">\n<h3>9 October — An attempt that stops</h3>\n'
                    '<p class="entry-meta">No result; a stronger statement.</p>\n<p>Body.</p></article>')
        draft = ('<article id="entry-x" data-claims="none"><h4>Test</h4>'
                 '<p>The statement was posed in <a href="#entry-old">the attempt</a>. Another sentence. '
                 'See <a href="#entry-gone">a missing one</a>.</p></article>')
        out, missing = dcs.entry_report(draft, notebook, 0)
        self.assertIn('entry-old\n  TITLE: 9 October — An attempt that stops\n  STATUS: No result; a stronger statement.\n'
                      '  [Test] The statement was posed in the attempt.', out)
        self.assertIn('entry-gone\n  TITLE: (NOT IN THE NOTEBOOK)', out)
        self.assertEqual(missing, {'entry-gone'})
        self.assertTrue(out.endswith('2 linking sentences, 2 entries, 1 not in the notebook.'))

    def test_width_cuts_long_lines(self):
        out, _ = dcs.report(DRAFT, REGISTRY, 20)
        self.assertIn('  REGISTERED: First lemma: holds f\n', out)




class CountsTest(unittest.TestCase):
    DRAFT = '''<article id="entry-2026-10-11-x">
<h3>11 October 2026 — A title with 3 in it, naming a lemma</h3>
<p>An unlabelled paragraph under the title, with 4 runs.</p>
<p><strong>Assessment of this line.</strong> The queue went from 31 to 33. Nothing else changed. Three builds were removed on 11 October 2026.</p>
<p><strong>New mathematics.</strong> A bound with 5 terms for \\(n\\ge2\\).</p>
<h4>The measurement</h4>
<p>Of 20 items the check saw ten. The exponent \\(1-2\\delta_0\\) and <code>lem:step-2</code> are not counts.</p>
<ul><li>One list item under the measurement with 7 cases.</li></ul>
<p><strong>Limit.</strong> Dated 12 October 2026 only. A 40-minute wait. <strong>31</strong> items remain.</p>
<p><strong>What the six entries did.</strong> Nothing with a number.</p>
<h4>What is added</h4>
<p>A heading the listing does not know, with 9 entries.</p>
<h4>Proof of the lemma</h4>
<p>Two integrations by parts.</p>
</article>'''

    def test_counts_in_bookkeeping_paragraphs_are_listed_and_others_are_not(self):
        found = dcs.counts(self.DRAFT)
        self.assertEqual(found, [
            ('', 'An unlabelled paragraph under the title, with 4 runs.'),   # the title marks no paragraph
            ('Assessment of this line', 'Assessment of this line. The queue went from 31 to 33.'),   # label kept
            ('Assessment of this line', 'Three builds were removed on 11 October 2026.'),
            ('The measurement', 'Of 20 items the check saw ten.'),
            ('The measurement', 'One list item under the measurement with 7 cases.'),
            ('Limit', 'A 40-minute wait.'),                      # a number before a hyphen; the date is not one
            ('Limit', '31 items remain.'),                       # bold at a later sentence's start is its text
            ('What is added', 'A heading the listing does not know, with 9 entries.'),
        ])                                                       # a number word in a label alone is not listed
        report = dcs.counts_report(self.DRAFT, 0)
        self.assertTrue(report.endswith('8 sentences with a count.'))
        self.assertIn('[Assessment of this line] Assessment of this line. The queue went from 31 to 33.', report)


class UniversalsTest(unittest.TestCase):
    """The four conclusions of 12 October 2026 that reviewers found wider than their statements, reconstructed
    from the review records in the paragraphs they stood in, the first drafts having been overwritten: a
    regression test of the patterns by their author, not evidence that the list is of use."""
    DRAFT = '''<article id="entry-x">
<h3>A title</h3>
<p><strong>New mathematics.</strong> A cap for common roots. So no witness of product form, symmetric or not, gives a static barrier above twice the least codimension.</p>
<p><strong>Goal progress.</strong> Unchanged. <strong>Bearing.</strong> Random majority systems are refuted in degree \\(n/2\\), so they are no near-half family whatever their width.</p>
<p><strong>Structural reason.</strong> The reason applies to every method that needs the rows to be monomials in a common basis.</p>
<h4>What the union does</h4>
<p>The cutoff does not move. A union can show a rate only if the core has one; it creates none.</p>
<h4>The statement</h4>
<p><strong>Lemma (a cap).</strong> For every family and all rows, no barrier exists at twice the width.</p>
<p><em>Proof.</em> Every factor is invertible, so no factor lowers the degree by more than one.</p>
<p><strong>Degenerate cases.</strong> With no rows nothing is claimed.</p>
<p><strong>Follow-up.</strong> Continuing: nothing closes the item, and every attempt is owed.</p>
<p><strong>Process assessment.</strong> No mistake to report; all checks ran.</p>
</article>'''

    def test_the_four_wide_conclusions_are_listed_and_statements_are_not(self):
        found, read = dcs.universals(self.DRAFT)
        self.assertEqual(found, [
            ('New mathematics', 'So no witness of product form, symmetric or not, gives a static barrier above '
                                'twice the least codimension.'),
            ('Goal progress', 'Bearing. Random majority systems are refuted in degree \\(n/2\\), so they are no '
                              'near-half family whatever their width.'),
            ('Structural reason', 'Structural reason. The reason applies to every method that needs the rows to '
                                  'be monomials in a common basis.'),
            ('What the union does', 'A union can show a rate only if the core has one; it creates none.'),
            ('Follow-up', 'Follow-up. Continuing: nothing closes the item, and every attempt is owed.'),
        ])
        self.assertEqual(read, 8)        # the lemma, its proof, the degenerate cases and the bookkeeping unread
        self.assertTrue(dcs.universals_report(self.DRAFT, 0).endswith('5 such sentences of 8 read.'))

    def test_words_of_exactness_are_listed_beside_their_paragraphs_conditions(self):
        draft = ('<article><h3>T</h3><h4>What it says</h4>'
                 '<p>Any such set has \\(T\\ge0\\) at every tilt, once \\[(\\tfrac12-d)L\\ge\\log(p/c)\\] holds. It is so.</p>'
                 '<p>The reach is the same \\(\\log(12M)/L\\), with \\(c\\ge0\\), \\(c&lt;p\\) and a symbol \\(L\\).</p>'
                 '<p>The step is immediate.</p>'
                 '<p>The bound holds with a constant.</p>'
                 '<p><strong>Lemma (a cap).</strong> It holds for every row, exactly.</p>'
                 '<p><strong>Owed attempt.</strong> Made at every length.</p></article>')
        found = dcs.exactness(draft)
        self.assertEqual([(where, conditions) for where, _, conditions in found], [
            ('What it says', ['(\\tfrac12-d)L\\ge\\log(p/c)']),       # the displayed condition of its paragraph
            ('What it says', ['c\\ge0', 'c<p']),                             # no display: the inline relation, not the symbol
            ('What it says', [])])                                   # nothing to put beside it: said in the report
        self.assertTrue(found[0][1].startswith('Any such set') and 'It is so' not in found[0][1])
        report = dcs.exactness_report(draft, 0)
        self.assertIn('      beside: no displayed or inline condition in its paragraph', report)
        self.assertTrue(report.endswith('3 such sentences.'))        # the statement and the bookkeeping unread
        self.assertEqual(dcs.exactness(self.DRAFT), [])
        # at most three conditions; a summing-up paragraph first; words left to the other listing or dropped
        more = ('<article><h3>T</h3><h4>Reading</h4>'
                '<p>It is exactly so, with \\(a&lt;b\\), \\(b\\le c\\), \\(c\\geqslant d\\), \\(d&gt;e\\).</p>'
                '<p>The same reviewer read it for every row, not at all quickly.</p>'
                '<p><strong>Goal progress.</strong> Unchanged. The reach is the same, and it cannot extend.</p>'
                '</article>')
        rows = dcs.exactness(more)
        self.assertEqual([(where, len(conditions)) for where, _, conditions in rows],
                         [('Reading', 3), ('Goal progress', 0)])
        self.assertIn('[Goal progress]', dcs.exactness_report(more, 0).splitlines()[1])

    def test_the_title_and_status_line_are_printed_and_summing_up_paragraphs_come_first(self):
        self.assertEqual(dcs.universals_report(self.DRAFT, 0).splitlines()[1], '  [title] A title')   # no status line
        draft = self.DRAFT.replace('<h3>A title</h3>', '<h3>Barriers stop at \\(2w-1\\)</h3>\n'
                                   '<p class="entry-meta">Working proof. No mathematics beyond a cap.</p>')
        lines = dcs.universals_report(draft, 0).splitlines()
        self.assertEqual(lines[1:3], ['  [title] Barriers stop at \\(2w-1\\)',
                                      '  [status line] Working proof. No mathematics beyond a cap.'])
        self.assertEqual(dcs.universals(draft), dcs.universals(self.DRAFT))     # the status line is not listed twice
        labels = [line.split(']')[0].strip(' [') for line in lines[3:-1]]
        self.assertEqual(labels, ['New mathematics', 'Goal progress', 'Structural reason', 'Follow-up',
                                  'What the union does'])

    def test_a_heading_saying_what_is_not_shown_or_naming_a_formula_is_read(self):
        draft = ('<article><h4>What is and is not shown</h4><p>Proved: no barrier exists above the cap.</p>'
                 '<h4>The formula at a point</h4><p>It holds for every density.</p>'
                 '<h4>What was built</h4><p>Nothing here is a conclusion.</p></article>')
        self.assertEqual([where for where, _ in dcs.universals(draft)[0]],
                         ['What is and is not shown', 'The formula at a point'])

    def test_a_word_inside_tex_or_an_identifier_does_not_count(self):
        draft = '<article><p><strong>Reading.</strong> The bound \\(\\text{for all } n\\) of <code>lem:no-drop</code> holds.</p></article>'
        self.assertEqual(dcs.universals(draft)[0], [])


class RunLogTest(unittest.TestCase):
    def test_a_run_is_logged_with_the_draft_s_entry_and_its_number_of_count_sentences(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            log = pathlib.Path(directory) / 'searches.jsonl'
            dcs.log_run(CountsTest.DRAFT, log)
            self.assertFalse(log.exists())      # the searches' log is not created by this tool
            log.write_text('')
            dcs.log_run(CountsTest.DRAFT, log)
            row = json.loads(log.read_text())
            self.assertEqual(row['query'], 'draft_counts entry-2026-10-11-x 8')
            dcs.log_run('<p>no article</p>', log)
            self.assertEqual(json.loads(log.read_text().splitlines()[1])['query'], 'draft_counts - 0')


class BareClaimsAndAnswersTest(unittest.TestCase):
    REGISTRY = {'claims': [{'id': 'prop:local-count-reach',
                            'summary': 'A multiset of points with at most kappa log(|t| + 3) of them in each unit; tilt a; '
                                       'beta_0 the rightmost real part; a margin eta; then T >= 0.'}]}
    DRAFT = ('<article id="entry-y" data-claims="none"><h3>T</h3>'
             '<p><strong>New mathematics.</strong> None of the points hides. The bound holds for \\(\\beta_0\\).</p>'
             '<h4>Reading</h4>'
             '<p>A count of fewer than \\(\\log\\tau\\) zeros of \\(\\zeta\\), the form of prop:local-count-reach, with '
             '\\(\\beta_0\\) fixed. A path research/x:y-z and a link #prop:not-a-claim are no citations.</p>'
             '<p><strong>Follow-up.</strong> Continuing: the reach is the same at every tilt.</p></article>')

    def test_a_claim_written_without_code_tags_is_cited(self):
        found = dcs.citations(self.DRAFT)
        self.assertEqual([claim for claim, _, _ in found], ['prop:local-count-reach'])
        self.assertEqual(dcs.cited('see <code>lem:a</code>, lem:a-b and lem:c'), ['lem:a', 'lem:a-b'])
        # a phrase with a colon, and an identifier inside a path or after another colon, are not claims
        self.assertEqual(dcs.cited('note:well-known, proof:by-induction, q:is-it, x.py:lem:a-b, (cor:c-d).'),
                         ['cor:c-d'])
        # a bare identifier the registry does not hold is listed and fails nothing; in code tags it does
        listed, missing = dcs.report('<article id="e"><p>By lem:not-there it holds.</p></article>', self.REGISTRY, 0)
        self.assertIn('lem:not-there\n  REGISTERED: (not in the registry; written without code tags', listed)
        self.assertEqual(missing, set())
        # a declared claim that no listed sentence cites is said aloud, not passed in a count of zero
        unseen = '<article id="e" data-claims="lem:x_y"><p>The lemma lem:x_y holds.</p></article>'
        self.assertIn('WARNING: the draft declares claims that no listed sentence cites', dcs.report(unseen, {'claims': []}, 0)[0])
        self.assertNotIn('declares claims that no listed', dcs.report(self.DRAFT, self.REGISTRY, 0)[0])

    def test_symbols_of_a_cited_statement_that_the_paragraph_does_not_name_are_listed(self):
        summaries = {c['id']: c['summary'] for c in self.REGISTRY['claims']}
        rows = dcs.unmentioned(self.DRAFT, summaries)
        self.assertEqual([(claim, where, missing) for claim, where, _, missing in rows],
                         [('prop:local-count-reach', 'Reading', ['kappa', 'eta'])])
        # beta_0 is in the paragraph; "eta" is not, though "zeta" and "beta" are: whole symbols are compared
        self.assertTrue(dcs.unmentioned_report(self.DRAFT, summaries, 0).endswith('1 such sentences.'))
        # the draft's own declared claim, a naming paragraph and a search's results are not listed
        own = self.DRAFT.replace('data-claims="none"', 'data-claims="prop:local-count-reach"')
        self.assertEqual(dcs.unmentioned(own, summaries), [])
        named = ('<article id="e" data-claims="none"><p><strong>Verification gate.</strong> Read: '
                 'prop:local-count-reach.</p><h4>Reading</h4><p>It holds. Record search. Found '
                 'prop:local-count-reach.</p></article>')
        self.assertEqual(dcs.unmentioned(named, summaries), [])
        # in a file of several articles each article's own claims are its own
        both = own + self.DRAFT.replace('entry-y', 'entry-z')
        self.assertTrue(dcs.unmentioned_report(both, summaries, 0).endswith('1 such sentences.'))

    def test_sentences_naming_line_numbers_are_listed_beside_those_lines(self):
        draft = ('<article id="e"><h4>What the lines do</h4>'
                 '<p>The step applies the sieve (lines 3 to 9 of the retained file). It needs nothing else. '
                 'At line 2 the weight is fixed, and lines 40 to 41 are cited.</p>'
                 '<p>A pipeline of five stages names no line.</p></article>')
        rows = dcs.naming_lines(draft)
        self.assertEqual([(where, ranges) for where, _, ranges in rows],
                         [('What the lines do', [(3, 9)]), ('What the lines do', [(2, 2), (40, 41)])])
        self.assertIn('2 such sentences, 3 ranges.', dcs.naming_lines_report(draft, 0))
        # several lines, several ranges, a double hyphen, and a range written backwards
        self.assertEqual(dcs.line_ranges('See lines 3, 7 and 10 to 20, lines 30--40 and line 5.'),
                         [(3, 3), (7, 7), (10, 20), (30, 40), (5, 5)])
        self.assertIn('lines 90-12: WRITTEN BACKWARDS',
                      dcs.naming_lines_report('<article id="e"><p>Read lines 90 to 12.</p></article>', 0))
        # a body paragraph that names no line, in a draft that names lines, is listed; a labelled one is not
        self.assertEqual(dcs.unanchored(draft), [('What the lines do', 'A pipeline of five stages names no line.')])
        self.assertTrue(dcs.naming_lines_report(draft, 0).endswith('1 such paragraphs.'))
        labelled = draft.replace('<p>A pipeline', '<p><strong>Limit.</strong> A pipeline')
        self.assertEqual(dcs.unanchored(labelled), [])
        self.assertEqual(dcs.unanchored('<article id="e"><h4>H</h4><p>No line is named anywhere.</p></article>'), [])
        source = [f'text of line {n}' for n in range(1, 13)]
        out = dcs.naming_lines_report(draft, 0, source)
        for expected in ('      3: text of line 3', '      6: text of line 6', '      ...', '      9: text of line 9',
                         '      2: text of line 2', 'lines 40-41: OUTSIDE THE FILE, which has 12 lines'):
            self.assertIn(expected, out)
        self.assertNotIn('7: text of line 7', out)                 # a long range is shown by its ends

    def test_summing_up_sentences_are_answered_by_key_and_a_changed_sentence_is_new(self):
        rows = dcs.summing_up(self.DRAFT)
        self.assertEqual([where for _, where, _ in rows], ['New mathematics', 'Follow-up'])   # not "Reading"
        form = dcs.answers_template(self.DRAFT)
        self.assertEqual(len(dcs.unanswered(self.DRAFT, form)), 2)                 # an empty form answers nothing
        short = form.replace('rests on: \n', 'rests on: the proposition\n')
        self.assertEqual(len(dcs.unanswered(self.DRAFT, short)), 2)                # fewer than four words
        vague = form.replace('rests on: \n', 'rests on: part two of the proposition\n')
        self.assertEqual(len(dcs.unanswered(self.DRAFT, vague)), 2)                # points at nothing
        filled = form.replace('rests on: \n', 'rests on: part two of prop:local-count-reach\n')
        self.assertEqual(dcs.unanswered(self.DRAFT, filled), [])
        for ground in ('the display \\(T\\ge0\\) of its paragraph', 'see #entry-old for the bound',
                       'the saved output research/results/x/out.txt', 'none: a statement of what was not done'):
            self.assertEqual(dcs.unanswered(self.DRAFT, form.replace('rests on: \n', f'rests on: {ground}\n')), [])
        changed = self.DRAFT.replace('None of the points hides', 'None of the points ever hides')
        self.assertEqual([where for _, where, _ in dcs.unanswered(changed, filled)], ['New mathematics'])


if __name__ == '__main__':
    unittest.main()
