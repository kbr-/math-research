"""Range of the residual nondefectiveness proposition on the PHP board (R = n+1 rows, N = n labels, GF(3)).

The proposition gives rank M(N-1) for generic forms whenever M <= m = C(R-1,2) * dim K_2(one row pair, N-2 labels).
The row Horace reduction needs it up to the total capacity gamma_3/(gamma_1-1), gamma_1 = R(N-1),
gamma_3 = C(R,3) * dim K_3(one row triple, N labels).  This script computes both local dimensions exactly
(nullspace of the zero-marginal conditions over GF(3)), compares them with the formula
delta_t(N) = sum_j (-1)^j C(t,j) (N)_{t-j}, and checks m >= capacity and the polynomial
2n^4 - 16n^3 + 25n^2 + 35n - 65 that the inequality reduces to under the formula.
Usage: python3 residual_range.py --ns 6,7,8,9,10 --out OUT.json"""
import argparse, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_short_generation_20260923'))
from second_degree_lift import marg_basis

def delta(t, N):
    return sum((-1) ** j * math.comb(t, j) * math.perm(N, t - j) for j in range(t + 1))

ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='6,7,8,9,10'); ap.add_argument('--out', required=True)
a = ap.parse_args(); rows = []
for n in map(int, a.ns.split(',')):
    R, N = n + 1, n
    k2 = marg_basis(N - 2, 2)[1].shape[1]; k3 = marg_basis(N, 3)[1].shape[1]
    m = math.comb(R - 1, 2) * k2; cap = math.comb(R, 3) * k3 / (R * (N - 1) - 1)
    poly = 2 * n**4 - 16 * n**3 + 25 * n**2 + 35 * n - 65
    rows.append(dict(n=n, K2_pair=k2, delta2=delta(2, N - 2), K3_triple=k3, delta3=delta(3, N), m=m,
                     capacity=round(cap, 2), m_ge_capacity=m >= cap, poly=poly))
    print(rows[-1], flush=True)
    assert k2 == delta(2, N - 2) and k3 == delta(3, N) and m >= cap and poly > 0
json.dump(rows, open(a.out, 'w'), indent=1)
