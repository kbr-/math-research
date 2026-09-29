"""The collision bound over all column sets, not only windows (29 September 2026; cycle bmd-20260929-zx;
thm:cube-far-near-collision-bound). The bound val P_E >= n binom(F+1,3) + F binom(n+1,3) + W(E) holds for every column
set E of size F n (the double Schur reduction and the collision-bound proof never use consecutiveness). Tested: over
all column sets E, the least W(E) is attained only at the minimizing windows. Completeness: a proved tail bound
(function tail) shows no set with a column beyond L = W* + max(F, n) + 1 can compete; sets with tail bound > W* are pruned. If so, and if the bound is
attained at those windows, the far-near limit of the component is that window (or its tie) among all column sets.
Reuses V, parts and least_nu of bmd_cube_far_near_joint_bound.py.
"""
import argparse
import importlib.util
import itertools
import os
from math import comb

spec = importlib.util.spec_from_file_location(
    "jb", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bmd_cube_far_near_joint_bound.py"))
jb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jb)


def W(F, n, E):
    E = sorted(E)
    Vt = {(f, g): jb.V(F, n, f, g, E) for f in range(F + 1) for g in range(n + 1) if f + g > 0}
    D0 = sum(E) - F * comb(n, 2) + n * comb(F, 2)
    best = None
    for ks in range(max(0, -D0), max(0, -D0) + 120):
        ns = ks + D0
        if best is not None and ks + ns > best:
            break
        for ka in jb.parts(ks, F):
            wk = sum((i + 1) * x for i, x in enumerate(ka))
            ksm = [sum(sorted(ka)[:f]) for f in range(F + 1)]
            need = tuple(max([0] + [Vt[(f, g)] - ksm[f] for f in range(F + 1) if (f, g) in Vt]) for g in range(n + 1))
            wn = jb.least_nu(need, ns, n)
            if wn is not None and (best is None or wk + wn < best):
                best = wk + wn
    return best


def tail(F, n, E):
    """Proved lower bound for W(E): the all-far cluster gives |kappa| >= A = sum_{e<0} (|e|-F+1)_+, the all-near
    cluster |nu| >= B = sum_{e>0} (e-n+1)_+, and W >= |kappa| + |nu| with |nu| - |kappa| = D0."""
    A = sum(max(0, -e - F + 1) for e in E if e < 0)
    B = sum(max(0, e - n + 1) for e in E if e > 0)
    D0 = sum(E) - F * comb(n, 2) + n * comb(F, 2)
    return max(A + B, 2 * A + D0, 2 * B - D0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    lines = []
    for F, n in [(2, 2), (2, 3), (3, 2), (2, 4), (3, 3)]:
        p = (F * n - 1) // 2
        wstar = min(W(F, n, list(range(-q, F * n - q))) for q in range(F - 1, F * n - n + 1))
        L = wstar + max(F, n) + 1  # a single column beyond L already costs more than wstar
        cols = list(range(-L, L + 1))
        cand, full = [], 0
        def rec(start, chosen, ab):
            nonlocal full
            if ab > wstar:
                return
            if len(chosen) == F * n:
                if tail(F, n, chosen) <= wstar:
                    cand.append(tuple(chosen))
                return
            for idx in range(start, len(cols) - (F * n - len(chosen)) + 1):
                e = cols[idx]
                inc = max(0, -e - F + 1) if e < 0 else max(0, e - n + 1)
                rec(idx + 1, chosen + [e], ab + inc)
        rec(0, [], 0)
        vals = {E: W(F, n, list(E)) for E in cand}
        m = min(vals.values())
        arg = [E for E, v in vals.items() if v == m]
        wins = all(E[-1] - E[0] == F * n - 1 for E in arg)
        second = min([v for v in vals.values() if v > m] or [None])
        lines.append(f"{F}x{n}: window minimum {wstar}; columns in [-{L},{L}] (complete by the tail bound): {len(cand)} sets with tail bound <= {wstar}; least W = {m} at {arg}; all windows: {wins}; next value {second}")
        print(lines[-1], flush=True)
    if a.out:
        open(a.out, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
