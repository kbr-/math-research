#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
"""Summarize the residual-coordinate closure runs and compare them with the generic count.

Generic count: for m axioms of degree l in k Boolean variables, the first d at which the
coefficient of t^d in (1+t)^k (1+t^l)^(-m) is not positive.  It is the dimension count obtained
when multiples of the axioms are as independent as the relation f^2 = 0 of the graded Boolean
ring allows; it is used as a yardstick only.
"""
import glob, json, os, sys
from math import comb

def dreg(k, l, m, dmax=60):
    for d in range(dmax + 1):
        c = sum((-1) ** j * comb(m + j - 1, j) * comb(k, d - l * j)
                for j in range(d // l + 1) if d - l * j <= k)
        if c <= 0:
            return d
    return None

def count_k(l, m, d, v):
    ks = [k for k in range(d, v + 1) if (dreg(k, l, m) or 10 ** 9) <= d]
    return max(ks) if ks else None

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    rows = []
    for f in sorted(glob.glob(os.path.join(here, '*_l*_d*.jsonl'))):
        recs = [json.loads(x) for x in open(f) if x.startswith('{')]
        recs = [r for r in recs if 'skipped' not in r]
        if not recs:
            continue
        l, nrows, d = recs[0]['ell'], recs[0]['rows'], recs[0]['d']
        n = 1 << l
        by = {}
        for r in recs:
            by.setdefault(r['seed'], []).append(r)
        cells = []
        for s, rs in sorted(by.items()):
            ref = [r['k'] for r in rs if r['refuted']]
            non = [r['k'] for r in rs if not r['refuted']]
            top = max(ref) if ref else None
            cells.append(('%s' % top) if non else ('>=%s' % top))
        m = nrows * (nrows - 1) // 2
        rows.append((l, nrows, d, cells, count_k(l, m, d, nrows * l), nrows * l))
    print('holes rows v d | largest refuted k per seed | generic count')
    for l, nrows, d, cells, pred, v in sorted(rows):
        print('%5d %4d %3d %d | %-24s | %s' % (1 << l, nrows, v, d, ', '.join(cells), pred))

if __name__ == '__main__':
    main()
