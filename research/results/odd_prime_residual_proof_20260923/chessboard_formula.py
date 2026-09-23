"""Lead check: the zero-marginal space on one t-set of rows with N labels is the top cycle space Z_{t-1} of the
t x N chessboard complex M_{t,N} (faces = rook placements; the boundary of a full placement removes one row, and
different removed rows give faces on different row sets, so boundary zero <=> all ordinary marginals zero).
Hence dim = delta_t(N) (the reduced Euler characteristic up to sign) whenever the reduced homology of M_{t,N}
below the top vanishes over GF(3).  The connectivity bound of Bjorner-Lovasz-Vrecica-Zivaljevic, as usually
quoted (M_{m,n} is (nu-2)-connected, nu = min(m, n, floor((m+n+1)/3))), predicts this for N >= 2t-1.
This script compares the exact GF(3) dimension with delta_t(N) for small t, N.
Usage: python3 chessboard_formula.py --out OUT.json"""
import argparse, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_short_generation_20260923'))
from second_degree_lift import marg_basis
def delta(t, N):
    return sum((-1) ** j * math.comb(t, j) * math.perm(N, t - j) for j in range(t + 1))
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args(); rows = []
for t, Ns in ((2, range(2, 7)), (3, range(3, 9)), (4, range(4, 9))):
    for N in Ns:
        d = marg_basis(N, t)[1].shape[1]
        rows.append(dict(t=t, N=N, dim=d, delta=delta(t, N), equal=d == delta(t, N), predicted=N >= 2 * t - 1))
        print(rows[-1], flush=True)
json.dump(rows, open(a.out, 'w'), indent=1)
