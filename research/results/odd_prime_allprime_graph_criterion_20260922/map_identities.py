"""Exact check of the p-dependent identities in the all-prime graph criterion (Theorem GCp).

Multilinear polynomials over F_p in v Boolean variables (dict frozenset -> coeff).  For p = 3, 5, 7
and random small instances (deterministic seeds) it checks, as polynomials after Boolean reduction
and pointwise on all 2^v Boolean points:
  dense map:   f = sum_i c_i g_i + E,  beta_i = f^(p-2) c_i
               P = 1 - sum_i beta_i g_i  equals  1 - f^(p-1) + f^(p-2) E
               f g_i P  equals  g_i (f - f^p) + f^(p-1) g_i E,  and g_i (f - f^p) vanishes on the cube
  fields:      f (beta^p - beta) vanishes on the cube
  small core:  A = prod_j (1 - F_j^(p-1)) = 1 - sum_j F_j * [F_j^(p-2) prod_{i<j}(1 - F_i^(p-1))],
               F_j A vanishes on the cube
  prefix:      beta_j = A G_j^(p-2) prod_{i<j} (1 - G_i^(p-1)),
               A - sum_j beta_j G_j = A prod_j (1 - G_j^(p-1)),
               and G_j, F_j times A prod (1 - G^(p-1)) vanish on the cube
  high core:   f = sum_j c_j F_j (Boolean multiple B = 0 here), A = 1 - f^(p-2) sum_j c_j F_j
               equals 1 - f^(p-1), and f F_j A vanishes on the cube
Selectors are g = 1 - L^(p-1) with random affine L; E, c_i are random multilinear polynomials.
Scope: all arithmetic is Boolean-reduced (multilinear), where f^p == f and beta^p == beta, so the
vanishing checks for g (f - f^p) and for the fields hold automatically; the identities are checked
modulo Booleanity only, the high core uses B = 0, and no degree bound is checked.
"""
import itertools, json, random, sys


def mul(P, Q, p):
    R = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = m1 | m2
            R[m] = (R.get(m, 0) + c1 * c2) % p
    return {m: c for m, c in R.items() if c}


def add(P, Q, p, s=1):
    R = dict(P)
    for m, c in Q.items():
        R[m] = (R.get(m, 0) + s * c) % p
    return {m: c for m, c in R.items() if c}


def pw(P, e, p):
    R = {frozenset(): 1}
    for _ in range(e):
        R = mul(R, P, p)
    return R


def rnd(v, deg, p, rng, terms=4):
    P = {}
    for _ in range(terms):
        d = rng.randint(0, deg)
        m = frozenset(rng.sample(range(v), d))
        P[m] = (P.get(m, 0) + rng.randrange(1, p)) % p
    return {m: c for m, c in P.items() if c}


def ev(P, x, p):
    return sum(c for m, c in P.items() if all(x[i] for i in m)) % p


def vanishes(P, v, p):
    return all(ev(P, x, p) == 0 for x in itertools.product((0, 1), repeat=v))


ONE = {frozenset(): 1}


def sel(v, p, rng):
    return add(ONE, pw(rnd(v, 1, p, rng, 3), p - 1, p), p, -1)


def run(p, v, seed):
    rng = random.Random(seed)
    ok = {}
    g = [sel(v, p, rng) for _ in range(3)]
    c = [rnd(v, 2, p, rng) for _ in range(3)]
    E = rnd(v, 3, p, rng)
    f = dict(E)
    for ci, gi in zip(c, g):
        f = add(f, mul(ci, gi, p), p)
    fp2 = pw(f, p - 2, p)
    fp1 = mul(fp2, f, p)
    fp = mul(fp1, f, p)
    beta = [mul(fp2, ci, p) for ci in c]
    P = dict(ONE)
    for bi, gi in zip(beta, g):
        P = add(P, mul(bi, gi, p), p, -1)
    ok["dense_product"] = P == add(add(ONE, fp1, p, -1), mul(fp2, E, p), p)
    good = True
    for gi in g:
        lhs = mul(mul(f, gi, p), P, p)
        first = mul(gi, add(f, fp, p, -1), p)
        good &= lhs == add(first, mul(mul(fp1, gi, p), E, p), p)
        good &= vanishes(first, v, p)
    ok["dense_companions"] = good
    ok["dense_fields"] = all(vanishes(mul(f, add(pw(b, p, p), b, p, -1), p), v, p) for b in beta)
    Fs = [rnd(v, 1, p, rng, 3) for _ in range(2)]
    A = dict(ONE)
    for F in Fs:
        A = mul(A, add(ONE, pw(F, p - 1, p), p, -1), p)
    tele, pref = dict(ONE), dict(ONE)
    for F in Fs:
        tele = add(tele, mul(F, mul(pw(F, p - 2, p), pref, p), p), p, -1)
        pref = mul(pref, add(ONE, pw(F, p - 1, p), p, -1), p)
    ok["small_core_telescoping"] = tele == A
    ok["small_core_companions"] = all(vanishes(mul(F, A, p), v, p) for F in Fs)
    Gs = [sel(v, p, rng) for _ in range(3)]
    pre, total = dict(ONE), dict(A)
    for G in Gs:
        bj = mul(mul(A, pw(G, p - 2, p), p), pre, p)
        total = add(total, mul(bj, G, p), p, -1)
        pre = mul(pre, add(ONE, pw(G, p - 1, p), p, -1), p)
    prod = mul(A, pre, p)
    ok["prefix_telescoping"] = total == prod
    ok["prefix_companions"] = all(vanishes(mul(X, prod, p), v, p) for X in Gs + Fs)
    cs = [rnd(v, 2, p, rng) for _ in Fs]
    fh = {}
    for cj, F in zip(cs, Fs):
        fh = add(fh, mul(cj, F, p), p)
    Ah = add(ONE, mul(pw(fh, p - 2, p), fh, p), p, -1)
    ok["high_core_product"] = Ah == add(ONE, pw(fh, p - 1, p), p, -1)
    ok["high_core_companions"] = all(vanishes(mul(mul(fh, F, p), Ah, p), v, p) for F in Fs)
    ok["nontrivial"] = bool(f) and bool(fh) and any(len(m) >= 2 for m in f)
    return ok


if __name__ == "__main__":
    out, allok = [], True
    for p in (3, 5, 7):
        for t in range(4):
            r = run(p, 6, 20260922 + 10 * p + t)
            out.append({"p": p, "trial": t, **r})
            allok &= all(r.values())
    json.dump({"all_ok": allok, "trials": out}, open(sys.argv[1], "w"), indent=1)
    print("trials", len(out), "all_ok", allok)
    bad = [(r["p"], r["trial"], k) for r in out for k, val in r.items() if val is False]
    print("failures", bad)
