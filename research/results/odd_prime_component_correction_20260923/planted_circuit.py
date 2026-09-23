"""Planted mid-size circuits in the low-density model B = F_3[s_1..s_12]/(s_i^3): k constraints (2k forms) drawn in a random
d-dimensional subspace, d < 2k, required to contain no circuit of at most three constraints and no deficient proper subset
(so the k constraints form one circuit), plus random constraints up to M = 8; the whole family must have no other circuit
of at most three.  First defect of B/(P_1..P_M) against the truncated prediction through degree K, against the circuit's span.
Usage: --configs 4:6,4:7,5:8,5:9 --trials --seed --K --out"""
import itertools, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LD = os.path.join(HERE, '..', 'odd_prime_low_density_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); K = int(a['--K']); v = 12; Mtot = 8
sys.argv = [sys.argv[0], '--vs', '', '--Ms', '', '--seed', a['--seed']]
exec(open(os.path.join(LD, 'products.py')).read().split('res = []')[0])
monc = [mons(v, k) for k in range(K + 1)]; B, W = series_W(v, Mtot, K); T = truncated(W); out = []
def rk(F, S): return rank3([F[2 * b] for b in S] + [F[2 * b + 1] for b in S])
for cfg in a['--configs'].split(','):
    k, d = map(int, cfg.split(':'))
    for tr in range(int(a['--trials'])):
        while True:
            Bas = rng.integers(0, 3, size=(d, v))
            if rank3(Bas) < d: continue
            F = [(rng.integers(0, 3, size=d) @ Bas) % 3 for _ in range(2 * k)] + [rng.integers(0, 3, size=v) for _ in range(2 * (Mtot - k))]
            if rk(F, range(k)) != d: continue
            if any(rk(F, S) < 2 * len(S) for j in range(1, k) for S in itertools.combinations(range(k), j)): continue
            if any(rk(F, S) < 2 * len(S) for j in (1, 2, 3) for S in itertools.combinations(range(Mtot), j)): continue
            break
        P = [polymul(polymul(lin(F[2 * b]), lin(F[2 * b])), polymul(lin(F[2 * b + 1]), lin(F[2 * b + 1]))) for b in range(Mtot)]
        H = hilbert(v, P, K, monc); fd = next((j for j in range(K + 1) if H[j] != T[j]), None)
        out.append(dict(circuit_size=k, circuit_span=d, trial=tr, H=H, T=T, first_defect=fd, forms=[f.tolist() for f in F]))
        print(k, d, tr, 'first defect', fd, H[4:], T[4:], flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1, default=int)
