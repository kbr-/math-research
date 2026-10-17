"""Sentences of a draft that cite a claim are listed beside the claim's registered statement."""
import json
import pathlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
    def test_a_width_too_short_to_read_is_refused(self):
        # 16 October 2026: --width 1 passed the brief hook and showed no sentence.
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp, 'd.html')
            draft.write_text('<p>Nothing.</p>')
            with patch.object(sys, 'argv', ['draft_claim_sentences.py', str(draft), '--width', '1']), \
                    patch('sys.stderr'), self.assertRaises(SystemExit) as stop:
                dcs.main()
            self.assertEqual(stop.exception.code, 2)

    def test_raw_tex_comparisons_survive_the_citation_report(self):
        draft = (r'<p>By <code>lem:first</code>, \(4\le D<\epsilon n/8\) and '
                 r'\(P_{<a}>0\) hold.</p><p>Also <code>lem:first</code> gives \[a<b>c\] and $$u<v. W>w$$.</p>')
        out, missing = dcs.report(draft, REGISTRY, 0)
        self.assertFalse(missing)
        self.assertIn(r'By lem:first, \(4\le D<\epsilon n/8\) and \(P_{<a}>0\) hold.', out)
        self.assertIn(r'Also lem:first gives \[a<b>c\] and $$u<v. W>w$$.', out)

    def test_sentences_are_listed_under_their_claim_with_labels(self):
        out, unregistered = dcs.report(DRAFT, REGISTRY, 0)
        self.assertIn('lem:first\n  REGISTERED: First lemma: holds for original instances only.', out)
        self.assertIn('  [New mathematics] By lem:first every core is excluded.', out)
        self.assertIn('  [The count] With prop:second and lem:first the budget is two-sided.', out)
        self.assertEqual(out.count('An item citing lem:first twice'), 1)
        self.assertEqual(unregistered, {'cor:missing'})

    def test_a_cited_claim_is_shown_with_what_it_rests_on(self):
        # 16 October 2026: a step of the proof a cited theorem rests on was repeated as new.
        registry = dict(REGISTRY, relationships=[
            {'type': 'depends_on', 'source': {'id': 'lem:first'}, 'target': {'id': 'lem:base'}},
            {'type': 'cites', 'source': {'id': 'lem:first'}, 'target': {'id': 'lem:other'}}])
        out, _ = dcs.report(DRAFT, registry, 0)
        self.assertIn('  RESTS ON (read their proofs for steps the draft may repeat): lem:base', out)
        self.assertNotIn('lem:other', out.split('RESTS ON')[1].split('\n')[0])

    def test_a_recorded_result_named_without_its_id_is_listed(self):
        # 16 October 2026: an i.i.d. lemma was applied to unequal weights through a sentence naming it in words.
        draft = ('<p><strong>Smallest case.</strong> The lower tail of such a sum is Gaussian by the recorded block '
                 'lower-tail statement once no single weight dominates. By lem:block-lower-tail the tail is '
                 'Gaussian. The recorded statement lem:first applies.</p>')
        found = dcs.unnamed_results(draft)
        self.assertEqual([where for where, _ in found], ['Smallest case'])
        self.assertIn('recorded block lower-tail statement', found[0][1])

    def test_a_declared_claim_is_shown_with_its_spec_summary(self):
        # 16 October 2026: a draft's own claim was never set beside its statement before the review.
        with tempfile.TemporaryDirectory() as root:
            spec = Path(root) / 'research' / 'results' / 'x_20261016' / 'claim-spec.json'
            spec.parent.mkdir(parents=True)
            spec.write_text(json.dumps({'claims': [{'id': 'lem:new-one', 'summary': 'A bound for dyadic grids only.'}]}))
            with patch.object(dcs, 'ROOT', Path(root)):
                out, _ = dcs.report(DRAFT, REGISTRY, 0)
        self.assertIn('lem:new-one\n  REGISTERED: (declared by this draft; spec research/results/x_20261016/'
                      'claim-spec.json) A bound for dyadic grids only.', out)

    def test_a_full_stop_inside_tex_does_not_split_a_sentence(self):
        found = dcs.citations(DRAFT)
        self.assertIn(('lem:new-one', 'New mathematics', 'New mathematics. lem:new-one: a bound \\(s<n/2.5\\) holds.'),
                      found)

    def test_declared_and_unregistered_claims_are_told_apart(self):
        out, _ = dcs.report(DRAFT, REGISTRY, 0)
        self.assertIn('lem:new-one\n  REGISTERED: (declared by this draft; not yet registered, and no spec found)', out)
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

    def test_header_paragraph_does_not_hide_title_or_status(self):
        notebook = ('<article id="entry-old"><h3>Existing title</h3>'
                    '<p><strong>Latest development.</strong> Navigation.</p>'
                    '<p class="entry-meta">Working result.</p></article>')
        draft = '<p>Read <a href="#entry-old">the existing entry</a>.</p>'
        out, missing = dcs.entry_report(draft, notebook, 0)
        self.assertFalse(missing)
        self.assertIn('TITLE: Existing title\n  STATUS: Working result.', out)
        report = dcs.universals_report(notebook, 0)
        self.assertIn('[title] Existing title', report)
        self.assertIn('[status line] Working result.', report)

    def test_missing_status_cannot_borrow_from_next_article(self):
        first = '<article id="entry-first"><h3>First title</h3><p>Body.</p></article>'
        second = ('<article id="entry-second"><h3>Second title</h3>'
                  '<p class="entry-meta">Second status.</p></article>')
        draft = '<p>Read <a href="#entry-first">the first entry</a>.</p>'
        out, missing = dcs.entry_report(draft, first + second, 0)
        self.assertFalse(missing)
        self.assertIn('TITLE: First title\n  STATUS: (NO STATUS LINE)', out)
        report = dcs.universals_report(first + second, 0)
        self.assertIn('[title] First title', report)
        self.assertNotIn('[status line]', report)
        self.assertEqual(dcs.article_header('<article><p>No heading.</p></article>'), None)
        self.assertEqual(dcs.article_header('<article><p class="entry-meta">Before the title.</p>'
                                            '<h3>Actual title</h3></article>'),
                         ('Actual title', None))




