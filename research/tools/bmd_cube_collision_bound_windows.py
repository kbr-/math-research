"""Least pairs and minimizing windows of the joint collision bound W (29 September 2026; cycle bmd-20260929-zv;
thm:cube-far-near-collision-bound, conj:cube-far-near-collision-bound-sharp).

For every F x n with 2 <= F <= n and F + n <= 9 (every middle component of the caterpillars with N <= 10, up to the
mirror S -> 1/S), computes the collision bound for every window [-p, Fn-1-p], F-1 <= p <= Fn-n, the minimizing
windows, and at each minimizing window the least-weight admissible pairs (kappa, nu). Reuses V, parts and least_nu of
bmd_cube_far_near_joint_bound.py.
"""
import argparse
import importlib.util
import os
from math import comb

spec = importlib.util.spec_from_file_location(
    "jb", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bmd_cube_far_near_joint_bound.py"))
jb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jb)


def analyse(F, n, p, want_pairs):
    q = F * n - 1 - p
    E = list(range(-p, q + 1))
    Vt = {(f, g): jb.V(F, n, f, g, E) for f in range(F + 1) for g in range(n + 1) if f + g > 0}
    D0 = sum(E) - F * comb(n, 2) + n * comb(F, 2)
    best, pairs = None, []
    for ks in range(max(0, -D0), max(0, -D0) + 80):
        ns = ks + D0
        if best is not None and ks + ns > best:
            break
        for ka in jb.parts(ks, F):
            wk = sum((i + 1) * x for i, x in enumerate(ka))
            ksm = [sum(sorted(ka)[:f]) for f in range(F + 1)]
            need = tuple(max([0] + [Vt[(f, g)] - ksm[f] for f in range(F + 1) if (f, g) in Vt]) for g in range(n + 1))
            wn = jb.least_nu(need, ns, n)
            if wn is None:
                continue
            w = wk + wn
            if best is None or w < best:
                best, pairs = w, [(ka, need, ns)]
            elif w == best:
                pairs.append((ka, need, ns))
    out = []
    if want_pairs:
        for ka, need, ns in pairs:
            wk = sum((i + 1) * x for i, x in enumerate(ka))
            for nu in jb.parts(ns, n):
                sm = [sum(sorted(nu)[:g]) for g in range(n + 1)]
                if all(sm[g] >= need[g] for g in range(n + 1)) and wk + sum((j + 1) * x for j, x in enumerate(nu)) == best:
                    out.append((ka, nu))
    return n * comb(F + 1, 3) + F * comb(n + 1, 3) + best, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    lines = []
    for F in range(2, 5):
        for n in range(F, 10 - F):
            vals = [analyse(F, n, p, False)[0] for p in range(F - 1, F * n - n + 1)]
            m = min(vals)
            arg = [F - 1 + i for i, v in enumerate(vals) if v == m]
            lines.append(f"{F}x{n}: W by p = {F - 1}..{F * n - n}: {vals}; minimizing p {arg}")
            for p in arg:
                _, prs = analyse(F, n, p, True)
                lines.append(f"    p={p} window [{-p},{F * n - 1 - p}]: least pairs {prs}")
            print("\n".join(lines[-1 - len(arg):]), flush=True)
    if a.out:
        open(a.out, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
