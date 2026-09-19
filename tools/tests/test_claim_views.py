import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from claim_views import claim_view, topic_map, markdown, duplicate_candidates, bundle_files


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


class ViewsTest(unittest.TestCase):
    def test_all_ids_and_unclassified_preserved(self):
        data = fixture()
        report = topic_map(data)
        self.assertEqual(set(report['unclassified']).union(*[set(t['claim_ids']) for t in report['topics']]),
                         {c['id'] for c in data['claims']})
        self.assertEqual(report['unclassified'], ['lem:c'])
        self.assertEqual([c['id'] for c in claim_view(data, '@unclassified')['claims']], ['lem:c'])
        self.assertEqual(len(claim_view(data)['claims']), 3)

    def test_lifecycle_partition_and_correction_warning(self):
        data = fixture()
        self.assertEqual([c['id'] for c in claim_view(data, lifecycle='active')['claims']], ['lem:a', 'lem:c'])
        old = claim_view(data, lifecycle='historical')
        self.assertEqual([c['id'] for c in old['claims']], ['lem:b'])
        self.assertIn('corrects by lem:a (reviewed)', markdown(old))
        self.assertIn('https://github.com/kbr-/math-research/blob/main/notebook.html#proof', markdown(old))

    def test_only_reviewed_supersession_moves_lifecycle(self):
        data = fixture()
        edge = data['relationships'][0]
        edge['type'] = 'supersedes'
        edge['target']['id'] = 'lem:c'
        edge['review_status'] = 'unreviewed'
        self.assertIn('lem:c', [c['id'] for c in claim_view(data, lifecycle='active')['claims']])
        edge['review_status'] = 'reviewed'
        self.assertNotIn('lem:c', [c['id'] for c in claim_view(data, lifecycle='active')['claims']])

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
        self.assertEqual(markdown(topic_map(data)), markdown(topic_map(data)))
        claim_view(data)
        self.assertEqual(data, before)

    def test_invalid_selection_fails(self):
        with self.assertRaises(ValueError):
            claim_view(fixture(), 'typo')
        with self.assertRaises(ValueError):
            duplicate_candidates(fixture(), 0)

    def test_navigable_bundle_preserves_ids_and_topic_links(self):
        import re
        data = fixture(); files = bundle_files(data)
        self.assertEqual(files, bundle_files(data))
        for target in re.findall(r'\]\(([^)]+)\)', files['topics.md']):
            self.assertIn(target, files)
        for claim in data['claims']:
            self.assertIn(claim['id'], files['all.md'])
        self.assertIn('lem:c', files['unclassified.md'])
        self.assertIn('lem:b', files['historical.md'])

    def test_cli_aliases_render_bundle_and_staleness(self):
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
            out = root / 'views'; table = root / 'index.md'
            self.assertEqual(run('render', '--out', str(table), '--views-out', str(out)).returncode, 0)
            self.assertEqual(run('validate', '--markdown', str(table), '--views-dir', str(out)).returncode, 0)
            (out / 'all.md').write_text('stale')
            stale = run('validate', '--markdown', str(table), '--views-dir', str(out))
            self.assertEqual(stale.returncode, 1)
            self.assertIn('all.md', stale.stdout)
            self.assertEqual(run('views', 'bundle', '--out', str(out)).returncode, 0)
            self.assertEqual(run('author', 'template', 'lem:new', '--out', str(root / 'request.json')).returncode, 0)
            self.assertIn('REQUIRED:', (root / 'request.json').read_text())


if __name__ == '__main__':
    unittest.main()
