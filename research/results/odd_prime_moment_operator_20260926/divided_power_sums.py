#!/usr/bin/env python3
"""Few-divided-power law (lem:divided-power-sums), validation over F_3 with m = 2, N = 7.

Statement: for chi = sum_i lambda_i phi_i^[5] with, in every column c, the nonzero parts phi_{i,c}
linearly independent in V_c^*, chi(A_1 tau) = 0 exactly when every single-divided-power event E_i holds
(P^(i)_{-c}(s_i, s'_i) = 0 for all c in supp phi_i), and the events are independent, so
Pr = prod_i q(|supp phi_i|).  The script samples product tops tau = e_2(l) e_2(l'), computes the
contraction chi(y tau) for all 14 cells y directly from tau in A_4 (560 coordinates), and checks per
sample that it vanishes exactly when all E_i hold; it reports the frequencies of E_1, E_2 and the
joint event.  A control pair with phi_{2,c} = phi_{1,c} on three columns violates the hypothesis.
"""
import itertools, json, sys
import numpy as np

N, m, P = 7, 2, 3
rng = np.random.default_rng(20260929)
Z4 = [(cols, cells) for cols in itertools.combinations(range(N), 4) for cells in itertools.product(range(m), repeat=4)]
Y = [(c, v) for c in range(N) for v in range(m)]
SPLITS = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]


def chi_value(phis, lams, mono):
    """sum_i lambda_i prod_j phi_i[c_j][v_j] on a 5-monomial given as ((c, v), ...)."""
    return sum(l * np.prod([ph[c][v] for c, v in mono]) for ph, l in zip(phis, lams)) % P


def kernel(phis, lams):
    K = np.zeros((len(Y), len(Z4)), dtype=np.int64)
    for a, (c, v) in enumerate(Y):
        for b, (cols, cells) in enumerate(Z4):
            if c not in cols:
                K[a, b] = chi_value(phis, lams, list(zip(cols, cells)) + [(c, v)])
    return K


def taus(L, Lp):
    """tau_z = sum over ordered disjoint pairs (Pq for l, Q for l') of l_P l'_Q; L, Lp: (S, N, m)."""
    S = L.shape[0]
    T = np.zeros((S, len(Z4)), dtype=np.int64)
    for b, (cols, cells) in enumerate(Z4):
        x = [L[:, cols[k], cells[k]] for k in range(4)]
        xp = [Lp[:, cols[k], cells[k]] for k in range(4)]
        acc = np.zeros(S, dtype=np.int64)
        for A, B in SPLITS:
            acc += x[A[0]] * x[A[1]] * xp[B[0]] * xp[B[1]] + x[B[0]] * x[B[1]] * xp[A[0]] * xp[A[1]]
        T[:, b] = acc % P
    return T


def single_events(phi, L, Lp):
    """E: P_{-c} = [X^2 Y^2] prod_{d in W, d != c} (1 + s_d X + s'_d Y) = 0 for all c in W."""
    W = [c for c in range(N) if any(phi[c])]
    s = {c: (L[:, c, :] @ np.array(phi[c])) % P for c in W}
    sp = {c: (Lp[:, c, :] @ np.array(phi[c])) % P for c in W}
    S = L.shape[0]
    ok = np.ones(S, dtype=bool)
    for c in W:
        poly = np.zeros((S, 3, 3), dtype=np.int64); poly[:, 0, 0] = 1
        for d in W:
            if d == c:
                continue
            new = poly.copy()
            new[:, 1:, :] += poly[:, :-1, :] * s[d][:, None, None]
            new[:, :, 1:] += poly[:, :, :-1] * sp[d][:, None, None]
            poly = new % P
        ok &= poly[:, 2, 2] == 0
    return ok


def run(name, phis, lams, samples, chunk=100000):
    K = kernel(phis, lams)
    counts = {'E1': 0, 'E2': 0, 'E1 and E2': 0, 'direct': 0, 'mismatch': 0, 'samples': 0}
    for _ in range(samples // chunk):
        L = rng.integers(0, P, size=(chunk, N, m)); Lp = rng.integers(0, P, size=(chunk, N, m))
        direct = ~np.any((taus(L, Lp) @ K.T) % P, axis=1)
        e1, e2 = single_events(phis[0], L, Lp), single_events(phis[1], L, Lp)
        counts['E1'] += int(e1.sum()); counts['E2'] += int(e2.sum()); counts['E1 and E2'] += int((e1 & e2).sum())
        counts['direct'] += int(direct.sum()); counts['mismatch'] += int((direct != (e1 & e2)).sum())
        counts['samples'] += chunk
    print(name, counts, flush=True)
    return counts


def main():
    out = {}
    def rand_phi():
        return [list(rng.integers(0, P, size=m)) for _ in range(N)]
    while True:
        p1, p2 = rand_phi(), rand_phi()
        if all(np.linalg.matrix_rank(np.array([p1[c], p2[c]])) == 2 and
               (p1[c][0] * p2[c][1] - p1[c][1] * p2[c][0]) % P for c in range(N)):
            break
    out['independent columns'] = {'phi': [p1, p2], **run('independent columns', [p1, p2], [1, 2], 1000000)}
    p3 = [list(p1[c]) if c < 3 else list(p2[c]) for c in range(N)]
    out['control: equal parts on three columns'] = {'phi': [p1, p3], **run('control', [p1, p3], [1, 2], 1000000)}
    if '--out' in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1, default=int)


if __name__ == '__main__':
    main()
