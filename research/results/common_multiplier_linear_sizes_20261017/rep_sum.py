"""Are the top-degree extra killers sums of domain killers of several representatives?

System: functional pigeonhole over F_2, n+1 pigeons, n holes, multilinear. Cases: 4x3 at D=2, K=1 with the ten
listed hit errors of row_search.json; 6x5 at D=3, K=2 with the partition errors E_A, |A| = 2, 3 (top_search.json,
excess 12). For an error E, let S(E) be the sum over all 2^m linear representatives E' of Ann_H(E') cap V_K,
plus C cap V_K. Each summand lies in Ann_C(E), so S(E) is inside it; the excess of top_search.json uses one
representative at a time.
Question (from pair_saving.py, whose positive control failed in log exceptional-products-1327a09273 because the
domain minimum may pair two different representatives): is Ann_C(E) cap V_K = S(E)?
Statement tested: the untested hypothesis that the extra killers are sums of domain killers of representatives:
dim Ann_C(E) = dim S(E) for every error listed.
Expected: no expectation is predicted; the script prints dim Ann_C, the best single representative, dim S.
Refuted by: dim S(E) < dim Ann_C(E) for some listed error, a killer no sum of domain kernels gives.
Possible because: the 4x3 identity uE = x10 Q_2 + x21 Q_1 uses two pigeon axioms at once, which a single
representative's domain kernel need not split.
Control: for x00 at 4x3, S equals Ann_C (single excess 0 already); asserted.
Refuted by: dim S(x00) different from dim Ann_C(x00) = 9.
Possible because: a bug in the space sum or in the representatives.
Positive control: S(E) must be at least the best single representative's domain side for every error; asserted.
Refuted by: dim S below the best single side, which a correct sum cannot give.
Possible because: a bug in the sum of spaces.
Baseline: the single-representative excess (top_search.json) bounds dim Ann_C - dim S above; it decides nothing.
Decisive at these sizes: one error with dim S below dim Ann_C decides; exact, no seeds involved here.
Parallel use: fourteen worker processes over the 6x5 representative chunks, one thread each.
Record checked: the claims read were conj:linear-kernel-transfer, check:dense-linear-kernels and
lem:closure-degree-locality; none decides sums over representatives.
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
CACHE = {}


def setup(n, D, K):
    if (n, D, K) not in CACHE:
        mono, full, nv, v = tq.systems(n + 1, n)
        cC = tq.prepare(pc.Closure(full, nv, D))
        cH = tq.prepare(pc.Closure(mono, nv, D))
        monos = [x for x in cC.monos if tq.deg(x) <= K]
        CK = tq.members(cC, monos)
        Q = [{0} | {1 << v(i, j) for j in range(n)} for i in range(n + 1)]
        CACHE[(n, D, K)] = (cC, cH, monos, CK, ls.representatives(Q), v)
    return CACHE[(n, D, K)]


def part(args):
    """The sum of domain kernels over representatives lo..hi, as basis vectors, and the best single side."""
    n, D, K, E, lo, hi = args
    cC, cH, monos, CK, reps, v = setup(n, D, K)
    total, best = tq.Space(), 0
    for _, s in reps[lo:hi]:
        k = dl.ann_poly(cH, monos, set(E) ^ s)
        best = max(best, len(k + CK))
        total = total + k
    return list(total.basis.values()), best


def measure(pool, n, D, K, E):
    cC, cH, monos, CK, reps, v = setup(n, D, K)
    r = len(reps)
    step = max(1, r // 14)
    parts = pool.map(part, [(n, D, K, sorted(E), lo, lo + step) for lo in range(0, r, step)])
    S = tq.Space([x for vecs, _ in parts for x in vecs]) + CK
    best = max(b for _, b in parts)
    annC = len(dl.ann_poly(cC, monos, set(E)))
    assert len(S) >= best, 'positive control: the sum contains each single side'
    return {'C_side': annC, 'best_single': best, 'rep_sum': len(S), 'unexplained': annC - len(S)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {}
    with multiprocessing.Pool(14) as pool:
        v3 = setup(3, 2, 1)[5]
        name = lambda t: 0 if t == '1' else 1 << v3(int(t[1]), int(t[2]))
        ctrl = measure(pool, 3, 2, 1, {name('x00')})
        assert ctrl['rep_sum'] == ctrl['C_side'] == 9, 'control'
        out['4x3 x00'] = ctrl
        hits = json.loads(pathlib.Path(__file__).with_name('row_search.json').read_text())['4x3 rows [1, 2]']['first']
        for h in hits:
            out['4x3 ' + '+'.join(h)] = measure(pool, 3, 2, 1, {name(t) for t in h})
        print('4x3', [(k, r['C_side'], r['best_single'], r['rep_sum']) for k, r in out.items()], flush=True)
        pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
        v5 = setup(5, 3, 2)[5]
        for a in (2, 3):
            E = {1 << v5(1, j) for j in range(a)} | {1 << v5(2, j) for j in range(a, 5)}
            out[f'6x5 |A|={a}'] = measure(pool, 5, 3, 2, E)
            print(f'6x5 |A|={a}', out[f'6x5 |A|={a}'], flush=True)
            pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
