"""Lossless migration, graph semantics, bounded retrieval and table regressions."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import claim_registry as cr


def tool(name, filename):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


search_tool = tool('claim_search', 'search-claims.py')
merge_tool = tool('merge_appends', 'merge-formalization-appends.py')


def source():
    return ('# Index\n\n' + cr.HEADER +
            '| `lem:partial` | Bound |S| with `x|y` | Partial Lean scope; stronger hypotheses only | '
            '[Proof](https://kbr.is-a.dev/math-research/#proof), [Lean](../formalization/a.lean) |\n\n' +
            '| `ex:correction` | Correct earlier bound | Refutation, not a full retraction | '
            '[Correction](https://kbr.is-a.dev/math-research/#correction) |\n')


def endpoint(label):
    return {'namespace': 'current', 'id': label, 'locator': None}


class ClaimRegistryTests(unittest.TestCase):
    def test_lossless_import_retains_partial_scope_and_order(self):
        d = cr.import_markdown(source())
        report = cr.reconcile(source(), d)
        self.assertEqual(report['claims'], 2)
        self.assertEqual(report['claim_links'], 3)
        self.assertEqual(d['claims'][0]['assessment'], 'Partial Lean scope; stronger hypotheses only')
        self.assertIsNone(d['claims'][0]['formalization']['status'])
        self.assertEqual(d['relationships'], [])

    def test_one_continuous_table_and_escaped_pipes(self):
        rows = cr.render(cr.import_markdown(source())).split(cr.HEADER)[1].splitlines()
        self.assertEqual(len(rows), 2)
        self.assertIn(r'Bound \|S\| with `x\|y`', rows[0])
        self.assertTrue(all(len(re.split(r'(?<!\\)\|', row)) == 6 for row in rows))
        self.assertEqual(cr.escape_cell(r'a\|b'), r'a\|b')
        self.assertEqual(cr.escape_cell(r'a\\|b'), r'a\\\|b')

    def test_generated_warning_is_visible_and_names_the_edit_workflow(self):
        rendered = cr.render(cr.import_markdown(source()))
        self.assertTrue(rendered.startswith('> **Automatically generated'))
        self.assertIn('whether human or agent', rendered)
        self.assertIn('[claims/index.json](claims/index.json)', rendered)
        self.assertIn('python3 tools/claim-index.py render', rendered)
        self.assertNotIn('<!--', rendered.split('# Index')[0])

    def test_import_rejects_ambiguity_and_nonrows(self):
        for bad in (source().replace('Bound |S|', 'Bound | ambiguous'),
                    source() + 'unparsed text\n', source().replace('`lem:partial`', '`bad label`'),
                    source().replace('`ex:correction`', '`lem:partial`')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                cr.import_markdown(bad)

    def test_link_parser_preserves_parentheses_and_angle_destinations(self):
        self.assertEqual(cr.markdown_links('[A](https://example.org/a(b)) [B](<../a b.md>)'),
                         [{'label': 'A', 'target': 'https://example.org/a(b)'},
                          {'label': 'B', 'target': '../a b.md'}])
        with self.assertRaises(ValueError): cr.markdown_links('[bad](unclosed')

    def test_schema_and_formalization_scope_guards(self):
        original = cr.import_markdown(source())
        for mutate in (lambda d: d.update(schema_version=2),
                       lambda d: d['claims'][0].update(unexpected=True),
                       lambda d: d['claims'][0]['formalization'].update(status='complete'),
                       lambda d: d['claims'][0].update(topics=['same', 'same'])):
            d = copy.deepcopy(original)
            mutate(d)
            with self.assertRaises(ValueError): cr.validate(d)

    def test_graph_references_are_not_dependencies(self):
        d = cr.import_markdown(source())
        view = cr.exported(d)
        self.assertEqual(len(view['claims'][0]['references']), 2)
        self.assertEqual(view['relationships'], [])
        self.assertEqual(view['reference_base'], 'research/CLAIM_INDEX.md')
        self.assertIn('absent edges', view['relationship_coverage'])
        edge = {'id': 'edge1', 'source': endpoint('ex:correction'),
                'target': endpoint('lem:partial'), 'type': 'corrects',
                'evidence': ['https://kbr.is-a.dev/math-research/#correction'], 'review_status': 'reviewed'}
        d['relationships'] = [edge]
        cr.validate(d)
        edge['target']['id'] = 'missing'
        with self.assertRaises(ValueError): cr.validate(d)
        edge['target'] = {'namespace': 'historical', 'id': 'lem:historical', 'locator': None}
        with self.assertRaises(ValueError): cr.validate(d)
        edge['target']['locator'] = '../php_codex_handoff/manuscript/CLAIM_INDEX.md'
        cr.validate(d)
        edge['evidence'] = []
        with self.assertRaises(ValueError): cr.validate(d)

    def test_local_targets_and_missing_anchors(self):
        d = cr.import_markdown(source())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'formalization').mkdir()
            (root/'formalization/a.lean').write_text('-- partial proof\n')
            (root/'notebook.html').write_text('<h4 id="proof">A</h4><h4 id="correction">B</h4>')
            self.assertTrue(cr.check_targets(d, root)['passed'])
            (root/'notebook.html').write_text('<h4 id="proof">A</h4>')
            self.assertFalse(cr.check_targets(d, root)['passed'])
            with self.assertRaises(ValueError): cr.local_target('../../outside.md', root)

    def test_stale_generated_view_is_rejected_by_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = cr.import_markdown(source())
            for c in data['claims']:
                c['record'] = '[External source](https://example.org/proof)'
            cr.write_json(root/'index.json', data)
            (root/'index.md').write_text('stale\n')
            command = [sys.executable, str(TOOLS/'claim-index.py'), '--registry', str(root/'index.json'),
                       'validate', '--markdown', str(root/'index.md')]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)['generated_markdown_current'])

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.json'
            path.write_text('{"claims":[],"claims":[]}')
            with self.assertRaises(ValueError): cr.read_json(path)

    def test_search_filters_keep_unknown_distinct_from_verified(self):
        d = cr.import_markdown(source())
        self.assertEqual(search_tool.search(d, ['stronger', 'hypotheses'])[0][1]['id'], 'lem:partial')
        self.assertEqual(len(search_tool.search(d, [], has_lean=True)), 1)
        self.assertEqual(len(search_tool.search(d, [], formalization='complete')), 0)
        self.assertEqual(len(search_tool.search(d, [], formalization='unknown')), 2)
        self.assertEqual(len(search_tool.search(d, [], status='refutation')), 1)

    def test_exact_lookup_and_omitted_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'registry.json'
            cr.write_json(path, cr.import_markdown(source()))
            command = [sys.executable, str(TOOLS/'search-claims.py'), '--registry', str(path)]
            exact = subprocess.run(command+['--show', 'lem:partial', '--json'], check=True,
                                   capture_output=True, text=True)
            self.assertEqual(json.loads(exact.stdout)['claims'][0]['assessment'],
                             'Partial Lean scope; stronger hypotheses only')
            result = subprocess.run(command+['--formalization', 'unknown', '-n', '1', '--json'],
                                    check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(result.stdout)['omitted'], 1)
            result = subprocess.run(command+['--show', 'missing'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_append_merge_and_conflicting_metadata(self):
        base = cr.import_markdown(source())
        left, right = copy.deepcopy(base), copy.deepcopy(base)
        for branch, label in ((left, 'lem:left'), (right, 'lem:right')):
            branch['claims'].append(dict(base['claims'][0], id=label))
        merged = json.loads(merge_tool.merge_registry(*map(json.dumps, (base, left, right))))
        self.assertEqual([c['id'] for c in merged['claims']][-2:], ['lem:left', 'lem:right'])
        right['claims'][0]['assessment'] = 'Changed coverage'
        with self.assertRaises(ValueError):
            merge_tool.merge_registry(*map(json.dumps, (base, left, right)))

    def test_repository_registry_and_retrieval(self):
        d = cr.load()
        self.assertEqual(cr.MARKDOWN.read_text(), cr.render(d))
        self.assertTrue(cr.check_targets(d)['passed'])
        for words, expected in [(['point', 'support', 'lower', 'bound'], 'lem:Boolean-design-point-support-lower-bound'),
                                (['two', 'form', 'no', 'fall', 'criterion'], 'thm:two-form-no-fall-criterion')]:
            ids = [c['id'] for _, c in search_tool.search(d, words)[:5]]
            self.assertIn(expected, ids)

    def test_real_structured_rebase_preserves_both_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args, check=True):
                return subprocess.run(['git', *args], cwd=root, check=check,
                                      text=True, capture_output=True)
            git('init', '-q', '-b', 'main')
            git('config', 'user.name', 'Registry Test')
            git('config', 'user.email', 'test@example.invalid')
            (root/'research/claims').mkdir(parents=True)
            base = cr.import_markdown(source())
            def write(label=None):
                data = copy.deepcopy(base)
                if label:
                    data['claims'].append(dict(base['claims'][0], id=label))
                cr.write_json(root/'research/claims/index.json', data)
                (root/'research/CLAIM_INDEX.md').write_text(cr.render(data))
                git('add', '.')
                git('commit', '-qm', label or 'base')
            write()
            git('checkout', '-qb', 'worker')
            write('lem:worker')
            git('checkout', '-q', 'main')
            write('lem:main')
            git('checkout', '-q', 'worker')
            self.assertNotEqual(git('rebase', 'main', check=False).returncode, 0)
            subprocess.run([sys.executable, str(TOOLS/'merge-formalization-appends.py')],
                           cwd=root, check=True, capture_output=True, text=True)
            data = cr.load(root/'research/claims/index.json')
            self.assertEqual([c['id'] for c in data['claims']][-2:], ['lem:main', 'lem:worker'])
            self.assertEqual((root/'research/CLAIM_INDEX.md').read_text(), cr.render(data))
            self.assertTrue((root/'.git/rebase-merge').exists())
            self.assertIn('UU research/claims/index.json', git('status', '--porcelain').stdout)


if __name__ == '__main__':
    unittest.main()
