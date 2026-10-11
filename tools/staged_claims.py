#!/usr/bin/env python3
"""Refuse a commit that stages a notebook entry whose declared claims the registry marks stale.

An entry declares its claims in data-claims on its article. The registry records, for each claim, hashes of the
entry it was built on; an entry edited after its claims were built makes those reviews stale, and the claim
check then fails. The finisher runs that check before any later edit, and nothing ran it at the commit: on
12 October 2026 an entry edited after the finisher was committed with the failure printed above the commit.

    staged_claims.py [--base REV]     check the commit being made (called by tools/git-hooks/pre-commit)
    staged_claims.py --base A --until B   audit the change from A to B against the working tree's registry

It compares each staged notebook with REV (HEAD by default; the hook passes HEAD^ for an amend), article by
article, and takes the claims declared by every article that is new or whose text changed, so an edit of an
entry's body counts as well as a new entry. It refuses when
  - a review of one of those claims is stale;
  - one of those claims is not in the registry;
  - such a notebook, or the registry, differs between the index and the working tree: the registry's hashes
    are of files, and the check reads the working tree, so the two must be the same for the answer to be about
    the commit.
Its work grows with the size of the staged notebooks (two readings of each) and the registry's load; it prints
the number of changed articles and claims and the time taken.
"""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'research/claims/index.json'
ARTICLE = re.compile(r'<article\b[^>]*>.*?</article>', re.S)
IDENT = re.compile(r'<article\b[^>]*\bid="([^"]*)"')
CLAIMS = re.compile(r'<article\b[^>]*\bdata-claims="([^"]*)"')


def git(root, *args, check=True):
    return subprocess.run(['git', *args], cwd=root, text=True, capture_output=True, check=check)


def articles(text):
    """Article id -> the article's whole text."""
    found = {}
    for match in ARTICLE.finditer(text):
        ident = IDENT.match(match.group(0))
        if ident:
            found[ident.group(1)] = match.group(0)
    return found


def changed_labels(old, new):
    """(number of new or changed articles, the claims they declare)."""
    before, labels, count = articles(old), set(), 0
    for ident, text in articles(new).items():
        if before.get(ident) == text:
            continue
        count += 1
        declared = CLAIMS.match(text)
        if declared:
            labels.update(label for label in declared.group(1).split() if label != 'none')
    return count, sorted(labels)


def stale(labels, root=ROOT):
    """(stale rows as (claim, field, reasons), labels missing from the registry), by the registry's coverage."""
    sys.path.insert(0, str(root / 'tools'))
    from claim_registry import load
    from claim_reviews import coverage
    data = load(root / REGISTRY)
    known = {claim['id'] for claim in data['claims']}
    report = coverage(data, root=root, labels=set(labels) & known)
    rows = [(row['id'], row['field'], row['reasons']) for row in report['fields'] if row['state'] == 'stale']
    return rows, sorted(set(labels) - known)


def check(root=ROOT, base='HEAD', until=None):
    """Messages refusing the commit; empty when it may go on. With until, the change from base to that
    revision is examined in place of the staged one, against the working tree's registry: an audit of a commit
    already made."""
    started = time.monotonic()
    span = ['--cached'] if until is None else [base, until]
    notebooks = git(root, 'diff', *span, '--name-only', '--diff-filter=AM', '--', '*.html').stdout.split()
    count, labels, touched = 0, set(), []
    for path in notebooks:
        old = git(root, 'show', f'{base}:{path}', check=False).stdout
        new = git(root, 'show', f'{until or ""}:{path}').stdout
        number, found = changed_labels(old, new)
        count += number
        if found:
            labels.update(found)
            touched.append(path)
    if not labels:
        return []
    unstaged = [] if until else git(root, 'diff', '--name-only', '--', *touched, REGISTRY).stdout.split()
    if unstaged:
        return ['Commit refused: ' + ', '.join(unstaged) + ' differ between the index and the working tree, and '
                'the staged entries declare claims whose registry hashes are of these files. Stage them, or '
                'set the unstaged changes aside, and commit again.']
    rows, missing = stale(sorted(labels), root)
    print(f'{count} staged articles are new or changed and declare {len(labels)} claims; checked in '
          f'{time.monotonic() - started:.1f} s.', file=sys.stderr)
    out = []
    for ident in sorted({row[0] for row in rows}):
        fields = ', '.join(row[1] for row in rows if row[0] == ident)
        reasons = sorted({reason for row in rows if row[0] == ident for reason in row[2]})
        out.append(f'  {ident}: stale {fields} ({"; ".join(reasons)})')
    out += [f'  {ident}: declared by a staged entry and not in the registry' for ident in missing]
    if out:
        out.append('Commit refused: a staged entry declares claims that the registry does not hold or whose '
                   'reviews are stale, the entry or the registry having changed after the claims were built. '
                   'Rebuild them (tools/claim-index.py author build with the entry\'s spec, then render), stage '
                   'the registry and commit again.')
    return out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='HEAD')
    parser.add_argument('--until', help='audit the change from --base to this revision instead of the staged one')
    args = parser.parse_args(argv)
    try:
        messages = check(ROOT, args.base, args.until)
    except Exception as error:                                         # a crash must not read as a pass
        print(f'Commit refused: tools/staged_claims.py failed ({type(error).__name__}: {error}); fix the tool or '
              'the registry and commit again.', file=sys.stderr)
        return 1
    for line in messages:
        print(line, file=sys.stderr)
    return 1 if messages else 0


if __name__ == '__main__':
    sys.exit(main())
