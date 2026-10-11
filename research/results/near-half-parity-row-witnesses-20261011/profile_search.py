#!/usr/bin/env python3
"""Largest symmetric static barrier against rows that are flats of codimension at most two, by weight profiles.

Statement tested.  Over F_2, f(x) = g(|x|) symmetric on F_2^n.  For a flat V of codimension w_V and a set T of
variables, the profile of (V, T) is the vector (number of points of V with x_T = 1 and weight k, mod 2), k = 0..n.
Criterion: f is a static barrier at D for a family of flats (odd weight, degree at most n - D - 1 on each flat)
exactly when g has odd inner product with the binomial vector (C(n, k) mod 2) and is orthogonal to the profile
of (V, T) for every flat V of the family and every |T| <= D - w_V.  A flat of codimension at most two is, up to
permutation, given by the sizes (p, q, r) of the sets of variables in the first form only, the second only and
both, with constants (c1, c2); or by one form on s variables with constant c.

Profile formula under test (lemma of the entry): the profile is
  z^|T| (1+z)^(a0 - t0) * sum over atom parities eps in Sol of prod_i Par(a_i - t_i, eps_i + t_i),
where Par(b, e) is the mod-2 enumerator of the vectors of parity e in F_2^b.

Quantities printed, for each n: the largest D for which some symmetric g is a static barrier against a set of
row types covering all weights, (a) for all flats of codimension at most two, (b) for flats whose forms have
at most two variables each (pair flats and subcubes), (c) for subcubes only.

Expected before the run.
- Control 1: at n = 8 the profile formula agrees with a direct enumeration of the flat's points for every type
  and every T-vector of total at most 2 that is checked (all of them); a disagreement means the formula or its
  implementation is wrong.
- Control 2, an independent method on record: (c) is 1 at every n here (prop:symmetric-barrier-bound, w = 2:
  largest D is 2w - 3 = 1), and (b) is 2 at n = 8 and 10 (the recorded enumeration for pair rows, w = 2,
  n = 7..10).  A different value means this script's criterion or search is wrong.
- The question: (a).  Hypothesis: (a) does not grow with n over n = 8, 10, 12, 14 (a ceiling depending on the
  width only).  Alternative: (a) increases with n.  I do not predict its value; (a) >= (b) >= (c) must hold.
  A growth slower than these four sizes can show would not be detected.
"""
import argparse
import itertools

import numpy as np


def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def binpar(m):
    """(1+z)^m mod 2 as a bit mask."""
    return sum(1 << i for i in range(m + 1) if (i & m) == i)


def par(b, e):
    """Mod-2 enumerator of the vectors of parity e in F_2^b; zero polynomial if b < 0."""
    if b < 0:
        return 0
    return sum(1 << i for i in range(e & 1, b + 1, 2) if (i & b) == i)


def weights_of(b, e):
    """Exact set of weights of vectors of parity e in F_2^b, as a bit mask."""
    return sum(1 << i for i in range(e & 1, b + 1, 2))


def sumset(a, b):
    r = 0
    i = 0
    while b >> i:
        if b >> i & 1:
            r |= a << i
        i += 1
    return r


class RowType:
    def __init__(self, n, atoms, sols, w, label):
        self.n, self.atoms, self.sols, self.w, self.label = n, atoms, sols, w, label
        self.a0 = n - sum(atoms)
        cover = 0
        for eps in sols:
            s = (1 << (self.a0 + 1)) - 1
            for a, e in zip(atoms, eps):
                s = sumset(s, weights_of(a, e))
            cover |= s
        self.cover = cover

    def profile(self, t0, ts):
        if t0 > self.a0 or any(t > a for t, a in zip(ts, self.atoms)):
            return 0
        tot = 0
        for eps in self.sols:
            term = 1
            for a, e, t in zip(self.atoms, eps, ts):
                term = clmul(term, par(a - t, e + t))
            tot ^= term
        return clmul(tot, binpar(self.a0 - t0)) << (t0 + sum(ts))

    def profiles_at(self, total):
        """Profiles of all T-vectors with |T| = total."""
        out = set()
        for ts in itertools.product(range(total + 1), repeat=len(self.atoms)):
            t0 = total - sum(ts)
            if t0 >= 0:
                out.add(self.profile(t0, ts))
        out.discard(0)
        return out


