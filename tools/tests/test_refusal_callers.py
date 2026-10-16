"""Every in-repository caller of a shared tool that builds an argument list for a refused subcommand can pass
the flag that answers the refusal.

On 16 October 2026 a refusal was added to `claim-index.py author build` (a notebook newer than the spec needs
--summaries-checked), and it broke two callers that build argument lists for it, tools/claim_rebase.py and then
tools/claim_refresh.py, each found only when a real run stopped.  REFUSALS lists such refusals by hand, with the
text of the refusal itself and the flag that answers it; this test checks the refusal is still there and that
each tool invoking the subcommand by a quoted argument list mentions the flag outside comments.

Limits: a new refusal is covered only once its row is added here (nothing finds refusals automatically); argument
lists built by splitting a string, by appending, or by in-process calls to the tool's main are not found; a line
is cut at its first "#", even inside a string, so an argument list after such a "#" on the same line is missed;
the callers are checked statically, not run.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# (tool file the refusal lives in, text of the refusal there, argument-list pattern of the subcommand, flag)
REFUSALS = [
    ('tools/claim_authoring.py', 'rerun with --summaries-checked',
     r"""['"]author['"],\s*['"]build['"]""", '--summaries-checked'),
]


def code(text):
    """Python source without its comment text, so a comment that names a flag does not count."""
    return '\n'.join(re.sub(r'#.*$', '', line) for line in text.splitlines())


def callers(pattern):
    """Tool sources under tools/ (hooks included, tests excluded) that build an argument list matching
    `pattern` outside comments."""
    found = []
    for path in sorted((ROOT / 'tools').rglob('*.py')):
        if 'tests' in path.relative_to(ROOT / 'tools').parts:
            continue
        if re.search(pattern, code(path.read_text(encoding='utf-8'))):
            found.append(path)
    return found


class RefusalCallerTest(unittest.TestCase):
    def test_each_refusal_is_real_and_each_caller_can_answer_it(self):
        for home, refusal, pattern, flag in REFUSALS:
            with self.subTest(refusal=flag):
                self.assertIn(refusal, (ROOT / home).read_text(encoding='utf-8'),
                              f'{home} no longer holds the refusal "{refusal}"; update REFUSALS')
                found = callers(pattern)
                self.assertTrue(found, f'no caller matches {pattern}; the pattern is stale')
                for path in found:
                    self.assertIn(flag, code(path.read_text(encoding='utf-8')),
                                  f'{path.relative_to(ROOT)} invokes the subcommand but cannot pass {flag}')

    def test_the_caller_scan_sees_the_known_callers_and_ignores_comments(self):
        names = {path.name for path in callers(REFUSALS[0][2])}
        self.assertTrue({'claim_rebase.py', 'claim_refresh.py'} <= names, names)
        self.assertNotIn('--summaries-checked', code("x = 1  # pass --summaries-checked"))


if __name__ == '__main__':
    unittest.main()
