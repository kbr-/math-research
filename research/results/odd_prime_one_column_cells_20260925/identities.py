#!/usr/bin/env python3
"""Exhaustive checks of the cell-resolvent identities and the three-shift obstruction (thm:cell-resolvents).

Coordinates over F_3: u (the chi factor's form, restricted and shifted by its constant) and
x_1..x_t (linear factors). C = h(u) prod x_j, C' = h(u + g) prod (x_j + d_j), every d_j != 0.
(a2) no chi, t = 2:        C - C' = -(d2 x1 + d1 x2 + d1 d2).
(a3) chi shifted (g != 0): C - C' = (-1)^(t+1) prod(d_j) g (u - g) prod_j (g u - d_j x_j).
(b)  no chi, t >= 3:       w = C - C' spans the functions of degree <= t-1 vanishing on
     Z = {C = 0 = C'}; every affine hyperplane meets supp(w); supp(w) lies in no hyperplane.
All identities are checked as functions on F_3^n for every choice of the shifts.
"""
import itertools, json, sys
import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from local_span import rank_mod3, points  # noqa: E402

P = 3
chi0 = lambda v: (1 - v * v) % P


def check_a2():
    X = points(2)
    ok = True
    for d1, d2 in itertools.product((1, 2), repeat=2):
        w = (X[:, 0] * X[:, 1] - (X[:, 0] + d1) * (X[:, 1] + d2)) % P
        r = (-(d2 * X[:, 0] + d1 * X[:, 1] + d1 * d2)) % P
        ok &= bool(np.all(w == r))
    return ok


def check_a3(tmax=4):
    out = {}
    for t in range(tmax + 1):
        X = points(t + 1)
        u = X[:, 0]
        ok = True
        for g in (1, 2):
            for ds in itertools.product((1, 2), repeat=t):
                C = chi0(u)
                Cp = chi0(u + g)
                R = g * (u - g) % P
                sign = (-1) ** (t + 1)
                for j, d in enumerate(ds):
                    x = X[:, j + 1]
                    C = C * x % P
                    Cp = Cp * (x + d) % P
                    R = R * (g * u - d * x) % P
                    sign *= d
                ok &= bool(np.all((C - Cp) % P == (sign * R) % P))
        out[t] = ok
    return out


def monomials(X, t, e):
    return [np.prod([X[:, i] ** ex[i] for i in range(t)], axis=0) % P
            for ex in itertools.product(range(3), repeat=t) if sum(ex) <= e]


def check_b(tmax=5):
    out = {}
    for t in range(2, tmax + 1):
        X = points(t)
        res = []
        for ds in itertools.product((1, 2), repeat=t):
            C = np.prod(X, axis=1) % P
            Cp = np.prod(X + np.array(ds), axis=1) % P
            w = (C - Cp) % P
            Z = (C == 0) & (Cp == 0)
            mons = monomials(X, t, t - 1)
            full, _ = rank_mod3(mons)
            rz, _ = rank_mod3([m[Z] for m in mons])
            dimU = full - rz
            # every hyperplane meets supp(w)?  supp(w) inside some hyperplane?
            lin = [c for c in itertools.product(range(P), repeat=t)
                   if any(c) and c[next(i for i in range(t) if c[i])] == 1]
            hyp_in_zero = 0
            supp_in_hyp = 0
            for c in lin:
                M = X @ np.array(c) % P
                for a in range(P):
                    hyp_in_zero += int(not np.any(w[M == a]))
                    supp_in_hyp += int(not np.any(w[M != a]))
            res.append((dimU, hyp_in_zero, supp_in_hyp, bool(np.any(w))))
        out[t] = {
            'shift_patterns': len(res),
            'dimU_values': sorted(set(r[0] for r in res)),
            'max_hyperplanes_inside_zero_set': max(r[1] for r in res),
            'max_hyperplanes_containing_support': max(r[2] for r in res),
            'w_nonzero_always': all(r[3] for r in res),
        }
    return out


def main():
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    res = {'a2': check_a2(), 'a3': check_a3(), 'b': check_b()}
    print(json.dumps(res), flush=True)
    if out:
        with open(out, 'w') as f:
            json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
