"""For single-form cases (one square l^2 puts a good monomial y_S into J_4), greedily find a
minimal set of degree-2 multipliers y_P with y_S in span{l^2 y_P} + T_4, and report l on the
cells of S and of the multipliers. Parallel over cases (14 workers).
Usage: python3 minimal.py --out PATH
"""
import argparse, json, sys
import numpy as np
from multiprocessing import get_context
sys.path.insert(0, 'research/results/odd_prime_kernel_alignment_20260921')
sys.path.insert(0, 'research/results/odd_prime_alignment_mechanism_20260922')
import alignment as A
from mechanism import echelon, reduce_vec
CTX = {}

def rows_for(G, f, mults):
    s = G['s']; q = {(u, v): int(f[u] * f[v] % 3) for u in range(s) for v in range(u + 1, s) if f[u] * f[v] % 3}
    out = []
    for m in mults:
        ms = set(m); row = np.zeros(len(G['mons']), dtype=np.uint8)
        for (u, v), c in q.items():
            if u in ms or v in ms: continue
            j = G['idx'].get(tuple(sorted(ms | {u, v})))
            if j is not None: row[j] = (row[j] + c) % 3
        out.append(row)
    return np.array(out, dtype=np.uint8)

def member(C, f, mults, v):
    if not mults: return not v.any()
    E, piv = echelon(A.nf(C, rows_for(C['G'], f, mults)))
    return not reduce_vec(E, piv, v).any()

def work(case):
    name, S, f = case
    C = CTX[name]; G = C['G']; j = G['good'].index(tuple(S)); v = C['Wq'][j]
    mults = list(G['mults'])
    assert member(C, f, mults, v)
    for m in list(mults):
        trial = [x for x in mults if x != m]
        if member(C, f, trial, v): mults = trial
    return dict(config=name, S=S, form=[int(x) for x in f], multipliers=[list(m) for m in mults],
                form_on_S=[int(f[u]) for u in S],
                form_on_multiplier_cells={str(u): int(f[u]) for m in mults for u in m})

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    R = json.load(open('research/results/odd_prime_alignment_mechanism_20260922/singles.json'))
    cases = []
    for o in R:
        for x in o['singles']:
            if x['minimal_size_if_at_most_2'] == 1:
                for S_ in x['sufficient_subsets']:
                    cases.append((o['config'], x['monomial'], o['forms'][S_[0]]))
    print(len(cases), 'single-form cases', flush=True)
    CTX['N8d4k4'] = A.prepare(('N8d4k4', A.CONFIGS['k4many']['N8d4k4']))[1]
    with get_context('fork').Pool(14) as P:
        out = P.map(work, cases, chunksize=1)
    json.dump(out, open(a.out, 'w'), indent=1)
    for o in out[:12]:
        print(o['S'], 'l on S', o['form_on_S'], 'multipliers', o['multipliers'])
