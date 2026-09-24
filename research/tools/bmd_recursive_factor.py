"""Test the recursive factorization Q_(2^j) = Q_(2^(j-1)) * R_j of the power-of-two factors.

Statement tested.  For j >= 1, is there a symmetric R_j in every dimension with R_j(0) = 1,
degree <= 2^j - 1, and Hasse multiplicity >= r_j(w) at every point of weight w, where
r_j(w) = 2^(j-1) for 1 <= w < 2^(j-1) and r_j(w) = 2^j - w for 2^(j-1) <= w < 2^j?
By multiplicity additivity, R_1 R_2 ... R_j is then a power-of-two factor Q_(2^j) (degree
sum (2^i - 1) = 2^(j+1) - j - 2, multiplicity >= 2^j - w at weights w < 2^j).  The conditions are
the dimension-free placement parities of bmd_symmetric_q with a per-weight order requirement.
Usage: bmd_recursive_factor.py JMAX --out PATH
"""
import argparse, json, time, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmd_symmetric_q import partitions, multisets, placement_parity, rank_and_basis, kernel_vector_with_low


def rows_for(req):
    """Condition rows (w, b, c) with sum(b) + sum(c) < req[w]."""
    rows = []
    for w, need in req.items():
        for t in range(need):
            for s1 in range(t + 1):
                for ob in multisets(s1, w):
                    for zb in partitions(t - s1):
                        rows.append((w, ob, zb))
    return rows


def solve(req, D):
    lams = [lam for s in range(D + 1) for lam in partitions(s)]
    cols = [lam for lam in lams if lam] + [()]          # constant column last (highest bit)
    rows = rows_for(req)
    mat = []
    for (w, ob, zb) in rows:
        v = 0
        for i, lam in enumerate(cols):
            if placement_parity(lam, ob, zb):
                v |= 1 << i
        mat.append(v)
    nonconst = len(cols) - 1
    r_all = len(rank_and_basis(mat))
    r_wo = len(rank_and_basis([v & ((1 << nonconst) - 1) for v in mat]))
    exists = r_all < r_wo + 1                            # a solution with constant coefficient 1
    sol = kernel_vector_with_low(mat, len(cols), nonconst) if exists else None
    return exists, cols, sol, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jmax', type=int)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = []
    for j in range(1, a.jmax + 1):
        t0 = time.time()
        half, K = 2 ** (j - 1), 2 ** j
        req = {w: (half if w < half else K - w) for w in range(1, K)}
        exists, cols, sol, nrows = solve(req, K - 1)
        rec = {'j': j, 'degree_bound': K - 1, 'requirement': req, 'rows': nrows, 'unknowns': len(cols),
               'R_exists': exists, 'seconds': round(time.time() - t0, 2)}
        if exists:
            rec['R'] = [list(cols[i]) for i in range(len(cols)) if sol >> i & 1]
        print(json.dumps({k: v for k, v in rec.items() if k not in ('R', 'requirement')}), flush=True)
        out.append(rec)
        json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
