#!/usr/bin/env python3
"""Count, over a range of commits, how the entries added to each notebook stand to its Where we stand.

Every cycle reviews a notebook's Where we stand, and tools/notebook-append.py refuses an entry while that
section is as the last commit has it, unless --stand-unchanged REASON says why; the entry then holds the
reason in a paragraph labelled Where we stand. This reads git, not a session: for each commit of the range
and each notebook it changes, the entries the commit adds are counted as

- changed: the commit also changes the notebook's Where we stand, and the entry holds no reason;
- with a reason: the entry holds the paragraph, whose text is the reason;
- neither: the section is unchanged and the entry holds no reason, so it was appended some other way than
  through the appender.

It prints one line of counts for each notebook and under it the reasons grouped by their text, most frequent
first, so a reason passed by rote shows as one line with a large count. A commit that changes a notebook
and adds no entry is not counted. The last line says what was read: commits, notebook versions, megabytes.

Usage: tools/stand_reasons.py RANGE [--notebook PATH ...]
  RANGE is a git revision range (main~60..main); --notebook limits the count to those paths.
"""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
import collections
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = re.compile(r'<article\b[^>]*?\sid="([^"]+)"[^>]*>.*?</article>', re.S)
REASON = re.compile(r'<p><strong>Where we stand\.</strong> Unchanged: (.*?)</p>', re.S)


def git(root, *arguments):
    return subprocess.run(['git', '-C', str(root), *arguments], capture_output=True, text=True, check=True).stdout


def version(root, revision, path):
    """The file at `path` in `revision`, or '' where the revision has none."""
    shown = subprocess.run(['git', '-C', str(root), 'show', f'{revision}:{path}'], capture_output=True, text=True)
    return shown.stdout if shown.returncode == 0 else ''


def stand(text):
    start = text.find('<section id="where-we-stand"')
    return None if start < 0 else text[start:text.index('</section>', start)]


def count(root, revisions, notebooks=None):
    """({notebook: Counter of 'added', 'changed', 'reason', 'neither'}, {notebook: Counter of reasons},
    (commits read, notebook versions read, their megabytes)) over the commits of the range `revisions`."""
    counts = collections.defaultdict(collections.Counter)
    reasons = collections.defaultdict(collections.Counter)
    commits = git(root, 'rev-list', '--reverse', '--no-merges', revisions).split()
    versions = size = 0
    for commit in commits:
        changed = git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', commit).split('\n')
        for path in changed:
            if not path.endswith('notebook.html') or (notebooks and path not in notebooks):
                continue
            before, after = version(root, f'{commit}^', path), version(root, commit, path)
            versions, size = versions + 2, size + len(before) + len(after)
            known = {match.group(1) for match in ARTICLE.finditer(before)}
            moved = stand(before) != stand(after)
            for match in ARTICLE.finditer(after):
                if match.group(1) in known:
                    continue
                counts[path]['added'] += 1
                reason = REASON.search(match.group(0))
                if reason:
                    counts[path]['reason'] += 1
                    reasons[path][' '.join(html.unescape(reason.group(1)).split())] += 1
                else:
                    counts[path]['changed' if moved else 'neither'] += 1
    return counts, reasons, (len(commits), versions, size / 1e6)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('revisions', metavar='RANGE')
    parser.add_argument('--notebook', action='append', metavar='PATH')
    options = parser.parse_args(argv)
    try:
        counts, reasons, (commits, versions, megabytes) = count(ROOT, options.revisions, options.notebook)
    except subprocess.CalledProcessError as error:
        print(f'stand_reasons: {error.stderr.strip()}', file=sys.stderr)
        return 1
    for path in sorted(counts):
        tally = counts[path]
        print(f"{path}: {tally['added']} entries added; {tally['changed']} with Where we stand changed; "
              f"{tally['reason']} with a reason; {tally['neither']} with neither")
        for reason, times in reasons[path].most_common():
            print(f'  {times} x {reason}')
    print(f'Read {commits} commits, {versions} notebook versions, {megabytes:.0f} MB')
    return 0


if __name__ == '__main__':
    sys.exit(main())
