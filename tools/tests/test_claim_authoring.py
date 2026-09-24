import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from claim_authoring import questionnaire, prepare
from claim_registry import import_markdown, upgrade, HEADER, render
from claim_reviews import FIELDS, digest, coverage
from claim_registration import check_entries
from claim_maintenance import maintenance
from claim_graph import query


class AuthoringTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'research').mkdir()
        (self.root / 'research/source.md').write_text('Fixture statement with proof and scoped correction.')
        self.empty = upgrade(import_markdown('# Index\n\n' + HEADER +
                             '| `lem:seed` | Seed | Working | [Source](source.md) |\n'))
        self.empty['claims'] = []
        self.empty['topic_definitions'] = [{'id': 'pc', 'title': 'PC', 'description': 'Polynomial calculus'}]
        self.notebook = '<section id="research-record"><article id="entry-a" data-claims="lem:a"><h4 id="a">A</h4><p>Proof.</p></article></section>'
        (self.root / 'notebook.html').write_text(self.notebook)

    def request(self, data, identifier='lem:a', existing=None):
        request = questionnaire(data, identifier)
        request['provenance'] = {'revision': 'a' * 40, 'date': '2026-09-20', 'reviewer': 'Fixture reviewer'}
        claim = copy.deepcopy(existing) if existing else {
            'id': identifier, 'summary': 'Precisely scoped fixture claim', 'assessment': 'Working proof',
            'record': '[Proof](../notebook.html#a)', 'mathematical_status': 'working_proof',
            'topics': ['pc'],
            'formalization': {'status': 'not_started', 'scope': 'No proof work assigned for fixture.',
                              'references': ['source.md'], 'artifacts': []},
            'significance': {'category': 'route_specific', 'rationale': 'Fixture route bridge.',
                             'novelty': 'not_claimed', 'publication_status': 'not_applicable',
                             'references': ['source.md'], 'next_action': None}}
        claim.pop('reviews', None)
        request['submissions'] = [{'claim': claim, 'dispositions': {
            field: {'state': 'reviewed', 'note': 'Fixture source reviewed for ' + field,
                    'targets': ['source.md'], 'next_action': None} for field in FIELDS}}]
        return request

    def test_new_claim_registration_render_exact_lookup_and_projection(self):
        before = copy.deepcopy(self.empty)
        proposed, report = prepare(self.empty, self.request(self.empty), self.root)
        self.assertEqual(self.empty, before)
        self.assertTrue(report['passed'])
        self.assertTrue(check_entries('', self.notebook, proposed, self.root)['passed'])
        self.assertIn('lem:a', render(proposed))
        path = self.root / 'registry.json'; path.write_text(json.dumps(proposed))
        output = subprocess.check_output([sys.executable, str(TOOLS / 'search-claims.py'),
                 '--registry', str(path), '--show', 'lem:a'], text=True)
        self.assertIn('lem:a', output)
        projected = subprocess.check_output([sys.executable, str(TOOLS / 'search-claims.py'),
                    '--registry', str(path), '--list', '--topic', 'pc', '--fields', 'id,summary',
                    '--format', 'tsv'], text=True)
        self.assertEqual(projected, 'lem:a\tPrecisely scoped fixture claim\n')
        self.assertEqual(coverage(proposed, self.root)['counts']['significance'], {'reviewed': 1})

    def test_unanswered_missing_review_and_stale_base_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.empty, questionnaire(self.empty, 'lem:a'), self.root)
        request = self.request(self.empty)
        del request['submissions'][0]['dispositions']['significance']
        with self.assertRaises(ValueError):
            prepare(self.empty, request, self.root)
        request = self.request(self.empty); request['base_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            prepare(self.empty, request, self.root)

    def test_pending_is_honest_and_requires_action(self):
        request = self.request(self.empty)
        submission = request['submissions'][0]
        submission['claim']['significance'] = None
        disposition = submission['dispositions']['significance']
        disposition.update(state='pending', note='Novelty of this exact encoding is unresolved.',
                           next_action='Compare fixture encoding with cited source theorem.')
        proposed, _ = prepare(self.empty, request, self.root)
        self.assertEqual(coverage(proposed, self.root)['counts']['significance'], {'pending': 1})
        disposition['next_action'] = None
        with self.assertRaises(ValueError):
            prepare(self.empty, request, self.root)

    def test_explicit_not_applicable_and_broken_source(self):
        request = self.request(self.empty)
        item = request['submissions'][0]
        item['claim']['mathematical_status'] = 'context'
        item['claim']['significance'] = None
        item['dispositions']['significance'].update(state='not_applicable',
            note='Administrative context record; no mathematical significance assertion.')
        proposed, _ = prepare(self.empty, request, self.root)
        self.assertEqual(coverage(proposed, self.root)['counts']['significance'], {'not_applicable': 1})
        item['claim']['record'] = '[Missing](absent.md)'
        with self.assertRaises(ValueError):
            prepare(self.empty, request, self.root)

    def test_correction_preserves_old_record_and_requires_target_review(self):
        initial = self.request(self.empty)
        initial['submissions'] += self.request(self.empty, 'lem:dependent')['submissions']
        initial['relationships'] = [{'id': 'dependent-a', 'type': 'depends_on',
            'source': {'namespace': 'current', 'id': 'lem:dependent', 'locator': None},
            'target': {'namespace': 'current', 'id': 'lem:a', 'locator': None},
            'scope': 'Fixture uses the original bound.', 'evidence': ['source.md'],
            'review_status': 'reviewed', 'review': {**initial['provenance'], 'note': 'Explicit proof use.'}}]
        base, _ = prepare(self.empty, initial, self.root)
        new_entry = '<article id="entry-fix" data-claims="lem:fix"><h4 id="fix">Correction</h4><p>Bound correction only.</p></article>'
        notebook = self.notebook.replace('</section>', new_entry + '</section>')
        (self.root / 'notebook.html').write_text(notebook)
        request = self.request(base, 'lem:fix')
        request['submissions'][0]['claim']['record'] = '[Correction](../notebook.html#fix)'
        request['relationships'] = [{'id': 'fix-a', 'type': 'corrects',
            'source': {'namespace': 'current', 'id': 'lem:fix', 'locator': None},
            'target': {'namespace': 'current', 'id': 'lem:a', 'locator': None},
            'scope': 'Bound in the original claim only.', 'evidence': ['source.md'],
            'review_status': 'reviewed', 'review': {**request['provenance'], 'note': 'Scoped correction.'}}]
        with self.assertRaises(ValueError):
            prepare(base, request, self.root)
        affected = self.request(base, 'lem:a', base['claims'][0])['submissions'][0]
        affected['dispositions']['mathematical_status']['note'] = 'Original statement retained; correction applies to its bound.'
        request['submissions'].append(affected)
        with self.assertRaisesRegex(ValueError, 'explicitly refresh significance review for fix-a'):
            prepare(base, request, self.root)
        affected['dispositions']['significance']['note'] = 'Corrected bound retains the route-specific significance; no independent novelty claim.'
        proposed, report = prepare(base, request, self.root)
        self.assertTrue(report['passed'])
        self.assertEqual(proposed['claims'][0]['record'], base['claims'][0]['record'])
        self.assertTrue(check_entries(self.notebook, notebook, proposed, self.root)['passed'])
        self.assertEqual(query(proposed, 'lem:a', 'impact')['nodes'][0]['id'], 'lem:dependent')
        self.assertIn('review scope', query(proposed, 'lem:a', 'impact')['scope'])

    def test_formalization_update_preserves_scope_distinction(self):
        base, _ = prepare(self.empty, self.request(self.empty), self.root)
        request = self.request(base, existing=base['claims'][0])
        request['submissions'][0]['claim']['formalization'].update(
            status='partial', scope='Only the explicit finite fixture is verified; general statement remains unverified.')
        proposed, report = prepare(base, request, self.root)
        self.assertTrue(report['passed'])
        self.assertEqual(proposed['claims'][0]['mathematical_status'], 'working_proof')
        self.assertEqual(proposed['claims'][0]['formalization']['status'], 'partial')

    def test_parallel_proposals_resume_merge_without_lost_ids(self):
        left, _ = prepare(self.empty, self.request(self.empty), self.root)
        right_request = self.request(self.empty, 'lem:b')
        # JSON round-trip models a saved, resumed questionnaire, including base fingerprint.
        right, _ = prepare(self.empty, json.loads(json.dumps(right_request)), self.root)
        spec = importlib.util.spec_from_file_location('append_merge', TOOLS / 'merge-formalization-appends.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        merged = json.loads(module.merge_registry(*(json.dumps(x) for x in (self.empty, left, right))))
        self.assertEqual([c['id'] for c in merged['claims']], ['lem:a', 'lem:b'])
        self.assertEqual(merged['claims'][0], left['claims'][0])
        self.assertTrue(maintenance(self.empty, merged, self.root)['passed'])


class BuildTest(unittest.TestCase):
    """author build: a compact spec expands into a complete request that prepare accepts."""
    setUp = AuthoringTest.setUp
    request = AuthoringTest.request
    def spec(self, claims, relationships=(), **extra):
        return dict(source={'record': '[Proof](../notebook.html#a)', 'targets': ['source.md'], 'label': 'Fixture entry'},
                    reviewer='Fixture reviewer', date='2026-09-24', topics=['pc'], claims=claims,
                    relationships=[list(r) for r in relationships], **extra)
    def item(self, cid):
        return {'id': cid, 'summary': 'Scoped fixture claim ' + cid, 'assessment': 'Working proof',
                'status': 'working_proof', 'rationale': 'Fixture bridge.', 'next_action': None}
    def test_build_new_claim_prepares(self):
        from claim_authoring import build
        request = build(self.empty, self.spec([self.item('lem:a')]), 'a' * 40)
        proposed, report = prepare(self.empty, request, self.root)
        self.assertTrue(report['passed'])
        self.assertEqual([c['id'] for c in proposed['claims']], ['lem:a'])
    def test_touched_existing_claim_is_refreshed_automatically(self):
        from claim_authoring import build
        base, _ = prepare(self.empty, self.request(self.empty), self.root)
        request = build(base, self.spec([self.item('lem:b')], [('lem:b', 'depends_on', 'lem:a', 'Uses the fixture bound.')]), 'b' * 40)
        self.assertEqual(sorted(s['claim']['id'] for s in request['submissions']), ['lem:a', 'lem:b'])
        refreshed = [s for s in request['submissions'] if s['claim']['id'] == 'lem:a'][0]
        self.assertIn('lem:b', refreshed['dispositions']['relationships']['note'])
        proposed, report = prepare(base, request, self.root)
        self.assertTrue(report['passed'])
        request['submissions'] = [s for s in request['submissions'] if s['claim']['id'] != 'lem:a']
        with self.assertRaises(ValueError):
            prepare(base, request, self.root)
    def test_new_claim_may_carry_formalization(self):
        from claim_authoring import build
        item = dict(self.item('lem:a'), formalization={
            'status': 'complete', 'scope': 'Whole statement.', 'references': ['source.md'], 'artifacts': []})
        request = build(self.empty, self.spec([item]), 'd' * 40)
        proposed, report = prepare(self.empty, request, self.root)
        self.assertTrue(report['passed'])
        self.assertEqual(proposed['claims'][0]['formalization']['status'], 'complete')
        self.assertIn('Lean artifacts', proposed['claims'][0]['reviews']['formalization']['note'])
    def test_overrides_update_existing_fields(self):
        from claim_authoring import build
        base, _ = prepare(self.empty, self.request(self.empty), self.root)
        request = build(base, self.spec([], overrides={'lem:a': {'assessment': 'Working proof; scope narrowed.'}},
                                        refresh={'lem:a': 'Scope narrowed at this checkpoint.'}), 'c' * 40)
        proposed, report = prepare(base, request, self.root)
        self.assertEqual(proposed['claims'][0]['assessment'], 'Working proof; scope narrowed.')


if __name__ == '__main__':
    unittest.main()
