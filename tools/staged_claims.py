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
  - such a notebook, or the registry, differs between the index and the working tree: the check reads both in
    the working tree, so index and working tree must agree for the answer to be about the commit. This also
    refuses a partial commit of a notebook that has other unstaged work in it;
  - the opening tag of a new or changed article cannot be read for its id or its data-claims.
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
    """(number of new or changed articles, the claims they declare, articles whose tag could not be read)."""
    before, labels, count, unread = articles(old), set(), 0, []
    known = set(before.values())
    for match in ARTICLE.finditer(new):
        text = match.group(0)
        if text in known:
            continue
        count += 1
        ident, declared = IDENT.match(text), CLAIMS.match(text)
        tag = text[:text.index('>') + 1]
        # A '>' inside an attribute value cuts the tag short: the cut leaves an odd number of quotes.
        if not ident or tag.count('"') % 2 or ('data-claims' in tag and not declared):
            unread.append(tag[:120])
        elif declared:
            labels.update(label for label in declared.group(1).split() if label != 'none')
    return count, sorted(labels), unread


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
    span = ['--cached', base] if until is None else [base, until]      # the index against the base, amend included
    notebooks = git(root, 'diff', *span, '--name-only', '--diff-filter=AM', '--', '*.html').stdout.split()
    count, labels, touched, unread = 0, set(), [], []
    for path in notebooks:
        old = git(root, 'show', f'{base}:{path}', check=False).stdout
        new = git(root, 'show', f'{until or ""}:{path}').stdout
        number, found, bad = changed_labels(old, new)
        count += number
        unread += [f'{path}: {tag}' for tag in bad]
        if found:
            labels.update(found)
            touched.append(path)
    if unread:
        return ['  ' + line for line in unread] + [
            'Commit refused: the opening tag of a new or changed article could not be read for its id or its '
            'data-claims (above), so its claims cannot be checked. Repair the tag and commit again.']
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
