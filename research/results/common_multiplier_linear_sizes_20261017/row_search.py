"""Does the 4x3 extra killer extend to more holes? Exhaustive search over errors on few pigeons' rows.

System: functional pigeonhole over F_2, n+1 pigeons, n holes, multilinear, D=2, K=1, which by
lem:closure-degree-locality is the case K=1 for linear errors below half the holes. At 4x3 (witness.json) the
error x10 + x21 + x22 has the extra killer 1 + x12 + x22, by the identity (1+x12+x22)(x10+x21+x22) = x10 Q_2 +
x21 Q_1 modulo the hole and functionality axioms; at n holes the same product leaves sum_{j!=k>=2} x1j x2k.
Question: for n = 4, 5, is there a linear error supported on the constant and the rows of pigeons {1,2} (n=4, 5)
or {0,1,2} (n=4) with a positive excess (C-side minus the best domain side over all linear representatives)?
Statement tested: the untested hypothesis that the 4x3 mechanism needs n = 3: no such error for n >= 4.
Expected: no expectation is predicted; the script counts errors with positive excess and prints the first ones.
Refuted by: a positive excess at n = 4 or 5, which would refute the hypothesis and start an unbounded family.
Possible because: other cancellations between pigeon axioms may cancel the leftover cross terms at larger n.
Control: at n = 3 the same search over rows {1,2} must find the witness error x10 + x21 + x22 (asserted).
Refuted by: the n = 3 search missing the witness, which would mean the search cannot see the mechanism.
Possible because: an enumeration or indexing error would skip it.
Positive control: the n = 3 control above is the positive control; the effect is present there by witness.json.
Decisive at these sizes: one error with positive excess decides it; the search is exhaustive, no seeds.
Parallel use: fourteen worker processes over chunks of the enumerated errors, one thread each.
Baseline: the bare count bounds each excess by mn + 1 - m minus the domain part; it decides nothing.
Record checked: the claims read were conj:linear-kernel-transfer (refuted at n=3 by witness.json),
check:dense-linear-kernels, lem:admissible-numbering-transfer and lem:closure-degree-locality; none decides it.
"""
import argparse
import importlib.util
import itertools
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


def excess(cC, cH, monos, C1, reps, E):
    annC = len(dl.ann_poly(cC, monos, E))
    best = max(len(dl.ann_poly(cH, monos, E ^ s) + C1) for _, s in reps)
    return annC - best


CACHE = {}


def setup(n):
    if n not in CACHE:
        m = n + 1
        mono, full, nv, v = tq.systems(m, n)
        cC = tq.prepare(pc.Closure(full, nv, 2))
        cH = tq.prepare(pc.Closure(mono, nv, 2))
        assert cC.proper
        monos = [x for x in cC.monos if tq.deg(x) <= 1]
        C1 = tq.members(cC, monos)
        assert len(C1) == m
        Q = [{0} | {1 << v(i, j) for j in range(n)} for i in range(m)]
        CACHE[n] = (cC, cH, monos, C1, ls.representatives(Q), v)
    return CACHE[n]


def chunk(task):
    """Errors whose first support bits are the given prefix; returns those with positive excess."""
    n, support, prefix = task
    cC, cH, monos, C1, reps, _ = setup(n)
    hits = []
    for rest in itertools.product((0, 1), repeat=len(support) - len(prefix)):
        E = {t for t, b in zip(support, prefix + rest) if b}
        if E:
            e = excess(cC, cH, monos, C1, reps, E)
            if e > 0:
                hits.append((sorted(E), e))
    return hits


def search(pool, n, pigeons, out):
    m = n + 1
    v = setup(n)[5]
    support = [0] + [1 << v(i, j) for i in pigeons for j in range(n)]
    split = min(6, len(support))
    tasks = [(n, support, p) for p in itertools.product((0, 1), repeat=split)]
    hits = [h for part in pool.map(chunk, tasks) for h in part]
    name = lambda mono: '1' if mono == 0 else '*'.join(f'x{k // n}{k % n}' for k in range(m * n) if mono >> k & 1)
    key = f'{m}x{n} rows {list(pigeons)}'
    out[key] = {'errors': 2 ** len(support) - 1, 'positive': len(hits),
                'max_excess': max([e for _, e in hits], default=0),
                'first': [[name(t) for t in E] for E, _ in hits[:10]]}
    print(key, out[key]['errors'], 'errors;', out[key]['positive'], 'with positive excess; first',
          out[key]['first'][:3], flush=True)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {}
    pool = multiprocessing.Pool(14)
    hits = search(pool, 3, (1, 2), out)
    witness = sorted({1 << 3, 1 << 7, 1 << 8})            # x10, x21, x22 at n = 3
    assert any(E == witness for E, _ in hits), 'control: the witness must be found at n = 3'
    for n, pigeons in ((4, (1, 2)), (5, (1, 2)), (4, (0, 1, 2))):
        search(pool, n, pigeons, out)
        pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
