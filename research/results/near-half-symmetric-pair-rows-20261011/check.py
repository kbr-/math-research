#!/usr/bin/env python3
"""Largest static barrier of a symmetric function against rows given by pair equations.

Statement tested: over F_2, for f(x) = g(|x|) of odd weight on n variables and a cover by flats each
defined by at most w consistent equations of the forms x_i = c or x_i + x_j = c, if f has degree at
most n - D - 1 on every flat then D <= max(4w - 3, 3w - 1).

A flat is, up to a permutation of the variables, a type: a1 variables fixed to one, a0 fixed to zero,
and free components (p, q), p >= q, p + q >= 2, with p variables equal to y and q equal to 1 + y;
equations used: a1 + a0 + sum(p + q - 1) <= w.  Since f is symmetric it has the same degree on all
flats of a type, and the flats of the types on which that degree is at most e cover the cube exactly
when every weight t has such a type with a point of weight t.  For every g of odd weight and every e
the script decides this by direct evaluation of the restricted function's algebraic normal form (it
does not use the reduction to subcubes of the entry's proof), and reports the largest D = n - e - 1.

Output: one line per (n, w) with the largest D found, the bound, and the number of types.
"""
import argparse
import itertools
import math


def types(n, w):
    out = []
    comps_by_cost = {}
    for cost in range(1, w + 1):
        k = cost + 1
        comps_by_cost[cost] = [(p, k - p) for p in range(k, (k - 1) // 2, -1) if p >= k - p]

    def comp_lists(budget, least):
        yield ()
        for cost in range(least, budget + 1):
            for idx, c in enumerate(comps_by_cost[cost]):
                for rest in comp_lists(budget - cost, cost):
                    yield (c,) + rest

    seen = set()
    for a1 in range(w + 1):
        for a0 in range(w + 1 - a1):
            for comps in comp_lists(w - a1 - a0, 1):
                comps = tuple(sorted(comps))
                used = a1 + a0 + sum(p + q for p, q in comps)
                if used > n or (a1, a0, comps) in seen:
                    continue
                seen.add((a1, a0, comps))
                out.append((a1, a0, comps))
    return out


def newton_degree(vals):
    """Degree of the symmetric function i -> vals[i] on len(vals) - 1 variables; -1 if zero."""
    d = -1
    cur = list(vals)
    for u in range(len(vals)):
        if cur[0]:
            d = u
        cur = [cur[i] ^ cur[i + 1] for i in range(len(cur) - 1)]
    return d


def restricted_degree(g, n, typ):
    a1, a0, comps = typ
    s = a1 + sum(q for _, q in comps)
    m = n - a1 - a0 - sum(p + q for p, q in comps)
    ds = [p - q for p, q in comps]
    k = len(comps)
    best = -1
    for T in range(1 << k):
        phi = [0] * (m + 1)
        sub = T
        while True:
            shift = s + sum(ds[c] for c in range(k) if sub >> c & 1)
            for i in range(m + 1):
                phi[i] ^= g[shift + i]
            if sub == 0:
                break
            sub = (sub - 1) & T
        d = newton_degree(phi)
        if d >= 0:
            best = max(best, d + bin(T).count("1"))
    return best


def covered_weights(n, typ):
    a1, a0, comps = typ
    k = len(comps)
    ws = set()
    for T in range(1 << k):
        ones = a1 + sum(p if T >> c & 1 else q for c, (p, q) in enumerate(comps))
        zeros = a0 + sum(q if T >> c & 1 else p for c, (p, q) in enumerate(comps))
        for t in range(ones, n - zeros + 1):
            ws.add(t)
    return ws


def largest_barrier(n, w):
    tl = types(n, w)
    cov = [covered_weights(n, t) for t in tl]
    binom_odd = [math.comb(n, t) & 1 for t in range(n + 1)]
    best = -1
    for bits in range(1, 1 << (n + 1)):
        g = [bits >> t & 1 for t in range(n + 1)]
        if sum(g[t] & binom_odd[t] for t in range(n + 1)) % 2 == 0:
            continue
        degs = [restricted_degree(g, n, t) for t in tl]
        for e in sorted(set(degs)):
            if n - e - 1 <= best:
                break
            got = set()
            for d, c in zip(degs, cov):
                if d <= e:
                    got |= c
            if len(got) == n + 1:
                best = max(best, n - e - 1)
                break
    return best, len(tl)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases", default="4:1,5:1,6:1,8:1,7:2,8:2,9:2,10:2,11:3,12:3")
    args = ap.parse_args()
    with open(args.out, "w") as fh:
        fh.write("n w largest_D bound types\n")
        for case in args.cases.split(","):
            n, w = map(int, case.split(":"))
            best, nt = largest_barrier(n, w)
            bound = max(4 * w - 3, 3 * w - 1)
            assert best <= bound, (n, w, best, bound)
            fh.write(f"{n} {w} {best} {bound} {nt}\n")
            fh.flush()
    print("done")


if __name__ == "__main__":
    main()
