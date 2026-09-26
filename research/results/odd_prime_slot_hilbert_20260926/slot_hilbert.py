"""Hilbert function of the falsifying set of an F_3 line in the cube (odd-prime thread, 26 Sept 2026).

Quantity (the per-slot restriction rank of the subspace criterion at p = 3, prop:no-sound-subflat-choice):
for r random dense affine forms L_1..L_r over F_3 on v Boolean variables, Z = {x in {0,1}^v : L_i(x) != 0 for
all i}, HF(Z, k) = rank over F_3 of the evaluation matrix of all multilinear monomials of degree <= k on Z.
Compared with: full = sum_{j<=k} C(v, j); the F_2 slot bound for a flat of codimension r,
flat = sum_{j<=k} C(v - r, j); the criterion's p = 3 slot bound 2^r * flat; and the number of quadric
multiples r * sum_{j<=k-2} C(v, j), and quadric_span, the exact dimension of their span as functions on the cube
(each multiple has degree <= k and vanishes on Z, so quadric_span <= removed = full - HF).
Rank by the recorded bit-sliced GF(3) elimination (gf3, OpenMP).
Usage: slot_hilbert.py --vs 12,14,16 --ks 2,3,4 --rs 2,4,6,8 --seeds 2 --out FILE"""
import argparse, itertools, json, os, sys, time
from math import comb
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3


def cube(v):
    return ((np.arange(2 ** v)[:, None] >> np.arange(v)[None, :]) & 1).astype(np.uint8)


def eval_matrix(pts, v, k):
    cols = [np.ones(len(pts), dtype=np.uint8)]
    for j in range(1, k + 1):
        cols.extend(pts[:, list(c)].prod(axis=1).astype(np.uint8) for c in itertools.combinations(range(v), j))
    return np.stack(cols, axis=1)


def run_case(v, k, r, seed, pts_all):
    rng = np.random.default_rng(seed)
    A = rng.integers(0, 3, size=(r, v)); b = rng.integers(0, 3, size=r)
    vals = (pts_all.astype(np.int64) @ A.T + b) % 3
    Z = pts_all[(vals != 0).all(axis=1)]
    full = sum(comb(v, j) for j in range(k + 1))
    flat = sum(comb(v - r, j) for j in range(k + 1))
    hf = int(gf3.rank(eval_matrix(Z, v, k), parallel=True)) if len(Z) else 0
    # span of the quadric multiples m * ((L_i)^2 - 1), deg m <= k - 2, as functions on the whole cube
    q = ((vals.astype(np.int64) ** 2 - 1) % 3).astype(np.uint8)          # (points, r)
    low = eval_matrix(pts_all, v, k - 2) if k >= 2 else np.zeros((len(pts_all), 0), np.uint8)
    rows = np.concatenate([(low * q[:, [i]]) % 3 for i in range(r)], axis=1).T.astype(np.uint8)
    qspan = int(gf3.rank(rows, parallel=True)) if rows.size else 0
    return dict(v=v, k=k, r=r, seed=seed, rank_forms=int(np.linalg.matrix_rank(A)), points=int(len(Z)),
                full=full, hf=hf, removed=full - hf, f2_flat=flat, f2_removed=full - flat,
                slot_bound_p3=min(full, 2 ** r * flat), quadric_multiples=r * sum(comb(v, j) for j in range(k - 1)),
                quadric_span=qspan)


ap = argparse.ArgumentParser()
ap.add_argument('--vs', default='12'); ap.add_argument('--ks', default='2,3'); ap.add_argument('--rs', default='2,4')
ap.add_argument('--seeds', type=int, default=2); ap.add_argument('--out', required=True); opt = ap.parse_args()
cases = [(v, k, r, s) for v in map(int, opt.vs.split(',')) for k in map(int, opt.ks.split(','))
         for r in map(int, opt.rs.split(',')) for s in range(opt.seeds)]
res = []; t0 = time.time(); cubes = {}
for v, k, r, s in cases:
    if v not in cubes:
        cubes[v] = cube(v)
    res.append(run_case(v, k, r, 1000 * v + 10 * r + s, cubes[v]))
    print(json.dumps(res[-1]), f'({time.time()-t0:.0f}s)', flush=True)
    json.dump(res, open(opt.out, 'w'), indent=1)
