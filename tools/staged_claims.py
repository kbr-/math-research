#!/usr/bin/env python3
"""Refuse a commit that stages a notebook entry whose declared claims the registry marks stale.

An entry declares its claims in data-claims on its article. The registry records, for each claim, hashes of the
entry it was built on; an entry edited after its claims were built makes those reviews stale, and the claim
check then fails. The finisher runs that check before any later edit, and nothing ran it at the commit: on
12 October 2026 an entry edited after the finisher was committed with the failure printed above the commit.

    staged_claims.py            check the commit being made (called by tools/git-hooks/pre-commit)

Looks only at the articles that the staged change adds or whose opening tag it changes, so its work grows with
the entries of one commit and not with the record; it prints the number of claims checked and the time taken.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = re.compile(r'^\+.*?<article\b[^>]*\bdata-claims="([^"]*)"', re.M)


def staged_labels(diff):
    """The claim identifiers declared by article tags on the added lines of a unified diff."""
    labels = []
    for found in ARTICLE.findall(diff):
        labels += [label for label in found.split() if label != 'none']
    return sorted(set(labels))


def stale(labels, root=ROOT):
    """(claim, field, reasons) for each stale review of the given claims, by the registry's own coverage."""
    sys.path.insert(0, str(root / 'tools'))
    from claim_registry import load
    from claim_reviews import coverage
    report = coverage(load(root / 'research' / 'claims' / 'index.json'), root=root, labels=set(labels))
    return [(row['id'], row['field'], row['reasons']) for row in report['fields'] if row['state'] == 'stale']


def main():
    started = time.monotonic()
    diff = subprocess.run(['git', 'diff', '--cached', '-U0', '--', '*.html'], cwd=ROOT, text=True,
                          capture_output=True, check=True).stdout
    labels = staged_labels(diff)
    if not labels:
        return 0
    rows = stale(labels)
    print(f'Staged entries declare {len(labels)} claims; checked in {time.monotonic() - started:.1f} s.',
          file=sys.stderr)
    if not rows:
        return 0
    for ident in sorted({row[0] for row in rows}):
        fields = ', '.join(row[1] for row in rows if row[0] == ident)
        reasons = sorted({reason for row in rows if row[0] == ident for reason in row[2]})
        print(f'  {ident}: stale {fields} ({"; ".join(reasons)})', file=sys.stderr)
    print('Commit refused: a staged entry declares claims whose registry reviews are stale, the entry or the '
          'registry having changed after the claims were built. Rebuild them (tools/claim-index.py author build '
          'with the entry\'s spec, then render), stage the registry and commit again.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
