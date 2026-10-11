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


if __name__ == '__main__':
    unittest.main()
