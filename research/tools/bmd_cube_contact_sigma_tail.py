"""Small-singular-value tail of the contact matrix over random real configurations (1 October 2026).

Absurd-bridge test of the (K) route review (cycle bmd-20261001-d), after Edelman's theorem: for an n x (n+k)
Gaussian matrix, P(sigma_min < eps) ~ c eps^(k+1), the exponent being the codimension k+1 of the rank-deficient
matrices.  For a smooth family of matrices, the small-eps exponent of P(sigma_min(A(a)) < eps) over a random
real configuration a is the real codimension of the rank-deficient locus near its real points (if it has any).

Here A = A_L(a) = (H_k(a_i,a_j))_(i<j, k<=L), H_k = [T^k]((1+a_iT)(1+a_jT))^(-3/2), R = binom(N,2).
L = R+1 is the contact matrix of (K) (expected codimension 3, slope 3); L = R is the control (contact R+3,
expected codimension 2, slope 2).  Rows are normalized columnwise by the column norms before the SVD.
The configurations are a_i uniform in [-1,1], translated to mean 0; separated with probability one.
Reports the empirical fraction below eps on a geometric grid and the fitted log-log slope on the tail.
Numerical double-precision evidence only.
"""
import argparse
import numpy as np


def coeff_matrix(a, L):
    N = len(a)
    pairs = [(i, j) for i in range(N) for j in range(i + 1, N)]
    A = np.zeros((len(pairs), L + 1))
    for r, (i, j) in enumerate(pairs):
        s, p = a[i] + a[j], a[i] * a[j]
        fm1, f = 0.0, 1.0
        A[r, 0] = 1.0
        for k in range(L):
            fn = -(s * (k + 1.5) * f + p * (k + 2) * fm1) / (k + 1)
            fm1, f = f, fn
            A[r, k + 1] = f
    return A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--samples", type=int, default=100000)
    ap.add_argument("--sizes", default="6,7,8")
    args = ap.parse_args()
    rng = np.random.default_rng(20261001)
    lines = []
    for N in [int(x) for x in args.sizes.split(",")]:
        R = N * (N - 1) // 2
        for L, name in ((R + 1, "K: L = R+1"), (R, "control: L = R")):
            sig = np.empty(args.samples)
            for t in range(args.samples):
                a = rng.uniform(-1, 1, N)
                a -= a.mean()
                A = coeff_matrix(a, L)
                A /= np.linalg.norm(A, axis=0)
                sv = np.linalg.svd(A, compute_uv=False)
                sig[t] = sv[-1] / sv[0]
            eps = np.logspace(-6, 0, 25)
            frac = np.array([(sig < e).mean() for e in eps])
            ok = (frac > 20 / args.samples) & (frac < 0.05)
            slope = np.polyfit(np.log(eps[ok]), np.log(frac[ok]), 1)[0] if ok.sum() >= 3 else float("nan")
            lines.append(f"N={N} {name}: samples {args.samples}; tail points used {int(ok.sum())}; "
                         f"fitted slope {slope:.2f}; fractions " +
                         " ".join(f"{e:.1e}:{f:.2e}" for e, f in zip(eps, frac) if f > 0))
            print(lines[-1], flush=True)
    with open(args.out, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
