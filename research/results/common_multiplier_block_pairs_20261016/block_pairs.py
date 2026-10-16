"""The head item's next attempt: block-pair errors on the functional pigeonhole system, at the window's top.

System: functional pigeonhole over F_2, 6 pigeons, 5 holes, multilinear ring, D=3 (proper,
check:functional-factor-kernels). C is its degree-3 closure, H the degree-3 closure of the hole and
functionality axioms alone (the domain model of partial matchings). Errors are degree-2 monomials x_a x_b
with a, b on distinct pigeons and distinct holes (on one pigeon or one hole they are monomial axioms), so
K + e = 1 + 2 = 3 = D. For an error set F and X in {C, H}: Ann_X(F) = {u in V_1 : u E in X for E in F}.
Statement tested (an untested hypothesis, stated so it can fail): conj:functional-kernel-transfer's
equality extended from variable errors to these monomial errors at the window's top: for every set F
below, dim Ann_C(F) = dim(Ann_H(F) + (C cap V_1)), total excess 0.
Expected: total excess 0 for every set; the script prints each set's dimensions.
Refuted by: a positive total excess for some set, a killer the pigeon axioms' derivations add, a joint
effect beyond supports.
Possible because: at K+e = D the membership u x_a x_b in C sits at the closure's top degree, where
pigeon-axiom multiples of degree 3 can enter, unlike the variable errors of the recorded checks.
Sets: {x00x11}, {x00x11, x22x33}, {x00x11, x11x22} (a chain), {x00x11, x01x10} (a crossing),
{x00x11, x00x22} (shared variable), and the three-error set {x00x11, x22x33, x34x43}.
Control: the variable set {x00, x11} at K=1 must give total excess 0, as check:functional-factor-kernels
recorded.
Positive control: the recorded instance of three_quantities.py (variables a, b, w, z; monomial axioms ab,
bz; linear axiom w+a+z; D=2; K=1; F={w}) must give total excess 1; asserted.
Refuted by: excess 0 there, which would mean the code cannot see a killer a linear axiom adds.
Possible because: a bug in the reused ann or intersection code would hide transported killers.
Baseline: Ann_C(F) contains Ann_H(F) + (C cap V_1) always, so the excess is at least 0; the bare count
dim V_1 = 31 bounds it above by 31 - 6; neither decides zero.
Record checked: conj:functional-kernel-transfer and check:functional-kernels-k2 cover variable errors only
(the conjecture says variable errors are load-bearing); the K=2 equality for x_a gives x_b u in Ann_H(x_a) +
(C cap V_2), which does not place u in Ann_H(x_a x_b) + (C cap V_1); check:functional-factor-kernels is the
K=1 variable case. None decides these sets.
"""
import argparse
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc

spec = importlib.util.spec_from_file_location(
    'three_quantities', ROOT / 'research/results/common_multiplier_transfer_test_20261016/three_quantities.py')
tq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    control = tq.positive_control()
    print('positive control', control, flush=True)
    assert control['total_excess'] == 1, 'positive control must give excess 1'
    mono, full, nv, v = tq.systems(6, 5)
    cC = tq.prepare(pc.Closure(full, nv, 3))
    cH = tq.prepare(pc.Closure(mono, nv, 3))
    assert cC.proper
    monos = [m for m in cC.monos if tq.deg(m) <= 1]
    x = lambda i, j: 1 << v(i, j)
    sets = {
        'variables x00,x11 (control)': [x(0, 0), x(1, 1)],
        'x00x11': [x(0, 0) | x(1, 1)],
        'x00x11,x22x33': [x(0, 0) | x(1, 1), x(2, 2) | x(3, 3)],
        'x00x11,x11x22 (chain)': [x(0, 0) | x(1, 1), x(1, 1) | x(2, 2)],
        'x00x11,x01x10 (crossing)': [x(0, 0) | x(1, 1), x(0, 1) | x(1, 0)],
        'x00x11,x00x22 (shared)': [x(0, 0) | x(1, 1), x(0, 0) | x(2, 2)],
        'x00x11,x22x33,x34x43': [x(0, 0) | x(1, 1), x(2, 2) | x(3, 3), x(3, 4) | x(4, 3)],
    }
    out = {'closure_dims': {'C': cC.dim, 'H': cH.dim}, 'sets': {}}
    for name, errors in sets.items():
        q, _, _ = tq.quantities(cC, cH, monos, errors)
        out['sets'][name] = q
        print(name, q, flush=True)
    assert out['sets']['variables x00,x11 (control)']['total_excess'] == 0, 'control: recorded K=1 excess 0'
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
    bad = [n for n, q in out['sets'].items() if q['total_excess'] > 0]
    print('PASS' if not bad else 'REFUTED: positive excess for ' + ', '.join(bad), flush=True)


if __name__ == '__main__':
    main()
