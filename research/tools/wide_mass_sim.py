#!/usr/bin/env python3
"""Cycle 215: Monte Carlo control of the matched-mass satisfaction mechanism, an intended and unproved claim recorded
in entry-2026-09-18-route-review-literal (the pinned single-wide-row dichotomy, parked there).

Reader: pinned rows A = {0..n/2-1}, wide rows B = the rest of {0..n}; pins (a, y) for every a in A and every label y;
each pin has the full-label incidences [j = z_{a,y,j}] on k wide rows j (a fixed set per pin, random), z uniform.
For a uniform rho' in Phi_0 (Q a uniform flat of dimension L2, R' a uniform (N+1)-set, mu' a uniform bijection of the
other rows onto the labels outside Q) the script computes F = sum over matched wide rows j of |S_j^m n Rem|, where
S_j^m is the union over matched pinned rows a of the cube sets of the pin (a, mu'(a)) on j and Rem the labels outside
Q not taken by pinned rows, and whether some term is satisfied by rho'.  It reports the mean of F against the lower
candidate bound b' Sigma_cap / (4 n^2) (Sigma_cap = sum_{j,x} min(n, m_{j,x})), the smallest F, and the share of
samples with a satisfied term.  Usage: wide_mass_sim.py --L 6 --L2 2 --k 32 --samples 400 --seed 1 --out FILE"""
import argparse, json, random, itertools

def flat(n, L, L2, rng):
    while True:
        vecs = [rng.randrange(1, n) for _ in range(L2)]
        span = {0}
        for v in vecs: span |= {x ^ v for x in span}
        if len(span) == 2 ** L2: break
    tr = rng.randrange(n)
    return sorted(x ^ tr for x in span)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=int, default=6); ap.add_argument('--L2', type=int, default=2)
    ap.add_argument('--k', type=int, default=0, help='wide rows per pin (0: all of B)')
    ap.add_argument('--samples', type=int, default=400); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--out', required=True)
    a = ap.parse_args(); rng = random.Random(a.seed)
    n = 2 ** a.L; N = 2 ** a.L2; rows = list(range(n + 1)); A = rows[:n // 2]; B = rows[n // 2:]
    k = a.k or len(B)
    # cubes: S[(a, y)][j] = {z}; stored as z[(a, y)] = dict j -> label
    z = {}
    for aa in A:
        for y in range(n):
            js = rng.sample(B, k)
            z[(aa, y)] = {j: rng.randrange(n) for j in js}
    # capped mass Sigma_cap = sum_{j, x} min(n, m_{j,x}), m_{j,x} = #{(a, y): y != x, x in S_j^{(a,y)}}
    m = {}
    for (aa, y), d in z.items():
        for j, lab in d.items():
            if lab != y: m[(j, lab)] = m.get((j, lab), 0) + 1
    sigma_cap = sum(min(n, v) for v in m.values())
    mu_max = max(len(d) for d in z.values())
    Fs = []; sat = 0; bounds = []
    for _ in range(a.samples):
        Q = flat(n, a.L, a.L2, rng); Qs = set(Q)
        Rp = set(rng.sample(rows, N + 1))
        others = [r for r in rows if r not in Rp]; labs = [x for x in range(n) if x not in Qs]; rng.shuffle(labs)
        mu = dict(zip(others, labs))
        pinned_labels = {mu[aa] for aa in A if aa not in Rp}
        Rem = set(labs) - pinned_labels
        bprime = sum(1 for j in B if j not in Rp)
        F = 0; satisfied = False
        for j in B:
            if j in Rp: continue
            Sm = set()
            for aa in A:
                if aa in Rp: continue
                d = z[(aa, mu[aa])]
                if j in d: Sm.add(d[j])
            F += len(Sm & Rem)
            if mu[j] in Sm: satisfied = True
        Fs.append(F); sat += satisfied; bounds.append(bprime * sigma_cap / (4 * n * n))
    rec = {'L': a.L, 'n': n, 'N': N, 'k': k, 'pins': len(z), 'mu_max': mu_max, 'sigma_cap': sigma_cap,
           'samples': a.samples, 'seed': a.seed, 'mean_F': sum(Fs) / len(Fs), 'min_F': min(Fs), 'max_F': max(Fs),
           'mean_bound': sum(bounds) / len(bounds), 'satisfied_share': sat / a.samples}
    print(json.dumps(rec))
    with open(a.out, 'a') as f: f.write(json.dumps(rec) + '\n')

if __name__ == '__main__':
    main()