class DecisionWordsTest(unittest.TestCase):
    # 17 October 2026: decisions justified as "the same question in a sharper form" and "decided by".
    def test_decision_reasons_are_listed_also_in_bookkeeping(self):
        draft = ('<p><strong>Owed attempt.</strong> The operation asks the same question in a sharper form.</p>'
                 '<p><strong>Follow-up.</strong> The split is decided by this entry\'s statements.</p>')
        self.assertEqual(len(dcs.exactness(draft)), 2)

    def test_conjectured_order_is_listed(self):
        # 17 October 2026: a Bearing claimed the conjectured order while its constant exceeded the goal's.
        draft = ('<p><strong>Goal progress.</strong> <strong>Bearing.</strong> The functions satisfy the goal '
                 'at the conjectured order.</p>')
        self.assertEqual(len(dcs.exactness(draft)), 1)

    def test_other_bookkeeping_words_stay_unlisted(self):
        draft = '<p><strong>Owed attempt.</strong> It was made exactly as named.</p>'
        self.assertEqual(dcs.exactness(draft), [])


class ComparisonsTest(unittest.TestCase):
    # 17 October 2026: an Owed attempt called a bound "below" a target it exceeded.
    def test_a_comparison_in_a_bookkeeping_paragraph_is_listed(self):
        draft = ('<p><strong>Owed attempt.</strong> Its purpose is met at \\((\\log\\log N)^{1/4}\\), below its '
                 'target \\(\\sqrt{N\\log N}\\).</p>')
        self.assertEqual(len(dcs.comparisons(draft)), 1)

    def test_dismissals_of_a_case_are_listed(self):
        # 17 October 2026: "which the cost keeps small" and "not improved", each wrong at the instance.
        for sentence in ('its bound times \\(y\\delta_0\\), which the cost keeps small.',
                         'it leaves \\(g\\) at the fine-grid order, not improved.'):
            with self.subTest(sentence=sentence):
                draft = f'<p><strong>Follow-up.</strong> A layer with \\(P<1\\): {sentence}</p>'
                self.assertEqual(len(dcs.comparisons(draft)), 1)

    def test_statements_and_words_without_formulas_are_not_listed(self):
        draft = ('<p><strong>Statement.</strong> Then \\(a\\) is below \\(b\\).</p>'
                 '<p><strong>Review.</strong> The objection above was right.</p>')
        self.assertEqual(dcs.comparisons(draft), [])


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


