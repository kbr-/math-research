#!/usr/bin/env python3
"""Exact degree-residue filter for the n=9, p=3 joint leading coefficient.

This computes where a SUFFICIENT coefficient is a unit, not the exception set.
Stages: sparse numerator multiplicities; valuation-tree pruning; exhaustive
partition checks and independent direct valuations on a bounded control range.
At most 254 numerator offsets remain active at each depth. Integer bookkeeping
only: no Jacobian, determinant matrix, floating-point arithmetic, or libraries.
"""
import argparse
from collections import Counter
from fractions import Fraction
import json
from time import perf_counter


def vp(x, p):
    assert x
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


def tree(h, a, b, p):
    assert a % p and p % 2
    weights = {k: min(h - 1, k // 2) - max(1, k - h + 1) + 1
               for k in range(2, 2 * h - 1)}
    assert all(w > 0 for w in weights.values())
    assert sum(weights.values()) == h * (h - 1) // 2
    denominator = sum(w * vp(k, p) for k, w in weights.items())
    pending = [(0, 1, 0, tuple(weights))]
    leaves = []
    visited = 0
    while pending:
        r, modulus, total, active = pending.pop()
        visited += 1
        if visited > 200000:
            raise RuntimeError('Sizing guard: too many tree nodes; no result')
        if total > denominator or not active:
            if not active:
                assert total >= denominator, 'Contradicts integer Hankel product'
            leaves.append({'residue': r, 'modulus': modulus,
                           'unit': total == denominator and not active,
                           'numerator_valuation_lower': total})
            continue
        next_modulus = modulus * p
        for digit in range(p):
            child = r + digit * modulus
            kept = tuple(k for k in active
                         if (2*a*child + 2*b + k) % next_modulus == 0)
            pending.append((child, next_modulus,
                            total + sum(weights[k] for k in kept), kept))
    # Tree construction makes the leaves disjoint; total cylinder mass is one.
    assert sum((Fraction(1, x['modulus']) for x in leaves), Fraction()) == 1
    unit_mass = sum((Fraction(1, x['modulus']) for x in leaves if x['unit']), Fraction())
    return weights, denominator, visited, leaves, unit_mass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    start = perf_counter()
    n, p, h, a, b = 9, 3, 128, 128, -448
    weights, denominator, visited, leaves, mass = tree(h, a, b, p)
    controls = []
    for d in range(7, 736):
        s = a*d+b
        exact = sum(w*vp(2*s+k,p) for k,w in weights.items())-denominator
        matches = [x for x in leaves if d % x['modulus'] == x['residue']]
        assert len(matches) == 1
        assert matches[0]['unit'] == (exact == 0)
        controls.append({'degree':d,'valuation':exact})
    small_controls = 0
    for small_h in range(2, 7):
        ws, dv, _, ls, _ = tree(small_h, 1, 0, 3)
        for small_s in range(7):
            exact_product = Fraction(1)
            for i in range(1, small_h):
                for j in range(i, small_h):
                    exact_product *= Fraction(2*small_s+i+j, i+j)
            assert exact_product.denominator == 1
            match = [x for x in ls if small_s % x['modulus'] == x['residue']]
            assert len(match) == 1 and match[0]['unit'] == (exact_product.numerator % 3 != 0)
            small_controls += 1
    depth_counts = Counter((x['modulus'],x['unit']) for x in leaves)
    result = {'scope':'Unit locus of sufficient joint coefficient, NOT generic exception set',
              'n':n,'p':p,'bulk_degree_min':7,'h':h,'s_affine':[a,b],
              'denominator_valuation':denominator,'visited_nodes':visited,
              'leaf_count':len(leaves),'unit_density':str(mass),
              'max_modulus':max(x['modulus'] for x in leaves),
              'leaf_counts':[{'modulus':m,'unit':u,'count':c}
                             for (m,u),c in sorted(depth_counts.items())],
              'leaves':sorted(leaves,key=lambda x:(x['modulus'],x['residue'])),
              'controls':controls,'small_exact_product_controls':small_controls,'elapsed_seconds':perf_counter()-start}
    with open(args.out,'w') as f:
        json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('leaves','controls')}))
    print('COEFFICIENT_TREE_COMPLETED')

if __name__ == '__main__':
    main()
