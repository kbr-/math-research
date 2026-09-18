#!/usr/bin/env python3
"""Cycle 216 checks for entry-2026-09-18-dense-forms (dense forms on the compact family).

(1) invariance: for every flat Q of dimension L2 in F_2^L, every (N+1)-set R' of the n+1 rows and a sampled bijection
    mu', the F_2-linear map sending a form L = sum_j <a_j, x_j> + c (coefficients (a_j)_j, c) to its restriction on
    V = Q^{R'} (linear parts B^T a_j for j in R', constant c + sum_{j in R'} <a_j, q0> + sum_{j not in R'} <a_j, mu'(j)>)
    is onto F_2^{v+1}, v = (N+1) L2; hence a uniform form restricts to a uniform affine form on V, for every rho'.
(2) span: sample a rank-w terms t = prod_k (1 + L_k) with uniform affine forms on F_2^v, and test whether 1 lies in
    their F_2-span inside the polynomials of degree <= w (multilinear), and whether they span that whole space;
    reports the success share against the bound a >= 2^w (D_w ln 2 + ln(1/eta)).
(3) coverage: for the same random readers, the uncovered share of V against (1 - 2^-w)^a.
Usage: dense_forms_check.py --out FILE"""
import argparse, itertools, json, math, random

def rank_f2(rows):
    rows = [r for r in rows if r]; rank = 0; basis = {}
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in basis: r ^= basis[h]
            else: basis[h] = r; rank += 1; break
    return rank, basis

def in_span(basis, r):
    while r:
        h = r.bit_length() - 1
        if h not in basis: return False
        r ^= basis[h]
    return True

def flats(L, L2):
    n = 2 ** L; seen = set()
    for vecs in itertools.combinations(range(1, n), L2):
        span = {0}
        for v in vecs: span |= {x ^ v for x in span}
        if len(span) != 2 ** L2: continue
        key = frozenset(span)
        if key in seen: continue
        seen.add(key)
        # a basis of the direction space
        rk, basis = rank_f2(list(span)); B = list(basis.values())
        for q0 in range(n):
            coset = frozenset(x ^ q0 for x in span)
            if min(coset) == q0: yield q0, B, coset

def invariance(L, L2, rng):
    n = 2 ** L; N = 2 ** L2; rows = range(n + 1); v = (N + 1) * L2; checked = 0; bad = 0
    dot = lambda a, x: bin(a & x).count('1') & 1
    for q0, B, Q in flats(L, L2):
        outside = [x for x in range(n) if x not in Q]
        for Rp in itertools.combinations(rows, N + 1):
            others = [j for j in rows if j not in Rp]; labs = outside[:]; rng.shuffle(labs); mu = dict(zip(others, labs))
            # images of the basis coefficient vectors: e_{j,bit} and the constant c
            images = []
            for j in rows:
                for bit in range(L):
                    a = 1 << bit
                    if j in Rp:
                        pos = Rp.index(j); lin = 0
                        for k, b in enumerate(B): lin |= dot(a, b) << (pos * L2 + k)
                        images.append((lin << 1) | dot(a, q0))
                    else:
                        images.append(dot(a, mu[j]))
            images.append(1)
            rk, _ = rank_f2(images); checked += 1; bad += (rk != v + 1)
    return {'check': 'invariance', 'L': L, 'L2': L2, 'v': v, 'restrictions': checked, 'not_onto': bad}

def monomials(v, w):
    idx = {}; 
    for k in range(w + 1):
        for S in itertools.combinations(range(v), k): idx[S] = len(idx)
    return idx

def product_poly(forms, v):
    # forms: list of (linear mask, const); returns multilinear polynomial of prod (1 + L) as a set of monomials (frozensets)
    poly = {frozenset()}
    for lin, c in forms:
        factor = [frozenset([i]) for i in range(v) if lin >> i & 1]
        if (c ^ 1): factor.append(frozenset())
        new = set()
        for m in poly:
            for f in factor: new ^= {m | f}
        poly = new
    return poly

def span_and_coverage(v, w, a, trials, rng):
    idx = monomials(v, w); D = len(idx); one = 1 << idx[()]
    ok_one = ok_all = 0; unc = 0.0
    for _ in range(trials):
        rowsb = []; terms = []
        for _ in range(a):
            forms = [(rng.getrandbits(v), rng.getrandbits(1)) for _ in range(w)]; terms.append(forms)
            poly = product_poly(forms, v); r = 0
            for m in poly: r |= 1 << idx[tuple(sorted(m))]
            rowsb.append(r)
        rk, basis = rank_f2(rowsb); ok_all += (rk == D); ok_one += in_span(basis, one)
        uncovered = 0
        for u in range(2 ** v):
            if not any(all((bin(lin & u).count('1') + c) % 2 == 0 for lin, c in forms) for forms in terms): uncovered += 1
        unc += uncovered / 2 ** v
    return {'check': 'span', 'v': v, 'w': w, 'a': a, 'D_w': D, 'trials': trials, 'one_in_span': ok_one / trials,
            'spans_all': ok_all / trials, 'mean_uncovered': unc / trials, 'predicted_uncovered': (1 - 2 ** -w) ** a,
            'bound_a_eta_0.01': math.ceil(2 ** w * (D * math.log(2) + math.log(100)))}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args(); rng = random.Random(a.seed); recs = []
    recs.append(invariance(3, 1, rng)); recs.append(invariance(3, 2, rng))
    for v, w, terms in [(8, 2, 20), (8, 2, 60), (8, 2, 120), (8, 2, 200), (10, 2, 250), (10, 3, 60), (10, 3, 400), (10, 3, 1400),
                        (10, 3, 8), (10, 4, 16)]:
        recs.append(span_and_coverage(v, w, terms, 40, rng))
    with open(a.out, 'a') as f:
        for r in recs: print(json.dumps(r)); f.write(json.dumps(r) + '\n')

if __name__ == '__main__':
    main()
