"""Which forms put a single good monomial into J_4 (graded kernel test of the alignment entry).

For every square trial of alignment_k4many.json whose intersection exceeded general position,
regenerate the forms (deterministic seeds), list the good monomials m with y_m in J_4 (exact
membership against an echelon basis mod 3, in the quotient coordinates of alignment.py), and for
each such m test which single forms and pairs of forms already put y_m in J_4.
Records the forms' coefficients on the cells of m. Runs trials in parallel (14 workers).
Usage: python3 mechanism.py --out PATH
"""
import argparse, itertools, json, sys, zlib
import numpy as np
from multiprocessing import get_context
sys.path.insert(0, 'research/results/odd_prime_kernel_alignment_20260921')
import alignment as A

SRC = 'research/results/odd_prime_kernel_alignment_20260921/alignment_k4many.json'
CTX = {}

def reduce_vec(E, pivcols, v):
    v = v.copy() % 3
    for row, c in zip(E, pivcols):
        if v[c]: v = (v + (3 - v[c]) * row) % 3
    return v

def echelon(M):
    E = A.rref3(M)
    piv = [int(np.nonzero(r)[0][0]) for r in E]
    E = np.array([(r * (2 if r[c] == 2 else 1)) % 3 for r, c in zip(E, piv)], dtype=np.uint8) if len(E) else E
    return E, piv

def work(key):
    name, h, t = key
    C = CTX[name]; G = C['G']; s = G['s']
    rng = np.random.default_rng(zlib.crc32(f'{name}|{h}|square|{t}'.encode()))
    F = [rng.integers(0, 3, size=s) for _ in range(h)]
    rows = [np.array(A._rows(G, f), dtype=np.uint8) for f in F]
    subsets = [S for size in (1, 2) for S in itertools.combinations(range(h), size)] + [tuple(range(h))]
    basis = {S: echelon(A.nf(C, np.vstack([rows[i] for i in S]))) for S in subsets}
    E, piv = basis[tuple(range(h))]
    singles = []
    for j, m in enumerate(G['good']):
        v = C['Wq'][j]
        if reduce_vec(E, piv, v).any(): continue
        ok = [S for S in subsets[:-1] if not reduce_vec(*basis[S], v).any()]
        size = min((len(S) for S in ok), default=None)
        singles.append(dict(monomial=list(m), minimal_size_if_at_most_2=size,
                            sufficient_subsets=[list(S) for S in ok if len(S) == size] if size else [],
                            coeffs_on_cells=[[int(F[i][u]) for u in m] for i in range(h)]))
    return dict(config=name, h=h, trial=t, forms=[[int(x) for x in f] for f in F], singles=singles)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    R = json.load(open(SRC))
    keys = [(r['config'], r['h'], r['trial']) for r in R['rows']
            if r['kind'] == 'square' and r['actual'] > r['predicted']]
    est = sum((h + h * (h - 1) // 2 + 1) for _, h, _ in keys) * 3.0 / 14
    print(f'{len(keys)} trials, estimated about {est/60:.1f} min on 14 workers', flush=True)
    for name in sorted({k[0] for k in keys}):
        CTX[name] = A.prepare((name, A.CONFIGS['k4many'][name]))[1]
    with get_context('fork').Pool(14) as P:
        out = P.map(work, keys, chunksize=1)
    json.dump(out, open(a.out, 'w'), indent=1)
    for o in out:
        print(o['config'], o['h'], o['trial'], 'single good monomials in J:', len(o['singles']),
              'minimal subset sizes (None = needs 3+ forms):', sorted({str(x['minimal_size_if_at_most_2']) for x in o['singles']}))
