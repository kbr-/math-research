"""Independent check of the power-of-two certificates L_j used by the small-k upper bound.

For each K = 2^j in the input, verifies directly (not through the solver's rank test) that
  * every partition in L_j has size <= 2^(j+1) - j - 2 (degree bound (i) of the reduction lemma);
  * the empty partition is in L_j (origin value 1, so origin order 0 in every dimension);
  * for every weight 1 <= w < K and every (b, c) with sum(b) + sum(c) < K - w, the number of
    distinct exponent vectors (equal parts not distinguished) counted by
    bmd_symmetric_q.placement_parity, summed over lambda in L_j, is even.
Finite and independent of n (dimension-free certificate lemma).  Seconds.
Usage: bmd_check_certificates.py QJSON OUTJSON
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmd_symmetric_q import conditions, placement_parity

data = {r['k']: r for r in json.load(open(sys.argv[1]))}
report = []
for j in range(4):
    K = 2 ** j
    L = {tuple(l) for l in data[K]['Q']}
    bound = 2 ** (j + 1) - j - 2
    rows = conditions(K)
    bad = [row for row in rows if sum(placement_parity(lam, row[1], row[2]) for lam in L) % 2]
    rec = {'K': K, 'partitions': len(L), 'max_size': max(sum(l) for l in L), 'degree_bound': bound,
           'has_constant': () in L, 'conditions_checked': len(rows), 'violations': len(bad)}
    rec['ok'] = rec['max_size'] <= bound and rec['has_constant'] and not bad
    print(json.dumps(rec), flush=True)
    report.append(rec)
json.dump(report, open(sys.argv[2], 'w'), indent=1)
print('ALL CERTIFICATES OK' if all(r['ok'] for r in report) else 'CERTIFICATE FAILURE')