class OwnSummariesTest(unittest.TestCase):
    def test_summaries_are_set_beside_the_drafts_own_statement(self):
        # 16 October 2026: the ledger said "is a matched image" where the lemma gave that image minus H.
        draft = ('<article><h3>16 October 2026 — Remainder identity</h3><p class="entry-meta">Working proof.</p>'
                 '<p><strong>Lemma (remainder identity).</strong> Without logical axioms, H+Q is a matched image, '
                 'and the remainder is that image minus H.</p>'
                 '<p><strong>Proof.</strong> Compare the terms.</p>'
                 '<p><strong>New mathematics.</strong> The remainder is the image. It is small.</p>'
                 '<p><strong>Degenerate cases.</strong> None.</p>'
                 '<h4 id="remainder-ledger">Remainder ledger</h4><ul><li><strong>Size.</strong> The remainder is a '
                 'matched image.</li></ul></article>')
        statements, summaries = dcs.own_summaries(draft)
        self.assertEqual([label for label, _ in statements], ['Lemma (remainder identity)'])
        self.assertIn('minus H', statements[0][1])
        self.assertEqual([where for where, _ in summaries], ['title', 'New mathematics', 'New mathematics', 'ledger'])
        self.assertEqual(summaries[1][1], 'The remainder is the image.')
        self.assertIn('Size. The remainder is a matched image.', summaries[3][1])
        report = dcs.own_summaries_report(draft, 0)
        self.assertIn('STATEMENT [Lemma (remainder identity)]', report)
        self.assertIn('4 summary sentences beside 1 statements.', report)
        # A draft that proves no statement of its own gets no listing.
        self.assertEqual(dcs.own_summaries('<p><strong>New mathematics.</strong> None.</p>'), ([], []))


class ConstructionStepsTest(unittest.TestCase):
    def test_unsourced_proof_sentences_about_a_recorded_construction_are_listed(self):
        # 16 October 2026: the first draft of the matched jet envelope wrote this from a picture of the compiler.
        draft = ('<p><strong>Proof.</strong> (a) Every compiler term carries exactly one placeholder (the compiler is '
                 'zero-respecting: an input line contributes its prefix times its clause placeholder), so '
                 '\\(A_t(x,0)=0\\). The record states that the segment "specializes to one minus its final prefix '
                 'product". By <code>thm:used-node-jet-erasure</code> the transform keeps the generators. '
                 'Then \\(D(x,0)=0\\) and \\(D(x,G)=1\\).</p>'
                 '<p><strong>Degenerate cases.</strong> The compiler of an empty list has no terms.</p>')
        found, read = dcs.construction_steps(draft)
        self.assertEqual(read, 4)
        self.assertEqual([where for where, _ in found], ['Proof'])
        self.assertTrue(found[0][1].startswith('(a) Every compiler term carries exactly one placeholder'))
        # Accepted, each with a listed word: a quoted record passage, a cited claim, an entry anchor, a sentence
        # outside a proof, and a proof sentence about the draft's own objects.
        report = dcs.construction_report(draft, 0)
        self.assertIn('1 such sentences of 4 proof sentences read.', report)
        anchored = '<p><strong>Proof.</strong> The construction keeps each tag (<a href="#entry-2026-10-12-used-tag-image">its record</a>).</p>'
        self.assertEqual(dcs.construction_steps(anchored)[0], [])
        # An attribute's quotes are no quotation: a link elsewhere does not source the sentence.
        linked = ('<p><strong>Proof.</strong> The compiler keeps each tag, as <a href="research/results/some-long'
                  '-file.txt">the run</a> shows.</p>')
        self.assertEqual(len(dcs.construction_steps(linked)[0]), 1)


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


