#!/usr/bin/env python3
"""Independent check of table_row_span on its smallest case.

Statement checked: for each system printed by the kernel with v <= 12, and each reported D, the
rank of K_D = sum_a (J_a, degree <= D) and the membership of 1 agree with a separate computation:
here J_a restricted to degree <= D is found as the kernel of the evaluation map from all polynomials
of degree <= D to functions on the complement-free cylinder R_a x {0,1}^(v-k), by brute force over
all 2^v points, with no use of the product structure the kernel relies on.
Argument: kernel JSON-lines file.  Polynomials are Python integers used as bit sets (small sizes).
"""
import itertools
import json
import sys


def nullspace(vectors):
    """Basis of combinations of the given integer bit-vectors that sum to zero, as index sets."""
    basis = {}
    out = []
    for i, vec in enumerate(vectors):
        comb = 1 << i
        while vec:
            p = vec.bit_length() - 1
            if p not in basis:
                basis[p] = (vec, comb)
                break
            bv, bc = basis[p]
            vec ^= bv
            comb ^= bc
        else:
            out.append(comb)
    return out


def span_rank(vectors, target):
    basis = {}
    for vec in vectors:
        while vec:
            p = vec.bit_length() - 1
            if p not in basis:
                basis[p] = vec
                break
            vec ^= basis[p]
    while target:
        p = target.bit_length() - 1
        if p not in basis:
            return len(basis), False
        target ^= basis[p]
    return len(basis), True


bad = checked = 0
for line in open(sys.argv[1]):
    if not line.startswith('{'):
        continue
    row = json.loads(line)
    v, k = row['v'], row['k']
    if v > 12:
        continue
    for entry in row['by_degree']:
        D = entry['D']
        monos = [sum(1 << i for i in c) for d in range(D + 1) for c in itertools.combinations(range(v), d)]
        gens = []
        for scope, table in row['rows']:
            pts = [x for x in range(1 << v)
                   if table[sum(((x >> s) & 1) << j for j, s in enumerate(scope))] == '1']
            # evaluation vector of each monomial on the cylinder's points
            evs = []
            for mo in monos:
                e = 0
                for j, x in enumerate(pts):
                    if x & mo == mo:
                        e |= 1 << j
                evs.append(e)
            for comb in nullspace(evs):
                gens.append(comb)          # bit i set: monomial monos[i] occurs
        rank, one = span_rank(gens, 1)     # monos[0] is the constant
        ok = rank == entry['rank'] and int(one) == entry['one_in_span']
        checked += 1
        bad += not ok
        print('v', v, 'seed', row['seed'], 'D', D, 'kernel', entry['rank'], entry['one_in_span'],
              'reference', rank, int(one), 'ok' if ok else 'MISMATCH')
print('checked', checked, 'mismatches', bad)
sys.exit(1 if bad else 0)
