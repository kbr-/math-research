"""Column-subalgebra model R = F_3[t_1..t_n]/(t_j^2, sum t_j) for occupancy pairs whose hole values are points of AG(2,3)
with multiplicity: full plane (n = 9) and the plane minus a point doubled (n = 16).  Through degree K, compares the
Hilbert function of R/(l_1, l_2) with HS_R/(1+t+t^2)^2 (untruncated) and each single combination's R/(l) with
HS_R/(1+t+t^2); reports first excess degrees.  Usage: --K --out"""
import itertools, json, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); K = int(a['--K'])
def hf(n, lins):
    H = [1]
    for k in range(1, K + 1):
        Bk = list(itertools.combinations(range(n), k)); idx = {b: i for i, b in enumerate(Bk)}; rows = []
        for S in itertools.combinations(range(n), k - 1):
            Sset = set(S)
            for lv in lins:
                r = np.zeros(len(Bk), dtype=np.uint8)
                for j in range(n):
                    if j not in Sset and lv[j] % 3: r[idx[tuple(sorted(S + (j,)))]] = lv[j] % 3
                rows.append(r)
        H.append(len(Bk) - gf3.rank(np.array(rows)))
    return H
def div(H, r):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]; c = [1] + [0] * K
    for _ in range(r): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(K + 1)]
    return [sum(H[i] * c[k - i] for i in range(k + 1)) for k in range(K + 1)]
plane = list(itertools.product(range(3), repeat=2))
configs = {'n9_full_plane': plane, 'n16_minus_point_doubled': [q for q in plane if q != (2, 2)] * 2}
out = {}
for name, pts in configs.items():
    n = len(pts); ones = [1] * n; p1 = [q[0] for q in pts]; p2 = [q[1] for q in pts]
    HR = hf(n, [ones]); H = hf(n, [ones, p1, p2]); W = div(HR, 2)
    singles = []
    for co in [(1, 0), (0, 1), (1, 1), (1, 2)]:
        ph = [(co[0] * x + co[1] * y) % 3 for x, y in zip(p1, p2)]; c = n - max(ph.count(v) for v in range(3))
        Hs = hf(n, [ones, ph]); Ws = div(HR, 1); ex = [h - w for h, w in zip(Hs, Ws)]
        singles.append(dict(coeffs=co, c=c, H=Hs, W=Ws, first_excess=next((k for k, e in enumerate(ex) if e > 0), None)))
    ex = [h - w for h, w in zip(H, W)]
    out[name] = dict(n=n, HR=HR, H=H, W_untruncated=W, excess=ex, first_joint_excess=next((k for k, e in enumerate(ex) if e > 0), None),
                     first_nonpositive_W=next((k for k, w in enumerate(W) if w <= 0), None), singles=singles)
    print(name, out[name]['H'], out[name]['W_untruncated'], 'joint first excess', out[name]['first_joint_excess'],
          'singles', [(s['c'], s['first_excess']) for s in singles], flush=True)
json.dump(out, open(a['--out'], 'w'), indent=1)