class PairingsTest(unittest.TestCase):
    DRAFT = ('<article id="entry-2026-10-16-x"><h3>T</h3><p class="entry-meta">S.</p>'
             '<p><strong>Lemma.</strong> No class is lost.</p>'
             '<p><strong>New mathematics.</strong> The cube gives <code>lem:cube</code> at every level. '
             'No level-wise floor follows.</p>'
             '<p><strong>Correction.</strong> Its conditional-use paragraph in <code>lem:sparse</code> applies '
             'to error kernels.</p></article>')
    NOTEBOOK = ('<article id="entry-a"><h3>Old</h3><p class="entry-meta">Old status.</p><p>Setting words here. '
                'Conditional use. The bound applies to the surviving weight of the common-kernel criterion, '
                'not to error kernels.</p></article>')
    CLAIMS = [{'id': 'lem:cube', 'summary': 'A free cube at each level.', 'record': '[x](#entry-b)'},
              {'id': 'lem:sparse', 'summary': 'Sparse weights keep h/s.', 'record': '[x](https://e/#entry-a)'}]

    def test_an_uncited_denial_is_paired_with_its_paragraph_s_claims_and_a_described_remark_with_its_record(self):
        rows = dcs.pairings(self.DRAFT)
        self.assertEqual([(where, claims) for where, _, claims, _ in rows],
                         [('New mathematics', ['lem:cube']), ('Correction', ['lem:sparse'])])
        self.assertEqual(rows[0][1], 'No level-wise floor follows.')      # the statement's own denial is skipped
        out = dcs.pairings_report(self.DRAFT, self.CLAIMS, self.NOTEBOOK, 0)
        self.assertIn('lem:cube: A free cube at each level.', out)
        self.assertIn('its record #entry-a: …', out)
        self.assertIn('surviving weight of the common-kernel criterion', out)
        self.assertNotIn('Old status', out)                               # title and status line are not passages
        self.assertIn('2 such sentences.', out)
        self.assertIsNone(dcs.best_window('<p>unrelated prose only</p>', {'kernels'}))


