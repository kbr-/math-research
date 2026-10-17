"""cor:linear-error-transfer against the recorded positive excesses at four holes.

check:top-degree-partition-kernels recorded, on the functional pigeonhole system with 5 pigeons and 4 holes at
D=2, K=1 (D = ceil(4/2), inside the corollary's range), single linear errors on two rows whose C-kernel exceeds
every linear representative's domain side plus C cap V_1. The corollary claims, for every linear error whose edge
set meets (i)-(iii) under some numbering, that the C-kernel equals the trivial representative's domain side plus
C cap V_1, which is stronger than the best-representative form. So an error meeting the criterion with positive
trivial-representative excess refutes the corollary.
Statement tested: for every linear error E = c + sum over a set of edges of pigeons 1 and 2 (any of the 2^9
choices of constant and edge set), if some numbering meets (i)-(iii) for E's edges, then
dim Ann_C(E) cap V_1 = dim(Ann_H(E) cap V_1 + C cap V_1). The extreme the question needs: a universal over
errors, so every error on the two rows is tried, and every hole order and pigeon order is searched for the
criterion.
Expected: no counterexample (the corollary's proof).
Refuted by: an error meeting the criterion with C-kernel larger than its domain side plus C cap V_1.
Possible because: the recorded positive excesses are errors on two rows at this size, and the proof may have a gap.
Control: the recorded count is reproduced: errors with positive trivial-representative excess exist on these two
rows (the record found 12 of 127 two-row errors with best-representative excess 1, so at least that many have
trivial-representative excess >= 1).
Refuted by: no positive trivial-representative excess at all, which would mean the code cannot see the record's
excess.
Possible because: a wrong board, degree or row choice.
Forced by counts: no count forces the outcome; each kernel is computed.
Positive control: the record's excess, as above, must be seen.
Baseline: the domain side plus C cap V_1 is always inside the C-kernel, so the excess is >= 0; nothing plainer
decides it.
Record checked: check:top-degree-partition-kernels (the excesses), ex:top-degree-linear-killer (an excess at three
holes), conj:representative-sum-transfer; none says which errors meet the criterion.
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
spec = importlib.util.spec_from_file_location(
    'dense_linear', ROOT / 'research/results/common_multiplier_dense_linear_20261016/dense_linear.py')
dl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dl)
spec = importlib.util.spec_from_file_location(
    'linear_criterion', ROOT / 'research/results/common_multiplier_linear_numbering_20261017/linear_criterion.py')
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)

M, N, D = 5, 4, 2


def meets(S):
    """Whether some numbering meets (i)-(iii) for the edge set S on M pigeons and N holes."""
    for ho in itertools.permutations(range(N)):
        hr = {h: k for k, h in enumerate(ho)}
        if any(hr[h] == N - 1 for _, h in S):
            continue
        firsts = {p for p, h in S if hr[h] == N - 2}
        lasts = {p for p, h in S if hr[h] == N - 3}
        if len(firsts) <= 1 and len(lasts) <= 1 and not (firsts and lasts and firsts == lasts):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    mono, full, nv, v = tq.systems(M, N)
    cC = tq.prepare(pc.Closure(full, nv, D))
    cH = tq.prepare(pc.Closure(mono, nv, D))
    assert cC.proper
    monos = [m for m in cC.monos if tq.deg(m) <= 1]
    C1 = tq.members(cC, monos)
    x = lambda i, j: 1 << v(i, j)
    edges = [(i, j) for i in (1, 2) for j in range(N)]
    rows = []
    for c in (0, 1):
        for k in range(1, len(edges) + 1):
            for S in itertools.combinations(edges, k):
                E = ({0} if c else set()) | {x(i, j) for i, j in S}
                aC = len(dl.ann_poly(cC, monos, E))
                aH = len(dl.ann_poly(cH, monos, E) + C1)
                rows.append({'constant': c, 'edges': S, 'excess': aC - aH, 'meets': meets(S)})
    positive = [r for r in rows if r['excess'] > 0]
    bad = [r for r in rows if r['excess'] > 0 and r['meets']]
    out = {'errors': len(rows), 'positive_excess': len(positive), 'meeting_criterion': sum(r['meets'] for r in rows),
           'counterexamples': bad[:10], 'counterexample_count': len(bad)}
    assert positive, 'positive control: the record found positive excess on two rows here'
    print(json.dumps({k: v for k, v in out.items() if k != 'counterexamples'}), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1, default=list) + '\n')


if __name__ == '__main__':
    main()
