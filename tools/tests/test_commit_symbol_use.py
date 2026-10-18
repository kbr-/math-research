import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'commit_symbol_use.py'
ENV = dict(os.environ, GIT_AUTHOR_NAME='Test', GIT_AUTHOR_EMAIL='test@example.invalid',
           GIT_COMMITTER_NAME='Test', GIT_COMMITTER_EMAIL='test@example.invalid')
PARSERS = all(importlib.util.find_spec(m) for m in ('tree_sitter', 'tree_sitter_python', 'tree_sitter_typescript'))

LAYER = {
    # top has no use: an import, a comment and a string don't count. middle and leaf are used only
    # inside it, so they have no user either; the `;` keeps x = 0 inside middle's body.
    'app/core.py': ('def leaf(): return 1\n'
                    'def middle(): return leaf(); x = 0\n'
                    'def top(): return middle()\n'
                    'def tested(): return helper_of_tested()\n'
                    'def helper_of_tested(): return 2\n'
                    'def live(): return 3\n'
                    'MAX_ITEMS = 5\n'
                    'class Row:\n'
                    '    __tablename__ = "rows"\n'),
    'app/main.py': 'from .core import live, top\nprint(live())  # top\nname = "top"\n',
    'tests/test_core.py': 'from app.core import tested\n\ndef test_tested():\n    assert tested()\n',
    # Page has no use, so Card, used only in Page's JSX, has none either; Used is used by a page.
    'web/src/widgets.tsx': ('export function Card() { return <div />; }\n'
                            'export function Page() { return <Card />; }\n'
                            'export const Used = () => 1;\n'),
    'web/src/app/x/page.tsx': ('import { Used } from "../../widgets";\n'
                               'export default function P() { return <b>{Used()}</b>; }\n'
                               'export async function generateMetadata() { return {}; }\n'),
}


@unittest.skipUnless(PARSERS, 'needs the tree-sitter, tree-sitter-python and tree-sitter-typescript packages')
class CommitSymbolUse(unittest.TestCase):
    """A scratch repository: a base commit, a layer commit with unused chains, and a later commit that
    uses the Python chain's top."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q', '-b', 'main')
        self.commit({'README.md': 'base\n'}, 'base')
        self.commit(LAYER, 'layer')
        self.commit({'app/main.py': LAYER['app/main.py'] + 'print(top())\n'}, 'later')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, env=ENV, check=True, text=True,
                              capture_output=True).stdout

    def commit(self, files, message):
        for name, text in files.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text)
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)

    def check(self, base, tip):
        return subprocess.run([str(TOOL), base, tip], cwd=self.root, text=True, capture_output=True)

    def test_candidate_grep_excludes_unparsed_artifacts(self):
        spec=importlib.util.spec_from_file_location('symbol_filter_fixture',TOOL)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        blobs=module.Blobs.__new__(module.Blobs);blobs.names=['top'];blobs.index={}
        with patch.object(module,'git',return_value='') as command:
            self.assertEqual(blobs.files_referencing('fixture','top'),[])
        args=command.call_args.args;paths=args[args.index('--')+1:]
        self.assertIn('*.py',paths);self.assertIn('*.tsx',paths)
        self.assertNotIn('*.md',paths);self.assertNotIn('*',paths)

    def test_a_chain_of_unused_symbols_is_found_in_one_pass(self):
        run = self.check('HEAD~2', 'HEAD~1')
        self.assertEqual(run.returncode, 1, run.stderr)
        recap = run.stdout.split('No user (fails the check):\n')[1]
        found = {line.split(': ')[1].split(' (')[0] for line in recap.splitlines()}
        self.assertEqual(found, {'top', 'middle', 'leaf', 'MAX_ITEMS', 'Page', 'Card'})
        self.assertIn('middle (app/core.py); only used by top', recap)
        self.assertIn('leaf (app/core.py); only used by middle', recap)
        self.assertIn('Card (web/src/widgets.tsx); only used by Page', recap)
        self.assertIn('6 symbols with no user, 1 used only by tests', run.stdout)

    def test_a_use_through_an_import_s_alias_is_a_use_and_an_alias_never_used_is_none(self):
        self.commit({'app/alias.py': 'def renamed(): return 1\ndef never(): return 2\ndef shelf(): return 3\n',
                     'app/user.py': 'from .alias import renamed as r, never as n\nimport shelf as s\nprint(r(), s)\n',
                     'web/src/a.ts': 'export function shown() { return 1; }\nexport function hidden() { return 2; }\n',
                     'web/src/b.ts': 'import { shown as s, hidden as h } from "./a";\nconsole.log(s());\n'}, 'aliases')
        run = self.check('HEAD~1', 'HEAD')
        self.assertEqual(run.returncode, 1, run.stderr)
        recap = run.stdout.split('No user (fails the check):\n')[1]
        # A module of a symbol's name, imported under an alias that is used, is no use of the symbol.
        self.assertEqual({line.split(': ')[1].split(' (')[0] for line in recap.splitlines()}, {'never', 'shelf', 'hidden'})

    def test_test_only_symbols_are_listed_and_keep_their_helpers_used(self):
        out = self.check('HEAD~2', 'HEAD~1').stdout
        self.assertIn('TESTS ONLY: tested (app/core.py)', out)
        for name in ('helper_of_tested', 'live', 'Used', 'Row', 'generateMetadata', ' P '):
            self.assertNotIn(name, out.replace('(', ' ').replace(')', ' '))

    def test_a_later_use_of_the_chain_top_is_the_first_use_of_the_whole_chain(self):
        out = self.check('HEAD~2', 'HEAD').stdout
        later = self.git('log', '-1', '--format=%h later').strip()
        for name in ('top', 'middle', 'leaf'):
            line = next(l for l in out.splitlines() if l.startswith(f'  NO USER: {name} '))
            self.assertTrue(line.endswith(f'; first used in {later}'), line)
        self.assertNotIn('first used', next(l for l in out.splitlines() if 'MAX_ITEMS' in l))

    def test_a_commit_that_only_adds_uses_passes(self):
        run = self.check('HEAD~1', 'HEAD')
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn('1 commits, 0 symbols with no user', run.stdout)
        self.assertNotIn('No user', run.stdout)

    def test_help_explains_the_tool_and_the_tip_defaults_to_head(self):
        run = subprocess.run([str(TOOL), '--help'], cwd=self.root, text=True, capture_output=True)
        self.assertEqual((run.returncode, run.stderr), (0, ''))
        self.assertIn('Flag symbols a commit adds without a user in that same commit.', run.stdout)
        self.assertIn('BASE', run.stdout)
        self.assertIn("Such a symbol is flagged NO USER", run.stdout)   # the whole description, as written
        default = subprocess.run([str(TOOL), 'HEAD~1'], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(default.stdout, self.check('HEAD~1', 'HEAD').stdout)
        self.assertIn('1 commits', default.stdout)
        self.assertIn('1 commits', self.check('HEAD~2', 'HEAD~1').stdout)   # a tip that is not HEAD ends the range
        self.assertIn('2 commits', subprocess.run([str(TOOL), 'HEAD~2'], cwd=self.root, text=True, capture_output=True).stdout)
        none = subprocess.run([str(TOOL)], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(none.returncode, 2)
        self.assertIn('BASE', none.stderr)


if __name__ == '__main__':
    unittest.main()
