"""Universal completion at the goal's box levels: a failure certificate on random samples.

Statement tested (the hypothesis of the entry's sufficiency proposition, at finite sizes): at (4,4),
X N i.i.d. uniform points of [0,1]^2 and Y evenly spread (one point uniform in each cell of a
sqrt(N) x sqrt(N) grid), G_k the pairs with |X^j - Y^j| <= L k^(1/4) sqrt(log N/N) in both
coordinates, k = 1, 2, ...: at every level k with m_k > m_(k+1), every maximum matching of G_k has a
matching of G_(k+1) inside its leftover with m_k - m_(k+1) edges (universal completion, C = 1).

Certificate of failure (the entry's lemma): at a level with m_k > m_(k+1), let D_Y be the Y-vertices
some maximum matching of G_k misses (reached from a free Y-vertex by an alternating path) and B_X the
X-vertices with a G_(k+1)-neighbour in D_Y. If B_X is matchable in G_k, a maximum matching of G_k
covers B_X (matroid extension), its X-leftover avoids B_X and its Y-leftover lies in D_Y, so the
leftover spans no edge of G_(k+1) and universal completion fails. Symmetrically with D_X and B_Y.
A second sufficient test (a reviewer's, unverified before this run): every leftover lies in
D_X u D_Y, so nu(G_(k+1)[D_X u D_Y]) < m_k - m_(k+1) forces failure.

Each sample runs levels k = 1..60 and stops at the first drop level where a test fires (one failing
level decides universal completion for the sample), or at m = 0; levels after a firing are not
computed, and a sample reaching k = 60 with no firing is reported undecided.

Expected (written before the run): at each sample with a drop, the certificate fires at some drop
level, most often at the lowest ones, where the deficient regions are wide against the next box.
Refuted by: a sample with a drop level at which neither certificate nor the second test fires.
Possible because: the certificate is only sufficient, and deficient regions narrower than the next
box would put every co-basis within reach of the other side.

Control: soundness on tiny instances, n = 4 and 5 points per side on a line with radius levels,
where every maximum matching is enumerated and universal completion decided by brute force; the
certificate must never fire where universal completion holds.
Refuted by: an instance where the certificate fires and the brute-force check finds completion.
Possible because: an error in the alternating reachability or in the matchability test would show
there.
Decisive at these sizes: each sample is decided on its own (a firing certifies failure there), so
no spread between seeds enters; what the sizes cannot decide is the limit, which no run reaches.
Parallel use: the samples run in a pool of 12 worker processes, one thread each.
Forced by counts: on the gadget the counts force only the drop (nu = 1 at radius 1, 2 at e), and on
the tiny instances only which ones have a drop; whether a test fires depends on which vertices are
missable, which no count fixes, so neither control is decided by its counts.
Positive control: the line gadget X = {0, 1.6}, Y = {0.8, 3.5} at radii 1 and e, where universal
completion fails (research/results/ultimate_matching_local_completion_20261017/gadget.txt); the
certificate must fire there.
Refuted by: the certificate not firing on the gadget.
Possible because: a wrong orientation of D_Y or B_X would miss it.
Baseline: the deficiencies alone decide nothing on the quantifier (a drop is necessary, not
sufficient for failure); thm:universal-completion-criterion (c) excludes the line's mechanism, small
isolated components, at these scales for L > 1/sqrt(2).
Record checked: thm:universal-completion-criterion (a)-(c), thm:local-completion-dichotomy (f) and
thm:per-level-count-matchings, searched in the words "universal completion every maximum matching
box levels deficiency" and "matroid extension maximum matching covering set leftover": none decides
the outcome at the box levels.
"""
import argparse
import itertools
import json
import math

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree
import ctypes
import os
import subprocess

# SciPy's maximum_bipartite_matching ran over 60 s on a level-2 graph of 4096 + 4096 vertices and
# 46810 edges (18 October 2026, cause not diagnosed); a compiled Hopcroft-Karp kernel replaces it,
# checked against networkx in the controls.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SO = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'box_completion_hk.so')
subprocess.run(['g++', '-O2', '-shared', '-fPIC', '-o', _SO, os.path.join(_HERE, 'hk.cpp')], check=True)
_hk = ctypes.CDLL(_SO).hk
_IP = ctypes.POINTER(ctypes.c_int)
_hk.argtypes = [ctypes.c_int, ctypes.c_int, _IP, _IP, _IP, _IP]
_hk.restype = ctypes.c_int


