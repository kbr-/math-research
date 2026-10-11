"""The framework's files keep to what every branch shares.

Other branches of this repository build on this framework for their own subjects, and a tool carried over
from one of them tends to bring its vocabulary along: the name of the branch, of its subject, or of a tool
this branch does not have. A reader here can do nothing with such a name. This test fails when a framework
file holds one.

The names are not written here, where they would be the very thing the test forbids: the test holds
their SHA-256 digests and compares the digests of each file's words. That keeps them out of the text and
out of a search of it; it is no secret, since the digest of a short word can be guessed. A branch that
uses these names on purpose does not take this file.
"""
import hashlib
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATHS = ('tools', '.claude', '.codex', 'AGENTS.md', 'CLAUDE.md', 'COMPUTATION_RULES.md', 'PROMPTS.md', 'compute.sh')
DIGESTS = frozenset((
    '14181e40c487d35587b3e1ac2cd5fd5cf55618035a47559982c6fba9f51048e9',
    '0d67acda89d1cef832f5a2268ba31804b4d419ef6279134ea75437b1c073f3ce',
    '027ba98d0fac94e8ceae0e3af2a2e557a2c366de23ebe8b56d90bd5000bfb69d',
    '0bdf48ac87ca773a0604f904db97e81a833c46aa766862e7b41cf757f3024108',
    '907d363236a9049c617eb6a6e451639645199743dcb755364c68420e41d6911e',
    '14a7c5f27515d8e03546a0b467b7666565aa9f0d1c29e212d326d2c0040d8d10',
    '69dd63a84347f3c6fdb695cbdbf5465e2a030dba13c96b986806232f2f29ba03',
    '4e37993ae43b672168b3bebd9dc33f92b183f03f5fa3d6d89150923b2102a5a1',
    '11d40417959631d3d2420e8cd8709893c11cd7a4db737af63e8d56cfa7866f85',
    '34f3aba31219244bac97957bcc7406ae95f217cf2d7b8bfcc546b6315f89ff55',
    'd40f048c864bf130c4b0a6fdd7eea8a1a77f2e79ca19e21c5c4ad28c78db2745',
    '3ba5dc9b39b9fa69fcce35532e257583e734ec73532bc7e09974f88b2d25efba'))
WORD = re.compile(r'[a-z]+(?:_[a-z]+)*')
_seen = {}


def named(candidate, digests):
    """Whether `candidate` is one of the names, by its digest; each distinct candidate is hashed once."""
    if candidate not in _seen:
        _seen[candidate] = hashlib.sha256(candidate.encode()).hexdigest()
    return _seen[candidate] in digests


def candidates(line):
    """The forms of a line's words that a name can take: a word, its parts between underscores taken
    together in every run, a word with the slash that follows it, and two words joined by a hyphen.
    Case is ignored."""
    line = line.lower()
    for word in WORD.finditer(line):
        parts = word.group().split('_')
        for start in range(len(parts)):
            for end in range(start + 1, len(parts) + 1):
                yield '_'.join(parts[start:end])
        after = line[word.end():word.end() + 1]
        if after == '/':
            yield parts[-1] + '/'
        elif after == '-':
            joined = WORD.match(line, word.end() + 1)
            if joined:
                yield parts[-1] + '-' + joined.group().split('_')[0]


def hits(text, digests=DIGESTS):
    """The 1-based numbers of the lines of `text` that hold a name."""
    return [number for number, line in enumerate(text.splitlines(), 1)
            if any(named(candidate, digests) for candidate in set(candidates(line)))]


class BranchNamesTest(unittest.TestCase):
    def test_the_forms_a_name_takes_are_all_found(self):
        digest = lambda *names: frozenset(hashlib.sha256(name.encode()).hexdigest() for name in names)
        zebra = digest('zebra')
        for line in ('a zebra crosses', 'Zebra.', "the zebra's stripes", 'tools/zebra.py', 'zebra_index', 'test_zebra_index.py',
                     'ZEBRA_PROTOCOL', 'zebra-work', '"zebra"', 'data-kind="zebra"', 'private/zebra'):
            self.assertEqual(hits(f'first\n{line}\nlast', zebra), [2], line)
        for line in ('zebras', 'zebrafish', 'a zebr a', ''):
            self.assertEqual(hits(line, zebra), [], line)
        self.assertEqual(hits('zebra_index.py\nzebra index\nindex_zebra\nthe_zebra_index_file', digest('zebra_index')), [1, 4])
        self.assertEqual(hits('in zebras/x/PLAN.md\nthe zebras ran\nzebras /x', digest('zebras/')), [1])
        self.assertEqual(hits('Crosses-zebra: 1\ncrosses zebra\nold_crosses-zebra_x', digest('crosses-zebra')), [1, 3])
        self.assertEqual(len(DIGESTS), 12)
        self.assertTrue(all(re.fullmatch(r'[0-9a-f]{64}', each) for each in DIGESTS))

    def test_no_framework_file_holds_a_name(self):
        listed = subprocess.run(['git', 'ls-files', '-z', '--', *PATHS], cwd=ROOT, capture_output=True, text=True, check=True)
        files = [name for name in listed.stdout.split('\0') if name]
        self.assertGreater(len(files), 100)
        found = []
        for name in files:
            try:
                text = (ROOT / name).read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue
            found += [f'{name}:{number}' for number in hits(text)]
        self.assertEqual(found, [], 'these lines name something only another branch has; say it in words every '
                                    'branch can use, or keep it in that branch (tools/branch_extension.py)')


if __name__ == '__main__':
    unittest.main()