class ConverseUseTest(unittest.TestCase):
    # The registered statement of 16 October 2026 that a draft used backwards, shortened.
    SUMMARIES = {'cor:edge-supported-error-ratio': (
        'Edge-supported error ratio: let an error tuple contain a component E = P m_gamma. If c_E(K) > 0, then '
        'some compatible label a\' of T has P(a\') != 0, c_E(K) >= q_T(K) >= h(K)/3^tau, and the ratio is bounded.')}

    def test_the_relation_assumed_in_an_if_clause_is_read(self):
        self.assertIn(('c(K)', '>', '0'), dcs.assumed_relations(self.SUMMARIES['cor:edge-supported-error-ratio']))

    def test_the_sentence_that_derived_the_hypothesis_is_flagged(self):
        draft = (r'<p><strong>Proof.</strong> The component, nonzero at that label, gives '
                 r'\(c(K)\ge q_T(K)&gt;0\) by part (i) of cor:edge-supported-error-ratio.</p>')
        flagged = dcs.converse_uses(draft, self.SUMMARIES)
        self.assertEqual([(c, r) for c, _, _, r in flagged], [('cor:edge-supported-error-ratio', ('c(K)', '>', '0'))])
        self.assertIn('CONVERSE USE?', dcs.converse_report(draft, self.SUMMARIES, 0))

    def test_a_use_that_assumes_the_hypothesis_is_not_flagged(self):
        draft = (r'<p>Since \(c_E(K)&gt;0\) was shown above, cor:edge-supported-error-ratio gives '
                 r'\(c_E(K)\ge q_T(K)\) and the ratio bound.</p>')
        self.assertEqual(dcs.converse_uses(draft, self.SUMMARIES), [])
        self.assertIn('No citing sentence derives', dcs.converse_report(draft, self.SUMMARIES, 0))

    def test_rewordings_of_the_mistake_are_flagged(self):
        for sentence in (r'Part (i) of cor:edge-supported-error-ratio applied with \(T\) as label set gives '
                         r'\(c(K)\ge q_T(K)&gt;0\).',
                         r'cor:edge-supported-error-ratio combined with \(q_T(K)&gt;0\) gives \(c(K)\ge q_T(K)&gt;0\).',
                         r'By cor:edge-supported-error-ratio, \(0&lt;q_T(K)\le c(K)\).',
                         r'By cor:edge-supported-error-ratio the rank is positive: c_E(K) > 0.'):
            with self.subTest(sentence=sentence):
                self.assertTrue(dcs.converse_uses(f'<p>{sentence}</p>', self.SUMMARIES))

    def test_supplied_hypotheses_are_not_flagged(self):
        for sentence in (r'For \(c_E(K)&gt;0\), cor:edge-supported-error-ratio gives \(c_E(K)\ge q_T(K)\).',
                         r'Let \(c_E(K)&gt;0\); then cor:edge-supported-error-ratio bounds the ratio.',
                         r'Assume that \(c_E(K)&gt;0\), so that cor:edge-supported-error-ratio applies.'):
            with self.subTest(sentence=sentence):
                self.assertEqual(dcs.converse_uses(f'<p>{sentence}</p>', self.SUMMARIES), [])

    def test_hypothesis_clauses_end_where_they_should(self):
        self.assertEqual(dcs.assumed_relations('Ratio: if c_E(K) > 0, the ratio R(K) > 1 holds.'),
                         [('c(K)', '>', '0')])
        self.assertEqual(dcs.assumed_relations('R(K) > 1 if and only if c_E(K) > 0.'), [])
        self.assertEqual(dcs.assumed_relations('R(K) > 1 only if c_E(K) > 0.'), [])
        self.assertIn(('c(K)', '>', '0'), dcs.assumed_relations('Let E be a component with c_E(K) > 0.'))
        self.assertIn(('h', '>', '0'), dcs.assumed_relations('Suppose h > 0, then the rank grows.'))

    def test_a_weak_chain_does_not_state_a_strict_relation(self):
        self.assertFalse(dcs._derives(['c(K)', 'q(K)', '0'], ['>=', '>='], ('c(K)', '>', '0')))
        self.assertTrue(dcs._derives(['c(K)', 'q(K)', '0'], ['>=', '>'], ('c(K)', '>', '0')))
        self.assertFalse(dcs._derives(['c(K)', 'q(K)', '0'], ['<=', '>'], ('c(K)', '>', '0')))


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

    def test_a_summing_up_sentence_applying_a_claim_beyond_its_symbols_needs_a_within_answer(self):
        # 17 October 2026: a Bearing applied a conversion lemma to grid functions outside the lemma's image.
        summaries = {'lem:smeared-conv': 'For Y evenly spread and delta >= 20/sqrt N, every class function G has its '
                                 'smeared discrepancy within 160 e sqrt N of the X-term of its cell averages.'}
        draft = ('<article id="x" data-claims="lem:own"><p><strong>Goal progress.</strong> Unchanged. '
                 '<strong>Bearing.</strong> Every chain has \\(|D(g)|\\le C\\), and by lem:smeared-conv these are bounds '
                 'of the smeared form.</p><p><strong>Proof.</strong> By lem:smeared-conv the bound follows.</p>'
                 '</article>')
        self.assertEqual([row[3] for row in dcs.domain_rows(draft, summaries)],
                         ['lem:smeared-conv'])                                                   # Proof: not asked
        form = dcs.answers_template(draft, summaries)
        self.assertEqual(len(dcs.unbounded(draft, form, summaries)), 1)
        filled = form.replace('within: \n', 'within: only class functions whose cell averages are chains\n')
        self.assertEqual(dcs.unbounded(draft, filled, summaries), [])
        named = draft.replace('these are bounds', 'with \\(\\delta\\ge20/\\sqrt N\\) these are bounds')
        self.assertEqual(dcs.domain_rows(named, summaries), [])                    # every symbol named: not asked

    def test_one_within_text_for_sentences_citing_different_claims_is_refused(self):
        # 17 October 2026: three within lines, for three claims, got one generic sentence.
        summaries = {'lem:smeared-conv': 'For Y evenly spread and delta >= 20/sqrt N, every class function G has its '
                                         'smeared discrepancy within 160 e sqrt N of the X-term of its cell averages.',
                     'cor:other-bound': 'For every graph with expansion epsilon and degree Delta the ratio R is at '
                                        'most 3 when tau <= D.'}
        draft = ('<article id="x" data-claims="lem:own"><p><strong>Goal progress.</strong> Unchanged. '
                 '<strong>Bearing.</strong> Every chain has \\(|D(g)|\\le C\\), and by lem:smeared-conv these are bounds '
                 'of the smeared form. Every family meets cor:other-bound, so no ratio exceeds three.</p></article>')
        form = dcs.answers_template(draft, summaries)
        generic = form.replace('within: \n', 'within: the head item and its sub-idea, in its own setting\n')
        self.assertEqual(len(dcs.repeated_within(draft, generic, summaries)), 1)
        lines = iter(['within: only chains, whose cell averages are class functions\n',
                      'within: the families are graphs of the stated expansion and degree\n'])
        import re
        specific = re.sub(r'within: \n', lambda _: next(lines), form)
        self.assertEqual(dcs.repeated_within(draft, specific, summaries), [])

    def test_a_follow_up_universal_needs_an_extreme_answer(self):
        # 17 October 2026: "lies on every boundary", answered by its source, was false at an extreme member.
        draft = ('<article id="x"><p><strong>Follow-up.</strong> Continuing. Next attempt: nested unions of '
                 'translates; their back boundary lies on every \\(\\partial A_k\\), so its multiplicity is '
                 '\\(K\\).</p><p><strong>Proof.</strong> Every edge is counted.</p></article>')
        self.assertEqual([where for _, where, _ in dcs.extreme_rows(draft)], ['Follow-up'])   # Proof: not asked
        form = dcs.answers_template(draft)
        self.assertEqual(len(dcs.unextreme(draft, form)), 1)
        filled = form.replace('extreme: \n', 'extreme: a translate that covers back edges lowers it\n')
        self.assertEqual(dcs.unextreme(draft, filled), [])

    def test_a_sentence_using_a_declared_part_by_letter_is_listed_under_the_declared_claim(self):
        # 17 October 2026: "by (a) no fixed-kernel sandpile adds one" dropped the statement's reversibility and was
        # never set beside the statement, naming no claim.
        draft = ('<article id="x" data-claims="lem:own-thing"><p><strong>Statement.</strong> (a) Every reversible '
                 'stage is electrical. (b) Another rule is not.</p><p><strong>Proof.</strong> (a) shows itself; by '
                 '(a) the rest.</p><p><strong>Follow-up.</strong> Continuing: by (a) no fixed-kernel sandpile adds '
                 'one. Part (b) shows a state-dependent rule leaves them. Then (a) gives the slack pair. The '
                 'flow (in cells) is computed. That lemma\'s (b) applies too.</p></article>')
        rows = [(claim, where, sentence[:20]) for claim, where, sentence in dcs.citations(draft)]
        self.assertEqual(rows, [('lem:own-thing', 'Follow-up', 'Follow-up. Continuin'),
                                ('lem:own-thing', 'Follow-up', 'Part (b) shows a sta'),
                                ('lem:own-thing', 'Follow-up', 'Then (a) gives the s')])
        # without a declared claim nothing is attributed
        self.assertEqual(dcs.citations(draft.replace('lem:own-thing', 'none')), [])

    def test_an_answer_that_limits_its_sentence_by_a_word_the_sentence_lacks_is_a_gap(self):
        form = dcs.answers_template(self.DRAFT)
        answer = lambda words: form.replace('rests on: \n', f'rests on: {words}\n')
        self.assertEqual(dcs.qualifier_gaps(self.DRAFT, answer('part two of prop:local-count-reach')), [])
        gaps = dcs.qualifier_gaps(self.DRAFT, answer('prop:local-count-reach, one direction only, as read'))
        self.assertEqual([(where, missing) for _, where, _, missing in gaps],
                         [('New mathematics', ['as read', 'one direction', 'only']),
                          ('Follow-up', ['as read', 'one direction', 'only'])])
        self.assertIn('the answer says: as read, one direction, only', dcs.qualifier_gaps_report(gaps))
        # the registered words in quotation marks are the claim's, not the answer's limit
        self.assertEqual(dcs.qualifier_gaps(self.DRAFT, answer('prop:local-count-reach, "under a count only"')), [])
        # an answer that rests on nothing limits nothing; an unanswered sentence is the other check's
        self.assertEqual(dcs.qualifier_gaps(self.DRAFT, answer('none: only a statement of what was not done')), [])
        self.assertEqual(dcs.qualifier_gaps(self.DRAFT, form), [])
        # the sentence itself carries the limit
        limited = self.DRAFT.replace('The bound holds for', 'Under a count only, the bound holds for')
        left = dcs.qualifier_gaps(limited, dcs.answers_template(limited).replace(
            'rests on: \n', 'rests on: prop:local-count-reach under a count only\n'))
        self.assertEqual(len(left), 2)
        self.assertFalse(any('Under a count only' in sentence for _, _, sentence, _ in left))
        # or the answer says where the entry states it, in five or more of the entry's consecutive words
        said = answer('prop:local-count-reach, given a count; stated in: A count of fewer than zeros')
        self.assertEqual(len(dcs.qualifier_gaps(self.DRAFT, said)), 2)             # not consecutive in the entry
        said = answer('prop:local-count-reach, given a count; stated in: "the form of prop:local-count-reach, with"')
        self.assertEqual(len(dcs.qualifier_gaps(self.DRAFT, said)), 2)             # the passage lacks "given"
        stating = self.DRAFT.replace('<h4>Reading</h4>', '<h4>Reading</h4><p>All this is given a count of the '
                                     'points in each unit.</p>')
        form2 = dcs.answers_template(stating)
        ok = form2.replace('rests on: \n', 'rests on: prop:local-count-reach, given a count; stated in: this is '
                           'given a count of the points\n')
        self.assertEqual(dcs.qualifier_gaps(stating, ok), [])
        # the sentence asked about cannot be its own place of statement, and curly quotation marks are quotes
        own = form2.replace('rests on: \n', 'rests on: prop:local-count-reach given it; stated in: the reach is '
                            'the same at every tilt\n')
        self.assertIn('Follow-up', [where for _, where, _, _ in dcs.qualifier_gaps(stating, own)])
        self.assertEqual(dcs.qualifier_gaps(self.DRAFT, answer('prop:local-count-reach, “under a count only”')), [])
        # the count over a file of articles counts a repeated sentence once
        two = self.DRAFT + self.DRAFT.replace('id="entry-y"', 'id="entry-z"')
        out = dcs.gaps_count(two, answer('prop:local-count-reach, one side only'), 1)
        self.assertIn('2\t2\tentry-y', out)
        self.assertTrue(out.endswith('2 distinct answered summing-up sentences in 2 articles; 2 of them have an '
                                     'answer that limits the sentence by a word it lacks (second column), from 1 '
                                     'answers files.'))
        self.assertEqual(len(dcs.qualifier_gaps(self.DRAFT, answer('prop:local-count-reach given it; stated in: '
                                                                   'the form of'))), 2)   # fewer than five words


