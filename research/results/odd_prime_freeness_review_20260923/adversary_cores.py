"""Minimal cores of the defects found by adversary.py: for each stored configuration with positive excess, the smallest
subfamilies S of constraints whose own quotient B/(P_b : b in S) (own prediction, truncated) has a defect by the family's
first defect degree; reports all minimal S with their span and whether the family itself has an overlapping quadruple."""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '..', 'odd_prime_low_density_20260923', 'products.py')).read()
exec(src.split("ap = argparse.ArgumentParser()")[0]); exec(src.split("opt = ap.parse_args(); rng = np.random.default_rng(opt.seed)")[1].split("res = []")[0])
out = []
import sys as _sys
for fn in _sys.argv[1:] or ('adversary_v8.json', 'adversary_v8_quadric.json'):
    d = json.load(open(os.path.join(HERE, fn))); v, M, K = d['v'], d['M'], d['K']; monc = [mons(v, k) for k in range(K + 1)]
    for run in d['runs']:
        mus = [np.array(m) for m in run['forms']]
        P = [polymul(polymul(lin(mus[2 * b]), lin(mus[2 * b])), polymul(lin(mus[2 * b + 1]), lin(mus[2 * b + 1]))) for b in range(M)]
        _, W = series_W(v, M, K); H = hilbert(v, P, K, monc); k0 = first_defect(H, W)
        if k0 is None: continue
        cores = []
        for s in range(1, M + 1):
            for S in itertools.combinations(range(M), s):
                _, WS = series_W(v, s, k0); HS = hilbert(v, [P[b] for b in S], k0, monc); kS = first_defect(HS, WS)
                if kS is not None and kS <= k0:
                    cores.append(dict(S=list(S), degree=kS, span=rank3([mus[2 * b + i] for b in S for i in (0, 1)])))
            if cores: break
        quad = min(rank3([mus[2 * b + i] for b in S for i in (0, 1)]) for S in itertools.combinations(range(M), 4))
        row = dict(file=fn, restart=run['restart'], first_defect=k0, excess=run['best_excess'], min_quadruple_span=quad, cores=cores)
        out.append(row); print(row, flush=True)
json.dump(out, open(os.path.join(HERE, 'adversary_cores.json' if not _sys.argv[1:] else 'loose_triples_adversary_cores.json' if 'loose' in _sys.argv[1] else 'adversary_cores.json'), 'w'), indent=1, default=int)
