#!/usr/bin/env python3
"""Brute-force check of Lemmas R1 and R2 of cycle 229 over F_2.

For the alternating form of rank 2 rho on F_2^n (standard symplectic form on the first 2 rho coordinates)
the script enumerates all d-dimensional subspaces by reduced echelon bases, counts those on which the
form vanishes, and compares the exact probability with
  R1: 2.39 * 2^(rho(rho+1)/2 - rho d)            (all rho)
  R2: 6 * 2^((log2 d)^2/6 - C(d,2))              (rho >= d, d <= n-1).
Usage: isotropy_bounds_check.py [--nmax 8] [--out FILE]"""
import argparse, itertools, json, math

def subspaces(n, d):
    """all d-subspaces of F_2^n as lists of basis vectors (reduced row echelon form)"""
    for pivots in itertools.combinations(range(n), d):
        free = [[c for c in range(p + 1, n) if c not in pivots] for p in pivots]
        for choice in itertools.product(*[range(1 << len(f)) for f in free]):
            basis = []
            for p, f, ch in zip(pivots, free, choice):
                v = 1 << p
                for k, c in enumerate(f):
                    if (ch >> k) & 1: v |= 1 << c
                basis.append(v)
            yield basis

def form(rho):
    def kappa(u, w):
        s = 0
        for k in range(rho):
            a, b = 2 * k, 2 * k + 1
            s ^= ((u >> a) & (w >> b) & 1) ^ ((u >> b) & (w >> a) & 1)
        return s
    return kappa

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--nmax', type=int, default=8); ap.add_argument('--out'); a = ap.parse_args()
    import sys
    out = open(a.out, 'w') if a.out else sys.stdout
    worst1 = worst2 = 0.0
    for n in range(4, a.nmax + 1):
        for d in range(2, min(4, n - 1) + 1):
            subs = list(subspaces(n, d))
            for rho in range(1, n // 2 + 1):
                k = form(rho)
                iso = sum(1 for B in subs if all(k(B[i], B[j]) == 0 for i in range(d) for j in range(i + 1, d)))
                p = iso / len(subs)
                r1 = 2.39 * 2 ** (rho * (rho + 1) / 2 - rho * d)
                line = dict(n=n, d=d, rho=rho, subspaces=len(subs), isotropic=iso, prob=p, R1=r1, R1_ok=p <= r1)
                worst1 = max(worst1, p / r1)
                if rho >= d:
                    r2 = 6 * 2 ** (math.log2(d) ** 2 / 6 - d * (d - 1) / 2)
                    line.update(R2=r2, R2_ok=p <= r2); worst2 = max(worst2, p / r2)
                print(json.dumps(line), file=out)
    print(json.dumps(dict(worst_ratio_R1=worst1, worst_ratio_R2=worst2)), file=out)

if __name__ == '__main__':
    main()
