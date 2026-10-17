"""Joint kernels of pairs against representative choices, at four pigeons and three holes (window review, (i)).

System: functional pigeonhole over F_2, 4 pigeons, 3 holes, multilinear, D = 2 (the top ceil(3/2)), K = 1; the ten
positive-excess errors of row_search.json, all 45 pairs (pair_saving.json's pairs).
For a pair: J = Ann_C(E1) cap Ann_C(E2) cap V_1; W = C cap V_1; over the 16 representatives E' = E + (sum of
pigeon axioms) of each error, a = max over pairs of dim(Ann_H(E1') cap Ann_H(E2') + W) (one pair of
representatives), a2 = max dim((Ann_H(E1') + W) cap (Ann_H(E2') + W)), b = dim of the sum over pairs of
Ann_H(E1') cap Ann_H(E2'), plus W, and I = dim((sum_E1' Ann_H(E1') + W) cap (sum_E2' Ann_H(E2') + W)), the
intersection of the per-error representative sums. Every one of these spaces lies in J, each summand killing both
errors modulo C, so a <= b <= dim J, a <= a2 <= I and b <= I <= dim J; the question needs the maxima over choices
(the largest explained part), which is why a and a2 are maxima.
Statement tested: the reviewer's report (window review, second stage) that on the 33 pairs not congruent modulo
span{Q_i}, dim J = 5, a = b = 4 and I = 5, so that the survivor is explained only by the intersection of the
per-error sums.
Expected: dim J = 5, a = a2 = b = 4, I = 5 on each of the 33 pairs; dim J = 7 on the 12 congruent pairs.
Refuted by: any of those values different on some pair, say a = 5 on a non-congruent pair.
Possible because: the reviewer's computation was independent of tools/pc_closure.py and took Ann_C(E) as a sum
over representatives; the closure here may differ.
Control: dim W = 4 and, for x00 alone, dim Ann_C = 9 (rep_sum.json); asserted.
Refuted by: dim W or the x00 kernel different from those values.
Possible because: a wrong closure or representative set changes them.
Forced by counts: nothing forces dim W = 4: the closure's degree-one part could hold combinations beyond the four
pigeon axioms.
Positive control: on a congruent pair, J equals one error's kernel, so dim J = 7 = I must be seen; asserted.
Refuted by: dim J or I different from 7 on a congruent pair.
Possible because: an error in the intersection would show there first.
Baseline: the containments a <= b <= dim J and a <= I <= dim J; they decide nothing about the gaps.
Record checked: check:top-degree-partition-kernels and conj:representative-sum-transfer (single errors, the sum
equal to Ann_C), lem:saving-monotonicity (savings, not kernels), pair_saving.json (savings only); none gives a, b
or I for pairs.
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

SRC = ROOT / 'research/results/common_multiplier_linear_sizes_20261017'
spec = importlib.util.spec_from_file_location('linear_sizes', SRC / 'linear_sizes.py')
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)
tq, dl = ls.tq, ls.dl
N = 3


def parse(name, v):
    return 0 if name == '1' else 1 << v(int(name[1]), int(name[2]))


def measure(cC, cH, monos, W, reps, E1, E2):
    J = dl.ann_poly(cC, monos, E1) & dl.ann_poly(cC, monos, E2)
    h1 = [dl.ann_poly(cH, monos, E1 ^ s) for _, s in reps]
    h2 = [dl.ann_poly(cH, monos, E2 ^ s) for _, s in reps]
    a = max(len((x & y) + W) for x, y in itertools.product(h1, h2))
    a2 = max(len((x + W) & (y + W)) for x, y in itertools.product(h1, h2))
    total = tq.Space() + W
    for x, y in itertools.product(h1, h2):
        total = total + (x & y)
    S1, S2 = tq.Space() + W, tq.Space() + W
    for x in h1:
        S1 = S1 + x
    for y in h2:
        S2 = S2 + y
    I = S1 & S2
    out = {'J': len(J), 'a': a, 'a2': a2, 'b': len(total), 'I': len(I)}
    assert a <= out['b'] <= out['J'] and a <= a2 <= out['I'] <= out['J'], f'containments {out}'
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    mono, full, nv, v = tq.systems(N + 1, N)
    cC = tq.prepare(pc.Closure(full, nv, 2))
    cH = tq.prepare(pc.Closure(mono, nv, 2))
    monos = [x for x in cC.monos if tq.deg(x) <= 1]
    W = tq.members(cC, monos)
    assert len(W) == 4, f'control: dim W = {len(W)}'
    assert len(dl.ann_poly(cC, monos, {parse('x00', v)})) == 9, 'control: x00'
    Q = [{0} | {1 << v(i, j) for j in range(N)} for i in range(N + 1)]
    reps = ls.representatives(Q)
    span_Q = {frozenset(s) for _, s in reps}
    hits = json.loads((SRC / 'row_search.json').read_text())['4x3 rows [1, 2]']['first']
    assert len(hits) == 10
    errors = [{parse(t, v) for t in E} for E in hits]
    rows, dist = [], {}
    for i, j in itertools.combinations(range(10), 2):
        congruent = frozenset(errors[i] ^ errors[j]) in span_Q
        r = measure(cC, cH, monos, W, reps, errors[i], errors[j])
        if congruent:
            assert r['J'] == 7 == r['I'], f'positive control {r}'
        rows.append({'pair': [hits[i], hits[j]], 'congruent': congruent, **r})
        key = f"{'congruent' if congruent else 'other'} J={r['J']} a={r['a']} a2={r['a2']} b={r['b']} I={r['I']}"
        dist[key] = dist.get(key, 0) + 1
    out = {'dim_V1': len(monos), 'dim_W': len(W), 'distribution': dist, 'pairs': rows}
    print(json.dumps(dist), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