def row_types(n):
    types = []
    for s in range(1, n + 1):
        for c in (0, 1):
            types.append(RowType(n, (s,), [(c,)], 1, f"one form on {s}, c={c}"))
    for p, q, r in itertools.product(range(n + 1), repeat=3):
        if p + q + r > n or p + r == 0 or q + r == 0 or p + q == 0:
            continue
        for c1, c2 in itertools.product((0, 1), repeat=2):
            sols = [(c1 ^ e, c2 ^ e, e) for e in (0, 1)]
            types.append(RowType(n, (p, q, r), sols, 2, f"forms on ({p},{q},{r}), c=({c1},{c2})"))
    return types


def is_pair(t):
    if t.w == 1:
        return t.atoms[0] <= 2
    p, q, r = t.atoms
    return p + r <= 2 and q + r <= 2


def is_subcube(t):
    if t.w == 1:
        return t.atoms[0] == 1
    return t.atoms == (1, 1, 0)


def brute_profile(n, t, t0, ts):
    """Direct enumeration: variables ordered atom by atom, free ones last; T takes the first t_i of each atom."""
    x = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    pos = 0
    parities = []
    for a, tt in zip(t.atoms + (t.a0,), tuple(ts) + (t0,)):
        mask = ((1 << a) - 1) << pos
        tmask = ((1 << tt) - 1) << pos
        ok &= (x & tmask) == tmask
        parities.append(np.bitwise_count(x & mask) & 1)
        pos += a
    insol = np.zeros(1 << n, dtype=bool)
    for eps in t.sols:
        m = np.ones(1 << n, dtype=bool)
        for pv, e in zip(parities, eps):
            m &= pv == e
        insol |= m
    ok &= insol
    counts = np.bincount(np.bitwise_count(x[ok]), minlength=n + 1) & 1
    return sum(int(c) << k for k, c in enumerate(counts))


def control_formula(n, types):
    checked = 0
    for t in types:
        for ts in itertools.product(range(3), repeat=len(t.atoms)):
            for t0 in range(3 - sum(ts)):
                if t0 <= t.a0 and all(a >= b for a, b in zip(t.atoms, ts)):
                    assert t.profile(t0, ts) == brute_profile(n, t, t0, ts), (t.label, t0, ts)
                    checked += 1
    return checked


def largest_barrier(n, types):
    """Largest D with a symmetric barrier against a covering subset of the types; a witness g and its types."""
    G = np.arange(1 << (n + 1), dtype=np.int64)
    parity = (np.bitwise_count(G) & 1).astype(bool)
    odd = parity[G & binpar(n)]
    full = (1 << (n + 1)) - 1
    bad = [np.zeros(1 << (n + 1), dtype=bool) for _ in types]
    best = (-1, None, None)
    for D in range(n + 1):
        cov = np.zeros(1 << (n + 1), dtype=np.int64)
        for t, b in zip(types, bad):
            if D - t.w >= 0:
                for v in t.profiles_at(D - t.w):
                    b |= parity[G & v]
            cov |= np.where(b, 0, t.cover)
        hit = np.flatnonzero(odd & (cov == full))
        if hit.size == 0:
            break
        g = int(hit[0])
        best = (D, g, [t.label for t, b in zip(types, bad) if not b[g]])
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sizes", default="8,10,12,14")
    args = ap.parse_args()
    with open(args.out, "w") as fh:
        for n in [int(s) for s in args.sizes.split(",")]:
            types = row_types(n)
            if n == 8:
                fh.write(f"control 1: formula equals enumeration on {control_formula(n, types)} profiles at n=8\n")
            for name, sel in (("all flats of codimension <= 2", types),
                              ("pair flats and subcubes", [t for t in types if is_pair(t)]),
                              ("subcubes", [t for t in types if is_subcube(t)])):
                D, g, good = largest_barrier(n, sel)
                gs = "".join(str(g >> k & 1) for k in range(n + 1)) if g is not None else "-"
                fh.write(f"n={n} rows={name} types={len(sel)} largest_D={D} g={gs} good_types={len(good or [])}\n")
                if good and len(good) <= 12:
                    fh.write("   " + "; ".join(good) + "\n")
                fh.flush()
    print("done")


if __name__ == "__main__":
    main()
