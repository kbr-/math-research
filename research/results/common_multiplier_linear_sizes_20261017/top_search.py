"""Does the extra killer persist at the top degree D = ceil(n/2) for more holes? Partition errors.

System: functional pigeonhole over F_2, n+1 pigeons, n holes, multilinear. row_search.json found linear errors
with positive excess at D=2, K=1 for n = 3, 4 (where D = 2 = ceil(n/2), the top of the basis range) and none for
n = 5 (D = 2 below the top 3); the errors found include E_A = sum_{j in A} x1j + sum_{j not in A} x2j.
By the hole symmetry the excess of E_A depends only on |A|, so |A| = 0..n covers the family.
Question: at the top degree with K = D - 1, that is n = 5, D = 3, K = 2, is the excess of some E_A positive?
The excess is dim(Ann_C(E) cap V_K) minus the max over the 2^m linear representatives E' of
dim(Ann_H(E') cap V_K + C cap V_K).
Statement tested: the untested hypothesis that the extra killers persist at the top degree, giving an unbounded
family (a positive excess at n = 5); its negation is that they need D = 2.
Expected: no expectation is predicted; the script prints each |A| with its excess.
Refuted by: excess 0 for every |A| at n = 5, which refutes persistence for this family at this size.
Possible because: the n = 3, 4 excess may come from an accident of degree 2 rather than of the top degree.
Control: at n = 3 and n = 4, D = 2, K = 1, some E_A must have positive excess (as row_search.json found).
Refuted by: no E_A with positive excess there, contradicting row_search.json.
Possible because: the K-general kernel code or the partition indexing could differ from row_search.py.
Positive control: the n = 3, 4 control is the positive control; the effect is present there by row_search.json.
Decisive at these sizes: one |A| with positive excess decides the question; exhaustive over |A|, no seeds.
Parallel use: fourteen worker processes, one per (n, |A|, representative chunk) task, one thread each.
Baseline: the bare count bounds each excess by dim V_K minus the domain part; it decides nothing.
Record checked: the claims read were conj:linear-kernel-transfer, check:dense-linear-kernels,
check:functional-kernels-k2 (variables at K=2 on this board, excess 0) and lem:closure-degree-locality; none
decides partition errors at the top degree.
"""
import argparse
import importlib.util
import json
import multiprocessing
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import pc_closure as pc

spec = importlib.util.spec_from_file_location('linear_sizes', pathlib.Path(__file__).with_name('linear_sizes.py'))
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)
tq, dl = ls.tq, ls.dl

CASES = ((3, 2, 1), (4, 2, 1), (5, 3, 2))       # (n, D, K)
CACHE = {}


def setup(n, D, K):
    key = (n, D, K)
    if key not in CACHE:
        m = n + 1
        mono, full, nv, v = tq.systems(m, n)
        cC = tq.prepare(pc.Closure(full, nv, D))
        cH = tq.prepare(pc.Closure(mono, nv, D))
        assert cC.proper
        monos = [x for x in cC.monos if tq.deg(x) <= K]
        CK = tq.members(cC, monos)
        Q = [{0} | {1 << v(i, j) for j in range(n)} for i in range(m)]
        CACHE[key] = (cC, cH, monos, CK, ls.representatives(Q), v)
    return CACHE[key]


def error(n, a, v):
    return {1 << v(1, j) for j in range(a)} | {1 << v(2, j) for j in range(a, n)}


def task(args):
    """('C', n, D, K, a) gives the C-side; ('H', n, D, K, a, lo, hi) the best domain side over reps lo..hi."""
    kind, n, D, K, a = args[:5]
    cC, cH, monos, CK, reps, v = setup(n, D, K)
    E = error(n, a, v)
    if kind == 'C':
        return len(dl.ann_poly(cC, monos, E))
    lo, hi = args[5:]
    return max(len(dl.ann_poly(cH, monos, E ^ s) + CK) for _, s in reps[lo:hi])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    pool = multiprocessing.Pool(14)
    out = {}
    for n, D, K in CASES:
        r = 2 ** (n + 1)
        step = max(1, r // 8)
        cside = pool.map(task, [('C', n, D, K, a) for a in range(n + 1)])
        parts = pool.map(task, [('H', n, D, K, a, lo, lo + step) for a in range(n + 1) for lo in range(0, r, step)])
        per = r // step
        rows = []
        for a in range(n + 1):
            best = max(parts[a * per:(a + 1) * per])
            rows.append({'|A|': a, 'C_side': cside[a], 'best_H_side': best, 'excess': cside[a] - best})
        out[f'{n + 1}x{n} D={D} K={K}'] = rows
        print(f'{n + 1}x{n} D={D} K={K}', [(x['|A|'], x['excess']) for x in rows], flush=True)
        pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
        if n < 5:
            assert any(x['excess'] > 0 for x in rows), 'control: an E_A with positive excess at D=2'


if __name__ == '__main__':
    main()