def maximum_bipartite_matching(A, perm_type='column'):
    """Mate (column) of each row, -1 when free: the compiled Hopcroft-Karp kernel."""
    A = csr_matrix(A)
    A.sort_indices()
    indptr = np.ascontiguousarray(A.indptr, dtype=np.int32)
    indices = np.ascontiguousarray(A.indices, dtype=np.int32)
    mx = np.empty(A.shape[0], dtype=np.int32)
    my = np.empty(A.shape[1], dtype=np.int32)
    _hk(A.shape[0], A.shape[1], indptr.ctypes.data_as(_IP), indices.ctypes.data_as(_IP),
        mx.ctypes.data_as(_IP), my.ctypes.data_as(_IP))
    return mx.astype(np.int64)


def graph(X, Y, r):
    """Biadjacency (rows X, columns Y) of the pairs within r in both coordinates."""
    pairs = cKDTree(X).query_ball_tree(cKDTree(Y), r, p=np.inf)
    rows = np.repeat(np.arange(len(X)), [len(p) for p in pairs])
    cols = np.fromiter(itertools.chain.from_iterable(pairs), dtype=np.int64, count=len(rows))
    return csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(len(X), len(Y)))


def match(A):
    """Maximum matching: mate of each row (-1 free) and of each column."""
    rmate = maximum_bipartite_matching(A, perm_type='column')
    cmate = np.full(A.shape[1], -1)
    cmate[rmate[rmate >= 0]] = np.nonzero(rmate >= 0)[0]
    return rmate, cmate


def missable_columns(A, rmate, cmate):
    """Columns left free by some maximum matching: reached from a free column by an alternating path."""
    AT = A.T.tocsr()
    reached = cmate < 0
    frontier = reached.copy()
    while frontier.any():
        rows = (AT[frontier].sum(axis=0).A1 > 0)  # rows adjacent to the frontier columns
        nxt = np.zeros_like(reached)
        mates = rmate[rows]
        nxt[mates[mates >= 0]] = True  # their partners (a free row here would augment)
        frontier = nxt & ~reached
        reached |= nxt
    return reached


def certificate(Ak, Ak1):
    """Return (fires, details) for the failure certificate at a level, given G_k and G_(k+1)."""
    rmate, cmate = match(Ak)
    nu = int((rmate >= 0).sum())
    DY = missable_columns(Ak, rmate, cmate)
    AkT = Ak.T.tocsr()
    DX = missable_columns(AkT, cmate, rmate)
    BX = (Ak1[:, DY].sum(axis=1).A1 > 0)
    BY = (Ak1[DX, :].sum(axis=0).A1 > 0)
    nuBX = int((maximum_bipartite_matching(Ak[BX], perm_type='column') >= 0).sum()) if BX.any() else 0
    nuBY = int((maximum_bipartite_matching(AkT[BY], perm_type='column') >= 0).sum()) if BY.any() else 0
    sub = Ak1[DX][:, DY]
    nuD = int((maximum_bipartite_matching(sub, perm_type='column') >= 0).sum()) if sub.nnz else 0
    return nu, dict(DX=int(DX.sum()), DY=int(DY.sum()), BX=int(BX.sum()), nuBX=nuBX,
                    BY=int(BY.sum()), nuBY=nuBY, nuD=nuD,
                    cert=bool(nuBX == BX.sum() or nuBY == BY.sum()))


def brute_universal(adj_k, adj_k1, n):
    """Universal completion at one level by enumerating every maximum matching (tiny n)."""
    def matchings(adj):
        edges = [(i, j) for i in range(n) for j in range(n) if adj[i][j]]
        best, found = 0, [()]
        for size in range(1, n + 1):
            cur = [c for c in itertools.combinations(edges, size)
                   if len({e[0] for e in c}) == size and len({e[1] for e in c}) == size]
            if not cur:
                break
            best, found = size, cur
        return best, found
    nu_k, maxk = matchings(adj_k)
    nu_k1, _ = matchings(adj_k1)
    d = nu_k1 - nu_k
    for M in maxk:
        ux = [i for i in range(n) if i not in {e[0] for e in M}]
        uy = [j for j in range(n) if j not in {e[1] for e in M}]
        sub = [[adj_k1[i][j] for j in uy] for i in ux]
        best = 0
        for size in range(1, min(len(ux), len(uy)) + 1):
            if any(all(sub[a][b] for a, b in zip(rows, cols))
                   for rows in itertools.combinations(range(len(ux)), size)
                   for cols in itertools.permutations(range(len(uy)), size)):
                best = size
        if best < d:
            return False
    return True


def line_instance(x, y, radii):
    X = np.column_stack([x, np.zeros(len(x))])
    Y = np.column_stack([y, np.zeros(len(y))])
    return [graph(X, Y, r) for r in radii]


