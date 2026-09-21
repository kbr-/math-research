import json, zlib, numpy as np, collections, sys
sys.path.insert(0, 'research/results/odd_prime_kernel_alignment_20260921')
import alignment as A
R = json.load(open('research/results/odd_prime_kernel_alignment_20260921/alignment_k4many.json'))
S = R['summary']
geo = {}
for name, cfg in A.CONFIGS['k4many'].items():
    N, d, k, seed, _ = cfg
    rng = np.random.default_rng(seed)
    nb = [[int(x) for x in rng.choice(N, size=d, replace=False)] for _ in range(N + 1)]
    cells = [(i, h) for i in range(N + 1) for h in nb[i][1:]]
    geo[name] = (cells, [x[0] for x in nb], N)
feat = collections.defaultdict(list)
for r in R['rows']:
    if r['kind'] != 'square': continue
    cells, dist, N = geo[r['config']]; s = len(cells)
    rng = np.random.default_rng(zlib.crc32(f"{r['config']}|{r['h']}|square|{r['trial']}".encode()))
    F = np.array([rng.integers(0, 3, size=s) for _ in range(r['h'])])
    rowz = sum(1 for f in F for i in range(N + 1) if all(f[u] == 0 for u, c in enumerate(cells) if c[0] == i))
    holez = sum(1 for f in F for h in range(N) if any(c[1] == h for c in cells) and all(f[u] == 0 for u, c in enumerate(cells) if c[1] == h))
    ex = r['actual'] > r['predicted']
    feat[(r['config'], ex)].append((rowz, holez, r['actual'] - r['predicted']))
for key in sorted(feat):
    v = feat[key]
    print(key, 'n', len(v), 'mean row-zero', round(np.mean([a for a,_,_ in v]),2), 'mean hole-zero', round(np.mean([b for _,b,_ in v]),2),
          'frac row-zero>0', round(np.mean([a>0 for a,_,_ in v]),2))
