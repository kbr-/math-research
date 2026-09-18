#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
"""Walsh spectrum of near-injective labelings of m rows by l-bit labels, and the largest density
boost of such a set on affine subspaces of small codimension of the label-bit space.

S_j = labelings of m rows whose image has exactly m - j labels (S_0: injective).  For an affine
subspace H = {chi_1 = e_1, ..., chi_s = e_s} the density boost of S is
  mu_H(S) / mu(S) = sum over chi in span(chi_1..chi_s) of (+-1) * hat S(chi) / hat S(0),
so codimension-one boosts are 1 + |hat S(chi)| / hat S(0), and higher codimensions are searched
greedily among the characters of largest coefficient (a lower bound on the maximum boost)."""
import argparse, itertools, json, sys, time
import numpy as np

def wht(a):
    n = a.shape[0]; h = 1
    while h < n:
        a = a.reshape(-1, 2, h)
        a = np.concatenate((a[:, 0, :] + a[:, 1, :], a[:, 0, :] - a[:, 1, :]), axis=1).reshape(-1)
        h *= 2
    return a

def describe(mask, m, l):
    return [(mask >> (l * i)) & ((1 << l) - 1) for i in range(m)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--l', type=int, default=3); ap.add_argument('--m', type=int, default=None)
    ap.add_argument('--top', type=int, default=40); ap.add_argument('--maxcodim', type=int, default=4)
    ap.add_argument('--out', default=None)
    args = ap.parse_args(); l = args.l; n = 1 << l; m = args.m or n; bits = m * l
    t0 = time.time(); idx = np.arange(1 << bits, dtype=np.int64)
    occ = np.zeros(1 << bits, dtype=np.int64)
    for i in range(m):
        occ |= np.int64(1) << ((idx >> (l * i)) & (n - 1))
    img = np.zeros(1 << bits, dtype=np.int8)
    for z in range(n):
        img += ((occ >> z) & 1).astype(np.int8)
    del occ, idx
    out = {'l': l, 'm': m, 'bits': bits, 'sets': {}}
    for j in range(0, 3):
        ind = (img == m - j).astype(np.int64); size = int(ind.sum())
        if size == 0: continue
        spec = wht(ind); del ind
        order = np.argsort(-np.abs(spec))[: args.top + 1]
        top = [(int(c), int(spec[c])) for c in order if c != 0][: args.top]
        rec = {'size': size, 'density': size / float(1 << bits),
               'top': [{'mask': c, 'rows': describe(c, m, l), 'coef_over_size': v / size} for c, v in top]}
        # greedy / exhaustive search among the top characters for the best boost at codim <= maxcodim
        cand = [c for c, _ in top[: min(args.top, 24)]]
        best = {}
        for s in range(1, args.maxcodim + 1):
            bb = (0.0, None)
            for combo in itertools.combinations(cand, s):
                span = {0}
                for c in combo: span |= {x ^ c for x in span}
                if len(span) != 1 << s: continue
                # best coset: choose signs e_i to maximise sum over span of sign(chi) * coef
                vals = []
                for signs in range(1 << s):
                    tot = 0
                    for sub in range(1 << s):
                        x = 0; sg = 1
                        for b in range(s):
                            if (sub >> b) & 1:
                                x ^= combo[b]
                                if (signs >> b) & 1: sg = -sg
                        tot += sg * int(spec[x])
                    vals.append(tot)
                v = max(vals) / size
                if v > bb[0]: bb = (v, [describe(c, m, l) for c in combo])
            best[s] = {'boost': bb[0], 'characters': bb[1]}
        rec['best_boost_among_top'] = best
        out['sets']['S_%d' % j] = rec
        del spec
    out['seconds'] = time.time() - t0
    s = json.dumps(out, indent=1)
    if args.out: open(args.out, 'w').write(s)
    for name, rec in out['sets'].items():
        print(name, 'size', rec['size'], 'density %.3e' % rec['density'])
        for t in rec['top'][:8]: print('   ', t['rows'], '%.4f' % t['coef_over_size'])
        for s_, b in rec['best_boost_among_top'].items(): print('   codim', s_, 'boost %.4f' % b['boost'], b['characters'])
if __name__ == '__main__':
    main()
