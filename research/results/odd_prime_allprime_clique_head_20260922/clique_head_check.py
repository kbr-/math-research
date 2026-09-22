"""Exact checks of the three countable claims of the all-prime clique-head entry (Theorem CHp).

(1) Lemma CH_delta.  A family containing every delta-subset of an m-set M leaves free exactly the
    sets of size at most k meeting M in at most delta-1 points, so
        J_{<=k} = sum_{j<=k} sum_{i<delta} C(m,i) C(s-m, j-i).
    The lemma claims J_{<=k} <= 2 C_delta C(s,k) exp(-mk/(2s)) with
        C_delta = (4(delta-1))^(delta-1) e^(1/4-(delta-1)),
    under 2 <= delta <= m and k, m <= s/4.  Every admissible (s, m, k, delta) in the tested range is
    checked against the closed form, and the closed form is confirmed against brute-force
    enumeration of all subsets for the smallest boards.

(2) The vanishing bound eps_p = 1 - (1 - 1/p)^delta.  For a nonzero homogeneous multilinear form
    B(a) = sum_S B_S prod_{u in S} a_u of degree delta in m variables over F_p, the entry's union
    bound needs Pr_a[B(a) = 0] <= eps_p for a uniform a in F_p^m.  Small cases are enumerated over
    all nonzero B and all points; larger ones sample B with deterministic seeds.  A single monomial
    attains the bound, so the test is tight and a wrong exponent would show.

(3) The Wilson coefficient step.  After multilinear (Boolean) reduction, the coefficient of
    prod_{u in S} x_u in 1 - L^delta, for |S| = delta and L = sum_u a_u x_u over F_p, must equal
    prod_{u in S} a_u.  Coefficients are recovered by Moebius inversion of the Boolean values.
    The projection step is checked too: substituting x_d = 1 - sum_{w != d} x_w for a distinguished
    cell d of a row must replace a_w by a_w - a_d on the other cells of that row.
"""
import itertools, json, random, sys
from math import comb, exp

import numpy as np


def c_delta(d):
    return (4 * (d - 1)) ** (d - 1) * exp(0.25 - (d - 1))


def j_le_k(s, m, k, d):
    return sum(comb(m, i) * comb(s - m, j - i) for j in range(k + 1) for i in range(min(d, j + 1)))


def j_brute(s, m, k, d):
    M = set(range(m))
    n = 0
    for j in range(k + 1):
        for A in itertools.combinations(range(s), j):
            if len(M.intersection(A)) < d:
                n += 1
    return n


