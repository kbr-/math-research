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


class ResemblanceTest(unittest.TestCase):
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

    def test_a_run_is_logged_with_the_claims_it_compared(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'logs/claim-searches.jsonl'
            tool.log_run(['prop:one', 'cor:two'], path)
            row = json.loads(path.read_text())
            self.assertEqual(row['query'], 'claim_resemblance prop:one cor:two')
            tool.log_run(['x'], path / 'under-a-file')                                # no error


if __name__ == '__main__':
    unittest.main()
