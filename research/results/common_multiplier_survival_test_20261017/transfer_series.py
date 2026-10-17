"""Transfer for Pang-form errors: the closure common kernel against the domain side, on the instances most unlike.

System: functional pigeonhole over F_2, m = n+1 pigeons, n holes, multilinear ring, D = 3, K = 1, C the degree-3
closure of all axioms, H that of the hole and functionality axioms alone. For a set of errors E (here
(1+q)x_e, q a sum of two disjoint edge variables), write A_C = common kernel in V_1 modulo C and
A_H = common kernel in V_1 modulo H of the same representatives. A_H + (C cap V_1) is inside A_C always (H inside
C, and C cap V_1 kills everything); the statement tested is equality, the transfer form that would be conjectured
from the survival test (two_family_kernel.json: dim A_C = 6 = dim(A_H + C cap V_1)). The extreme the question needs:
equality of two spaces one inside the other, so the script compares their dimensions; representatives are fixed
as written ((1+q)x_e), and the conjectured form names them.
Instances: (a) the survival test, 6 x 5, two families on the edges sharing nothing with their q; (b) 6 x 5, the same
two families on every edge (60 errors, which collapse to the two factors through the pigeon-row sums); (c) 6 x 5,
the first family alone on its twelve edges, where q1 is a domain killer; (d) 7 x 6, the families q1 = x00+x11,
q2 = x22+x33 on the edges sharing nothing with their q (pigeons 2..6 x holes 2..5 and pigeons 0,1,4,5,6 x holes
0,1,4,5).
Expected: equality in (a), recorded; in (b), (c), (d) not predicted.
Refuted by: dim A_C > dim(A_H + C cap V_1) at some instance, a killer from the pigeon axioms beyond the domain side.
Possible because: ex:top-degree-linear-killer exhibits such a killer for one linear error at 4 x 3 at its top
degree, and (b)'s errors collapse modulo C to linear factors whose kernels the pigeon axioms enlarge.
Control: in (c), q1 must lie in A_C and in A_H (q1(1+q1) = 0 in the multilinear ring).
Refuted by: q1 missing from either kernel, which would mean the error polynomials are built wrongly.
Possible because: a wrong product or edge list would change the errors.
Forced by counts: the control's outcome is forced by the identity q1(1+q1) = 0, so it tests the error
construction and the kernel routine, not the mathematics.
Positive control: three_quantities.positive_control() must give excess 1 (a transported killer seen).
Refuted by: excess 0 there, which would mean the kernel code cannot see a transported killer.
Possible because: a bug in the kernel or in the space sums would hide transported killers.
Baseline: the containment A_H + C cap V_1 inside A_C gives dim A_C >= that dimension; the bare count gives
dim A_C <= dim V_1. Neither decides equality.
Record checked: the upper bounds lem:saving-monotonicity and ex:support-saving-not-inherited,
conj:functional-kernel-transfer (variables only), conj:representative-sum-transfer (single linear errors, which
bears on (b) through the collapse), lem:factor-ideal-domination; none decides these instances.
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
spec = importlib.util.spec_from_file_location(
    'dense_linear', ROOT / 'research/results/common_multiplier_dense_linear_20261016/dense_linear.py')
dl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dl)


def board(m, n):
    mono, full, nv, v = tq.systems(m, n)
    cC = tq.prepare(pc.Closure(full, nv, 3))
    cH = tq.prepare(pc.Closure(mono, nv, 3))
    assert cC.proper
    monos = [mm for mm in cC.monos if tq.deg(mm) <= 1]
    assert len(monos) == m * n + 1
    C1 = tq.members(cC, monos)
    assert len(C1) == m, 'C cap V_1 should be the pigeon axioms'
    return cC, cH, monos, C1, (lambda i, j: 1 << v(i, j))


def compare(cC, cH, monos, C1, errors):
    AC = AH = None
    for E in errors:
        kC, kH = dl.ann_poly(cC, monos, E), dl.ann_poly(cH, monos, E)
        AC = kC if AC is None else AC & kC
        AH = kH if AH is None else AH & kH
    return AC, AH, {'errors': len(errors), 'dim_A_C': len(AC), 'dim_A_H': len(AH),
                    'dim_A_H_plus_C1': len(AH + C1), 'excess': len(AC) - len(AH + C1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    assert tq.positive_control()['total_excess'] == 1, 'positive control'
    out = {}
    cC, cH, monos, C1, x = board(6, 5)
    p1, p2 = {0, x(0, 0), x(1, 1)}, {0, x(2, 2), x(3, 3)}
    fam = lambda p, edges: [pc.multiply(p, {x(*e)}) for e in edges]
    e1 = [(i, j) for i in range(2, 6) for j in (2, 3, 4)]
    e2 = [(i, j) for i in (0, 1, 4, 5) for j in (0, 1, 4)]
    every = [(i, j) for i in range(6) for j in range(5)]
    _, _, out['a'] = compare(cC, cH, monos, C1, fam(p1, e1) + fam(p2, e2))
    _, _, out['b'] = compare(cC, cH, monos, C1, fam(p1, every) + fam(p2, every))
    AC, AH, out['c'] = compare(cC, cH, monos, C1, fam(p1, e1))
    q1 = 0
    for t, mm in enumerate(monos):
        if mm in (x(0, 0), x(1, 1)):
            q1 |= 1 << t
    single = tq.Space()
    single.add(q1)
    assert len(AC + single) == len(AC) and len(AH + single) == len(AH), 'control: q1 kills its own family'
    print(json.dumps(out), flush=True)
    cC, cH, monos, C1, x = board(7, 6)
    p1, p2 = {0, x(0, 0), x(1, 1)}, {0, x(2, 2), x(3, 3)}
    e1 = [(i, j) for i in range(2, 7) for j in (2, 3, 4, 5)]
    e2 = [(i, j) for i in (0, 1, 4, 5, 6) for j in (0, 1, 4, 5)]
    _, _, out['d'] = compare(cC, cH, monos, C1, fam(p1, e1) + fam(p2, e2))
    print(json.dumps(out), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
