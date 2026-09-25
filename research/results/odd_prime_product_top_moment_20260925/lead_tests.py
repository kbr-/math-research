"""Cheap tests of the universality review's leads, on the weak monomial algebra over F_3.

(1) Quadratic Littlewood-Offord lead: for fixed l' and cell y, q(l) = chi(y e_2(l) e_2(l')) is a quadratic form
    in l.  Reports its rank for chi a full-support divided power and for a uniform chi (m = 2, N = 8).  A
    low-rank inverse theorem would transfer only if the collapse gave low rank.
(2) Two-layer Gauss-sum identity: sum over all l of omega^{q(l)} equals 3^n (i/sqrt3)^rho eta(disc), checked
    exactly for random chi, y, l' at m = 1, N = 7 (3^7 values of l).
(3) Design bridge, order 2: E[9^excess] at the fill point from the saved histograms, against 6, the number
    of subgroups of F_3^2 (Cohen-Lenstra second moment).
Usage: python3 lead_tests.py OUT.json"""
import itertools, json, sys
import numpy as np

def cells(m, N): return [(c, i) for c in range(N) for i in range(m)]

def rank_mod3(M):
    M = M.copy() % 3; r = 0; rows, cols = M.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i, c]), None)
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]; M[r] = (M[r] * (1 if M[r, c] == 1 else 2)) % 3
        for i in range(rows):
            if i != r and M[i, c]: M[i] = (M[i] - M[i, c] * M[r]) % 3
        r += 1
    return r

def quad_matrix(chi, m, N, y, lp):
    """Symmetric matrix Q with q(l) = sum_{a<b} Q[a,b] l_a l_b: coefficient of l_a l_b in chi(y e_2(l) e_2(l'))."""
    C = cells(m, N); n = len(C); Q = np.zeros((n, n), dtype=np.int64)
    for a, b in itertools.combinations(range(n), 2):
        ca, cb = C[a][0], C[b][0]
        if ca == cb or y[0] in (ca, cb): continue
        s = 0
        for a2, b2 in itertools.combinations(range(n), 2):
            c1, c2 = C[a2][0], C[b2][0]
            if len({ca, cb, c1, c2, y[0]}) < 5: continue
            mono = tuple(sorted([y, C[a], C[b], C[a2], C[b2]]))
            s += chi(mono) * lp[a2] * lp[b2]
        Q[a, b] = Q[b, a] = s % 3
    return Q

rng = np.random.default_rng(20260925)
out = {}
# (1) ranks, m = 2, N = 8
m, N = 2, 8
phi = {(c, i): int(rng.integers(0, 3)) for c in range(N) for i in range(m)}
for c in range(N):
    if all(phi[(c, i)] == 0 for i in range(m)): phi[(c, 0)] = 1
table = {}
def chi_div(mono): return int(np.prod([phi[x] for x in mono])) % 3
def chi_rand(mono):
    if mono not in table: table[mono] = int(rng.integers(0, 3))
    return table[mono]
res = {}
for name, chi in (("divided_power", chi_div), ("uniform", chi_rand)):
    ranks = []
    for _ in range(6):
        lp = rng.integers(0, 3, m * N); y = (int(rng.integers(0, N)), 0)
        Q = quad_matrix(chi, m, N, y, lp)
        ranks.append(int(rank_mod3((Q * 2) % 3)))   # the Gram matrix of q is Q/2 = 2Q off the diagonal
    res[name] = ranks
    print(name, "ranks of q over 6 draws (m=2, N=8, 16 variables):", ranks, flush=True)
out["quadratic_ranks_m2_N8"] = res
# (2) Gauss-sum identity, m = 1, N = 7
m, N = 1, 7
omega = np.exp(2j * np.pi / 3); ok = 0; trials = 0; worst = 0.0
allL = np.array(list(itertools.product(range(3), repeat=m * N)))
for _ in range(8):
    table.clear()
    lp = rng.integers(0, 3, m * N); y = (int(rng.integers(0, N)), 0)
    Q = quad_matrix(chi_rand, m, N, y, lp)
    vals = (np.einsum('ka,ab,kb->k', allL, np.triu(Q, 1), allL)) % 3
    direct = np.sum(omega ** vals)
    G = (2 * Q) % 3                       # Gram matrix: q(l) = l^T G l / 2 ... diagonalise over F_3
    # rank and discriminant by symmetric elimination
    A = G.copy() % 3; n = A.shape[0]; diag = []
    for k in range(n):
        piv = next((i for i in range(k, n) if A[i, i] % 3), None)
        if piv is None:
            pair = next(((i, j) for i in range(k, n) for j in range(i + 1, n) if A[i, j] % 3), None)
            if pair is None: break
            i, j = pair; A[i] = (A[i] + A[j]) % 3; A[:, i] = (A[:, i] + A[:, j]) % 3; piv = i
        A[[k, piv]] = A[[piv, k]]; A[:, [k, piv]] = A[:, [piv, k]]
        d = A[k, k] % 3; diag.append(d); inv = 1 if d == 1 else 2
        for i in range(k + 1, n):
            f = (A[i, k] * inv) % 3
            if f: A[i] = (A[i] - f * A[k]) % 3; A[:, i] = (A[:, i] - f * A[:, k]) % 3
    rho = len(diag); disc = int(np.prod(diag)) % 3 if diag else 1
    eta = 1 if disc == 1 else -1
    # q(l) = sum_{a<b} Q_ab l_a l_b = (1/2) l^T Q l = 2 l^T Q l ; with Gram G = 2Q, q = l^T G l diag form sum d_k u_k^2
    formula = 3 ** n * (1j / np.sqrt(3)) ** rho * eta
    trials += 1; err = abs(direct - formula); worst = max(worst, err); ok += err < 1e-6
    print(f"Gauss identity trial: rank {rho}, direct {direct:.4f}, formula {formula:.4f}", flush=True)
out["gauss_identity_m1_N7"] = {"trials": trials, "agree": int(ok), "max_error": float(worst)}
# (3) second moment at the fill point from the saved near-fill histograms
sec = {}
for f in ("near_fill_m2_N7-9.json", "near_fill_m1_N9-12.json"):
    d = json.load(open(f"research/results/odd_prime_product_top_moment_20260925/{f}"))
    for r in d["runs"]:
        if r["dim_A5"] != r["by_B"][-1]["B"] * r["r"]: continue       # square fill only
        h = r["excess_histogram_at_B_max"]; t = sum(h)
        sec[f"m{d['m']}_N{r['N']}"] = {"samples": t, "E_3": sum(3 ** k * h[k] for k in range(16)) / t,
                                       "E_9": sum(9 ** k * h[k] for k in range(16)) / t}
print("second moments at square fill:", sec, flush=True)
out["cohen_lenstra_moments_at_fill"] = {"prediction_E3": 2, "prediction_E9": 6, "observed": sec}
json.dump(out, open(sys.argv[1], "w"), indent=1)
