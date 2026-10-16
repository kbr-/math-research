"""Smallest case of the next attempt: do top-degree extra killers give a joint saving beyond the domain model?

System: functional pigeonhole over F_2, 4 pigeons, 3 holes, multilinear, D=2=ceil(3/2) (the top), K=1. Errors:
the first 10 of the 12 errors with positive excess that row_search.py found on rows {1,2} (row_search.json
lists ten), all 45 pairs.
For a pair (E1, E2) the saving modulo C is rank1 + rank2 - stacked rank = dim V_1 - dim(Ann_C(E1) + Ann_C(E2)).
The domain saving is the largest, over pairs of linear representatives, of dim V_1 - dim(A1 + A2), where
Ai = Ann_H(Ei') + C cap V_1; with Ann_C(Ei) containing Ai, the C-saving is at most this, so the comparison asks
how much smaller it is: the gap is domain saving minus C-saving, and a gap of 0 means the extra killers keep
the domain saving.
Statement tested: the untested hypothesis that the extra killers leave the joint saving at the domain model's
value (gap 0) for every pair.
Expected: no expectation is predicted; the script prints the distribution of (C-saving, domain saving).
Refuted by: some pair with a positive gap, where the extra killers lower the saving below the domain model.
Possible because: Ann_C(E1) + Ann_C(E2) can exceed every A1 + A2 by the extra killers of each error.
Control: the pair (x00, x11), monomial errors on distinct cells, must give gap 0 (lem:functional-killer-transfer
at this size: its kernels are the domain model's).
Refuted by: a positive gap for (x00, x11).
Possible because: a bug in the sum of spaces or the representative loop would show one.
Positive control: a pair (E, E) of a hit error has C-saving dim V_1 - dim Ann_C(E) and domain saving one more,
since Ann_C(E) exceeds every A by one dimension, so its gap is the single excess 1; asserted.
Refuted by: a gap other than 1 for (E, E).
Possible because: a bug in the pair maximum over representatives.
Baseline: the summed-rank bound gives saving at most min(rank1, rank2); it decides nothing.
Record checked: the claims read were ex:support-saving-not-inherited (a domain saving lost at 4x3, D=3),
lem:functional-killer-transfer and check:dense-linear-kernels; none decides these pairs.
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

spec = importlib.util.spec_from_file_location('linear_sizes', pathlib.Path(__file__).with_name('linear_sizes.py'))
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)
tq, dl = ls.tq, ls.dl
N = 3


def parse(name, v):
    if name == '1':
        return 0
    return 1 << v(int(name[1]), int(name[2]))


def pair(cC, cH, monos, C1, reps, E1, E2):
    dimV = len(monos)
    c_saving = dimV - len(dl.ann_poly(cC, monos, E1) + dl.ann_poly(cC, monos, E2))
    k1 = [dl.ann_poly(cH, monos, E1 ^ s) + C1 for _, s in reps]
    k2 = [dl.ann_poly(cH, monos, E2 ^ s) + C1 for _, s in reps]
    d_saving = max(dimV - len(a + b) for a, b in itertools.product(k1, k2))
    return c_saving, d_saving


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    mono, full, nv, v = tq.systems(N + 1, N)
    cC = tq.prepare(pc.Closure(full, nv, 2))
    cH = tq.prepare(pc.Closure(mono, nv, 2))
    monos = [x for x in cC.monos if tq.deg(x) <= 1]
    C1 = tq.members(cC, monos)
    Q = [{0} | {1 << v(i, j) for j in range(N)} for i in range(N + 1)]
    reps = ls.representatives(Q)
    hits = json.loads(pathlib.Path(__file__).with_name('row_search.json').read_text())['4x3 rows [1, 2]']['first']
    assert len(hits) == 10, 'row_search.json lists the first ten of its twelve hits'
    errors = [{parse(t, v) for t in E} for E in hits]
    ctrl = pair(cC, cH, monos, C1, reps, {parse('x00', v)}, {parse('x11', v)})
    assert ctrl[1] - ctrl[0] == 0, 'control'
    same = pair(cC, cH, monos, C1, reps, errors[0], errors[0])
    assert same[1] - same[0] == 1, 'positive control'
    rows = []
    for a, b in itertools.combinations(range(len(errors)), 2):
        cs, ds = pair(cC, cH, monos, C1, reps, errors[a], errors[b])
        rows.append({'pair': [hits[a], hits[b]], 'C_saving': cs, 'domain_saving': ds, 'gap': ds - cs})
    dist = {}
    for r in rows:
        dist[f"{r['C_saving']},{r['domain_saving']}"] = dist.get(f"{r['C_saving']},{r['domain_saving']}", 0) + 1
    out = {'control': ctrl, 'same_pair': same, 'pairs': rows, 'distribution (C_saving,domain_saving)': dist}
    print('control', ctrl, 'same', same, 'distribution', dist, flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
