"""The band review's decisive test: killers of a dense linear error on the six-by-five functional board.

System: functional pigeonhole over F_2, 6 pigeons, 5 holes, multilinear ring, D=3, K=1 (as in
check:block-pair-kernels). C is the degree-3 closure of all axioms, H that of the hole and functionality axioms
alone, Q_i = 1 + sum_j x_ij the pigeon axioms, C cap V_1 = span{Q_i}. Errors: E1 = sum_{j<5} x_jj and
E2 = sum_{j<5} x_{j+1,j}. Their linear representatives modulo span{Q_i} are E + sum_i c_i Q_i, c in F_2^6, 64 each.
Statement tested (the review's Prediction, untested): for E1, is dim Ann_C(E1) cap V_1 equal to
max over representatives E' of dim(Ann_H(E') cap V_1 + span{Q_i})? Likewise for E2 and for the pair, where the
joint side is the max over pairs of representatives of dim(Ann_H(E1') cap Ann_H(E2') cap V_1 + span{Q_i}).
Expected: not predicted; the review states both outcomes. The script prints, for each error and the pair, the
C-side dimension, the best H-side dimension and its representative, and the excess.
Refuted by: no single outcome is predicted; a positive excess means the pigeon axioms add killers beyond every
linear representative's domain model, and zero means transfer holds for this error at this size.
Possible because: the pigeon axioms are degree-one members, through which killers are transported, and no
admissible numbering reaches any representative (the band review's Attempt).
Control: the monomial error x00 must give excess 0 with the representative c = 0, as recorded by
check:functional-factor-kernels at K=1.
Refuted by: a positive excess for x00, contradicting lem:functional-killer-transfer at this size.
Possible because: a bug in the polynomial-error kernel code would show spurious killers.
Positive control: the recorded instance of three_quantities.py (a linear axiom transporting a killer) must give
excess 1; asserted.
Refuted by: excess 0 there, which would mean the code cannot see a transported killer.
Possible because: a bug in the kernel or in the space sums would hide transported killers.
Baseline: Ann_C(E) always contains Ann_H(E') + span{Q_i} for every representative E', so the excess is at least
0; the bare count dim V_1 = 31 bounds it by 31 - 6 minus the best domain part. Neither decides it.
Record checked: lem:admissible-numbering-transfer and its polynomial extension (band review, Decision) need an
admissible numbering, which no linear representative of E1 has (band review, Attempt); lem:functional-killer-
transfer covers each monomial x_jj alone, not their sum; conj:monomial-kernel-transfer concerns monomial errors.
None decides these kernels.
"""
import argparse
import importlib.util
import itertools
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


def ann_poly(c, monos, error):
    """{f in span(monos) : f * error in c} for a polynomial error given as a set of monomials."""
    rows = []
    for t, m in enumerate(monos):
        rows.append((tq.red(c, c.vector(pc.multiply({m}, set(error)))), 1 << t))
    piv, kern = {}, tq.Space()
    for x, tag in rows:
        for p in sorted(piv, reverse=True):
            if x >> p & 1:
                x ^= piv[p][0]
                tag ^= piv[p][1]
        if x:
            piv[x.bit_length() - 1] = (x, tag)
        else:
            kern.add(tag)
    return kern


def add_poly(a, b):
    return set(a) ^ set(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    control = tq.positive_control()
    print('positive control', control, flush=True)
    assert control['total_excess'] == 1, 'positive control'
    mono, full, nv, v = tq.systems(6, 5)
    cC = tq.prepare(pc.Closure(full, nv, 3))
    cH = tq.prepare(pc.Closure(mono, nv, 3))
    assert cC.proper
    monos = [m for m in cC.monos if tq.deg(m) <= 1]
    C1 = tq.members(cC, monos)
    assert len(C1) == 6, 'C cap V_1 should be the six pigeon axioms'
    x = lambda i, j: 1 << v(i, j)
    Q = [{0} | {x(i, j) for j in range(5)} for i in range(6)]
    E1 = {x(j, j) for j in range(5)}
    E2 = {x(j + 1, j) for j in range(5)}
    reps = []
    for c in itertools.product((0, 1), repeat=6):
        shift = set()
        for i, ci in enumerate(c):
            if ci:
                shift = add_poly(shift, Q[i])
        reps.append((c, shift))
    out = {'closure_dims': {'C': cC.dim, 'H': cH.dim}}

    def single(name, E):
        annC = ann_poly(cC, monos, E)
        best, arg = -1, None
        for c, shift in reps:
            d = len(ann_poly(cH, monos, add_poly(E, shift)) + C1)
            if d > best:
                best, arg = d, c
        res = {'C_side': len(annC), 'best_H_side': best, 'best_rep': arg, 'excess': len(annC) - best}
        out[name] = res
        print(name, res, flush=True)
        return annC

    single('control x00', {x(0, 0)})
    assert out['control x00']['excess'] == 0, 'null control'
    # Second run, after the review: a control on the polynomial path. x00 + Q_0 has the C-kernel of x00 (15),
    # but its trivial representative's domain side is 10 (reviewer's hand count); the maximum over
    # representatives, reached at c = (1,0,...,0), must restore 15.
    shifted = add_poly({x(0, 0)}, Q[0])
    single('control x00+Q0', shifted)
    trivial = len(ann_poly(cH, monos, shifted) + C1)
    out['control x00+Q0']['trivial_rep_H_side'] = trivial
    print('control x00+Q0 trivial representative H side', trivial, flush=True)
    assert out['control x00+Q0']['C_side'] == 15 and out['control x00+Q0']['excess'] == 0, 'polynomial control'
    assert trivial < 15, 'the trivial representative must fall short, or the control shows nothing'
    a1 = single('E1', E1)
    a2 = single('E2', E2)
    joint_C = len(a1 & a2)
    # each error's 64 domain kernels computed once, then the 4096 pairs intersected
    h1s = [(c, ann_poly(cH, monos, add_poly(E1, s))) for c, s in reps]
    h2s = [(c, ann_poly(cH, monos, add_poly(E2, s))) for c, s in reps]
    best, arg = -1, None
    for (c1, h1), (c2, h2) in itertools.product(h1s, h2s):
        d = len((h1 & h2) + C1)
        if d > best:
            best, arg = d, (c1, c2)
    out['pair'] = {'C_side': joint_C, 'best_H_side': best, 'best_reps': arg, 'excess': joint_C - best}
    print('pair', out['pair'], flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
