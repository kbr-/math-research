#!/usr/bin/env python3
"""Zero-sum sets of a paired row and the sharing property of a minimal counterexample.

Statement computed (side notebook near-half-pc-degree, lem:paired-row-minimal-counterexample (4)): for pair
weights a_1..a_h modulo an odd q, a set J of pairs is a zero-sum set when some signs eta in {+1,-1}^J give
sum eta_j a_j = 0 mod q.  w is the least size of a zero-sum set.  The lemma's part (4): "for every
(w-1)-subset I of J there is another J' in the family, J' != J, with J' containing I; likewise for every
w-subset".  A family of zero-sum sets shares at size k when every k-subset of each member lies in another
member; the lemma's condition is sharing at size w, which implies sharing at size w-1.  A least
counterexample to conj:paired-row-symbols needs a nonempty family of zero-sum sets sharing at size w, so
the program prunes at each of the two sizes: remove members having a k-subset in no other remaining member,
until stable, and reports the size of what is left (the largest subfamily sharing at size k; such families
are closed under union).  Exact; 2^h sets.
Arguments: --out PATH, then rows h:q:a_1,...,a_h; one JSON line per row.
"""
import argparse
import json
from itertools import combinations


def zero_sum_sets(weights, q):
    """Bitmasks of the nonempty sets of pairs carrying a signed zero-sum modulo q."""
    h = len(weights)
    sums = [None] * (1 << h)
    sums[0] = frozenset([0])
    found = []
    for mask in range(1, 1 << h):
        low = (mask & -mask).bit_length() - 1
        a = weights[low] % q
        rest = sums[mask ^ (1 << low)]
        sums[mask] = frozenset((s + a) % q for s in rest) | frozenset((s - a) % q for s in rest)
        if 0 in sums[mask]:
            found.append(mask)
    return found


def analyse(weights, q):
    members = zero_sum_sets(weights, q)
    if not members:
        return {'zero_sum_sets': 0, 'w': None, 'by_size': {}, 'sharing': None, 'pruned_size': 0,
                'sharing_at_w': None, 'pruned_size_at_w': 0}
    w = min(bin(m).count('1') for m in members)

    def prune(k):
        subsets = {m: [sum(1 << i for i in c)
                       for c in combinations([i for i in range(len(weights)) if m >> i & 1], k)]
                   for m in members}

        def lonely(family):
            count = {}
            for m in family:
                for s in subsets[m]:
                    count[s] = count.get(s, 0) + 1
            return [m for m in family if any(count[s] < 2 for s in subsets[m])]

        family = list(members)
        alone = lonely(family)
        whole = not alone
        while alone:
            drop = set(alone)
            family = [m for m in family if m not in drop]
            alone = lonely(family)
        return whole, len(family)

    sharing, left = prune(w - 1)
    sharing_w, left_w = prune(w)
    sizes = {}
    for m in members:
        sizes[bin(m).count('1')] = sizes.get(bin(m).count('1'), 0) + 1
    return {'zero_sum_sets': len(members), 'w': w, 'by_size': {str(k): sizes[k] for k in sorted(sizes)},
            'sharing': sharing, 'pruned_size': left, 'sharing_at_w': sharing_w, 'pruned_size_at_w': left_w}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', required=True)
    ap.add_argument('rows', nargs='+', help='h:q:a_1,...,a_h')
    args = ap.parse_args()
    with open(args.out, 'w') as out:
        for row in args.rows:
            h, q, listed = row.split(':')
            weights = [int(x) for x in listed.split(',')]
            if len(weights) != int(h) or int(q) % 2 == 0 or int(h) > 20:
                raise SystemExit(f'{row}: need h weights, odd q, h <= 20')
            out.write(json.dumps({'h': int(h), 'q': int(q), 'weights': weights, **analyse(weights, int(q))}) + '\n')


if __name__ == '__main__':
    main()
