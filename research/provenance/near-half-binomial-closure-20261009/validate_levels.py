#!/usr/bin/env python3
"""Validate binomial_closure's level sizes on satisfiable systems against truncated_buchberger.

Statement checked (lem:binomial-closure-classes, dimension part): for each satisfiable system
printed by the kernel in mode 2 with k = 2 (blocks read in F_4 with y = b_1 + g b_2), and each
D from w to min(n, w + extra), the kernel's cumulative count of live classes with a vector of
weight at most j equals the number of standard monomials of degree at most j of the degree-D
closure of the clause polynomials and Boolean axioms over F_2, for every j <= D; and the kernel
reports no dead vector.  The reference completes the system to the truncated pair condition, so
its standard monomials are the monomials divisible by no leading monomial.
Arguments: kernel JSON-lines file, extra.
"""
import itertools
import json
import sys
sys.path.insert(0, 'tools')
import truncated_buchberger as tb

LOG = {(1, 0): 0, (0, 1): 1, (1, 1): 2}          # log_g of b_1 + g b_2 in F_4, g^2 = g + 1
extra = int(sys.argv[2])
bad = checked = 0
for line in open(sys.argv[1]):
    if not line.startswith('{'):
        continue
    row = json.loads(line)
    if row['mode'] != 2 or row['k'] != 2:
        continue
    n, w = row['n'], row['w']
    axioms = []
    for blocks, exps, lam in row['rows']:
        for bits in itertools.product((0, 1), repeat=2 * len(blocks)):
            ys = [tuple(bits[2 * s:2 * s + 2]) for s in range(len(blocks))]
            allowed = all(y != (0, 0) for y in ys) and \
                sum(c * LOG[y] for c, y in zip(exps, ys)) % 3 == lam
            if not allowed:
                forms = [(1 << (2 * b + j), bits[2 * s + j] ^ 1)
                         for s, b in enumerate(blocks) for j in range(2)]
                axioms.append(tb.affine_product(n, forms))
    for D in range(w, min(n, w + extra) + 1):
        leads, const = tb.complete(tb.boolean_axioms(n) + [set(a) for a in axioms], D)
        assert not const
        supports = [frozenset(i for i, e in enumerate(m) if e) for m in leads if max(m) == 1]
        ref = []
        count = 0
        for j in range(D + 1):
            for sub in itertools.combinations(range(n), j):
                fs = frozenset(sub)
                if not any(s <= fs for s in supports):
                    count += 1
            ref.append(count)
        got = row['cumulative'][str(D)]
        ok = got['h'] == ref and got['dead'] == 0 and got['zero_dead'] == 0
        checked += 1
        bad += not ok
        print('m', row['m'], 't', row['t'], 'R', row['R'], 'seed', row['seed'], 'D', D,
              'kernel', got['h'], 'reference', ref, 'ok' if ok else 'MISMATCH')
print('checked', checked, 'mismatches', bad)
sys.exit(1 if bad else 0)
