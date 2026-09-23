"""Check of the pattern theorem's explicit elements on one row triple (rows a,b,c = 0,1,2), labels 0..L-1, over F_3.
For each L: (1) q_02*y_{1,0}, q_01*y_{2,0} and e_{!=x} = sum_{d != x} q_01*y_{2,d} - q_12*y_{0,x} - q_02*y_{1,x} (x = 0, 1)
equal the stated tuple sets (supports with coefficient 1); (2) their smallest tuples are (1,0,2), (1,2,0), (1,2,3),
(0,2,3); (3) every tuple with a 0 on a row above a 1 is the smallest tuple of some q_pq*y_{o,d}; (4) the leading-term
count 3(L-2)+4 equals (L)_3 - delta_3(L+1).  Usage: python3 verify_patterns.py --Ls 4,5,6,7,8,9 --out OUT.json"""
import argparse, itertools, json, math
def delta(t, N): return sum((-1) ** j * math.comb(t, j) * math.perm(N, t - j) for j in range(t + 1))
def qprod(p, q, o, d, L):                 # q_{pq} * y_{o,d} as a dict tuple -> coefficient mod 3
    out = {}
    for c1, c2 in itertools.permutations(range(L), 2):
        f = [None] * 3; f[p], f[q], f[o] = c1, c2, d
        if len(set(f)) == 3: out[tuple(f)] = (out.get(tuple(f), 0) + 1) % 3
    return out
def add(*terms):
    out = {}
    for c, v in terms:
        for k, x in v.items(): out[k] = (out.get(k, 0) + c * x) % 3
    return {k: x for k, x in out.items() if x}
ap = argparse.ArgumentParser(); ap.add_argument('--Ls', default='4,5,6,7,8,9'); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
for L in map(int, a.Ls.split(',')):
    tup = list(itertools.permutations(range(L), 3)); ok = {}
    e = {x: add(*[(1, qprod(0, 1, 2, d, L)) for d in range(L) if d != x], (-1, qprod(1, 2, 0, x, L)), (-1, qprod(0, 2, 1, x, L))) for x in (0, 1)}
    want = {x: {t: 1 for t in tup if x not in t} for x in (0, 1)}
    ok['e_identities'] = all(e[x] == want[x] for x in (0, 1))
    A, B = qprod(0, 2, 1, 0, L), qprod(0, 1, 2, 0, L)
    ok['q_products'] = A == {t: 1 for t in tup if t[1] == 0} and B == {t: 1 for t in tup if t[2] == 0}
    ok['leading_terms'] = [min(A), min(B), min(e[0]), min(e[1])] == [(1, 0, 2), (1, 2, 0), (1, 2, 3), (0, 2, 3)]
    d2 = [t for t in tup if any(t[i] == 0 and t[j] == 1 for i in range(3) for j in range(i + 1, 3))]
    lt_q = {min(qprod(p, q, o, d, L)) for (p, q, o) in ((0, 1, 2), (0, 2, 1), (1, 2, 0)) for d in range(L) if qprod(p, q, o, d, L)}
    ok['d2_multiples_are_leading'] = set(d2) <= lt_q
    ok['count'] = len(d2) + 4 == len(tup) - delta(3, L + 1) and len(d2) == 3 * (L - 2)
    res.append(dict(L=L, **ok)); print(res[-1], flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
