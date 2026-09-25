#!/usr/bin/env python3
"""Three-way merge of the claim registry by record ID in a paused rebase or merge.

Reads stages 1 (base), 2 (upstream: HEAD during a rebase) and 3 (the commit being replayed) of
research/claims/index.json. In every list of records (claims, relationships, topic definitions
and so on) a record changed on one side takes that side's version, new records of either side are
kept (upstream order first, then the replayed side's new records in order), and a deletion on one
side is applied when the other side left the record unchanged. A record changed differently on
both sides, or deleted on one side and changed on the other, is a conflict: the tool then writes
nothing and lists the conflicts. Other top-level values merge the same way.

It then writes the registry and re-renders research/CLAIM_INDEX.md. It does not stage files or
continue Git operations. Use it when merge-formalization-appends.py refuses because existing claims
changed on both sides.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

REGISTRY = 'research/claims/index.json'


def _key(item):
    if isinstance(item, dict) and 'id' in item:
        return 'id:' + str(item['id'])
    return 'value:' + json.dumps(item, sort_keys=True)


def _merge_list(name, base, ours, theirs, conflicts):
    b = {_key(x): x for x in base}; o = {_key(x): x for x in ours}; t = {_key(x): x for x in theirs}
    out = []
    for k, ov in o.items():
        if k in b and k not in t:
            if ov != b[k]:
                conflicts.append(f'{name} {k}: deleted by the replayed side, changed upstream')
                out.append(ov)
            continue
        tv = t.get(k)
        if tv is None or tv == ov or (k in b and tv == b[k]):
            out.append(ov)
        elif k in b and ov == b[k]:
            out.append(tv)
        else:
            conflicts.append(f'{name} {k}: changed on both sides')
            out.append(ov)
    for k, tv in t.items():
        if k in o:
            continue
        if k in b:
            if tv != b[k]:
                conflicts.append(f'{name} {k}: deleted upstream, changed by the replayed side')
            continue
        out.append(tv)
    return out


def merge(base, ours, theirs):
    """Return (merged registry, list of conflicts)."""
    conflicts = []
    merged = {}
    for k in list(ours) + [k for k in theirs if k not in ours]:
        b, o, t = base.get(k), ours.get(k), theirs.get(k)
        if isinstance(o, list) and isinstance(t, list) and (b is None or isinstance(b, list)):
            merged[k] = _merge_list(k, b or [], o, t, conflicts)
        elif k not in ours:
            if k in base and t != b:
                conflicts.append(f'top-level {k}: deleted upstream, changed by the replayed side')
            elif k not in base:
                merged[k] = t
        elif k not in theirs:
            if k in base and o != b:
                conflicts.append(f'top-level {k}: deleted by the replayed side, changed upstream')
                merged[k] = o
            elif k not in base:
                merged[k] = o
        elif t == b or t == o:
            merged[k] = o
        elif o == b:
            merged[k] = t
        else:
            conflicts.append(f'top-level {k}: changed on both sides')
            merged[k] = o
    return merged, conflicts


def _stage(n, path):
    return json.loads(subprocess.check_output(['git', 'show', f':{n}:{path}']))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--registry', default=REGISTRY, help='registry path relative to the repository root')
    parser.add_argument('--no-render', action='store_true', help='do not re-render CLAIM_INDEX.md')
    args = parser.parse_args()
    merged, conflicts = merge(_stage(1, args.registry), _stage(2, args.registry), _stage(3, args.registry))
    if conflicts:
        print(f'{len(conflicts)} conflicting records; nothing written. Resolve them manually:')
        print('\n'.join(conflicts))
        return 1
    with open(args.registry, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print('Merged ' + ', '.join(f'{k}: {len(v)}' for k, v in merged.items() if isinstance(v, list)))
    if not args.no_render:
        tool = Path(__file__).resolve().parent / 'claim-index.py'
        subprocess.check_call([sys.executable, str(tool), 'render'])
    print('Review, then stage the registry and generated views and continue the rebase.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
