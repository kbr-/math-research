"""Graded alignment test for ternary selector blocks against the good-matching space.

Graded ring A = F3[y]/(y_u^2) on the s nondistinguished cells of a random d-neighbour graph PHP
(N holes, N+1 rows, first neighbour distinguished). A homogeneous degree-k weight f in W (span of
good matching monomials) can lie in a block's Macaulay kernel Mac_k + I_k only if f lies in
J_k = T_k + sum_i tau_i A_{k-2}, tau_i the degree-two part of the i-th input, T_k spanned by the
old degree-two top forms times A_{k-2}. Every monomial containing a same-row or same-hole pair
lies in T_k, so we work in Q' = span of matching monomials (independent sets of the collision
graph) and add the remaining old top forms: y_u * (cells of row i) for u in hole p_i, and the
product of the cell sums of two rows with the same distinguished hole.

For each block, in Q = A_k/T_k: q = dim Q, w' = dim image(W), beta = dim image(J_k); reports the
actual dim(image W cap image J) and the general-position prediction max(0, w'+beta-q).
Kinds: 'square' (tau = l^2, l uniform), 'generic' (uniform quadratic form), 'randomW' (control:
W replaced by a uniform random subspace of dimension w'). The h sweep covers the nonvacuous band
q-w' < beta < q. Jobs run in parallel worker processes (default 14, one thread each).
Usage: python3 alignment.py --config NAME --out PATH [--workers 14]
"""
import argparse, itertools, json, os, zlib
import numpy as np
from multiprocessing import get_context

def rref3(M):
    M = (M % 3).astype(np.uint8); rows, cols = M.shape; r = 0
    for c in range(cols):
        if r == rows: break
        piv = np.nonzero(M[r:, c])[0]
        if len(piv) == 0: continue
        p = r + piv[0]
        if p != r: M[[r, p]] = M[[p, r]]
        if M[r, c] == 2: M[r, c:] = (M[r, c:] * 2) % 3
        nz = np.nonzero(M[r + 1:, c])[0] + r + 1
        if len(nz):
            f = (3 - M[nz, c]).astype(np.uint8)[:, None]
            M[nz, c:] = (M[nz, c:] + f * M[r, c:]) % 3
        r += 1
    return M[:r]

def full_rref3(M):
    """Reduced row echelon form mod 3 and pivot columns; rows compressed by random projection."""
    M = (M % 3).astype(np.uint8); rows, cols = M.shape
    if rows > cols + 40:
        R = np.random.default_rng(99).integers(0, 3, size=(cols + 40, rows)).astype(np.float64)
        M = ((R @ M.astype(np.float64)) % 3).astype(np.uint8)
    E = rref3(M); piv = []
    for r in range(E.shape[0]):
        c = int(np.nonzero(E[r])[0][0]); piv.append(c)
        if E[r, c] == 2: E[r] = (E[r] * 2) % 3
    for r in range(E.shape[0] - 1, -1, -1):
        c = piv[r]; above = np.nonzero(E[:r, c])[0]
        if len(above):
            f = (3 - E[above, c]).astype(np.uint8)[:, None]
            E[above] = (E[above] + f * E[r]) % 3
    return E, piv

def rank3(M):
    if not M.shape[0]: return 0
    rows, cols = M.shape
    if rows > cols + 40:
        R = np.random.default_rng(7).integers(0, 3, size=(cols + 40, rows)).astype(np.float64)
        M = ((R @ (M % 3).astype(np.float64)) % 3).astype(np.uint8)
    return rref3(M).shape[0]

def nf(C, M):
    """Normal form modulo T in quotient coordinates (non-pivot columns)."""
    if not M.shape[0]: return np.zeros((0, len(C['free'])), dtype=np.uint8)
    M = M.astype(np.float64)
    if C['Tb'].shape[0]:
        M = M - M[:, C['piv']] @ C['Tb'].astype(np.float64)
    return (np.mod(M, 3)[:, C['free']]).astype(np.uint8)

def build(N, d, k, seed):
    rng = np.random.default_rng(seed)
    nb = [[int(x) for x in rng.choice(N, size=d, replace=False)] for _ in range(N + 1)]
    dist = [r[0] for r in nb]
    cells = [(i, h) for i in range(N + 1) for h in nb[i][1:]]
    s = len(cells)
    coll = lambda u, v: cells[u][0] == cells[v][0] or cells[u][1] == cells[v][1]
    def indep(m): return all(not coll(u, v) for u, v in itertools.combinations(m, 2))
    mons = [m for m in itertools.combinations(range(s), k) if indep(m)]
    idx = {m: j for j, m in enumerate(mons)}
    mults = [m for m in itertools.combinations(range(s), k - 2) if indep(m)]
    rowcells = {i: [u for u, c in enumerate(cells) if c[0] == i] for i in range(N + 1)}
    quads = []
    for u in range(s):
        for i in range(N + 1):
            if i != cells[u][0] and dist[i] == cells[u][1]:
                quads.append({tuple(sorted((u, v))): 1 for v in rowcells[i]})
    for i in range(N + 1):
        for i2 in range(i + 1, N + 1):
            if dist[i] == dist[i2]:
                quads.append({tuple(sorted((v, v2))): 1 for v in rowcells[i] for v2 in rowcells[i2]})
    good = []
    for m in mons:
        rs = [cells[u][0] for u in m]
        hs = [cells[u][1] for u in m] + [dist[r] for r in rs]
        if len(set(rs)) == k and len(set(hs)) == 2 * k: good.append(m)
    return dict(s=s, mons=mons, idx=idx, mults=mults, quads=quads, good=good)

