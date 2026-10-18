"""A module-level constant (an upper-case name) is assigned once per module of tools/: a second assignment
silently replaces the first for every function that reads it.  On 18 October 2026 a new RELATION pattern in
tools/draft_claim_sentences.py replaced the module's RELATION, which two other listings read, and the suite
passed; the build's author found it while renaming (commit 85459c244 holds the exposing form)."""
import ast
import collections
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def repeated_constants(source):
    """[(name, line numbers)] for the upper-case names assigned more than once at a module's top level."""
    seen = collections.defaultdict(list)
    for node in ast.parse(source).body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        for target in targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                seen[target.id].append(node.lineno)
    return [(name, lines) for name, lines in seen.items() if len(lines) > 1]


class ModuleConstantsTest(unittest.TestCase):
    def test_the_exposing_form_is_refused(self):
        exposing = subprocess.run(['git', 'show', '85459c244:tools/draft_claim_sentences.py'], cwd=ROOT,
                                  capture_output=True, text=True)
        if exposing.returncode:
            self.skipTest('commit 85459c244 not in this clone')
        self.assertEqual([name for name, _ in repeated_constants(exposing.stdout)], ['RELATION'])

    def test_a_constant_read_and_reassigned_inside_a_function_is_not_counted(self):
        self.assertEqual(repeated_constants('LIMIT = 1\ndef f():\n    LIMIT = 2\n    return LIMIT\n'), [])
        self.assertEqual(repeated_constants('LIMIT = 1\nLIMIT = 2\n'), [('LIMIT', [1, 2])])

    def test_no_module_of_tools_assigns_a_constant_twice(self):
        found = {}
        for path in sorted((ROOT / 'tools').rglob('*.py')):
            if 'tests' in path.relative_to(ROOT / 'tools').parts:
                continue
            repeated = repeated_constants(path.read_text(encoding='utf-8'))
            if repeated:
                found[str(path.relative_to(ROOT))] = repeated
        self.assertEqual(found, {}, 'rename one of each pair, or merge them')


if __name__ == '__main__':
    unittest.main()
