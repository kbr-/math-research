#!/usr/bin/env python3
"""Linked-cluster test for clause members, p = 3, N = 12, slice m = 13 (mod 3), degrees <= 7.

Statement under test (prop:hilbert-factorization and its linked-cluster reading): in the range of the
filtered freeness transfer, H(Z_Omega) = H(slice) * H(gr F^Omega) / H(T_forms) for a member cut by forms
with allowed values Omega; hence H(A and B) * H(slice) = H(A) * H(B) when A and B use independent forms,
with Omega-level corrections when they share forms.  Through degree 5 the identity only says that the drops
from the slice add (they start at degree 3); the product term first appears at degree 6.  This script
computes H through degree 7 for the slice, A, B and A and B, for (i) forms on disjoint supports,
(ii) dense independent forms, (iii) shared forms (the two-block pair), and compares both identities.
One elimination per set: the column pivots of the evaluation matrix, columns in degree order, give every
prefix rank at once.
"""
import itertools, json, sys
import numpy as np
here = __file__.rsplit('/', 1)[0]
sys.path.insert(0, here + '/../odd_prime_closure_route_review_20260925')
from vanishing_tops import rref3

N, m, DM = 12, 13, 7
COLS = [mu for d in range(DM + 1) for mu in itertools.combinations(range(N), d)]
DEG = np.array([len(mu) for mu in COLS])


def hilbert_points(pts):
    """Hilbert function of gr F^pts through DM: pivots of the evaluation matrix per degree."""
    E = np.ones((len(pts), len(COLS)), dtype=np.int64)
    for j, mu in enumerate(COLS):
        for h in mu:
            E[:, j] *= pts[:, h]
    _, piv = rref3(E % 3)
    return [int(np.sum(DEG[list(piv)] == d)) for d in range(DM + 1)]


def hilbert_grid(omega, d):
    """Hilbert function of polynomial functions (each variable degree <= 2) on omega in F_3^d."""
    mons = sorted(itertools.product(range(3), repeat=d), key=sum)
    E = np.array([[int(np.prod([pow(int(x), a, 3) if a else 1 for x, a in zip(pt, mu)])) % 3 for mu in mons]
                  for pt in omega], dtype=np.int64)
    _, piv = rref3(E)
    return [int(sum(1 for i in piv if sum(mons[i]) == k)) for k in range(2 * d + 1)]


def series_mul(a, b):
    return np.convolve(a, b)[:DM + 1].tolist()


def series_div(a, b):
    out = []
    for k in range(DM + 1):
        v = (a[k] if k < len(a) else 0) - sum(out[i] * (b[k - i] if k - i < len(b) else 0) for i in range(k))
        out.append(v // b[0])
    return out


def clause_ok(phi, i, j, ki, kj):
    """Allowed by the clause 'l_i = ki and l_j != kj' being false."""
    return lambda c: not (int(np.dot(phi[i], c) % 3) == ki and int(np.dot(phi[j], c) % 3) != kj)


def main():
    rng = np.random.default_rng(20260928)
    cube = np.array(list(itertools.product((0, 1), repeat=N)), dtype=np.int64)
    sl = cube[cube.sum(axis=1) % 3 == m % 3]
    HS = hilbert_points(sl)
    print('slice', HS, flush=True)
    omega_clause = [w for w in itertools.product(range(3), repeat=2) if not (w[0] == 0 and w[1] != 0)]
    HT = hilbert_grid(list(itertools.product(range(3), repeat=2)), 2)
    out = {'slice': HS, 'cases': {}}
    cases = {}
    phi = rng.integers(1, 3, size=(4, N)); phi[0:2, 6:] = 0; phi[2:4, :6] = 0
    cases['disjoint supports'] = (phi, clause_ok(phi, 0, 1, 0, 0), clause_ok(phi, 2, 3, 0, 0), 'independent')
    phi = rng.integers(1, 3, size=(4, N))
    cases['dense independent'] = (phi, clause_ok(phi, 0, 1, 0, 0), clause_ok(phi, 2, 3, 0, 0), 'independent')
    phi = rng.integers(1, 3, size=(2, N))
    cases['shared forms (two-block pair)'] = (phi, clause_ok(phi, 0, 1, 0, 0), clause_ok(phi, 0, 1, 1, 1), 'shared')
    for name, (phi, A, B, kind) in cases.items():
        H = {}
        for label, f in (('A', A), ('B', B), ('A and B', lambda c: A(c) and B(c))):
            pts = sl[np.array([f(c) for c in sl])]
            H[label] = hilbert_points(pts)
        lhs = series_mul(H['A and B'], HS); rhs = series_mul(H['A'], H['B'])
        rec = {'H': H, 'H(AB)H(S)': lhs, 'H(A)H(B)': rhs,
               'multiplicative_through': next((d - 1 for d in range(DM + 1) if lhs[d] != rhs[d]), DM),
               'drop_A': [s - a for s, a in zip(HS, H['A'])], 'drop_B': [s - b for s, b in zip(HS, H['B'])],
               'drop_AB': [s - x for s, x in zip(HS, H['A and B'])]}
        # Omega-level factorization prediction H(Z) = H(S) * H(Omega) / H(T) for single clauses
        HO = hilbert_grid(omega_clause, 2)
        pred = series_div(series_mul(HS, HO), HT)
        rec['omega_prediction_single_clause'] = pred
        if kind == 'shared':
            omega_ab = [w for w in omega_clause if not (w[0] == 1 and w[1] != 1)]
            rec['omega_prediction_AB'] = series_div(series_mul(HS, hilbert_grid(omega_ab, 2)), HT)
        else:
            HO4 = np.convolve(HO, HO).tolist()
            rec['omega_prediction_AB'] = series_div(series_mul(HS, HO4), np.convolve(HT, HT).tolist())
        out['cases'][name] = rec
        print(name, json.dumps(rec), flush=True)
    if '--out' in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
