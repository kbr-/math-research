"""(-1)-curve prediction for plane curves with fat points at the four vertices of the unit square.

Statement tested.  The four vertices of {0,1}^2 are in linear general position, so the blow-up of the plane at them
is a del Pezzo surface of degree 5, whose only (-1)-curves are the exceptional divisors and the six lines through
two of the points.  Removing every line L_ij with d - m_i - m_j < 0 as a fixed component (repeatedly) leaves a nef
class, which is non-special in characteristic 0, so the dimension of degree-d polynomials with multiplicity m_i at
the points is max(0, C(d+2,2) - sum C(m_i+1,2)) of the reduced class.  This script prints the prediction for the
cases passed as D:K:m0 (multiplicity K at (1,0), (0,1), (1,1) and m0 at the origin), for comparison with the plain
mode of bmd_cube_plane_rows.
"""
import sys
from itertools import combinations


def predict(d, m):
    m = list(m)
    changed = True
    while changed:
        changed = False
        for i, j in combinations(range(4), 2):
            if d >= 0 and m[i] > 0 and m[j] > 0 and d - m[i] - m[j] < 0:
                d -= 1; m[i] -= 1; m[j] -= 1; changed = True
    if d < 0:
        return 0
    return max(0, (d + 2) * (d + 1) // 2 - sum(x * (x + 1) // 2 for x in m))


for arg in sys.argv[1:]:
    D, K, m0 = map(int, arg.split(":"))
    print(f"plain D={D} K={K} m0={m0}: predicted dimension {predict(D, [m0, K, K, K])}")
