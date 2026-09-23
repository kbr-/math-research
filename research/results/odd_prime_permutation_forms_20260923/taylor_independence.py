"""Independence of the Frobenius and Koszul syzygies of square tops at the orbit specialization (n holes, weak
unary PHP top algebra): rows l_j * m e_j (m in the basis of A_1) and l_k^2 e_j - l_j^2 e_k (k < j), in coordinates
of (+)_j A_2 e_j, ordered by the largest form index so that prefix ranks give every M.  Full rank M*gamma_1 + C(M,2)
at one specialization makes the generators independent for generic forms (an open condition).
Usage: python3 taylor_independence.py ORBIT_RESULT.json OUT.json"""
import json, os, sys, time
import numpy as np
REC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_degree_four_20260923')
sys.path.insert(0, REC); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a4lib as L
from a4lib import gf3
from gf3_prefix import prefix_ranks
res = json.load(open(sys.argv[1])); L.setup(res['n']); t0 = time.time()
Q1, g1 = L.quotient(1, 12); Q2, g2 = L.quotient(2, 12)
basis1 = [q['cols'][c] for q in Q1.values() for c in q['nonp']]
ls = [np.array(l) for l in res['forms']]; M = len(ls)
sq = [L.normal_form(L.square(l), Q2, g2) % 3 for l in ls]
def lin(l): return {(u,): int(c) for u, c in enumerate(l) if c % 3}
rows, ends = [], []
for j in range(M):
    for m in basis1:
        r = np.zeros(M * g2, dtype=np.uint8); r[j * g2:(j + 1) * g2] = L.normal_form(L.mul({m: 1}, lin(ls[j])), Q2, g2) % 3; rows.append(r)
    for k in range(j):
        r = np.zeros(M * g2, dtype=np.uint8); r[j * g2:(j + 1) * g2] = sq[k]; r[k * g2:(k + 1) * g2] = (-sq[j]) % 3; rows.append(r)
    ends.append(len(rows))
P, W = gf3.pack(np.array(rows))[:2]
ranks = prefix_ranks(P, W, M * g2, ends)
out = dict(n=res['n'], gamma_1=g1, gamma_2=g2, runs=[dict(M=j + 1, rank=ranks[j], generators=ends[j]) for j in range(M)])
bad = [x['M'] for x in out['runs'] if x['rank'] != x['generators']]
print('generators dependent at M =', bad or None, f'({time.time()-t0:.0f}s)')
json.dump(out, open(sys.argv[2], 'w'), indent=1)
