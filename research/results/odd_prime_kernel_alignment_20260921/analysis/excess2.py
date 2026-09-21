import json, sys, zlib, numpy as np, collections
sys.path.insert(0, 'research/results/odd_prime_kernel_alignment_20260921')
import alignment as A
R = json.load(open('research/results/odd_prime_kernel_alignment_20260921/alignment_k4many.json'))
cases = [('N8d4k4', 4, 18), ('N8d4k4', 4, 5), ('N9d4k4', 7, 8), ('N9d4k4', 5, 7)]
prep = {}
for name, h, t in cases:
    if name not in prep: prep[name] = A.prepare((name, A.CONFIGS['k4many'][name]))[1]
    C = prep[name]; G = C['G']; s = G['s']; cfg = A.CONFIGS['k4many'][name]
    rng = np.random.default_rng(cfg[3]); N = cfg[0]
    nb = [[int(x) for x in rng.choice(N, size=cfg[1], replace=False)] for _ in range(N + 1)]
    cells = [(i, hh) for i in range(N + 1) for hh in nb[i][1:]]
    rng = np.random.default_rng(zlib.crc32(f"{name}|{h}|square|{t}".encode()))
    F = np.array([rng.integers(0, 3, size=s) for _ in range(h)])
    B = []
    for f in F: B += A._rows(G, f)
    Jb = A.rref3(A.nf(C, np.array(B, dtype=np.uint8)))
    Wq = C['Wq']; w = Wq.shape[0]; M = np.vstack([Wq, Jb])
    E = A.rref3(np.hstack([M, np.eye(M.shape[0], dtype=np.uint8)]))
    ker = np.array([row[M.shape[1]:M.shape[1] + w] for row in E if not row[:M.shape[1]].any()])
    Wb = A.rref3(ker % 3)
    rowzero = sorted({i for f in F for i in range(N + 1) if all(f[u] == 0 for u, c in enumerate(cells) if c[0] == i)})
    print(name, h, t, 'excess dim', Wb.shape[0], 'rows where some form vanishes:', rowzero)
    for v in Wb:
        mons = [G['good'][j] for j in np.nonzero(v)[0]]
        common = set.intersection(*[{cells[u][0] for u in m} for m in mons])
        print('   vector with', len(mons), 'monomials; rows in every monomial:', sorted(common))
