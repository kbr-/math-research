"""tools/commit_message_checks.py: figures of a framework commit message and conditions of registered claims."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('commit_message_checks', ROOT / 'tools/commit_message_checks.py')
cmc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmc)


class FigureTest(unittest.TestCase):
    def test_a_figure_needs_each_number_in_a_saved_output_the_commit_carries(self):
        # 16 October 2026: four figures seen on the terminal and saved nowhere.
        message = 'Tool: x\n\nSuite: 1191 tests in 8.5 s; it flags 10 calls, 8 distinct briefs.\n# 99 tests\n'
        files = {'research/results/run/suite.txt': 'Ran 1191 tests in 8.5s: OK',
                 'research/results/run/replay.txt': '10 reviewer briefs flagged'}
        paths = ['tools/x.py', *files]
        self.assertEqual(cmc.unsourced(message, paths, files.get), [])
        self.assertEqual(cmc.unsourced(message.replace('8.5 s', '8.6 s'), paths, files.get), ['8.6 s'])
        self.assertEqual(cmc.unsourced(message, ['tools/x.py'], files.get), ['1191 tests', '8.5 s', '10 calls'])
        # A paragraph naming a file is checked against that file only (the builds' reviewer, 17 October 2026).
        self.assertEqual(cmc.unsourced('Tool: x\n\nIt flags 10 calls (suite.txt).\n', paths, files.get), ['10 calls'])
        self.assertEqual(cmc.unsourced('Tool: x\n\nIt flags 10 calls (replay.txt).\n', paths, files.get), [])
        # the refusal names the files each paragraph was checked against
        self.assertEqual(cmc.searched_files('Tool: x\n\nIt flags 10 calls (replay.txt).\n', paths), [['replay.txt']])
        self.assertEqual(cmc.figures('1514 texts, 56 paragraphs, 13 conditions over 9 commits'),
                         ['1514 texts', '56 paragraphs', '13 conditions', '9 commits'])
        self.assertEqual(cmc.figures('# 3 tests in a comment line\nNo figure here.'), [])
        self.assertEqual(cmc.figures('5 of 15 framework commits; 38 of 1562 commands; 12.6 MB read'),
                         ['5 of 15', '38 of 1562', '12.6 MB'])

    def test_only_framework_commits_are_checked(self):
        self.assertTrue(cmc.is_framework(['tools/a.py', 'research/results/x/out.txt']))
        self.assertTrue(cmc.is_framework(['compute.sh']))
        self.assertFalse(cmc.is_framework(['tools/a.py', 'notebook.html']))       # a research entry's commit
        self.assertFalse(cmc.is_framework(['research/results/x/out.txt']))


class ConditionTest(unittest.TestCase):
    def test_a_dropped_condition_of_a_new_claim_is_listed(self):
        # 16 October 2026: a message dropped "Gamma > 0" and turned "at most" into "about".
        claims = [('thm:tradeoff', 'Over any field, if Gamma=(n/2+1)/K-max(k,2)-3>0, every refutation of size s '
                                   'has ln s >= Gamma^2/(8(n+M)), with at most M extension axioms.')]
        bare = 'Main: tradeoff\n\nthm:tradeoff: every refutation has ln s >= Gamma^2/(8(n+M)), about M axioms.'
        listed = [c for _, c in cmc.dropped_conditions(bare, claims)]
        self.assertEqual(len(listed), 2)
        self.assertTrue(listed[0].startswith('if Gamma'))
        full = ('thm:tradeoff: if Gamma=(n/2+1)/K-max(k,2)-3>0, every refutation has ln s >= Gamma^2/(8(n+M)), '
                'with at most M extension axioms.')
        self.assertEqual(cmc.dropped_conditions(full, claims), [])
        self.assertEqual(cmc.dropped_conditions('A message that names no claim.', claims), [])

    def test_a_condition_after_a_semicolon_belongs_to_the_claim_the_sentence_names(self):
        # 17 October 2026: the condition stood after a semicolon of the sentence naming the claim and was refused
        claims = [('conj:x', 'Conjecture: excess at the middle sizes; the only-if direction at K = 1 (n <= 4) is '
                             'cor:y.')]
        message = ('Registers conj:x (positive excess at the middle sizes, checked at n = 3 to 6; its only-if '
                   'direction at K = 1 (n <= 4) is cor:y) and check:z.')
        self.assertEqual(cmc.dropped_conditions(message, claims), [])

    def test_a_dropped_condition_needs_a_confirmation_line(self):
        # 17 October 2026: a flagged message was committed unchanged.
        dropped = [('cor:linear-error-transfer', 'when S misses three holes')]
        self.assertEqual(cmc.unconfirmed('Main: x\n\nThe criterion holds.', dropped), dropped)
        ok = 'Main: x\n\nThe criterion holds.\n\nConditions checked: cor:linear-error-transfer (an in-particular case).'
        self.assertEqual(cmc.unconfirmed(ok, dropped), [])
        # naming another claim that contains this one's name as a prefix does not confirm it
        other = 'Main: x\n\nConditions checked: cor:linear-error-transfer-two (another).'
        self.assertEqual(cmc.unconfirmed(other, dropped), dropped)

    def test_a_dropped_degree_window_in_an_entry_is_listed(self):
        # 17 October 2026: a General statement dropped both degree windows of its claim.
        claims = [('prop:p', '(a) If D >= l+1, the least degree is l. (b) If D >= l + ceil(l/2), it is ceil(l/2).')]
        bare = 'prop:p: the least common degree is \\(\\ell\\), and the combined one \\(\\lceil\\ell/2\\rceil\\).'
        self.assertEqual(len(cmc.dropped_conditions(bare, claims, windows_only=True)), 2)
        full = ('prop:p: degree \\(\\ell\\) when \\(D\\ge\\ell+1\\), and \\(\\lceil\\ell/2\\rceil\\) when '
                '\\(D\\ge\\ell+\\lceil\\ell/2\\rceil\\).')
        self.assertEqual(cmc.dropped_conditions(full, claims, windows_only=True), [])
        # other conditions are left to the reader in an entry
        other = [('prop:q', 'If H > 0 and beta < 1, the bound holds.')]
        self.assertEqual(cmc.dropped_conditions('prop:q: the bound holds.', other, windows_only=True), [])

    def test_new_claims_are_those_absent_from_the_old_index(self):
        old = '{"claims": [{"id": "lem:a", "summary": "A."}]}'
        new = '{"claims": [{"id": "lem:a", "summary": "A."}, {"id": "lem:b", "summary": "B, if c."}]}'
        self.assertEqual(cmc.new_claims(old, new), [('lem:b', 'B, if c.')])
        self.assertEqual(len(cmc.new_claims('', new)), 2)


class SuiteAfterTest(unittest.TestCase):
    def test_shared_code_needs_a_whole_suite_run_after_its_last_edit(self):
        # 17 October 2026: a hook change was committed after its own module's tests only.
        import json
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            (top / 'tools/hooks').mkdir(parents=True)
            (top / 'tools/tests').mkdir()
            (top / 'tools/hooks/guard.py').write_text('x = 1\n')
            (top / 'tools/shared.py').write_text('y = 1\n')
            (top / 'tools/user.py').write_text('import shared\n')
            (top / 'tools/alone.py').write_text('z = 1\n')
            (top / 'tools/by-path.py').write_text('w = 1\n')
            (top / 'tools/loader.py').write_text("spec = load(ROOT / 'tools/by-path.py')\n")
            self.assertEqual(cmc.shared_code(['tools/by-path.py'], top), ['tools/by-path.py'])   # loaded by path
            self.assertEqual(cmc.shared_code(['AGENTS.md', 'notes.md'], top), ['AGENTS.md'])   # read by a test
            self.assertEqual(cmc.shared_code(['tools/hooks/guard.py', 'tools/shared.py', 'tools/alone.py',
                                              'tools/tests/test_alone.py', 'compute.sh'], top),
                             ['tools/hooks/guard.py', 'tools/shared.py', 'compute.sh'])
            self.assertIn('whole suite', cmc.suite_after(['tools/hooks/guard.py'], top))      # no run yet
            stamp = top / 'tools/tests/.suite-pass.json'
            stamp.write_text(json.dumps({'unix_s': os.stat(top / 'tools/hooks/guard.py').st_mtime + 5}))
            self.assertIsNone(cmc.suite_after(['tools/hooks/guard.py'], top))
            os.utime(top / 'tools/hooks/guard.py', (9e9, 9e9))                               # edited after it
            self.assertIn('tools/hooks/guard.py', cmc.suite_after(['tools/hooks/guard.py'], top))
            self.assertIsNone(cmc.suite_after(['tools/alone.py'], top))                     # its own tests do
            # a suite figure must be the last passing run's (17 October 2026: "1341 tests in 9.4 s" was written
            # before the run, which failed, and a stale provenance file let it pass)
            stamp.write_text(json.dumps({'unix_s': 1, 'tests': 1341, 'seconds': 9.8}))
            claimed = 'The suite ran 1341 tests in 9.4 s after the last edit to shared code.'
            self.assertEqual(cmc.suite_figures_unmatched(claimed, top), ['1341 tests in 9.4 s'])
            self.assertEqual(cmc.suite_figures_unmatched(claimed.replace('9.4', '9.8'), top), [])
            both = ('the whole suite first failed on three browser timing limits alone, 1341 tests in 17.0 s, and '
                    'once rerun passed, 1341 tests in\n9.8 s')
            self.assertEqual(cmc.suite_figures_unmatched(both, top), [])                   # the failed run is said so
            self.assertEqual(cmc.suite_figures_unmatched('Nothing failed: ' + claimed, top),  # a denial is no report
                             ['1341 tests in 9.4 s'])
            self.assertEqual(cmc.suite_figures_unmatched('Ran 1342 tests in 9.8s: OK', top), ['1342 tests in 9.8s'])
            for module_run in ('test_goal_progress: 60 tests in 1.0 s', "the guard's and the tool's tests after it, "
                               '34 tests in 0.2 s'):                                       # one module's run
                self.assertEqual(cmc.suite_figures_unmatched(module_run, top), [], module_run)
            stamp.write_text(json.dumps({'unix_s': 1, 'tests': 1341}))                     # an older stamp: no seconds
            self.assertEqual(cmc.suite_figures_unmatched(claimed.replace('9.4', '9.8'), top), ['1341 tests in 9.8 s'])


class UnlabelledScriptTest(unittest.TestCase):
    """A research script staged without the lines compute.sh asks of a run there is refused at commit."""
    COMPUTE = cmc.compute_module(ROOT)
    LABELLED = ('"""Checks an identity.\nRefuted by: a nonzero difference printed for some n tested.\n'
                'Possible because: the telescoping could drop a boundary term somewhere.\n'
                'Baseline: the bare count of terms decides nothing about the identity here.\n'
                'Record checked: lem:example read, and it does not decide this identity.\n"""\n')

    def check(self, path, text):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / path
            target.parent.mkdir(parents=True)
            target.write_text(text)
            return cmc.unlabelled_scripts([path], Path(tmp), self.COMPUTE)

    def test_the_copied_in_scratch_script_is_refused(self):
        # The exposing case's shape: a docstring and checks, none of the labelled lines.
        found = self.check('research/results/x_20261017/check.py', '"""Check F = Z(Z+1)G for n = 1..6."""\n')
        self.assertTrue(found and 'Refuted by' in found[0])

    def test_a_labelled_script_and_a_tool_pass(self):
        self.assertEqual(self.check('research/results/x_20261017/check.py', self.LABELLED), [])
        self.assertEqual(self.check('tools/helper.py', '"""No labels."""\n'), [])

    def test_a_script_that_tests_nothing_says_so(self):
        text = '"""No statement tested: it converts saved outputs into one table for the entry."""\n'
        self.assertEqual(self.check('research/results/x_20261017/table.py', text), [])


