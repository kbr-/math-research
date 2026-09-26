"""Exact characteristic sums of restricted constants: |E omega^{c(pi)}| = |perm(omega^A)|/n!.

Tested statement (route review, 26 September 2026): with omega = exp(2 pi i/3) and c(pi) =
sum_i a_{i,pi(i)} for a uniform permutation pi of [n], |perm(omega^A)|/n! decays with n for
dense interaction (uniform random A over F_3, full-support product statistics
a_{it} = alpha_i beta_t), stays bounded away from 0 for the identity (fixed points), and
equals 1 for row plus column statistics. Permanents are exact up to floating point, by
Ryser's formula with Gray-code updates (2^n n operations), vectorized in numpy.
Usage: permanent_phases.py --out PATH [--nmax N] [--trials T] [--seed SEED]
"""
import argparse, json, math
import numpy as np

def perm_ryser(M):
    n = M.shape[0]
    # Ryser: perm = (-1)^n sum_{S} (-1)^{|S|} prod_i sum_{j in S} M_ij, all subsets at once
    masks = np.arange(1, 1 << n)
    bits = ((masks[:, None] >> np.arange(n)[None, :]) & 1).astype(np.complex128)  # (2^n-1, n)
    rowsums = bits @ M.T  # (2^n-1, n): sum over j in S of M_ij
    signs = (-1.0) ** bits.real.sum(axis=1)
    return (-1) ** n * np.sum(signs * np.prod(rowsums, axis=1))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nmax", type=int, default=14)
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260926)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    w = np.exp(2j * np.pi / 3)
    out = {"seed": a.seed, "trials": a.trials, "rows": []}
    for n in range(4, a.nmax + 1, 2):
        f = math.factorial(n)
        row = {"n": n}
        u = rng.integers(0, 3, n); v = rng.integers(0, 3, n)
        row["row_plus_column"] = round(abs(perm_ryser(w ** ((u[:, None] + v[None, :]) % 3))) / f, 6)
        row["identity"] = round(abs(perm_ryser(w ** np.eye(n))) / f, 6)
        rnd, prod = [], []
        for _ in range(a.trials):
            rnd.append(abs(perm_ryser(w ** rng.integers(0, 3, (n, n)))) / f)
            al = rng.integers(1, 3, n); be = rng.integers(1, 3, n)
            prod.append(abs(perm_ryser(w ** ((al[:, None] * be[None, :]) % 3))) / f)
        row["uniform_random_max"] = round(max(rnd), 6)
        row["product_statistic_max"] = round(max(prod), 6)
        out["rows"].append(row)
        print(json.dumps(row), flush=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)

if __name__ == "__main__":
    main()
