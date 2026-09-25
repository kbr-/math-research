#!/usr/bin/env python3
"""Local cell-resolvent test for one-column pairs whose restrictions differ in several factors.

Statement tested (local form). Let C = prod_j h_j(x_j) and C' = prod_j h_j(x_j + beta_j) on
t independent coordinates x_1..x_t over F_3, with h_j(x) = x (linear factor) or chi_0(x) = 1 - x^2,
and every beta_j != 0. Put d = deg C - 1 (the degree budget of v(C_v - C'_v) in the proposition
prop:one-column-pair-lifting, after removing the common cell v and the unshifted factors Q).
Question: does w = C - C' lie in the span of m * P, where P is a product of factors (M - a) and
chi_a(M) on affine forms M in x_1..x_t, P vanishes on Z = {C = 0 = C'}, and deg m + deg P <= d?
Such P are "cell resolvents": product constraints implied by the pair, of degree below the pair.

Functions on F_3^t are identified with reduced polynomials; all ranks are exact over F_3.
Sizes: t <= 4 gives 3^t <= 81 points and at most 120 affine hyperplanes, so the enumeration of
products of at most d factors is small (seconds).
"""
import itertools, json, sys
import numpy as np

P = 3


def points(t):
    return np.array(list(itertools.product(range(P), repeat=t)), dtype=np.int64)


def rank_mod3(rows):
    """Exact rank over F_3 of an integer matrix (rows), by elimination with numpy row ops."""
    A = np.array(rows, dtype=np.int64) % P
    if A.size == 0:
        return 0, A
    r = 0
    nrows, ncols = A.shape
    for c in range(ncols):
        piv = np.nonzero(A[r:, c])[0]
        if piv.size == 0:
            continue
        p = r + piv[0]
        A[[r, p]] = A[[p, r]]
        inv = 1 if A[r, c] == 1 else 2
        A[r] = (A[r] * inv) % P
        nz = np.nonzero(A[:, c])[0]
        nz = nz[nz != r]
        A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % P
        r += 1
        if r == nrows:
            break
    return r, A[:r]


def in_span(basis_rows, v):
    r0, _ = rank_mod3(basis_rows)
    r1, _ = rank_mod3(list(basis_rows) + [v])
    return r1 == r0


def run(spec):
    """spec: list of 'lin' or 'chi' factors, all shifted by beta_j (default 1)."""
    t = len(spec)
    X = points(t)
    betas = [1] * t

    def h(kind, vals):
        return vals % P if kind == 'lin' else (1 - vals * vals) % P

    C = np.ones(len(X), dtype=np.int64)
    Cp = np.ones(len(X), dtype=np.int64)
    for j, kind in enumerate(spec):
        C = C * h(kind, X[:, j]) % P
        Cp = Cp * h(kind, X[:, j] + betas[j]) % P
    w = (C - Cp) % P
    Z = (C == 0) & (Cp == 0)
    degC = sum(1 if k == 'lin' else 2 for k in spec)
    d = degC - 1
    # affine forms up to scalar: linear parts with first nonzero coordinate 1, constants 0..2
    lin = [c for c in itertools.product(range(P), repeat=t) if any(c) and c[next(i for i in range(t) if c[i])] == 1]
    forms = []  # values of M - a at all points (vanishing set {M = a}), and chi_a(M)
    for c in lin:
        M = X @ np.array(c) % P
        for a in range(P):
            forms.append(('lin', (M - a) % P))
            forms.append(('chi', (1 - (M - a) ** 2) % P))
    # products of factors with total degree <= d
    deg = {'lin': 1, 'chi': 2}
    # monomials of degree <= e (reduced: exponents <= 2)
    def monomials(e):
        out = []
        for ex in itertools.product(range(3), repeat=t):
            if sum(ex) <= e:
                out.append(np.prod([X[:, i] ** ex[i] for i in range(t)], axis=0) % P if t else np.ones(len(X), dtype=np.int64))
        return out
    mons = {e: monomials(e) for e in range(d + 1)}
    rows = []
    basis_box = [np.zeros((0, len(X)), dtype=np.int64)]
    count_P = 0

    def flush():
        if rows:
            _, b = rank_mod3(list(basis_box[0]) + rows)
            basis_box[0] = b
            rows.clear()
    # enumerate multisets of factors, pruning by vanishing on Z only at the end
    def rec(start, cur, curdeg):
        nonlocal count_P
        if cur is not None and not np.any(cur[Z]):
            count_P += 1
            for m in mons[d - curdeg]:
                rows.append(cur * m % P)
            if len(rows) >= 4000:
                flush()
            return  # a multiple of a vanishing product adds nothing new beyond multipliers
        for i in range(start, len(forms)):
            kind, vals = forms[i]
            nd = curdeg + deg[kind]
            if nd > d:
                continue
            nxt = vals if cur is None else cur * vals % P
            rec(i, nxt, nd)
    if not np.any(Z):  # the empty product vanishes on an empty Z
        count_P += 1
        rows.extend(mons[d])
    rec(0, None, 0)
    # the function space of degree <= d (reduced), for the codimension report
    full_rank, _ = rank_mod3(mons[d])
    flush()
    basis = basis_box[0]
    span_rank = len(basis)
    ok = in_span(basis, w) if span_rank else (not np.any(w))
    # all functions of degree <= d vanishing on Z
    vz = [m for m in mons[d]]
    Zidx = np.nonzero(Z)[0]
    # dimension of {f in deg<=d : f|Z = 0} = full_rank - rank of restriction
    restr_rank, _ = rank_mod3([m[Zidx] for m in mons[d]])
    return {
        'spec': spec, 't': t, 'deg_C': degC, 'budget': d,
        'deg_w_nonzero': bool(np.any(w)), 'Z_size': int(Z.sum()),
        'vanishing_products': count_P, 'span_rank': int(span_rank),
        'dim_deg_le_budget_vanishing_on_Z': int(full_rank - restr_rank),
        'w_vanishes_on_Z': bool(not np.any(w[Z])),
        'w_in_product_span': bool(ok),
    }


def main():
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    specs = [['lin'], ['chi'], ['lin', 'lin'], ['chi', 'lin'], ['lin', 'lin', 'lin'],
             ['chi', 'lin', 'lin'], ['lin', 'lin', 'lin', 'lin']]
    res = []
    for s in specs:
        r = run(s)
        print(json.dumps(r), flush=True)
        res.append(r)
    if out:
        with open(out, 'w') as f:
            json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
