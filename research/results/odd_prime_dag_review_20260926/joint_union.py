"""Joint restriction test for the DAG-dag review (odd-prime thread, 26 Sept 2026).

Tested statement (the joint form of the subspace criterion's exclusion step): the criterion needs a nonzero
polynomial of degree <= k vanishing on the falsifying sets of all high-rank slots at once, that is on their
union. Quantity: vanish(S) = dim of multilinear polynomials of degree <= k vanishing on Z_1 u ... u Z_S,
= full - rank of the evaluation matrix on the union, for
  F_3: S random dense lines of r forms, Z_s = {L_{s,i}(x) != 0 for all i} (a union of up to 2^r flats);
  F_2: S random affine flats of codimension r in the cube (the F_2 falsifying sets), ranks over F_2.
Prediction (entry-2026-09-26-slot-hilbert): at F_3 a single slot keeps almost everything and vanishing
polynomials come from quadric multiples, so vanish(S) should drop to about r^S C(v,<=k-2S), zero once 2S > k;
at F_2 each flat kills few dimensions and vanish(S) stays positive for more slots.
Ranks: GF(3) by the recorded gf3 module, GF(2) by research/tools/rank_modp.py.
Usage: joint_union.py --vs 14,16 --ks 3,4 --rs 4,8 --smax 5 --seeds 2 --out FILE"""
import argparse, json, os, sys, time
from math import comb
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
import itertools
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import gf3
from rank_modp import rank_mod_p


def cube(v):  # as in odd_prime_slot_hilbert_20260926/slot_hilbert.py
    return ((np.arange(2 ** v)[:, None] >> np.arange(v)[None, :]) & 1).astype(np.uint8)


def eval_matrix(pts, v, k):  # as in slot_hilbert.py: all multilinear monomials of degree <= k
    cols = [np.ones(len(pts), dtype=np.uint8)]
    for j in range(1, k + 1):
        cols.extend(pts[:, list(c)].prod(axis=1).astype(np.uint8) for c in itertools.combinations(range(v), j))
    return np.stack(cols, axis=1)


def f3_masks(pts, v, r, S, rng):
    masks = []
    for _ in range(S):
        A = rng.integers(0, 3, size=(r, v)); b = rng.integers(0, 3, size=r)
        vals = (pts.astype(np.int64) @ A.T + b) % 3
        masks.append((vals != 0).all(axis=1))
    return masks


def f2_masks(pts, v, r, S, rng):
    masks = []
    while len(masks) < S:
        A = rng.integers(0, 2, size=(r, v)); c = rng.integers(0, 2, size=r)
        m = (((pts.astype(np.int64) @ A.T) % 2) == c).all(axis=1)
        if np.linalg.matrix_rank(A) == r and m.any():   # real rank is fine as a filter only; flats checked nonempty
            masks.append(m)
    return masks


def rank2(E):
    rows = [np.stack([np.nonzero(col)[0], np.ones(int(col.sum()), dtype=np.int64)], axis=1) for col in E.T]
    return rank_mod_p(rows, E.shape[0], 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vs', default='14'); ap.add_argument('--ks', default='3,4')
    ap.add_argument('--rs', default='4'); ap.add_argument('--smax', type=int, default=5)
    ap.add_argument('--seeds', type=int, default=2); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = []
    for v in map(int, a.vs.split(',')):
        pts = cube(v)
        for k in map(int, a.ks.split(',')):
            full = sum(comb(v, j) for j in range(k + 1))
            E = eval_matrix(pts, v, k)
            for r in map(int, a.rs.split(',')):
                for seed in range(a.seeds):
                    run_series(out, a, pts, E, v, k, r, full, seed)


def run_series(out, a, pts, E, v, k, r, full, seed):
    for field, maker in (('F3', f3_masks), ('F2', f2_masks)):
        rng = np.random.default_rng(100000 * v + 1000 * k + 100 * r + 10 * seed + (3 if field == 'F3' else 2))
        masks = maker(pts, v, r, a.smax, rng)
        union = np.zeros(len(pts), dtype=bool)
        for S, m in enumerate(masks, start=1):
            union |= m
            t0 = time.time()
            Eu = E[union]
            rk = int(gf3.rank(Eu, parallel=True)) if field == 'F3' else rank2(Eu)
            row = dict(field=field, v=v, k=k, r=r, seed=seed, S=S, union_points=int(union.sum()),
                       full=full, vanish=full - rk,
                       quadric_product_prediction=(sum(comb(v, j) for j in range(k - 2 * S + 1)) * r ** S
                                                   if field == 'F3' and k >= 2 * S else 0),
                       seconds=round(time.time() - t0, 2))
            out.append(row); print(json.dumps(row), flush=True)
            with open(a.out, 'w') as fh:
                json.dump(out, fh, indent=1)

if __name__ == '__main__':
    main()
