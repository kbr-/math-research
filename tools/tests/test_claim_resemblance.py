"""The draft-time resemblance search: a spec's claims against registered summaries."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

TOOLS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import claim_resemblance as tool

REGISTERED = [
    {'id': 'ex:old-degrees', 'summary': 'Exact refutation degrees of random parity clause systems at twenty variables.'},
    {'id': 'lem:unrelated', 'summary': 'A spectral sequence of a filtered complex converges under a finiteness condition.'},
    {'id': 'prop:other', 'summary': 'Colourings of circular cliques have logarithmic game value.'},
]
SPEC = {'claims': [{'id': 'ex:new-degrees',
                    'summary': 'Exact refutation degrees of random parity clause systems at twenty and thirty variables.'}],
        'relationships': [['ex:new-degrees', 'cites', 'prop:other', 'a note']]}


class ClassBoundsTest(unittest.TestCase):
    HERE = '[r](https://example.org/branches/here/#entry-a)'
    PROVED = 'working_proof'
    TABLE = [{'name': 'Lipschitz functions', 'object': r'\b(?:\d-)?lipschitz (?:functions?|profiles?)|\bramps?\b',
              'hypothesis': r'\bevery lipschitz g\b', 'within': ['functions Lipschitz on cells']},
             {'name': 'functions Lipschitz on cells', 'object': r'lipschitz on (?:each )?cells?',
              'hypothesis': r'lipschitz on each (?:open )?cell', 'within': []},
             {'name': 'nested chains', 'object': r'\bnested chains?\b', 'hypothesis': r'\bnested chain', 'within': []}]
    REG = [{'id': 'lem:split', 'record': HERE, 'mathematical_status': PROVED,
            'summary': 'For every bounded G Lipschitz on each open cell of mesh 2^(-j): the bound.'},
           {'id': 'lem:elsewhere', 'record': '[r](https://example.org/branches/other/#entry-b)',
            'mathematical_status': PROVED, 'summary': 'Every G Lipschitz on each cell: a bound.'},
           {'id': 'conj:open', 'record': HERE, 'mathematical_status': 'conjecture',
            'summary': 'Every G Lipschitz on each cell: a conjectured bound.'},
           {'id': 'lem:rounding', 'record': HERE, 'mathematical_status': PROVED,
            'summary': 'Every grid function h of cost at most M: it rounds to r, a nested chain.'}]

    def test_a_ramp_lists_the_bound_of_the_class_containing_it(self):
        # 18 October 2026: a ramp lemma was proved by a new chaining while the cellwise split gave it at once.
        found = tool.class_listing(self.REG, 'For every 1-Lipschitz profile phi the ramp R has a bound.',
                                   self.TABLE, 'branches/here/')
        self.assertEqual([(name, [r[0] for r in rows]) for name, rows, _ in found],
                         [('functions Lipschitz on cells', ['lem:split'])])
        self.assertEqual(tool.class_listing(self.REG, 'Each ramp of width w.', self.TABLE, 'branches/here/')[0][1][0][0],
                         'lem:split')

    def test_words_outside_the_class_and_cited_ids_do_not_fire(self):
        for text in ('On the event of lem:cellwise-lipschitz-split, a count of points.',
                     'A Lipschitz cost on the edges of a Markov chain.',
                     'The down-set {s < phi(t)} has a bound.'):
            with self.subTest(text=text):
                self.assertEqual(tool.class_listing(self.REG, text, self.TABLE, 'branches/here/'), [])

    def test_only_hypotheses_proved_claims_and_the_notebooks_own_are_listed(self):
        found = tool.class_listing(self.REG, 'Every nested chain g of cost 2.', self.TABLE, 'branches/here/')
        # lem:rounding names a nested chain only in its conclusion, after the colon (a conclusion written before
        # the first colon is listed: the false listing of the replay's judgement)
        self.assertEqual(found, [])
        found = tool.class_listing(self.REG, 'G Lipschitz on each cell', self.TABLE, 'branches/here/')
        self.assertEqual([r[0] for r in found[0][1]], ['lem:split'])     # not the conjecture, not another notebook's

    def test_the_cut_off_keeps_the_newest(self):
        reg = [dict(self.REG[0], id=f'lem:s{i}') for i in range(5)]
        found = tool.class_listing(reg, 'G Lipschitz on each cell', self.TABLE, 'branches/here/', limit=2)
        self.assertEqual(([r[0] for r in found[0][1]], found[0][2]), (['lem:s3', 'lem:s4'], 5))

    def test_claim_ids_are_stripped_by_the_registry_s_own_prefixes(self):
        pattern = tool.claim_id_pattern([{'id': 'imp:lipschitz-thing'}, {'id': 'lem:x'}])
        self.assertEqual(pattern.sub(' ', 'by imp:lipschitz-thing and lem:x').split(), ['by', 'and'])

    def test_the_marker_names_a_side_notebook_and_not_the_main_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            side = pathlib.Path(tmp) / 'research' / 'branches' / 'here' / 'notebook.html'
            side.parent.mkdir(parents=True)
            side.write_text('')
            self.assertEqual(tool.notebook_marker(side), 'branches/here/')
            self.assertIsNone(tool.notebook_marker(pathlib.Path(tmp) / 'notebook.html'))
            self.assertEqual(tool.class_table(side), [])                    # no table declared, no listing
            (side.parent / 'claim-classes.json').write_text(json.dumps({'classes': self.TABLE}))
            self.assertEqual(len(tool.class_table(side)), 3)

    def test_the_hypothesis_skips_a_setting_and_stops_at_the_conclusion(self):
        ids = tool.claim_id_pattern([{'id': 'lem:x'}])
        self.assertEqual(tool.hypothesis_part('For X i.i.d. uniform, with probability tending to one: for every j with '
                                              '1 <= j <= l and every Lipschitz G: |sum_i G(X_i)| <= C.', ids),
                         'for every j with 1 <= j <= l and every lipschitz g')
        self.assertNotIn('nested chain', tool.hypothesis_part('Every grid function h some theta makes r a nested chain'
                                                              ' with cost bounded.', ids))

    def test_cellwise_in_a_conclusion_does_not_fire_the_notebooks_table(self):
        notebook = TOOLS.parent / 'research' / 'branches' / 'ultimate-matching' / 'notebook.html'
        table = tool.class_table(notebook)
        self.assertEqual(tool.object_classes('The duality for flows: its cellwise sum is the functional.', table), [])

    def test_the_exposing_case_lists_the_cellwise_split_on_the_record(self):
        # lem:monotone-path-ramps against the claims registered before it, through the notebook's own table
        notebook = TOOLS.parent / 'research' / 'branches' / 'ultimate-matching' / 'notebook.html'
        registry = json.loads((TOOLS.parent / 'research' / 'claims' / 'index.json').read_text())['claims']
        ids = [c['id'] for c in registry]
        self.assertIn('lem:monotone-path-ramps', ids, 'the exposing claim was renamed: update this test')
        index = ids.index('lem:monotone-path-ramps')
        text = registry[index]['summary']                      # the registered summary, not a paraphrase
        found = tool.class_listing(registry[:index], text, tool.class_table(notebook), 'branches/ultimate-matching/')
        listed = {other for _, rows, _ in found for other, _ in rows}
        self.assertIn('lem:cellwise-lipschitz-split', listed)

    def test_the_finisher_refuses_an_entry_that_names_no_listed_bound(self):
        import resemblance_coverage as coverage
        claims = self.REG + [{'id': 'lem:ramps', 'record': self.HERE, 'mathematical_status': self.PROVED,
                              'summary': 'For every 1-Lipschitz profile phi the ramp R has a bound.'}]
        entry = ('<article id="e" data-kind="research" data-claims="lem:ramps"><p><strong>Record comparison.'
                 '</strong> New, by a chaining.</p></article>')
        self.assertEqual(coverage.class_missing(entry, claims, self.TABLE, 'branches/here/'),
                         [('lem:ramps', 'functions Lipschitz on cells', 'lem:split')])
        named = entry.replace('New, by a chaining.', 'lem:split, at the mesh of the ramp, gives it.')
        self.assertEqual(coverage.class_missing(named, claims, self.TABLE, 'branches/here/'), [])


class SiblingTest(unittest.TestCase):
    def test_claims_registered_beside_a_related_claim_are_listed_unless_related(self):
        # 16 October 2026: a spec related thm:conjunction-quotient-rank and missed its sibling, the contraction.
        entry = '[Cut code](https://example.org/#entry-2026-10-07-cut-code)'
        registered = [{'id': 'thm:rank', 'summary': 'Exact rank.', 'record': entry},
                      {'id': 'thm:contraction', 'summary': 'Contraction of the count.', 'record': entry},
                      {'id': 'lem:classes', 'summary': 'Classes.', 'record': entry},
                      {'id': 'lem:alone', 'summary': 'Elsewhere.', 'record': '[x](https://example.org/#entry-x)'}]
        spec = {'claims': [{'id': 'cor:new', 'summary': 's'}],
                'relationships': [['cor:new', 'cites', 'thm:rank', 'n'], ['cor:new', 'cites', 'lem:classes', 'n'],
                                  ['cor:new', 'cites', 'lem:alone', 'n']]}
        found = tool.siblings(registered, spec)
        self.assertEqual([(ident, [other for other, _ in rows]) for ident, rows in found],
                         [('lem:classes', ['thm:contraction']), ('thm:rank', ['thm:contraction'])])
        # Related in the spec, it is no longer listed.
        spec['relationships'].append(['cor:new', 'depends_on', 'thm:contraction', 'n'])
        self.assertEqual(tool.siblings(registered, spec), [])


class ResemblanceTest(unittest.TestCase):
    def test_spec_values_outside_the_schema_are_reported(self):
        bad = {'claims': [{'id': 'ex:a', 'status': 'finite_check', 'category': 'computation', 'novelty': 'none'}],
               'relationships': [['ex:a', 'uses', 'lem:b', 'x']]}
        found = tool.spec_value_problems(bad)
        self.assertEqual(len(found), 3)
        self.assertTrue(any("'computation'" in f for f in found))
        self.assertTrue(any("'uses'" in f for f in found))
        self.assertEqual(tool.spec_value_problems(SPEC), [])

    def test_the_nearest_registered_claim_comes_first(self):
        (ident, found), = tool.resemblances(REGISTERED, SPEC, 2)
        self.assertEqual(ident, 'ex:new-degrees')
        self.assertEqual(found[0][1], 'ex:old-degrees')
        self.assertGreater(found[0][0], tool.SIMILAR_AT)
        self.assertEqual(len(found), 2)

    def test_a_claim_is_not_compared_with_its_own_registration(self):
        again = {'claims': [dict(REGISTERED[0])]}
        (_, found), = tool.resemblances(REGISTERED, again, 3)
        self.assertNotIn('ex:old-degrees', [ident for _, ident, _ in found])

    def test_a_registered_sibling_of_the_spec_is_not_compared(self):
        sibling = {'id': 'ex:twin-degrees', 'summary': SPEC['claims'][0]['summary']}
        spec = {'claims': SPEC['claims'] + [sibling]}
        results = dict(tool.resemblances(REGISTERED + [sibling], spec, 3))
        self.assertNotIn('ex:twin-degrees', [ident for _, ident, _ in results['ex:new-degrees']])
        self.assertEqual(results['ex:new-degrees'][0][1], 'ex:old-degrees')

    def test_the_command_prints_scores_and_marks_related_claims(self):
        with tempfile.TemporaryDirectory() as folder:
            registry = pathlib.Path(folder) / 'index.json'
            registry.write_text(json.dumps({'claims': REGISTERED}))
            spec = pathlib.Path(folder) / 'spec.json'
            spec.write_text(json.dumps(SPEC))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(tool.main([str(spec), '--registry', str(registry), '--count', '3']), 0)
        text = out.getvalue()
        self.assertIn('3 registered claims compared', text)
        self.assertRegex(text, r'0\.\d\d ex:old-degrees: Exact refutation')
        self.assertIn('prop:other (related in the spec)', text)
        # the listed claims are to be applied to the next attempt, not only compared for generality
        self.assertIn('apply each to the entry\'s next attempt', text)

    def test_a_queued_item_the_claim_answers_is_listed_and_an_unrelated_one_is_not(self):
        notebook = ('<section id="lead-queue"><h2>Queue</h2><ol>'
                    '<li data-check="entry-a:s1"><a href="#entry-a">entry-a:s1</a> (check): Compute exact refutation '
                    'degrees of random parity clause systems at thirty variables.</li>'
                    '<li data-check="entry-a:s2"><a href="#entry-a">entry-a:s2</a> (check): Retrieve the published '
                    'statement about spectral gaps of hyperbolic surfaces and compare hypotheses.</li>'
                    '</ol></section>')
        import lead_queue
        nodes = lead_queue.parse_tree(notebook)[1]
        found = tool.queued_matches(nodes, SPEC)
        self.assertEqual([(claim, queued) for _, claim, queued in found], [('ex:new-degrees', 'entry-a:s1')])
        self.assertGreaterEqual(found[0][0], tool.QUEUED_AT)
        with tempfile.TemporaryDirectory() as folder:
            registry = pathlib.Path(folder) / 'index.json'
            registry.write_text(json.dumps({'claims': REGISTERED}))
            spec = pathlib.Path(folder) / 'spec.json'
            spec.write_text(json.dumps(SPEC))
            page = pathlib.Path(folder) / 'notebook.html'
            page.write_text(notebook)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                tool.main([str(spec), '--registry', str(registry), '--notebook', str(page)])
        self.assertIn('2 queued items compared', out.getvalue())
        self.assertRegex(out.getvalue(), r'ex:new-degrees ~ queued entry-a:s1')
        self.assertNotIn('entry-a:s2:', out.getvalue())

    def test_a_working_context_sentence_the_claim_restates_comes_first(self):
        notebook = ('<section id="working-context"><h2>Working</h2><p><a href="#sparse">Sparse weights</a> give '
                    '\\(h_w(K)\\ge h(K)/s\\). Copied sources keep their certificates at logarithmic depth. '
                    'Norms pay orbit size.</p></section>')
        sentences = tool.context_sentences(notebook)
        self.assertEqual([link for _, link in sentences], ['#sparse', '', ''])
        spec = {'claims': [{'id': 'prop:x', 'summary': 'A weight supported on one class keeps the weighted rank; '
                            'sparse combinations of s classes keep a 1/s share.', 'assessment': 'Working proof.'}]}
        [(ident, rows)] = tool.context_matches(sentences, spec)
        self.assertEqual(ident, 'prop:x')
        self.assertTrue(rows[0][1].startswith('Sparse weights give'))
        self.assertGreater(rows[0][0], rows[1][0])
        self.assertEqual(tool.context_sentences('<p>No context section.</p>'), [])
        with tempfile.TemporaryDirectory() as folder:
            registry = pathlib.Path(folder) / 'index.json'
            registry.write_text(json.dumps({'claims': REGISTERED}))
            path = pathlib.Path(folder) / 'spec.json'
            path.write_text(json.dumps(spec))
            page = pathlib.Path(folder) / 'notebook.html'
            page.write_text(notebook)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                tool.main([str(path), '--registry', str(registry), '--notebook', str(page)])
        self.assertIn('nearest Working mathematical context sentences', out.getvalue())
        self.assertIn('[#sparse]', out.getvalue())

    def test_a_run_is_logged_with_the_claims_it_compared(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'logs/claim-searches.jsonl'
            tool.log_run(['prop:one', 'cor:two'], path)
            row = json.loads(path.read_text())
            self.assertEqual(row['query'], 'claim_resemblance prop:one cor:two')
            tool.log_run(['x'], path / 'under-a-file')                                # no error


if __name__ == '__main__':
    unittest.main()
