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
from claim_reviews import Evidence, make_review, coverage, verified_declarations


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
    def test_verification_selection_does_not_trust_filename_or_header(self):
        header='Declarations: MathResearch.claim\n'
        good="'MathResearch.claim' depends on axioms: [propext, Classical.choice, Quot.sound]\n"
        self.assertEqual(verified_declarations(header),set())
        self.assertEqual(verified_declarations(header+'error: build failed\n'),set())
        self.assertEqual(verified_declarations(header+good),{'MathResearch.claim'})
        self.assertEqual(verified_declarations(good+'FAIL: another check failed\n'),set())
        self.assertEqual(verified_declarations(good.replace('Quot.sound','sorryAx')),set())
    def test_minimal_listing_is_complete_untruncated_and_ordered(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            data=cr.import_markdown(source())
            data['claims'][0]['summary']='long ' * 100
            cr.write_json(root/'index.json', data)
            cmd=[sys.executable,str(TOOLS/'claim-index.py'),'--registry',str(root/'index.json'),
                 'list','--fields','id,summary','--format','tsv']
            result=subprocess.run(cmd,check=True,capture_output=True,text=True)
            expected=''.join(c['id']+'\t'+c['summary']+'\n' for c in data['claims'])
            self.assertEqual(result.stdout,expected)
            self.assertEqual(result.stderr,'')
            limited=subprocess.run(cmd+['-n','1'],check=True,capture_output=True,text=True)
            self.assertEqual(limited.stdout,expected.splitlines(keepends=True)[0])
            self.assertIn('1 matches omitted',limited.stderr)
            reordered=subprocess.run(cmd+['--fields','summary,id','--status','refutation'],
                                     check=True,capture_output=True,text=True)
            self.assertEqual(reordered.stdout,'Correct earlier bound\tex:correction\n')
            output=root/'out.tsv'
            saved=subprocess.run(cmd+['--out',str(output)],check=True,capture_output=True,text=True)
            self.assertEqual(saved.stdout,'')
            self.assertEqual(output.read_text(),expected)

    def test_minimal_projection_escaping_and_null_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);data=cr.import_markdown(source())
            data['claims'][0]['significance']='literal \\N\tand\nnewline'
            cr.write_json(root/'index.json',data)
            command=[sys.executable,str(TOOLS/'search-claims.py'),'--registry',str(root/'index.json'),
                     '--list','--fields','significance','--format','tsv']
            result=subprocess.run(command,check=True,capture_output=True,text=True)
            self.assertEqual(result.stdout,'literal \\\\N\\tand\\nnewline\n\\N\n')

    def test_upgrade_preserves_legacy_fields_and_does_not_infer_reviews(self):
        old=cr.import_markdown(source());new=cr.upgrade(old)
        self.assertEqual(new['schema_version'],2)
        self.assertEqual(new['relationships'],[])
        for a,b in zip(old['claims'],new['claims']):
            for field in ('id',*cr.TEXT_FIELDS): self.assertEqual(a[field],b[field])
            self.assertEqual(b['reviews'],{})
        self.assertEqual(cr.upgrade(new),new)

    def test_field_reviews_detect_only_relevant_source_changes(self):
        data=cr.upgrade(cr.import_markdown(source()));claim=data['claims'][0]
        claim['mathematical_status']='working_proof'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'notebook.html'
            original='<section><h4 id="proof">A</h4><p>Exact statement.</p></section>'
            path.write_text(original)
            claim['reviews']['mathematical_status']=make_review(data,claim,'mathematical_status',
                ['https://kbr.is-a.dev/math-research/#proof'],revision='a'*40,date='2026-09-19',
                reviewer='Test',note='Read statement',evidence=Evidence(root))
            cr.validate(data)
            self.assertEqual(coverage(data,root)['counts']['mathematical_status']['reviewed'],1)
            self.assertEqual(coverage(data,root)['by_topic']['unclassified']['claims'],2)
            path.write_text(original.replace('</section>','<h4 id="later">Later</h4></section>'))
            self.assertEqual(coverage(data,root)['counts']['mathematical_status']['reviewed'],1)
            path.write_text(original.replace('Exact statement','Changed statement'))
            self.assertEqual(coverage(data,root)['counts']['mathematical_status']['stale'],1)
            path.write_text(original);claim['summary']='Changed claim'
            self.assertEqual(coverage(data,root)['counts']['mathematical_status']['stale'],1)

    def test_reviewed_empty_metadata_is_not_accepted(self):
        data=cr.upgrade(cr.import_markdown(source()))
        c=data['claims'][0]
        c['reviews']['formalization']={'state':'reviewed','revision':'a'*40,'date':'2026-09-19',
            'reviewer':'Test','note':'Unsupported review','next_action':None,
            'claim_sha256':'a'*64,'value_sha256':'b'*64,
            'evidence':[{'target':'https://example.org','sha256':None}]}
        with self.assertRaises(ValueError):cr.validate(data)

    def test_no_record_review_becomes_stale_when_lean_inventory_changes(self):
        data=cr.upgrade(cr.import_markdown(source()));c=data['claims'][0]
        c['formalization']['status']='no_record';c['formalization']['scope']='No explicit mapping in audited inventory.'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'research').mkdir()
            (root/'research/inventory.json').write_text('{}')
            c['reviews']['formalization']=make_review(data,c,'formalization',['inventory.json'],
                revision='a'*40,date='2026-09-19',reviewer='Test',note='Explicit mapping census only.',evidence=Evidence(root))
            self.assertEqual(coverage(data,root)['counts']['formalization']['reviewed'],1)
            (root/'formalization/claims').mkdir(parents=True)
            (root/'formalization/claims/New.lean').write_text('-- new recorded claim')
            self.assertEqual(coverage(data,root)['counts']['formalization']['stale'],1)

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
        for mutate in (lambda d: d.update(schema_version=3),
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

    def test_historical_search_uses_statements_and_validated_anchors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manuscript = root/'php_codex_handoff/manuscript'
            (manuscript/'chapters').mkdir(parents=True)
            (manuscript/'CLAIM_INDEX.md').write_text(
                '| [Theorem 1](chapters/one.md#one) | Additive elimination | working-proof | '
                '[`thm:one`](latex/one.tex#L1) |\n')
            chapter = manuscript/'chapters/one.md'
            chapter.write_text('<a id="one"></a>\n### Theorem 1\n\n'
                               'A PC refutation loses no fan-in factor.\n\n'
                               '**Proof.** Zebrafish appear only in this proof.\n'
                               '<a id="next"></a>\nUnicorn appears in the next statement.\n')
            rows = search_tool.historical_matches(['PC', 'refutation'], root)
            self.assertEqual([r['id'] for r in rows], ['thm:one'])
            self.assertEqual(rows[0]['source'],
                             'php_codex_handoff/manuscript/chapters/one.md#one')
            self.assertEqual(search_tool.historical_matches(['zebrafish'], root), [])
            self.assertEqual(search_tool.historical_matches(['unicorn'], root), [])
            chapter.write_text(chapter.read_text().replace('id="one"', 'id="missing"'))
            with self.assertRaisesRegex(ValueError, 'historical anchor'):
                search_tool.historical_matches(['PC'], root)

    def test_default_display_surfaces_historical_elimination_without_changing_tsv(self):
        command = [sys.executable, str(TOOLS/'search-claims.py'),
                   'one', 'block', 'additive', 'elimination', '-n', '1']
        display = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertIn('historical:thm:one-elimination', display)
        self.assertLessEqual(display.count('  historical:'), 3)
        tsv = subprocess.run(command+['--format', 'tsv'], check=True,
                             capture_output=True, text=True).stdout
        self.assertEqual(len(tsv.splitlines()), 1)
        self.assertNotIn('historical:', tsv)

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
        # Rendering and link targets of the real registry are checked by `claim-index.py validate`,
        # which tools/check-claims.py runs next to this test; only retrieval is tested here.
        d = cr.load()
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