def controls(rng):
    out = {}
    gk, gk1 = line_instance([0, 1.6], [0.8, 3.5], [1.0, math.e])
    nu, det = certificate(gk, gk1)
    out['gadget'] = dict(nu_k=nu, **det)
    sound = dict(instances=0, drops=0, universal_fails=0, cert_fires=0, cert_fires_where_holds=0,
                 nuD_fires=0, nuD_fires_where_holds=0)
    for n, reps in ((4, 1500), (5, 300)):
        for _ in range(reps):
            x, y = rng.uniform(0, n, n), rng.uniform(0, n, n)
            gk, gk1 = line_instance(x, y, [1.0, math.e])
            nu_k, det = certificate(gk, gk1)
            nu_k1 = int((maximum_bipartite_matching(gk1, perm_type='column') >= 0).sum())
            sound['instances'] += 1
            if nu_k1 == nu_k:
                continue
            sound['drops'] += 1
            ak = (gk.toarray() > 0).tolist()
            ak1 = (gk1.toarray() > 0).tolist()
            holds = brute_universal(ak, ak1, n)
            sound['universal_fails'] += (not holds)
            sound['cert_fires'] += det['cert']
            sound['cert_fires_where_holds'] += (det['cert'] and holds)
            nuD = det['nuD'] < nu_k1 - nu_k
            sound['nuD_fires'] += nuD
            sound['nuD_fires_where_holds'] += (nuD and holds)
    out['soundness'] = sound
    import networkx as nx
    agree = 0
    for rep in range(200):
        n = int(rng.integers(20, 200))
        A = csr_matrix((rng.random((n, n)) < rng.uniform(0.005, 0.05)).astype(np.int8))
        G = nx.algorithms.bipartite.from_biadjacency_matrix(A)
        ref = len(nx.bipartite.maximum_matching(G, top_nodes=range(n))) // 2
        agree += int((maximum_bipartite_matching(A) >= 0).sum()) == ref
    out['kernel_against_networkx'] = dict(graphs=200, agree=agree)
    return out


def sample(N, L, seed):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 1, (N, 2))
    g = int(round(math.sqrt(N)))
    assert g * g == N
    cells = np.stack(np.meshgrid(np.arange(g), np.arange(g), indexing='ij'), -1).reshape(-1, 2)
    Y = (cells + rng.uniform(0, 1, (N, 2))) / g
    s1 = math.sqrt(math.log(N) / N)
    levels, prev = [], None
    for k in range(1, KMAX + 1):
        A = graph(X, Y, L * k ** 0.25 * s1)
        m = N - int((maximum_bipartite_matching(A, perm_type='column') >= 0).sum())
        levels.append(dict(k=k, m=m))
        if prev is not None and levels[-2]['m'] > m:
            _, det = certificate(prev, A)
            det['nuD_below_drop'] = det['nuD'] < levels[-2]['m'] - m
            levels[-2].update(det)
            if det['cert'] or det['nuD_below_drop']:
                break  # one failing level decides the sample
        if m == 0:
            break
        prev = A
    return levels


KMAX = 60  # levels tried per sample; a sample stopped here with no firing is reported as undecided
WORKERS = 12  # one process per sample, one thread each


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--sizes', type=int, nargs='+', default=[4096, 16384, 65536])
    args = ap.parse_args()
    result = dict(controls=controls(np.random.default_rng(20261018)), samples=[])
    c = result['controls']
    assert c['gadget']['cert'], c['gadget']
    assert c['soundness']['cert_fires_where_holds'] == 0, c['soundness']
    assert c['soundness']['nuD_fires_where_holds'] == 0, c['soundness']
    assert c['kernel_against_networkx']['agree'] == 200, c['kernel_against_networkx']
    print('controls', json.dumps(c))
    jobs = [(N, L, seed) for N in args.sizes for L in (0.5, 1.0) for seed in range(3)]
    from multiprocessing import Pool
    with Pool(min(WORKERS, len(jobs))) as pool:
        runs = pool.starmap(sample, [(N, L, 1000 * N + 10 * int(2 * L) + seed) for N, L, seed in jobs])
    for (N, L, seed), lv in zip(jobs, runs):
        if True:
            if True:
                drops = [v for v in lv if 'cert' in v]
                rec = dict(N=N, L=L, seed=seed, levels=lv,
                           drop_levels=len(drops),
                           cert_levels=sum(v['cert'] for v in drops),
                           nuD_levels=sum(v['nuD_below_drop'] for v in drops))
                result['samples'].append(rec)
                print(N, L, seed, 'm by level', [v['m'] for v in lv], 'drops', rec['drop_levels'],
                      'certified', rec['cert_levels'], 'nuD test', rec['nuD_levels'], flush=True)
                with open(args.out, 'w') as f:
                    json.dump(result, f, indent=1)


if __name__ == '__main__':
    main()
