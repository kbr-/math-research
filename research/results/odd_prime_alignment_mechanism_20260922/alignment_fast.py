"""Same graded alignment test as research/results/odd_prime_kernel_alignment_20260921/alignment.py
(same graphs, good monomials, block kinds and deterministic seeds), with bit-sliced GF(3)
elimination in C (gf3.c), a chunked old-relation basis built in the parent with OpenMP, and a
sparse normal form into quotient coordinates. Workers use the serial library.
Usage: python3 alignment_fast.py --config NAME --out PATH [--workers 14] [--trials-square T]
"""
import argparse, json, os, sys, zlib
import numpy as np, scipy.sparse as sp
from multiprocessing import get_context
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_kernel_alignment_20260921'))
import alignment as A, gf3

def sparse_rows(G, qf):
    """Rows q*y_m over all multipliers m, as a CSR matrix over matching monomials."""
    r, c, v = [], [], []; n = len(G['mons']); k = 0
    for m in G['mults']:
        ms = set(m); acc = {}
        for (u, w), coef in qf.items():
            if u in ms or w in ms: continue
            j = G['idx'].get(tuple(sorted(ms | {u, w})))
            if j is not None: acc[j] = (acc.get(j, 0) + coef) % 3
        acc = {j: x for j, x in acc.items() if x}
        if acc:
            r += [k] * len(acc); c += list(acc); v += list(acc.values()); k += 1
    return sp.csr_matrix((np.array(v, dtype=np.int32), (r, c)), shape=(k, n))

CTX = {}
def prepare(name, cfg):
    N, d, k, seed, _ = cfg
    G = A.build(N, d, k, seed); n = len(G['mons'])
    T = sp.vstack([sparse_rows(G, q) for q in G['quads']]).tocsr() if G['quads'] else sp.csr_matrix((0, n))
    E = np.zeros((0, 2 * ((n + 63) // 64)), dtype=np.uint64); W = (n + 63) // 64
    for lo in range(0, T.shape[0], 4096):
        P, W = gf3.pack(T[lo:lo + 4096].toarray() % 3)
        E, W, piv = gf3.rref(None, full=True, parallel=True, packed=(np.vstack([E, P]), W, n))
    piv = list(piv) if T.shape[0] else []
    free = np.array(sorted(set(range(n)) - set(piv)), dtype=np.int64)
    EF = gf3.unpack(E, W, n)[:, free].astype(np.int32) if len(piv) else np.zeros((0, len(free)), np.int32)
    C = dict(G=G, n=n, q=len(free), free=free, piv=np.array(piv, dtype=np.int64), EF=EF)
    Wm = sp.csr_matrix((np.ones(len(G['good']), dtype=np.int32),
                        (np.arange(len(G['good'])), [G['idx'][m] for m in G['good']])), shape=(len(G['good']), n))
    C['Wq'] = nf(C, Wm); C['wp'] = gf3.rank(C['Wq'], parallel=True)
    return C

def nf(C, S):
    out = np.zeros((S.shape[0], C['q']), dtype=np.uint8)
    for lo in range(0, S.shape[0], 1024):
        X = S[lo:lo + 1024]
        Y = X[:, C['free']].toarray().astype(np.int64)
        if len(C['piv']): Y = Y - (X[:, C['piv']] @ C['EF'])
        out[lo:lo + 1024] = np.mod(Y, 3).astype(np.uint8)
    return out

def job(args):
    name, h, kind, t = args
    C = CTX[name]; G = C['G']; s = G['s']
    rng = np.random.default_rng(zlib.crc32(f'{name}|{h}|{kind}|{t}'.encode()))
    rows = []
    for _ in range(h):
        if kind == 'generic':
            qf = {(u, v): int(rng.integers(0, 3)) for u in range(s) for v in range(u + 1, s)}
        else:
            a_ = rng.integers(0, 3, size=s)
            qf = {(u, v): int(a_[u] * a_[v] % 3) for u in range(s) for v in range(u + 1, s)}
        rows.append(sparse_rows(G, {e: c for e, c in qf.items() if c}))
    Jq = nf(C, sp.vstack(rows).tocsr())
    Jb, W, pj = gf3.rref(Jq); beta = len(pj)
    Wm = rng.integers(0, 3, size=(C['wp'], C['q'])).astype(np.uint8) if kind == 'randomW' else C['Wq']
    wimg = gf3.rank(Wm)
    Wp, _ = gf3.pack(Wm)
    both = gf3.rref(None, packed=(np.vstack([Wp, Jb]), W, C['q']))[2].shape[0]
    actual = wimg + beta - both
    return dict(config=name, h=h, kind=kind, trial=t, beta=beta, w_image=wimg, actual=actual,
                predicted=max(0, wimg + beta - C['q']))

CONFIGS = {'check': {'N8d4k4': (8, 4, 4, 5, 2)}, 'd5': {'N8d5k4': (8, 5, 4, 7, 16)}}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True)
    ap.add_argument('--config', default='d5'); ap.add_argument('--workers', type=int, default=14)
    a = ap.parse_args(); jobs = []; summary = {}
    for name, cfg in CONFIGS[a.config].items():
        C = prepare(name, cfg); CTX[name] = C; m = len(C['G']['mults'])
        hs = list(range(max(1, (C['q'] - C['wp']) // m - 1), C['q'] // max(1, m - 2) + 3))
        summary[name] = dict(N=cfg[0], d=cfg[1], k=cfg[2], seed=cfg[3], s=C['G']['s'], matching_monomials=C['n'],
                             q=C['q'], w_image=C['wp'], good=len(C['G']['good']), multipliers=m, h_sweep=hs)
        print(name, summary[name], flush=True)
        ctl = max(2, cfg[4] // 4)
        jobs += [(name, h, 'square', t) for h in hs for t in range(cfg[4])]
        jobs += [(name, h, kind, t) for h in hs for kind in ('generic', 'randomW') for t in range(ctl)]
    print('jobs', len(jobs), flush=True)
    with get_context('fork').Pool(a.workers) as P:
        rows = P.map(job, jobs, chunksize=1)
    json.dump(dict(summary=summary, rows=rows), open(a.out, 'w'), indent=1)
    for r in rows:
        if r['actual'] > r['predicted']: print(r)