class NewListingsTest(unittest.TestCase):
    """The vanishing-factor, hypothesis-restriction and unread-section listings (17 October 2026)."""

    def test_a_vanishing_factor_without_its_place_is_listed(self):
        # 16 October 2026: a factor inside a commutator certificate was used as if it stood outside.
        draft = ('<article id="entry-x"><p><strong>Proof.</strong> The factor \\(1-L_k\\) is zero at \\(a\\), so '
                 'the term vanishes. The factor sits outside the commutator, so it vanishes there too. '
                 'Products of \\(D+1\\) elements vanish.</p></article>')
        found = dcs.vanishing_steps(draft)
        self.assertEqual(len(found), 1)
        self.assertIn('is zero at', found[0][1])

    def test_a_restriction_no_proof_step_names_is_listed(self):
        # 16 October 2026: characteristic two was stated where the proof needed only 0/1-valued definitions.
        draft = ('<article id="entry-x"><p><strong>Hypotheses, each with its step.</strong> Characteristic two: '
                 'the substitution. Acyclic definitions: the map \\(\\varphi\\).</p><p><strong>Proof.</strong> The '
                 'map is defined because the definitions are acyclic; the substitution is a ring map.</p></article>')
        self.assertEqual([r for r, _ in dcs.hypothesis_restrictions(draft)], ['characteristic two'])
        self.assertEqual(dcs.hypothesis_restrictions(draft.replace('ring map', 'ring map in characteristic two')), [])

    def test_a_notebook_adds_its_own_words_and_a_denial_is_no_use(self):
        notebook = '<section id="working-context" data-listing-words="restriction=nonrecursive; position=commutators?">'
        words = dcs.listing_words(notebook)
        self.assertEqual(words, {'restriction': 'nonrecursive', 'position': 'commutators?'})
        draft = ('<article id="entry-x"><p><strong>Hypotheses, each with its step.</strong> Nonrecursive '
                 'definitions: the count. Characteristic two: the substitution.</p><p><strong>Proof.</strong> '
                 'Characteristic two is not used here. The factor \\(1-L_k\\) is zero in the commutator, so the '
                 'term vanishes.</p></article>')
        self.assertEqual([r for r, _ in dcs.hypothesis_restrictions(draft)], ['characteristic two'])
        self.assertEqual([r for r, _ in dcs.hypothesis_restrictions(draft, words)],
                         ['nonrecursive', 'characteristic two'])
        self.assertEqual(len(dcs.vanishing_steps(draft)), 1)              # the general words do not place it
        self.assertEqual(dcs.vanishing_steps(draft, words), [])           # the notebook's commutator does

    def test_a_part_listed_as_unread_is_listed_where_cited(self):
        # 16 October 2026: a draft cited a section its own spec listed as not read.
        spec = {'claims': [{'id': 'imp:tradeoff', 'assessment': 'Use as imported; Sections 2 to 4 beyond Lemma '
                                                                '3.1 not read.'}]}
        registry = {'claims': [{'id': 'imp:other', 'summary': 'x', 'assessment': 'Theorem 8 read; the proof of '
                                'Proposition 24 was not read; the import rests on its statement.'}]}
        draft = ('<article id="entry-x"><p>By Section 3 of the source the degree bound holds. imp:other\'s '
                 'Proposition 24 gives the projection. Section 5 is read.</p></article>')
        found = dcs.unread_citations(draft, registry, spec)
        self.assertEqual([part for _, part, _ in found], ['section 3'])
        self.assertEqual(dcs.unread_citations(draft, registry), [])        # the statement of Proposition 24 was read

    def test_the_motivating_spec_marks_its_unread_sections(self):
        spec = json.loads((pathlib.Path(__file__).resolve().parents[2] /
                           'research/results/extended_pigeonhole_tradeoff_20261016/claim-spec.json').read_text())
        parts = {(kind, n) for _, kind, n in dcs.unread_parts({'claims': []}, set(), spec)}
        self.assertTrue({('section', '2'), ('section', '3'), ('section', '4')} <= parts, parts)


if __name__ == '__main__':
    unittest.main()
