#!/usr/bin/env python3
"""Build a source-pinned normality-exception inventory; unknown is never empty.

The small scope manifest contains reviewed theorem applications, not inferred
scope from prose. Any changed source summary/status fails closed for re-review.
This is an inventory builder, not an exception-search or cutoff algorithm.
"""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def summary_hash(claim):
    return hashlib.sha256(claim['summary'].encode()).hexdigest()


def inventory(registry, spec, n_max, p_max):
    if not (1 <= n_max <= spec['n_max'] and 3 <= p_max <= spec['p_max']):
        raise ValueError('Requested bounds exceed the reviewed inventory scope')
    if spec['version'] != 1:
        raise ValueError('Unknown inventory scope format')
    claims = {c['id']: c for c in registry['claims']}
    evidence = {}
    for rule in spec['complete_empty'] + spec['partial']:
        cid = rule['claim']
        claim = claims.get(cid)
        if (claim is None or claim['mathematical_status'] != 'working_proof'
                or summary_hash(claim) != rule['summary_sha256']):
            raise ValueError(f'{cid}: source changed or is not a working proof; re-review scope')
        evidence[cid] = {'record': claim['record'], 'summary_sha256': summary_hash(claim),
                         'mathematical_status': claim['mathematical_status']}
    primes = [p for p in range(3, p_max + 1, 2)
              if all(p % q for q in range(2, int(p**0.5) + 1))]
    rows = []
    for n in range(1, n_max + 1):
        for p in primes:
            complete = [r for r in spec['complete_empty']
                        if r['dimension_min'] <= n <= r['dimension_max']]
            partial = [r for r in spec['partial'] if (r['n'], r['p']) == (n, p)]
            rows.append({'n': n, 'p': p,
                         'status': 'complete' if complete else 'unresolved',
                         'exception_set': [] if complete else None,
                         'evidence': [r['claim'] for r in complete + partial],
                         'certified_normal_degrees': [r['normal_degrees'] for r in partial]})
    return {'version': 1, 'scope': 'E_(n,p) = {d >= 2: generic original determinant is zero}',
            'basis': 'Recorded working proofs; no new computation or formal verification inferred',
            'n_max': n_max, 'p_max': p_max, 'odd_primes': primes,
            'complete_pairs': sum(r['status'] == 'complete' for r in rows),
            'unresolved_pairs': sum(r['status'] != 'complete' for r in rows),
            'evidence': evidence, 'pairs': rows}


def markdown(data):
    lines = ['# Generic normality exception inventory', '',
             'An empty set is recorded only when a cited working proof covers every degree. '
             'Unresolved entries are **not** empty sets. This inventory does not supply a stopping algorithm.', '',
             f"Scope: dimensions 1–{data['n_max']}; odd primes through {data['p_max']}.", '',
             '| Dimension | Complete empty sets | Unresolved pairs |',
             '|---:|---:|---:|']
    for n in range(1, data['n_max'] + 1):
        rows = [r for r in data['pairs'] if r['n'] == n]
        complete = sum(r['status'] == 'complete' for r in rows)
        lines.append(f'| {n} | {complete} | {len(rows)-complete} |')
    lines += ['', f"Total: **{data['complete_pairs']} complete**, **{data['unresolved_pairs']} unresolved**.", '',
              'Evidence:', '']
    lines += [f"- `{cid}`: {e['record']} ({e['mathematical_status']})."
              for cid, e in data['evidence'].items()]
    for row in data['pairs']:
        for known in row['certified_normal_degrees']:
            lines += ['', f"For n={row['n']}, p={row['p']}, certified normal degrees: "
                      + json.dumps(known, sort_keys=True) + '. The complete exception set remains unresolved.']
    lines += ['', 'The pairwise machine-readable inventory is in `inventory.json`. '
              'Bounds may be reduced according to measured cost, as requested by the user.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=ROOT/'research/claims/index.json')
    parser.add_argument('--scope', type=Path, default=ROOT/'research/normality-inventory-scope.json')
    parser.add_argument('--n-max', type=int, default=10)
    parser.add_argument('--p-max', type=int, default=97)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--markdown', type=Path)
    args = parser.parse_args()
    try:
        data = inventory(json.loads(args.registry.read_text()), json.loads(args.scope.read_text()),
                         args.n_max, args.p_max)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    args.out.write_text(json.dumps(data, indent=2) + '\n')
    if args.markdown:
        args.markdown.write_text(markdown(data))
    print(f"{len(data['pairs'])} pairs: {data['complete_pairs']} complete; "
          f"{data['unresolved_pairs']} unresolved. No unknown set was returned as empty.")


if __name__ == '__main__':
    main()
