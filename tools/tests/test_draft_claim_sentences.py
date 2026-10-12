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


if __name__ == '__main__':
    unittest.main()
