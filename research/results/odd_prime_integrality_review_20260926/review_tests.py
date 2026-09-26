"""Tests for the integrality route review (odd-prime thread, 26 Sept 2026).

T1 (von zur Gathen-Roche lead): the rational degree of the symmetric function f(x) = [sum_{i<=m} x_i != 0 mod 3]
on {0,1}^m, i.e. the largest k with the k-th finite difference Delta^k f(0) != 0 (the multilinear coefficient of
any k-set). A characteristic-0 encoding of the constraint "L != 0 mod 3" for L = sum of m cells needs this degree.
T2 (rock-paper-scissors bridge): for a random dense form L over F_3 on the (n+1) x n board, the distribution of
L mod 3 over uniformly random placements (each pigeon in a uniform hole, collisions allowed, as in weak PHP)
and over random injections of n pigeons, estimated by Monte Carlo.
Usage: review_tests.py --out FILE"""
import argparse, json
from math import comb
import numpy as np


def mod3_degree(m):
    f = [0 if w % 3 == 0 else 1 for w in range(m + 1)]
    diffs = [sum((-1) ** (k - j) * comb(k, j) * f[j] for j in range(k + 1)) for k in range(m + 1)]
    return max(k for k in range(m + 1) if diffs[k] != 0), diffs


def residues(n, samples, seed):
    rng = np.random.default_rng(seed)
    A = rng.integers(0, 3, size=(n + 1, n)); c0 = int(rng.integers(0, 3))
    placements = rng.integers(0, n, size=(samples, n + 1))
    vals_weak = (A[np.arange(n + 1)[None, :], placements].sum(axis=1) + c0) % 3
    perms = np.argsort(rng.random((samples, n)), axis=1)                    # injections of pigeons 0..n-1
    vals_inj = (A[np.arange(n)[None, :], perms].sum(axis=1) + c0) % 3
    return [float((vals_weak == r).mean()) for r in range(3)], [float((vals_inj == r).mean()) for r in range(3)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    t1 = []
    for m in range(1, 16):
        deg, diffs = mod3_degree(m)
        t1.append(dict(m=m, rational_degree=deg, top_differences=diffs[-3:]))
    t2 = [dict(n=n, seed=s, weak=w, injective=i) for n in (10, 30, 100) for s in (0, 1) for w, i in [residues(n, 200000, s)]]
    json.dump(dict(T1=t1, T2=t2), open(a.out, 'w'), indent=1)
    for r in t1: print(r)
    for r in t2: print(r)


if __name__ == '__main__':
    main()
