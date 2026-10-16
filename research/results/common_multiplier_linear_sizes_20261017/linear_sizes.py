"""A falsification test of conj:linear-kernel-transfer at its reduced degree, across board sizes.

System: functional pigeonhole over F_2, m = n+1 pigeons, n holes, multilinear ring, at D=2, K=1, for
n = 3, 4, 5, 6. By lem:closure-degree-locality, D=2 is the whole case K=1 of the conjecture for linear errors.
C is the degree-2 closure of all axioms, H that of the hole and functionality axioms, C cap V_1 = span{Q_i}
(asserted). For each linear error E: the C-side dim(Ann_C(E) cap V_1) against the best domain side,
max over the 2^m linear representatives E' = E + sum c_i Q_i of dim(Ann_H(E') cap V_1 + span{Q_i}).
Errors: the two diagonal sums of the band review, and 24 random linear errors per size (seed 20261017, each
coefficient and the constant uniform in F_2). Pairs: the diagonal pair and 4 random pairs per size, with the
joint maximum over pairs of representatives; at n=6 only the diagonal pair (16384 pairs of representatives).
Statement tested: conj:linear-kernel-transfer at K=1: every excess (C-side minus best domain side) is 0.
Expected: every excess 0.
Refuted by: a positive excess for some single error or pair at some size.
Possible because: the conjecture rests on two errors at one size; random errors mix constants and all rows.
Control: x00 gives excess 0 at the trivial representative at every size.
Refuted by: a positive excess for x00, contradicting lem:functional-killer-transfer.
Possible because: a bug in the polynomial kernel code or the degree-2 closure would show spurious killers.
Positive control: x00 + Q_0 must give a trivial-representative domain side below its C-side at every size
(the representative maximum must do work), and the transported-killer instance of three_quantities.py must
give excess 1; both asserted.
Refuted by: the trivial representative of x00 + Q_0 reaching the C-side, or excess 0 at the instance.
Possible because: a wrong representative loop or kernel would hide the difference.
Lemma control: at n=5 the diagonal sums give C-side 7 at D=2, as at D=3 (check:dense-linear-kernels),
which lem:closure-degree-locality predicts; asserted.
Refuted by: a C-side other than 7 at D=2 for either diagonal sum.
Possible because: an error in the lemma or in the closure at D=2 would change the kernel.
Baseline: Ann_C(E) contains Ann_H(E') + span{Q_i} for every representative, so each excess is at least 0; the
bare count bounds it by dim V_1 - m = mn + 1 - m minus the domain part. Neither decides it.
Record checked: conj:linear-kernel-transfer (the statement), check:dense-linear-kernels (n=5, two errors, D=3),
lem:admissible-numbering-transfer (monomial errors with a numbering), lem:closure-degree-locality (reduces to
D=2), check:functional-kernels-k2 (variables at K=2). None decides random linear errors at these sizes.
"""
import argparse
import importlib.util
import itertools
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tq = load('three_quantities', 'research/results/common_multiplier_transfer_test_20261016/three_quantities.py')
dl = load('dense_linear', 'research/results/common_multiplier_dense_linear_20261016/dense_linear.py')


def representatives(Q):
    reps = []
    for c in itertools.product((0, 1), repeat=len(Q)):
        shift = set()
        for i in [i for i, ci in enumerate(c) if ci]:
            shift ^= Q[i]
        reps.append((c, shift))
    return reps


def domain_kernels(cH, monos, E, reps):
    return [(c, dl.ann_poly(cH, monos, set(E) ^ s)) for c, s in reps]


def best_single(kernels, C1):
    return max(((len(k + C1), c) for c, k in kernels), key=lambda t: t[0])


def best_pair(k1, k2, C1):
    best = (-1, None)
    for (c1, h1), (c2, h2) in itertools.product(k1, k2):
        d = len((h1 & h2) + C1)
        if d > best[0]:
            best = (d, (c1, c2))
    return best


def board(n, rng, out):
    m = n + 1
    mono, full, nv, v = tq.systems(m, n)
    cC = tq.prepare(pc.Closure(full, nv, 2))
    cH = tq.prepare(pc.Closure(mono, nv, 2))
    assert cC.proper
    monos = [x for x in cC.monos if tq.deg(x) <= 1]
    C1 = tq.members(cC, monos)
    assert len(C1) == m, 'C cap V_1 should be the pigeon axioms'
    x = lambda i, j: 1 << v(i, j)
    Q = [{0} | {x(i, j) for j in range(n)} for i in range(m)]
    reps = representatives(Q)
    variables = [x(i, j) for i in range(m) for j in range(n)]
    errors = {'x00': {x(0, 0)}, 'x00+Q0': {x(0, 0)} ^ Q[0],
              'E1': {x(j, j) for j in range(n)}, 'E2': {x(j + 1, j) for j in range(n)}}
    for t in range(24):
        errors[f'random{t}'] = {u for u in [0] + variables if rng.random() < 0.5}
    res = {'dims': {'C': cC.dim, 'H': cH.dim, 'V1': len(monos)}, 'single': {}, 'pairs': {}}
    kernels, annC = {}, {}
    for name, E in errors.items():
        annC[name] = dl.ann_poly(cC, monos, E)
        kernels[name] = domain_kernels(cH, monos, E, reps)
        best, arg = best_single(kernels[name], C1)
        res['single'][name] = {'C_side': len(annC[name]), 'best_H_side': best, 'best_rep': arg,
                               'excess': len(annC[name]) - best}
    trivial = len(kernels['x00+Q0'][0][1] + C1)
    res['single']['x00+Q0']['trivial_rep_H_side'] = trivial
    assert res['single']['x00']['excess'] == 0, 'null control'
    assert trivial < res['single']['x00+Q0']['C_side'], 'positive control on the representative path'
    if n == 5:
        assert res['single']['E1']['C_side'] == 7 and res['single']['E2']['C_side'] == 7, 'lemma control'
    pairs = [('E1', 'E2')]
    if n <= 5:
        pairs += [(f'random{2 * t}', f'random{2 * t + 1}') for t in range(4)]
    for a, b in pairs:
        best, arg = best_pair(kernels[a], kernels[b], C1)
        joint = len(annC[a] & annC[b])
        res['pairs'][f'{a},{b}'] = {'C_side': joint, 'best_H_side': best, 'best_reps': arg, 'excess': joint - best}
    res['max_excess'] = max([r['excess'] for r in res['single'].values()] +
                            [r['excess'] for r in res['pairs'].values()])
    out[f'{m}x{n}'] = res
    print(f'{m}x{n}', 'dims', res['dims'], 'max excess', res['max_excess'],
          'E1', res['single']['E1'], 'x00+Q0 trivial', trivial, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    control = tq.positive_control()
    assert control['total_excess'] == 1, 'positive control'
    print('positive control', control, flush=True)
    rng = random.Random(20261017)
    out = {}
    for n in (3, 4, 5, 6):
        board(n, rng, out)
        pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
