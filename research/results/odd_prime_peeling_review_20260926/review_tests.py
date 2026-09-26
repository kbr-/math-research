"""Cheap tests for the peeling-line route review (odd-prime thread, 26 September 2026).

B1 (3-adic bridge): for m = N + 3 pigeons, a virtual degree sequence d_i = 1 (mod 3) summing to
   N + 3^S matches every k-set count with k < 3^S, by Lucas's theorem C(N + 3^S, k) = C(N, k) mod 3.
   Checks the congruence for N = 5..20, S = 2, 3 and k < 3^S, and exhibits sequences summing to N + 9
   with every degree at most N.
L3 (immunity): AR03-type arguments need constraints that no low-degree polynomial certifies; over F_3
   each weak-PHP row sum_j x_ij = 1 and each onto column is itself a degree-1 polynomial vanishing
   exactly on its Boolean solutions (for columns with collisions).  Checks, for rows of length d <= 7,
   that sum_j x_j - 1 vanishes on all Boolean x with sum = 1 (mod 3), i.e. immunity 1.
Usage: review_tests.py --out FILE"""
import argparse, itertools, json
from math import comb

ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); opt = ap.parse_args()
res = {}
ok = True; examples = []
for N in range(5, 21):
    for S in (2, 3):
        good = all((comb(N + 3 ** S, k) - comb(N, k)) % 3 == 0 for k in range(3 ** S))
        ok = ok and good
    total = N + 9; m = N + 3; extra = total - m      # extra holes over one per pigeon, multiple of 3
    seq = [1] * m
    for c in range(extra // 3):                      # spread the extra in steps of 3 (degree 4 pigeons)
        seq[c % m] += 3
    examples.append(dict(N=N, m=m, degrees=seq, degrees_sum=sum(seq), max_degree=max(seq),
                         all_one_mod3=all(d % 3 == 1 for d in seq), max_at_most_N=max(seq) <= N))
res['B1_lucas_congruence_all'] = ok
res['B1_examples'] = examples
imm = {}
for d in range(1, 8):
    imm[d] = all((sum(x) - 1) % 3 == 0 for x in itertools.product((0, 1), repeat=d) if sum(x) % 3 == 1)
res['L3_row_linear_certifies'] = imm
json.dump(res, open(opt.out, 'w'), indent=1)
print(json.dumps(dict(B1=ok, L3=imm)))
