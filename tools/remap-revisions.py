#!/usr/bin/env python3
"""Keep the commit hashes recorded in the claim registry valid when history is rewritten.

Review `revision` fields in research/claims/index.json name commits. A rebase or amend rewrites
those commits, and the fields then name commits that the branch no longer contains.

--check lists every recorded revision that is not an ancestor of HEAD and exits 1 if there is one.
tools/check-claims.py runs it, so a stale hash fails before a push.

Otherwise the tool remaps. The old -> new pairs come from one of:
  --match OLD_RANGE NEW_RANGE  pair the commits of two ranges by author date and subject,
                               e.g. after a rebase: --match ORIG_BASE..ORIG_HEAD main..HEAD;
  --mapping FILE               a JSON object {old: new} (full hashes);
  --pairs                      "old new" lines on stdin, the format of Git's post-rewrite hook.
It then
  1. replaces every mapped `revision` value in the registry;
  2. updates a review's stored claim/value hash only where it matched the registry before the remap
     and differs after it, so only hashes that changed through the remap are touched (a
     relationships review hashes its edges, including their review revisions);
  3. updates recorded attention fingerprints the same way (a fingerprint covers correction edges);
  4. re-renders research/CLAIM_INDEX.md.
It stages and commits nothing.
"""

import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from claim_reviews import claim_digest, digest, field_value  # noqa: E402
from claim_attention import fingerprint  # noqa: E402

REGISTRY = ROOT / 'research/claims/index.json'
ATTENTION = ROOT / 'research/claims/attention.json'
HASH = re.compile(r'[0-9a-f]{40}')


def revisions(node):
    """Yield every dict holding a `revision` key."""
    if isinstance(node, dict):
        if 'revision' in node:
            yield node
        for value in node.values():
            yield from revisions(value)
    elif isinstance(node, list):
        for value in node:
            yield from revisions(value)


def remap_registry(data, mapping):
    """Return (remapped copy, number of revision fields changed, review hashes refreshed)."""
    new = copy.deepcopy(data)
    changed = 0
    for holder in revisions(new):
        if holder['revision'] in mapping:
            holder['revision'] = mapping[holder['revision']]; changed += 1
    old_claims = {c['id']: c for c in data['claims']}
    refreshed = []
    for claim in new['claims']:
        before = old_claims[claim['id']]
        for field, review in claim.get('reviews', {}).items():
            pairs = (('claim_sha256', claim_digest(before), claim_digest(claim)),
                     ('value_sha256', digest(field_value(data, before, field)), digest(field_value(new, claim, field))))
            for key, was, now in pairs:
                if review.get(key) == was != now:
                    review[key] = now; refreshed.append(f'{claim["id"]}.{field}.{key}')
    return new, changed, refreshed


def remap_attention(attention, old, new):
    """Replace recorded fingerprints that changed only through the remap; return the count."""
    moved = {}
    old_claims = {c['id']: c for c in old['claims']}
    for claim in new['claims']:
        was, now = fingerprint(old, old_claims[claim['id']]), fingerprint(new, claim)
        if was != now:
            moved[(claim['id'], was)] = now
    count = 0
    for event in attention.get('events', []):
        key = (event.get('claim'), event.get('fingerprint'))
        if key in moved:
            event['fingerprint'] = moved[key]; count += 1
    return count


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)


def match(old_range, new_range):
    def listing(spec):
        rows = [line.split('\t', 2) for line in git('log', '--reverse', '--format=%H\t%at\t%s', spec).splitlines()]
        keys = {}
        for commit, stamp, subject in rows:
            if (stamp, subject) in keys:
                raise SystemExit(f'Two commits in {spec} share author date and subject: {subject}')
            keys[(stamp, subject)] = commit
        return keys
    old, new = listing(old_range), listing(new_range)
    unmatched = [s for (_, s) in old if (_, s) not in new]
    if unmatched:
        raise SystemExit('Old commits without a rewritten counterpart: ' + '; '.join(unmatched))
    return {old[k]: new[k] for k in old}


def stale(data):
    reachable = set(git('rev-list', 'HEAD').split())
    counts = {}
    for holder in revisions(data):
        rev = holder['revision']
        if rev not in reachable:
            counts[rev] = counts.get(rev, 0) + 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true', help='fail if a recorded revision is not an ancestor of HEAD')
    mode.add_argument('--match', nargs=2, metavar=('OLD_RANGE', 'NEW_RANGE'))
    mode.add_argument('--mapping', type=Path)
    mode.add_argument('--pairs', action='store_true', help='read "old new" lines from stdin')
    parser.add_argument('--no-render', action='store_true')
    args = parser.parse_args()
    data = json.loads(REGISTRY.read_text(encoding='utf-8'))
    if args.check:
        found = stale(data)
        if found:
            print(f'{len(found)} recorded revisions are not ancestors of HEAD ({sum(found.values())} fields):')
            for rev, n in sorted(found.items()):
                print(f'  {rev}  {n} fields')
            print('History was rewritten after they were recorded; remap them with tools/remap-revisions.py.')
            return 1
        print('Every recorded revision is an ancestor of HEAD.')
        return 0
    if args.match:
        mapping = match(*args.match)
    elif args.mapping:
        mapping = json.loads(args.mapping.read_text())
    else:
        mapping = dict(line.split()[:2] for line in sys.stdin if line.strip())
    bad = [h for pair in mapping.items() for h in pair if not HASH.fullmatch(h)]
    if bad:
        raise SystemExit('Mappings need full 40-character hashes: ' + ', '.join(bad[:5]))
    mapping = {o: n for o, n in mapping.items() if o != n}
    new, changed, refreshed = remap_registry(data, mapping)
    text = json.dumps(new, indent=2, ensure_ascii=False) + '\n'
    leftover = [o for o in mapping if o in text]
    if leftover:
        raise SystemExit('Old hashes also occur outside revision fields; nothing written: ' + ', '.join(leftover))
    attention = json.loads(ATTENTION.read_text(encoding='utf-8'))
    moved = remap_attention(attention, data, new)
    REGISTRY.write_text(text, encoding='utf-8')
    ATTENTION.write_text(json.dumps(attention, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{len(mapping)} commits remapped: {changed} revision fields, {len(refreshed)} review hashes, '
          f'{moved} attention fingerprints.')
    if not args.no_render:
        subprocess.check_call([sys.executable, str(TOOLS / 'claim-index.py'), 'render'], cwd=ROOT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