def check_lemma():
    rows, ok, worst = [], True, 0.0
    for s in range(8, 41, 4):
        for m in range(2, s // 4 + 1):
            for k in range(1, s // 4 + 1):
                for d in range(2, min(m, 6) + 1):
                    J = j_le_k(s, m, k, d)
                    bound = 2 * c_delta(d) * comb(s, k) * exp(-m * k / (2 * s))
                    ratio = J / bound
                    worst = max(worst, ratio)
                    ok &= ratio <= 1.0
                    rows.append({"s": s, "m": m, "k": k, "delta": d, "J": J, "ratio": ratio})
    brute = all(j_le_k(s, m, k, d) == j_brute(s, m, k, d)
                for s in (8, 12) for m in (2, 3) for k in (1, 2, 3) for d in (2, 3) if d <= m and k <= s // 4)
    return {"cases": len(rows), "all_within_bound": ok, "max_ratio": worst, "closed_form_matches_brute": brute,
            "tightest": max(rows, key=lambda r: r["ratio"])}


def monomial_matrix(p, m, d):
    """Rows: all points of F_p^m.  Columns: the values of prod_{u in S} a_u for the d-subsets S."""
    subsets = list(itertools.combinations(range(m), d))
    pts = np.array(list(itertools.product(range(p), repeat=m)), dtype=np.int64)
    cols = [np.prod(pts[:, list(S)], axis=1) % p for S in subsets]
    return subsets, np.stack(cols, axis=1)


def max_zero_fraction(p, mat, forms, chunk=256):
    """Largest fraction of points at which one of the given nonzero forms vanishes."""
    best, arg, npts = 0.0, None, mat.shape[0]
    for i in range(0, forms.shape[1], chunk):
        blk = forms[:, i:i + chunk]
        zeros = ((mat @ blk) % p == 0).sum(axis=0)
        j = int(np.argmax(zeros))
        if float(zeros[j]) / npts > best:
            best, arg = float(zeros[j]) / npts, blk[:, j].tolist()
    return best, arg


def check_eps():
    out, ok = [], True
    cases = [(3, 4, 2, None), (3, 5, 2, None), (5, 4, 3, None), (5, 5, 4, None), (7, 4, 3, None),
             (3, 6, 3, 4000), (5, 6, 4, 500), (7, 5, 4, 500), (5, 6, 2, 500), (7, 6, 5, 100)]
    for p, m, d, samples in cases:
        subsets, mat = monomial_matrix(p, m, d)
        eps = 1 - (1 - 1 / p) ** d
        if samples is None:
            forms = np.array(list(itertools.product(range(p), repeat=len(subsets))), dtype=np.int64).T
            forms = forms[:, forms.any(axis=0)]
        else:
            rng = np.random.default_rng(20260922 + 100 * p + 10 * m + d)
            forms = rng.integers(0, p, size=(len(subsets), samples), dtype=np.int64)
            forms = forms[:, forms.any(axis=0)]
            single = np.zeros((len(subsets), 1), dtype=np.int64)
            single[0, 0] = 1
            forms = np.concatenate([forms, single], axis=1)
        best, arg = max_zero_fraction(p, mat, forms)
        ok = ok and bool(best <= eps + 1e-12)
        out.append({"p": p, "m": m, "delta": d, "exhaustive": samples is None, "forms": int(forms.shape[1]),
                    "eps_p": eps, "max_zero_fraction": best, "attained": bool(abs(best - eps) < 1e-12),
                    "argmax": arg})
    return {"all_within_bound": ok, "cases": out}


def multilinear_coeffs(values, v):
    """Moebius inversion: coefficient of prod_{u in S} x_u from values on the Boolean cube."""
    c = {}
    for S in itertools.chain.from_iterable(itertools.combinations(range(v), j) for j in range(v + 1)):
        c[S] = sum((-1) ** (len(S) - len(T)) * values[T] for T in
                   itertools.chain.from_iterable(itertools.combinations(S, j) for j in range(len(S) + 1)))
    return c


def check_wilson():
    out, ok = [], True
    for p in (3, 5, 7):
        d, v = p - 1, p - 1
        rng = random.Random(20260922 + p)
        for t in range(3):
            a = [rng.randrange(1, p) for _ in range(v)]
            vals = {}
            for x in itertools.product((0, 1), repeat=v):
                S = tuple(i for i in range(v) if x[i])
                L = sum(a[i] for i in S) % p
                vals[S] = (1 - pow(L, d, p)) % p
            c = multilinear_coeffs(vals, v)
            S = tuple(range(v))
            want = 1
            for u in S:
                want = want * a[u] % p
            got = c[S] % p
            ok &= got == want
            out.append({"p": p, "trial": t, "a": a, "coeff": got, "prod_a": want, "match": got == want})
    return {"all_match": ok, "trials": out}


def check_projection():
    """x_d -> 1 - sum_{w != d} x_w turns sum_w a_w x_w + a_d x_d into const + sum_w (a_w - a_d) x_w."""
    ok = True
    rng = random.Random(20260922)
    for p in (3, 5, 7):
        for _ in range(5):
            w = 6
            a = [rng.randrange(p) for _ in range(w)]
            ad = rng.randrange(p)
            proj = [(x - ad) % p for x in a]
            for x in itertools.product(range(2), repeat=w):
                xd = (1 - sum(x)) % p
                lhs = (sum(ai * xi for ai, xi in zip(a, x)) + ad * xd) % p
                rhs = (ad + sum(ai * xi for ai, xi in zip(proj, x))) % p
                ok &= lhs == rhs
    return {"all_match": ok}


if __name__ == "__main__":
    res = {"lemma_CH_delta": check_lemma(), "eps_p": check_eps(), "wilson": check_wilson(),
           "projection": check_projection()}
    allok = (res["lemma_CH_delta"]["all_within_bound"] and res["lemma_CH_delta"]["closed_form_matches_brute"]
             and res["eps_p"]["all_within_bound"] and res["wilson"]["all_match"] and res["projection"]["all_match"])
    res["all_ok"] = allok
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    print("lemma cases", res["lemma_CH_delta"]["cases"], "max J/bound", round(res["lemma_CH_delta"]["max_ratio"], 4))
    print("eps cases", len(res["eps_p"]["cases"]), "within bound", res["eps_p"]["all_within_bound"],
          "attained", sum(c["attained"] for c in res["eps_p"]["cases"]))
    print("wilson", res["wilson"]["all_match"], "projection", res["projection"]["all_match"])
    print("all_ok", allok)
