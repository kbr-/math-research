#!/usr/bin/env python3
"""Information budget of W's clauses versus equations (strategy review, 26 September 2026).

Heuristic tested: a clause with prefix k excludes a fraction at most (1/3)(2/3)^k of assignments on which
its forms are uniform. Naive count: n^K blocks with h clauses each exclude at most B_naive = n^K h (1/3)(2/3)^k.
Block count: every clause of a block needs all its prefix forms nonzero, so a block excludes at most (2/3)^k in
total whatever h is, and the family at most B_block = n^K (2/3)^k. The conditioning law (a conjecture) charges about 1/2 degree per n-1 random equations,
each excluding 2/3. So B, measured in equations, is below one when B < 1, and the predicted degree loss is
negligible. Reports B for k = 2.5(K+1) ln n, h = n^2.
Usage: info_budget.py --out PATH
"""
import argparse, json, math
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
rows = []
for K in (1, 2, 3, 5):
    for e in (3, 6, 9, 12):
        n = 10.0 ** e
        k = 2.5 * (K + 1) * math.log(n)
        logB = K * math.log(n) + 2 * math.log(n) - math.log(3) + k * math.log(2 / 3)
        logBb = K * math.log(n) + k * math.log(2 / 3)
        rows.append({'K': K, 'n': f'1e{e}', 'k': round(k, 1), 'log10_naive_h_n2': round(logB / math.log(10), 2),
                     'log10_block': round(logBb / math.log(10), 2)})
json.dump(rows, open(a.out, 'w'), indent=1); print(json.dumps(rows))
