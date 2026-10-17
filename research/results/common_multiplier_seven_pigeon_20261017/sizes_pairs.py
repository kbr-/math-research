"""The window review's Decisive test: partition errors of every size at n holes and n + 1 pigeons, D = ceil(n/2),
K = D - 1, singles first, then pairs.

Reuses research/results/common_multiplier_route_review_20261017/mixing_pairs_65.py's functions with its board set
by --holes. For each |A| up to n/2 (the pigeon swap sends E_A to E_{A^c}), the single error E_A with A an initial
segment: its closure kernel, its best single representative's domain side plus W, and the sum over its
representatives of their domain kernels plus W (the excess is closure kernel minus best single). Then for every
size pair whose both sizes have positive excess, one pair per orbit of (|A|, |B|, |A cap B|) under the holes'
symmetry, not congruent (B not the complement of A), the quantities J, a, b, I of mixing_pairs_65.py.
Statement tested: the window review's Prediction at n = 6 (seven pigeons, six holes, D = 3, K = 2): outcomes
(a) single excess 0 at |A| = 2 (and at |A| = 1), (b) dim J = a on every orbit, (c) a < b = dim J, (d) b < dim J on
some orbit, (e) a single kernel above its representative sum.
Expected: no outcome is predicted. The run at n = 4 (five pigeons, four holes) is the smallest size, run first for
the plumbing, and must reproduce mixing_pairs_54.json (single 8 at |A| = 2; J = 6, a = b = 5, I = 6 on the
overlap-1 orbit) and check:top-degree-partition-kernels' excesses at n = 4 (0, 0, 1 by |A| = 0, 1, 2).
Refuted by: at n = 6, any outcome of (a)-(e) is possible; at n = 4, a figure different from the recorded ones.
Possible because: at n = 6 the record has no single excess at |A| = 1, 2.
Control: at n = 4 the recorded figures above; asserted when --holes 4.
Refuted by: a different figure at n = 4.
Possible because: a changed setup or a wrong orbit choice would change them.
Forced by counts: nothing forces them; they are computed.
Positive control: the n = 4 overlap-1 orbit has b < dim J (mixing_pairs_54.json), so the run sees an intersection
kernel where one is known; asserted when --holes 4.
Refuted by: b = dim J there.
Possible because: a broken sum or intersection would hide it.
Baseline: a <= b <= I <= dim J; the excess is at least 0; neither decides the outcome.
Decisive at these sizes: exact dimensions, no seeds; one dimension decides each comparison.
Parallel use: fourteen worker processes over the first error's representatives, one thread each; the serial
closure setup at n = 6 took about five minutes in mixing_pairs_76.json's run.
Record checked: the claims read were check:top-degree-partition-kernels, conj:representative-sum-transfer and
check:representative-intersection-kernels; none gives the n = 6 single excesses at |A| = 1, 2.
"""
import argparse
import importlib.util
import itertools
import json
import math
import multiprocessing
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / 'research/results/common_multiplier_route_review_20261017/mixing_pairs_65.py'
spec = importlib.util.spec_from_file_location('mixing_pairs_65', SRC)
mp = importlib.util.module_from_spec(spec)
sys.modules['mixing_pairs_65'] = mp     # so the pool's worker function pickles
spec.loader.exec_module(mp)


def single(size):
    st = mp.setup()
    E = mp.error(tuple(range(size)))
    C_side = len(mp.dl.ann_poly(st['cC'], st['monos'], E))
    kernels = mp.domain_kernels(E)
    best = max(len(k + st['W']) for k in kernels)
    rep_sum = len(mp.summed(kernels, st['W']))
    return {'size': size, 'C_side': C_side, 'best_single': best, 'rep_sum': rep_sum, 'excess': C_side - best}


def orbits(sizes, n):
    out = {}
    for s, t in itertools.combinations_with_replacement(sizes, 2):
        A = tuple(range(s))
        for B in itertools.combinations(range(n), t):
            complement = set(B) == set(range(n)) - set(A)
            if B != A and not complement:
                out.setdefault((s, t, len(set(A) & set(B))), (A, B))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--holes', type=int, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--pair-all', action='store_true',
                    help='pair every size from 1 to n/2, not only those with positive single excess: zero excess '
                         'gives Ann_C(E) = U + W, but an intersection with another kernel can still exceed the sum '
                         'over representative pairs (the reviewer, 17 October 2026)')
    ap.add_argument('--skip-singles', action='store_true', help='singles already in sizes_pairs_n6.json')
    ap.add_argument('--known', type=int, default=None,
                    help='a size whose pairs with itself were already computed (mixing_pairs_76.json: 3 at n = 6)')
    args = ap.parse_args()
    n = args.holes
    mp.N, mp.D = n, math.ceil(n / 2)
    mp.K = mp.D - 1
    t0 = time.time()
    st = mp.setup()
    out = {'holes': n, 'D': mp.D, 'K': mp.K, 'dim_V': len(st['monos']), 'dim_W': len(st['W']),
           'setup_seconds': round(time.time() - t0, 1), 'singles': [], 'pairs': []}
    for size in ([] if args.skip_singles else range(n // 2 + 1)):
        out['singles'].append(single(size))
        print(json.dumps(out['singles'][-1]), flush=True)
        pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
    if n == 4 and not args.skip_singles:
        assert [r['excess'] for r in out['singles']] == [0, 0, 1], f"control: excesses {out['singles']}"
        assert out['singles'][2]['C_side'] == 8, 'control: single kernel at |A| = 2'
    if args.pair_all:
        positive = list(range(1, n // 2 + 1))
    else:
        positive = [r['size'] for r in out['singles'] if r['excess'] > 0]
    with multiprocessing.Pool(14) as pool:
        for key, (A, B) in sorted(orbits(positive, n).items()):
            if args.known is not None and key[0] == key[1] == args.known:
                continue
            r = mp.measure_orbit(pool, key, A, B)
            out['pairs'].append(r)
            print(json.dumps(r), flush=True)
            pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
    if n == 4 and args.known != 2:     # with --known 2 the control's orbit is skipped (the reviewer found the
        # first version indexing an empty list there, so that run, sizes_pairs_n4_known.json, could not pass)
        one = [r for r in out['pairs'] if tuple(r['sizes_and_overlap']) == (2, 2, 1)][0]
        assert (one['J'], one['a'], one['b'], one['I']) == (6, 5, 5, 6), f'control: {one}'
        assert one['b'] < one['J'], 'positive control'


if __name__ == '__main__':
    main()
