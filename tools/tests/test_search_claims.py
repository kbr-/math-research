import importlib.util
import sys
import unittest
from pathlib import Path

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


if __name__ == '__main__':
    unittest.main()
