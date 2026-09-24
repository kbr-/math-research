"""Structure of the space of symmetric power-of-two factors Q_K (K = 2^j), dimension-free.

For K and degree bound D = 2K - j - 2, computes over F_2:
  * the dimension of the kernel of the dimension-free parity conditions (all symmetric Q of degree
    <= D meeting the multiplicity bounds, any constant term);
  * whether the coefficient of each m_lambda with |lambda| < K is the same in every solution with
    constant term 1 (forced), and whether it equals 1 (agreement with the truncation of prod(1+x)^-1);
  * the forced coefficients in each degree >= K.
Seconds for K <= 8.  Usage: bmd_factor_space.py K --out PATH
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmd_symmetric_q import partitions, conditions, placement_parity


def rref(rows, ncols):
    rows = list(rows); piv = []; r = 0
    for c in range(ncols):
        p = next((i for i in range(r, len(rows)) if rows[i] >> c & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> c & 1:
                rows[i] ^= rows[r]
        piv.append(c); r += 1
    return rows[:r], piv


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('K', type=int); ap.add_argument('--out', required=True)
    a = ap.parse_args(); K = a.K; j = int(math.log2(K)); D = 2 * K - j - 2
    cols = [lam for s in range(D + 1) for lam in partitions(s)]
    mat = []
    for (w, ob, zb) in conditions(K):
        v = 0
        for i, lam in enumerate(cols):
            if placement_parity(lam, ob, zb):
                v |= 1 << i
        mat.append(v)
    R, piv = rref(mat, len(cols))
    free = [c for c in range(len(cols)) if c not in set(piv)]
    # kernel basis: one vector per free column
    basis = []
    for f in free:
        x = 1 << f
        for i, pc in enumerate(piv):
            if R[i] >> f & 1:
                x |= 1 << pc
        basis.append(x)
    const = cols.index(())
    # a coefficient is forced among solutions with constant 1 iff every kernel vector with
    # constant 0 has that coordinate 0; build the subspace with constant 0 and its support
    with1 = [b for b in basis if b >> const & 1]
    with0 = [b for b in basis if not b >> const & 1]
    if with1:
        base = with1[0]
        with0 += [b ^ base for b in with1[1:]]
    support0 = 0
    for b in with0:
        support0 |= b
    forced = {}
    for i, lam in enumerate(cols):
        if not support0 >> i & 1:
            forced[str(lam)] = (base >> i & 1) if with1 else None
    low_forced_all = all(str(l) in forced for l in cols if sum(l) < K)
    low_is_truncation = low_forced_all and all(forced[str(l)] == 1 for l in cols if sum(l) < K)
    rec = {'K': K, 'degree_bound': D, 'unknowns': len(cols), 'kernel_dimension': len(basis),
           'solutions_with_constant_1': bool(with1),
           'affine_dimension': len(with0) if with1 else None,
           'low_part_forced': low_forced_all, 'low_part_is_truncation': low_is_truncation,
           'forced_high_terms': {k: v for k, v in forced.items() if sum(eval(k)) >= K and v == 1},
           'free_high_degrees': sorted({sum(cols[i]) for i in range(len(cols)) if support0 >> i & 1})}
    print(json.dumps(rec), flush=True)
    json.dump(rec, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
