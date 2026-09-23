"""Writes the systems for the column-splitting tests at a given n: members P (first forms) and P' (the rest) of a robust
column span with hole functions PHIS, the whole span S, and S plus k = 1..K uniform random forms (one seed).
Usage: python3 make_systems.py --n 10 --phis 'a;b;c' --split 2 --K 3 --seed 1 --out SYS.json"""
import json, sys
import numpy as np
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); n = int(a['--n']); P1 = n + 1
PH = [[int(x) for x in s.split(',')] for s in a['--phis'].split(';')]; sp = int(a['--split']); K = int(a['--K'])
col = lambda phi: [list(phi) for _ in range(P1)]
rng = np.random.default_rng(1500 + int(a['--seed'])); rand = [rng.integers(0, 3, size=(P1, n)).tolist() for _ in range(K)]
S = [col(p) for p in PH]
sysm = {'A': [], 'P': S[:sp], 'Pp': S[sp:], 'S': S}
for k in range(1, K + 1): sysm[f'S_r{k}'] = S + rand[:k]
json.dump(sysm, open(a['--out'], 'w'))
