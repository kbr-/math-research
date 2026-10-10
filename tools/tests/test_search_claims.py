import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('search_claims', TOOLS / 'search-claims.py')
search_claims = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search_claims)


def edge(source, kind, target):
    return {'source': {'namespace': 'current', 'id': source},
            'target': {'namespace': 'current', 'id': target}, 'type': kind}


class NewerVersionsTest(unittest.TestCase):
    def test_refinements_and_formalizations_are_listed_for_the_older_claim(self):
        data = {'claims': [{'id': i, 'formalization': {'status': s}} for i, s in
                           [('thm:old', 'no_record'), ('audit:lean', 'complete'), ('lem:user', None)]],
                'relationships': [edge('audit:lean', 'refines', 'thm:old'),
                                  edge('lem:user', 'depends_on', 'thm:old')]}
        self.assertEqual(search_claims.newer_versions(data, 'thm:old'),
                         [('audit:lean', 'refines', 'complete')])
        self.assertEqual(search_claims.newer_versions(data, 'audit:lean'), [])

class RankedSearchTest(unittest.TestCase):
    def test_exact_stem_precedes_short_prefix_without_losing_partial_matches(self):
        data = {'claims': [
            {'id': 'lem:early', 'summary': 'A ree argument', 'assessment': ''},
            {'id': 'lem:later', 'summary': 'Rees homogenization', 'assessment': ''},
        ]}
        ranked = search_claims.search(data, ['Rees'])
        self.assertEqual([claim['id'] for _, claim in ranked],
                         ['lem:later', 'lem:early'])

    def test_stemming_and_multiword_coverage_are_preserved(self):
        data = {'claims': [
            {'id': 'lem:partial', 'summary': 'Filtered modules', 'assessment': ''},
            {'id': 'lem:complete', 'summary': 'Filtered modules and barcodes', 'assessment': ''},
            {'id': 'lem:other', 'summary': 'Unrelated geometry', 'assessment': ''},
        ]}
        ranked = search_claims.search(data, ['module', 'barcode'])
        self.assertEqual([claim['id'] for _, claim in ranked],
                         ['lem:complete', 'lem:partial'])


class UnvalidatedReadTest(unittest.TestCase):
    """A search answers from the registry as written; it is validated only to say why it cannot be read."""

    GOOD = {'claims': [{'id': 'lem:one', 'summary': 'Filtered modules', 'assessment': ''}], 'relationships': []}
    BAD = {'claims': [{'id': 'lem:one', 'assessment': ''}], 'relationships': []}

    def run_tool(self, written, validated):
        calls, out = [], io.StringIO()

        def load(path):
            calls.append('load')
            if isinstance(validated, Exception):
                raise validated
            return validated
        argv = ['search-claims.py', 'modules', '--list', '--fields', 'id,summary']
        with mock.patch.object(search_claims, 'read_json', lambda path: calls.append('read') or written), \
                mock.patch.object(search_claims, 'load', load), mock.patch.object(sys, 'argv', argv), \
                mock.patch('recovery_evidence.observe'), contextlib.redirect_stdout(out):
            try:
                search_claims.run()
            except SystemExit as stop:
                return calls, out.getvalue(), stop.code
        return calls, out.getvalue(), 0

    def test_a_search_reads_the_registry_without_validating_it(self):
        self.assertEqual(self.run_tool(self.GOOD, ValueError('never asked')), (['read'], 'lem:one\tFiltered modules\n', 0))

    def test_a_registry_that_cannot_be_answered_from_is_validated_to_say_why(self):
        calls, out, code = self.run_tool(self.BAD, ValueError('lem:one: no summary'))
        self.assertEqual((calls, out, code), (['read', 'load'], '', 'search-claims: lem:one: no summary'))
        # A registry the validation passes is answered from as validated; a fault of the tool itself is not hidden.
        self.assertEqual(self.run_tool(self.BAD, self.GOOD), (['read', 'load'], 'lem:one\tFiltered modules\n', 0))
        with self.assertRaises(KeyError):
            self.run_tool(self.BAD, self.BAD)
        self.assertEqual(self.run_tool(ValueError, self.GOOD)[0], ['read', 'load'])    # not a registry at all


if __name__ == '__main__':
    unittest.main()