class RefusalDefTest(unittest.TestCase):
    # The exposing case, 17 October 2026: two refusal functions written into compute.sh, quoted from its diff.
    LINES = ['def scripts_with_process_pool(command):', 'def pool_admission_error(command, threads, pool_workers):',
             '    refusal = pool_admission_error(command, args.threads, args.pool_workers)']
    MESSAGE = 'Ultimate matching: ...\n\ncompute.sh refuses a named script that starts a process pool ...\n'

    def test_new_refusal_functions_in_a_gate_need_a_bypass_line(self):
        self.assertEqual(cmc.new_refusal_functions(self.LINES, [], self.MESSAGE),
                         ['pool_admission_error', 'scripts_with_process_pool'])
        named = self.MESSAGE + 'Bypass tried: --pool-workers 1 --threads 14 on the 14-worker script, refused.\n'
        self.assertEqual(cmc.new_refusal_functions(self.LINES, [], named), [])

    def test_an_edited_or_ordinary_function_is_not_new(self):
        edited = ['def pool_admission_error(command, threads, pool_workers, extra=None):']
        removed = ['def pool_admission_error(command, threads, pool_workers):']
        self.assertEqual(cmc.new_refusal_functions(edited, removed, self.MESSAGE), [])
        self.assertEqual(cmc.new_refusal_functions(['def render_table(rows):', 'x = error_count + 1'], [],
                                                   self.MESSAGE), [])

    def test_its_stated_limit_a_function_named_otherwise(self):
        # The cheapest way around, tried before the commit: a gate function with a neutral name is not seen.
        self.assertEqual(cmc.new_refusal_functions(['def pool_gate(command):'], [], self.MESSAGE), [])


