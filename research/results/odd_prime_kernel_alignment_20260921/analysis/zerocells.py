import json, zlib, numpy as np, collections
R = json.load(open('research/results/odd_prime_kernel_alignment_20260921/alignment_k4many.json'))
S = R['summary']; tab = collections.Counter()
for r in R['rows']:
    if r['kind'] != 'square': continue
    s = S[r['config']]['s']
    rng = np.random.default_rng(zlib.crc32(f"{r['config']}|{r['h']}|square|{r['trial']}".encode()))
    F = np.array([rng.integers(0, 3, size=s) for _ in range(r['h'])])
    if 'forms' in r: assert (F == np.array(r['forms'])).all()
    zc = int((F == 0).all(axis=0).sum())
    ex = r['actual'] > r['predicted']
    tab[(r['config'], 'zero-cells>0' if zc else 'no zero cell', 'excess' if ex else 'match')] += 1
for k in sorted(tab): print(k, tab[k])
