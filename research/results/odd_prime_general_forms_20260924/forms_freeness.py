"""Freeness of the weak algebra without row sums over arbitrary linear forms, over F_3.

Tested statement (thm:general-forms-freeness): with g = floor(N/(2t-1)) column groups, the m*g grouped row
sums l_{b,G} = sum_{j in G} x_bj make A~ (m rows, N columns) free through t over u(W) = F_3[W]/(w^3); so
general forms (outside a proper closed set) of any number d <= m*g are free through t. Free through t
means HF(A~/(forms)A~)_k = [q^k](1+mq)^N/(1+q+q^2)^d for k <= t (openness lemma, cover form).
Also records, for comparison only, the largest d at which seeded uniformly random F_3 forms are free
(random F_3 forms are not general in the Zariski sense), and the positivity bound on d.
Ranks: research/tools/rank_modp.cpp. Usage: python3 forms_freeness.py OUT.json"""
import itertools, json, sys, time
from math import comb
import numpy as np
sys.path.insert(0, 'research/tools')
from rank_modp import rank_mod_p

def basis(N, m, k):
    return [(S, lab) for S in itertools.combinations(range(N), k) for lab in itertools.product(range(m), repeat=k)]

def hf_quotient(N, m, k, forms):
    """forms: list of arrays a[j][b] (N x m) over F_3."""
    if k == 0: return 1
    tgt = {b: i for i, b in enumerate(basis(N, m, k))}; rows = []
    for a in forms:
        nz = [(j, b, int(a[j][b])) for j in range(N) for b in range(m) if a[j][b] % 3]
        for S, lab in basis(N, m, k - 1):
            full = dict(zip(S, lab)); row = {}
            for j, b, v in nz:
                if j in full: continue
                g = dict(full); g[j] = b; T = tuple(sorted(g))
                c = tgt[(T, tuple(g[x] for x in T))]; row[c] = (row.get(c, 0) + v) % 3
            rows.append(row)
    return len(tgt) - rank_mod_p(rows, len(tgt), 3)

def pred(N, m, d, t):
    hs = [comb(N, k) * m ** k for k in range(t + 1)]
    inv = [{0: 1, 1: -1, 2: 0}[k % 3] for k in range(t + 1)]; ser = [1] + [0] * t
    for _ in range(d): ser = [sum(ser[a] * inv[k - a] for a in range(k + 1)) for k in range(t + 1)]
    return [sum(hs[a] * ser[k - a] for a in range(k + 1)) for k in range(t + 1)]

def free_through(N, m, forms, t):
    P = pred(N, m, len(forms), t); hf = []
    for k in range(t + 1):
        hf.append(hf_quotient(N, m, k, forms))
        if hf[-1] != P[k]: return k - 1, hf, P[:k + 1]
    return t, hf, P

def grouped(N, m, t):
    g = N // (2 * t - 1); size = 2 * t - 1; forms = []
    for G in range(g):
        cols = range(G * size, (G + 1) * size) if G < g - 1 else range(G * size, N)
        for b in range(m):
            a = np.zeros((N, m), dtype=int)
            for j in cols: a[j][b] = 1
            forms.append(a)
    return forms

def main():
    out = {'grouped': [], 'random': [], 'failures': []}; t0 = time.time()
    for m, N, t in [(1, 6, 2), (2, 6, 2), (3, 6, 2), (1, 10, 3), (2, 10, 3), (1, 9, 2), (2, 9, 2)]:
        F = grouped(N, m, t); ft, hf, P = free_through(N, m, F, t)
        rec = {'m': m, 'N': N, 't': t, 'd': len(F), 'free_through': ft, 'hf': hf, 'pred': P}
        out['grouped'].append(rec); print('grouped', json.dumps(rec), flush=True)
        if ft < t: out['failures'].append(('grouped', m, N, t))
    rng = np.random.default_rng(20260924)
    for m, N, t in [(2, 6, 2), (3, 6, 2), (2, 9, 2), (2, 9, 3), (1, 10, 3), (2, 10, 3)]:
        g = N // (2 * t - 1); pos = max(d for d in range(0, 60) if min(pred(N, m, d, t)) >= 0)
        rows = []
        for d in range(1, pos + 2):
            F = [rng.integers(0, 3, (N, m)) for _ in range(d)]
            ft, hf, P = free_through(N, m, F, t); rows.append({'d': d, 'free_through': ft, 'hf': hf, 'pred': P})
        best = max([r['d'] for r in rows if r['free_through'] >= t], default=0)
        rec = {'m': m, 'N': N, 't': t, 'theorem_d': m * g, 'positivity_d': pos, 'largest_free_random_d': best, 'rows': rows}
        out['random'].append(rec); print('random', m, N, t, 'theorem', m * g, 'positivity', pos, 'random best', best, flush=True)
    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(sys.argv[1], 'w'), indent=1); print('failures', out['failures'], 'seconds', out['seconds'])

if __name__ == '__main__':
    main()
