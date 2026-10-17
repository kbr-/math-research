"""The survival review's Decisive test: a joint common killer of two Pang families on the six-by-five board.

System: functional pigeonhole over F_2, 6 pigeons, 5 holes, multilinear ring, D=3, K=1. C is the degree-3
closure of all axioms, H that of the hole and functionality axioms alone, Q_i = 1 + sum_j x_ij, C cap V_1 =
span{Q_i} (dimension 6). Families q1 = x00 + x11 and q2 = x22 + x33; errors E_{nu,e} = (1 + q_nu) x_e for the
edges e sharing no pigeon and no hole with an edge of q_nu: nu = 1 on pigeons 2..5 x holes 2,3,4, nu = 2 on
pigeons 0,1,4,5 x holes 0,1,4, twelve each.
Statement tested (the review's Prediction): is A = Ann_C(all 24 errors) cap V_1 strictly larger than
C cap V_1? The script also computes F = Ann_C(1+q1) cap Ann_C(1+q2) cap V_1, which lem:factor-ideal-domination
(b) puts inside A (room K+e+g = 1+1+1 <= 3); a killer of A outside F would witness a mechanism beyond factor
domination. The extreme the question needs: A is an intersection of kernels, and the survival question asks for
its dimension against dim(C cap V_1) = 6, so the script compares dim A with 6 and dim F with dim A; no maximum
over representatives enters, since the C-kernels do not depend on the representative.
Expected: not predicted; the review states both outcomes, A = C cap V_1 or A strictly larger.
Refuted by: no single outcome is predicted; dim A > 6 means the pigeon axioms give a joint linear killer,
dim A = 6 means none exists here.
Possible because: the review's hand argument shows no domain linear common killer (dim Z = 0), so any killer
beyond C cap V_1 must come from the closure's non-domain part, which can be nonzero (ex:top-degree-linear-killer).
Also asserted, for the summed condition: the summed ranks 31 - dim Ann_C(E) over the 24 errors reach H = 25.
Control: each single error's domain-side kernel Ann_H(E) + C cap V_1 is inside its C-kernel (containment, always).
Refuted by: an H-side kernel not inside the C-kernel, which would mean the closures are built wrongly.
Possible because: a wrong axiom list or degree would break H inside C.
Positive control: three_quantities.positive_control() (a linear axiom transporting a killer) must give excess 1.
Refuted by: excess 0 there, which would mean the kernel code cannot see a transported killer.
Possible because: a bug in the kernel or in the space sums would hide transported killers.
Null control: the monomial error x00 has C-kernel dimension 15, as recorded by the dense-linear script's control.
Refuted by: another dimension, contradicting the recorded check:functional-factor-kernels computations.
Possible because: a changed tool or axiom list would shift the kernel.
Baseline: the support bound dim V_1|_S = 31 > H = 25 decides nothing; the trivial containment C cap V_1 inside A
gives dim A >= 6, and the bare count gives dim A <= 31. Neither decides the question.
Record checked: lem:saving-monotonicity, lem:domain-model-stacked-rank, ex:support-saving-not-inherited (upper
bounds), lem:factor-ideal-domination (lower bound F inside A), conj:representative-sum-transfer (single linear
errors), conj:functional-kernel-transfer and check:functional-factor-kernels (variables only); none gives dim A.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    control = tq.positive_control()
    assert control['total_excess'] == 1, 'positive control'
    mono, full, nv, v = tq.systems(6, 5)
    cC = tq.prepare(pc.Closure(full, nv, 3))
    cH = tq.prepare(pc.Closure(mono, nv, 3))
    assert cC.proper
    monos = [m for m in cC.monos if tq.deg(m) <= 1]
    assert len(monos) == 31
    C1 = tq.members(cC, monos)
    assert len(C1) == 6, 'C cap V_1 should be the six pigeon axioms'
    x = lambda i, j: 1 << v(i, j)
    assert len(dl.ann_poly(cC, monos, {x(0, 0)})) == 15, 'null control'
    p1 = {0, x(0, 0), x(1, 1)}                     # 1 + q1
    p2 = {0, x(2, 2), x(3, 3)}                     # 1 + q2
    edges1 = [(i, j) for i in range(2, 6) for j in (2, 3, 4)]
    edges2 = [(i, j) for i in (0, 1, 4, 5) for j in (0, 1, 4)]
    errors = [('q1', e, pc.multiply(p1, {x(*e)})) for e in edges1] + \
             [('q2', e, pc.multiply(p2, {x(*e)})) for e in edges2]
    assert len(errors) == 24
    A, ranks, rows = None, [], []
    for fam, e, E in errors:
        assert len(E) == 3 and all(tq.deg(m) <= 2 for m in E), 'each error is (1 + q) x_e, three terms'
        kC = dl.ann_poly(cC, monos, E)
        kH = dl.ann_poly(cH, monos, E) + C1
        assert len(kH + kC) == len(kC), 'control: the domain side lies inside the C-kernel'
        ranks.append(31 - len(kC))
        rows.append({'family': fam, 'edge': e, 'error_terms': len(E), 'C_kernel': len(kC), 'H_side': len(kH),
                     'rank': 31 - len(kC)})
        A = kC if A is None else (A & kC)
    F = dl.ann_poly(cC, monos, p1) & dl.ann_poly(cC, monos, p2)
    common_H = None
    for fam, e, E in errors:
        k = dl.ann_poly(cH, monos, E)
        common_H = k if common_H is None else (common_H & k)
    out = {'closure_dims': {'C': cC.dim, 'H': cH.dim}, 'errors': rows,
           'summed_rank': sum(ranks), 'H_capacity': 31 - 6,
           'dim_A': len(A), 'dim_C_cap_V1': 6, 'dim_F': len(F), 'dim_F_inside_A': len(F & A),
           'dim_A_plus_F': len(A + F), 'dim_common_H_kernel': len(common_H),
           'dim_common_H_plus_C1': len(common_H + C1)}
    assert out['dim_F_inside_A'] == out['dim_F'], 'lem:factor-ideal-domination (b): F inside A'
    print(json.dumps({k: out[k] for k in out if k != 'errors'}), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
