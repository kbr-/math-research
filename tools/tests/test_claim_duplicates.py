import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from claim_duplicates import duplicate_candidates


def fixture():
    claims = [{'id': name, 'summary': summary, 'assessment': '',
               'record': '[proof](../notebook.html#proof)', 'topics': topics,
               'mathematical_status': status}
              for name, summary, topics, status in [
                  ('lem:a', 'A finite field rank lower bound', ['rank'], 'working_proof'),
                  ('lem:b', 'A finite field rank lower bound', ['rank', 'field'], 'retracted'),
                  ('lem:c', 'Disjoint graph matching theorem', [], None)]]
    return {'claims': claims,
            'topic_definitions': [{'id': t, 'title': t, 'description': t} for t in ['rank', 'field']],
            'relationships': [{'id': 'correction', 'type': 'corrects', 'review_status': 'reviewed',
                               'source': {'namespace': 'current', 'id': 'lem:a'},
                               'target': {'namespace': 'current', 'id': 'lem:b'}}]}


class DuplicatesTest(unittest.TestCase):
    def test_deterministic_no_mutation_and_no_accepted_duplicates(self):
        data = fixture()
        before = copy.deepcopy(data)
        first = duplicate_candidates(data)
        self.assertEqual(first, duplicate_candidates(data))
        self.assertEqual(first['claim_ids'], ['lem:a', 'lem:b', 'lem:c'])
        self.assertEqual(len(first['candidates']), 1)
        self.assertEqual(first['candidates'][0]['score'], 1)
        self.assertFalse(first['candidates'][0]['accepted_relationship'])
        self.assertEqual(first['candidates'][0]['disposition'], 'unreviewed_candidate')
        self.assertEqual(data, before)

    def test_invalid_threshold_fails(self):
        with self.assertRaises(ValueError):
            duplicate_candidates(fixture(), 0)

    def test_cli_duplicates_and_author(self):
        import json
        import subprocess
        import tempfile
        import claim_registry as cr
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = cr.upgrade(cr.import_markdown('# Index\n\n' + cr.HEADER +
                '| `lem:a` | Claim | Working proof | [Source](https://example.test/source) |\n'))
            registry = root / 'registry.json'; registry.write_text(json.dumps(data))
            command = [sys.executable, str(Path(__file__).resolve().parents[1] / 'claim-index.py'),
                       '--registry', str(registry)]
            def run(*args):
                return subprocess.run(command + list(args), text=True, capture_output=True)
            table = root / 'index.md'
            self.assertEqual(run('render', '--out', str(table)).returncode, 0)
            self.assertEqual(run('validate', '--markdown', str(table)).returncode, 0)
            self.assertEqual(run('duplicates', '--out', str(root / 'dup.json')).returncode, 0)
            self.assertIn('candidates', json.loads((root / 'dup.json').read_text()))
            self.assertEqual(run('author', 'template', 'lem:new', '--out', str(root / 'request.json')).returncode, 0)
            self.assertIn('REQUIRED:', (root / 'request.json').read_text())


if __name__ == '__main__':
    unittest.main()