def times(G, q, out):
    n = len(G['mons'])
    for m in G['mults']:
        ms = set(m); row = np.zeros(n, dtype=np.uint8); nz = False
        for (u, v), c in q.items():
            if u in ms or v in ms: continue
            j = G['idx'].get(tuple(sorted(ms | {u, v})))
            if j is None: continue
            row[j] = (row[j] + c) % 3; nz = True
        if nz: out.append(row)

CTX = {}

def prepare(item):
    name, (N, d, k, seed, trials) = item
    G = build(N, d, k, seed); n = len(G['mons'])
    Tr = []
    for q in G['quads']: times(G, q, Tr)
    if Tr: Tb, piv = full_rref3(np.array(Tr, dtype=np.uint8))
    else: Tb, piv = np.zeros((0, n), dtype=np.uint8), []
    free = [c for c in range(n) if c not in set(piv)]
    C = dict(G=G, Tb=Tb, piv=piv, free=free, n=n, q=len(free))
    W = np.zeros((len(G['good']), n), dtype=np.uint8)
    for a_, m in enumerate(G['good']): W[a_, G['idx'][m]] = 1
    C['Wq'] = nf(C, W); C['wp'] = rank3(C['Wq'])
    return name, C

def job(args):
    name, h, kind, t = args
    C = CTX[name]; G = C['G']; s = G['s']
    rng = np.random.default_rng(zlib.crc32(f'{name}|{h}|{kind}|{t}'.encode()))
    forms = []
    B = []
    for _ in range(h):
        if kind == 'generic':
            qf = {(u, v): int(rng.integers(0, 3)) for u in range(s) for v in range(u + 1, s)}
        else:
            a_ = rng.integers(0, 3, size=s); forms.append([int(x) for x in a_])
            qf = {(u, v): int(a_[u] * a_[v] % 3) for u in range(s) for v in range(u + 1, s)}
        times(G, {e: c for e, c in qf.items() if c}, B)
    Jq = nf(C, np.array(B, dtype=np.uint8)) if B else np.zeros((0, C['q']), dtype=np.uint8)
    Jb = rref3(Jq) if Jq.shape[0] <= Jq.shape[1] + 40 else rref3(((np.random.default_rng(5).integers(0, 3, size=(Jq.shape[1] + 40, Jq.shape[0])).astype(np.float64) @ Jq.astype(np.float64)) % 3).astype(np.uint8))
    beta = Jb.shape[0]
    Wm = rng.integers(0, 3, size=(C['wp'], C['q'])).astype(np.uint8) if kind == 'randomW' else C['Wq']
    wimg = rank3(Wm)
    actual = wimg + beta - rank3(np.vstack([Wm, Jb]))
    out = dict(config=name, h=h, kind=kind, trial=t, beta=beta, w_image=wimg, actual=actual,
               predicted=max(0, wimg + beta - C['q']))
    if kind == 'square':
        out['beta_per_form'] = [rank3(nf(C, np.array(r, dtype=np.uint8))) for r in
                                [_rows(G, f) for f in forms]]
        if actual > out['predicted']: out['forms'] = forms
    return out

def _rows(G, a_):
    s = G['s']; B = []
    times(G, {(u, v): int(a_[u] * a_[v] % 3) for u in range(s) for v in range(u + 1, s)
              if a_[u] * a_[v] % 3}, B)
    return B if B else [np.zeros(len(G['mons']), dtype=np.uint8)]

CONFIGS = {
    'band': {'N6d4k3': (6, 4, 3, 1, 6), 'N8d4k3': (8, 4, 3, 2, 4)},
    'k4many': {'N8d4k4': (8, 4, 4, 5, 20), 'N9d4k4': (9, 4, 4, 6, 12)},
    'all': {'N6d4k3': (6, 4, 3, 1, 6), 'N8d4k3': (8, 4, 3, 2, 4), 'N8d4k4': (8, 4, 4, 5, 4),
            'N9d4k4': (9, 4, 4, 6, 3)},
}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True)
    ap.add_argument('--config', default='band'); ap.add_argument('--workers', type=int, default=14)
    ap.add_argument('--count-only', action='store_true'); a = ap.parse_args()
    jobs = []; summary = {}
    items = list(CONFIGS[a.config].items())
    with get_context('fork').Pool(min(a.workers, len(items))) as P:
        prepared = P.map(prepare, items, chunksize=1)
    for (name, cfg), (_, C) in zip(items, prepared):
        CTX[name] = C
        m = len(C['G']['mults'])
        hs = list(range(max(1, (C['q'] - C['wp']) // m - 1), C['q'] // max(1, m - 2) + 3))
        summary[name] = dict(N=cfg[0], d=cfg[1], k=cfg[2], seed=cfg[3], s=C['G']['s'],
                             matching_monomials=C['n'], q=C['q'], w_image=C['wp'],
                             good=len(C['G']['good']), multipliers=m, h_sweep=hs)
        print(name, summary[name], flush=True)
        jobs += [(name, h, kind, t) for h in hs for kind in ('square', 'generic', 'randomW')
                 for t in range(cfg[4])]
    print('jobs', len(jobs), flush=True)
    if not a.count_only:
        with get_context('fork').Pool(a.workers) as P:
            rows = P.map(job, jobs, chunksize=1)
        json.dump(dict(summary=summary, rows=rows), open(a.out, 'w'), indent=1)
        for r in rows:
            if r['actual'] != r['predicted'] or 0 < r['predicted'] < r['w_image']:
                print(r)