class BypassTest(unittest.TestCase):
    # The exposing commit, 17 October 2026: a new check wired into the finisher, no bypass named in its message.
    ADDED = ['tools/resemblance_coverage.py', 'tools/tests/test_resemblance_coverage.py']
    LINES = ['    import resemblance_coverage   # tools/resemblance_coverage.py says why; it also requires the paragraph',
             '    resemblance_coverage.validate(entry, root)']
    MESSAGE = 'Exposed degree occupancy: exposed vertices with margins cost no factor three each\n\nFramework: ...\n'

    def test_a_new_check_wired_in_without_a_bypass_line_is_refused(self):
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, self.LINES, self.MESSAGE), ['resemblance_coverage'])

    def test_a_bypass_line_or_an_unwired_tool_passes(self):
        named = self.MESSAGE + 'Bypass tried: a cites edge in the spec, and an entry without the paragraph; both refused.\n'
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, self.LINES, named), [])
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, ['    x = 1'], self.MESSAGE), [])
        self.assertEqual(cmc.unbypassed_checks(['tools/hooks/new_hook.py'], ['import new_hook'], self.MESSAGE), [])
        short = self.MESSAGE + 'Bypass tried: none.\n'
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, self.LINES, short), ['resemblance_coverage'])

    def test_a_module_added_earlier_and_wired_now_is_caught(self):
        # Its reviewer, 17 October 2026: add the module in one commit and wire it in the next. check_staged passes
        # the modules of the last RECENT commits with this commit's; the function sees them as added.
        earlier = ['tools/resemblance_coverage.py']
        self.assertEqual(cmc.unbypassed_checks([] + earlier, self.LINES, self.MESSAGE), ['resemblance_coverage'])
        self.assertGreaterEqual(cmc.RECENT, 10)

    def test_the_cheapest_ways_around_are_caught(self):
        for line in ('from resemblance_coverage import validate',
                     "spec = importlib.util.spec_from_file_location('m', ROOT / 'tools/resemblance_coverage.py')"):
            self.assertEqual(cmc.unbypassed_checks(self.ADDED, [line], self.MESSAGE), ['resemblance_coverage'], line)
        self.assertIn('compute.sh', cmc.CALLERS)
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, ['import resemblance_coverage_extra'], self.MESSAGE), [])

    def test_a_mention_or_the_module_s_own_file_is_not_a_wiring(self):
        # Its replay: a finisher message naming "tools/resemblance_coverage.py" and edits of the module itself.
        mention = "raise ValueError('rebuild with python3 tools/resemblance_coverage.py SPEC')"
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, [mention], self.MESSAGE), [])
        # The replay's false hit: "claim_refresh.py (AGENTS.md, ...)" in a message read as a call.
        message = "'tools/resemblance_coverage.py (AGENTS.md, index maintenance)')"
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, [message], self.MESSAGE), [])

    def test_a_run_by_path_and_the_branch_hooks_are_wirings(self):
        # Its reviewer, 17 October 2026: 5f3b7ed74 ran a check by its path, and dff02446e wired one into the
        # branch commit-msg hook; the rewritten check had dropped both.
        by_path = "    tool = Path(__file__).resolve().parents[1] / 'resemblance_coverage.py'"
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, [by_path], self.MESSAGE), ['resemblance_coverage'])
        self.assertIn('tools/git-hooks-branch/commit-msg', cmc.CALLERS)
        # Its third reading: loading or running by bare name.
        for line in ("mod = importlib.import_module('resemblance_coverage')", "__import__('resemblance_coverage')",
                     "runpy.run_module('resemblance_coverage')",
                     "subprocess.run([sys.executable, '-m', 'resemblance_coverage'])"):
            self.assertEqual(cmc.unbypassed_checks(self.ADDED, [line], self.MESSAGE), ['resemblance_coverage'], line)
        own = ('tools/resemblance_coverage.py', 'import resemblance_coverage')
        self.assertEqual(cmc.unbypassed_checks(self.ADDED, [own], self.MESSAGE), [])


if __name__ == '__main__':
    unittest.main()
