"""Distribution mod 3 of the restricted constant of a form under a uniform random matching.

Tested statement (route review, 26 September 2026): for a form L = sum a_{it} x_{it} on the
n x n board, the constant c(pi) = sum_i a_{i,pi(i)} left by filling the board with a uniform
random perfect matching pi is (a) constant when a_{it} = u_i + v_t (row plus column
statistics), (b) far from uniform for sparse interaction (a = identity: fixed points mod 3,
Poisson(1) mod 3), and (c) close to uniform for dense interaction (uniform random a, and a
full-support product statistic a_{it} = alpha_i beta_t). Reports the total-variation
distance from uniform on F_3 of the empirical distribution, per case.
Usage: constant_equidistribution.py --out PATH [--n N] [--samples S] [--seed SEED]
"""
import argparse, json
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--samples", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260926)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    n, S = a.n, a.samples
    u = rng.integers(0, 3, n); v = rng.integers(0, 3, n)
    alpha = rng.integers(1, 3, n); beta = rng.integers(1, 3, n)
    cases = {
        "row_plus_column": (u[:, None] + v[None, :]) % 3,
        "identity_fixed_points": np.eye(n, dtype=np.int64),
        "uniform_random": rng.integers(0, 3, (n, n)),
        "product_statistic_full_support": (alpha[:, None] * beta[None, :]) % 3,
    }
    perms = np.argsort(rng.random((S, n)), axis=1)  # S uniform permutations
    rows = np.arange(n)[None, :]
    res = {"n": n, "samples": S, "seed": a.seed, "cases": {}}
    for name, A in cases.items():
        c = A[rows, perms].sum(axis=1) % 3
        freq = np.bincount(c, minlength=3) / S
        res["cases"][name] = {"freq": freq.round(5).tolist(),
                              "tv_from_uniform": round(float(0.5 * np.abs(freq - 1/3).sum()), 5)}
    # Poisson(1) mod 3 reference for the identity case
    from math import exp, factorial
    ref = [exp(-1) * sum(1 / factorial(j) for j in range(r, 60, 3)) for r in range(3)]
    res["poisson1_mod3_reference"] = [round(x, 5) for x in ref]
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res))

if __name__ == "__main__":
    main()
