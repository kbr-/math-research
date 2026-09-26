#!/usr/bin/env python3
"""Reduced homology over F_3 of matching complexes M(G[S]) of row sets S of a bipartite graph.

Tests conj:graph-matching-connectivity: if every U within the s-row set S has |N(U)| >= 3|U| (and every row has
degree 5), then H~_{s-2}(M(G[S]); F_3) = 0, the condition under which the matching extension of the complete board
(BLVZ chessboard connectivity, N >= 2s-1) transfers to graph boards row set by row set. Faces are partial matchings
(sets of cells with distinct rows and distinct holes). Samples: random 5-subsets of h holes per row, filtered by the
expansion condition, with h chosen near 3s to force overlaps; plus the tightest case |N(S)| = 3s.
Exact GF(3) ranks by FLINT nmod_mat_rank (rank_mod3.c, built to $RANK_BIN), validated against the NumPy
reference elimination rank3 on every sample with s <= 3.
"""
import itertools, json, os, subprocess, sys
import numpy as np
sys.path.insert(0, '/home/kbr/dev/math-auxiliary/research/results/odd_prime_dense_review_20260926')
from restricted_span import rank3

rng = np.random.default_rng(20260926)

def faces_by_dim(nbrs):
    rows = range(len(nbrs)); out = {}
    def rec(i, used_rows, used_holes, face):
        if face:
            out.setdefault(len(face) - 1, []).append(tuple(face))
        for r in range(i, len(nbrs)):
            for t in nbrs[r]:
                if t not in used_holes:
                    rec(r + 1, used_rows | {r}, used_holes | {t}, face + [(r, t)])
    rec(0, frozenset(), frozenset(), [])
    return out

RANK_BIN = os.environ.get('RANK_BIN', '/home/kbr/.claude/jobs/d56a25e2/tmp/rank_mod3')


def flint_ranks(mats):
    """mats: list of (rows, cols, entries dict) -> ranks over F_3 from the FLINT helper."""
    lines = []
    for r, c, ent in mats:
        lines.append(f'{r} {c} {len(ent)}')
        lines.extend(f'{i} {j} {v}' for (i, j), v in ent.items())
    out = subprocess.run([RANK_BIN], input='\n'.join(lines) + '\n', capture_output=True, text=True, check=True)
    return [int(x) for x in out.stdout.split()]


def reduced_homology(nbrs, q, validate=False):
    F = faces_by_dim(nbrs)
    idx = {d: {f: i for i, f in enumerate(F.get(d, []))} for d in range(0, q + 2)}
    idx[-1] = {(): 0}
    def bd(d):   # boundary C_d -> C_{d-1}, sparse
        src = F.get(d, [])
        tgt = idx[d - 1]
        ent = {}
        for i, f in enumerate(src):
            for j in range(len(f)):
                key = (i, tgt[f[:j] + f[j + 1:]])
                ent[key] = (ent.get(key, 0) + (-1) ** j) % 3
        return len(src), len(tgt), {k: v for k, v in ent.items() if v}
    nq = len(F.get(q, []))
    mats = [bd(q), bd(q + 1)]
    rq, rq1 = flint_ranks(mats)
    if validate:
        dense = []
        for r, c, ent in mats:
            M = np.zeros((max(r, 1), max(c, 1)), dtype=np.int64)
            for (i, j), v in ent.items():
                M[i, j] = v
            dense.append(rank3(M) if r and c else 0)
        assert dense == [rq, rq1], (dense, rq, rq1)
    return nq - rq - rq1


def expands(nbrs, c=3):
    s = len(nbrs)
    for u in range(1, s + 1):
        for U in itertools.combinations(range(s), u):
            if len(set().union(*[nbrs[i] for i in U])) < c * u:
                return False
    return True

def main():
    res = []
    # controls: chessboard 3 x 4 (N < 2s-1) should have nonzero H_1; 2 rows with the same 5 holes: H_0 = 0
    ctrl = {'chessboard_3x4_H1': reduced_homology([frozenset(range(4))] * 3, 1, True),
            'chessboard_4x5_H2': reduced_homology([frozenset(range(5))] * 4, 2),
            'chessboard_3x5_H1': reduced_homology([frozenset(range(5))] * 3, 1, True),
            'two_rows_same_5_H0': reduced_homology([frozenset(range(5))] * 2, 0, True)}
    print(ctrl, flush=True)
    for s in (2, 3, 4, 5):
        for h in (3 * s, 3 * s + 2, 4 * s):
            if h < 5:
                continue
            tested = fails = 0
            tries = 0
            while tested < (60 if s < 5 else 30) and tries < 200000:
                tries += 1
                nbrs = [frozenset(rng.choice(h, size=5, replace=False).tolist()) for _ in range(s)]
                if not expands(nbrs):
                    continue
                tested += 1
                if reduced_homology(nbrs, s - 2, validate=(s <= 3)) != 0:
                    fails += 1
            res.append({'s': s, 'holes': h, 'tested': tested, 'nonzero_H_s-2': fails})
            print(res[-1], flush=True)
    if '--out' in sys.argv:
        json.dump({'samples': res, 'controls': ctrl}, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)

if __name__ == '__main__':
    main()
