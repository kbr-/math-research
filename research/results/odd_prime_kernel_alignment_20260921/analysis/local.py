import json, sys, zlib, itertools, numpy as np
sys.path.insert(0, 'research/results/odd_prime_kernel_alignment_20260921')
import alignment as A
def geo(name):
    N, d, k, seed, _ = A.CONFIGS['k4many'][name]
    rng = np.random.default_rng(seed)
    nb = [[int(x) for x in rng.choice(N, size=d, replace=False)] for _ in range(N + 1)]
    return [(i, h) for i in range(N + 1) for h in nb[i][1:]]
for name, h, t in [('N8d4k4', 4, 18), ('N9d4k4', 5, 7), ('N9d4k4', 7, 8)]:
    C = A.prepare((name, A.CONFIGS['k4many'][name]))[1]; G = C['G']; cells = geo(name); s = len(cells)
    rng = np.random.default_rng(zlib.crc32(f"{name}|{h}|square|{t}".encode()))
    F = np.array([rng.integers(0, 3, size=s) for _ in range(h)])
    coll = lambda u, v: cells[u][0] == cells[v][0] or cells[u][1] == cells[v][1]
    hits = []
    for m in G['good']:
        for a, b in itertools.combinations(m, 2):
            comp = [u for u in range(s) if u not in (a, b) and not coll(u, a) and not coll(u, b)]
            cd = [u for u in m if u not in (a, b)]
            for i, f in enumerate(F):
                sup = [u for u in comp if f[u] != 0]
                if sorted(sup) == sorted(cd): hits.append((m, (a, b), i))
    ms = sorted({x[0] for x in hits})
    print(name, h, t, 'good monomials made single by one form and one pair:', len(ms), ms[:6])
