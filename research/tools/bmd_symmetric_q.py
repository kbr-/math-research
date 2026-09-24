"""Symmetric n-independent factors Q_k for the product construction P = prod_i(1+x_i) * Q_k.

Statement tested.  For each k, is there a symmetric Q in F_2[x_1, x_2, ...], written as
sum_lambda c_lambda m_lambda (monomial symmetric functions, lambda of size <= D), with origin order
below k and Hasse multiplicity >= k-|a| at every point a of weight 1 <= |a| < k, for every n?
Then P has multiplicity >= |a| + (k-|a|) = k off the origin (prod(1+x_i) has multiplicity |a| at a),
the same origin order as Q, and degree n + deg Q.  The product reduction needs D = 2k - m(k),
m(k) = floor(log2 k) + 2.

Conditions.  By symmetry one point per weight w suffices: a = (1^w, 0, ...).  The coefficient of
z^beta in m_lambda(a+z) is the parity of the number of exponent vectors alpha in the orbit of lambda
with prod_i binom(alpha_i, beta_i) a_i^(alpha_i - beta_i) odd.  Nonzero parts may sit at a position
with a_i = 1 and beta_i a bit-submask of alpha_i (Lucas), or at a position with a_i = 0 and
alpha_i = beta_i; every other position holds 0.  The count therefore does not depend on n once n
exceeds the positions used, so the system describes Q for all large n at once.

The linear algebra is over a few hundred unknowns and runs in seconds (measured below); this is
orchestration-sized work, not a heavy loop.
Usage: bmd_symmetric_q.py KMAX --out PATH
"""
import argparse, functools, json, math, time


def partitions(total, maxpart=None):
    if maxpart is None:
        maxpart = total
    if total == 0:
        yield ()
        return
    for p in range(min(total, maxpart), 0, -1):
        for rest in partitions(total - p, p):
            yield (p,) + rest


def multisets(total, length, maxpart=None):
    """Nonincreasing tuples of nonnegative ints of given length summing to total."""
    if maxpart is None:
        maxpart = total
    if length == 0:
        if total == 0:
            yield ()
        return
    for p in range(min(total, maxpart), -1, -1):
        for rest in multisets(total - p, length - 1, p):
            yield (p,) + rest


def placement_parity(lam, ones_beta, zero_beta):
    """Parity of assignments of the nonzero parts of lam to positions (see module docstring)."""
    parts = sorted(set(lam))
    counts = tuple(lam.count(p) for p in parts)
    positions = [(1, b) for b in ones_beta] + [(0, c) for c in zero_beta]

    @functools.lru_cache(maxsize=None)
    def go(i, rem):
        if i == len(positions):
            return 1 if not any(rem) else 0
        kind, b = positions[i]
        total = 0
        if b == 0 and kind == 1:
            total += go(i + 1, rem)          # alpha_i = 0
        for j, p in enumerate(parts):
            if rem[j] == 0:
                continue
            ok = (p == b) if kind == 0 else (p >= b and (b & ~p) == 0)
            if ok:
                nxt = rem[:j] + (rem[j] - 1,) + rem[j + 1:]
                total += go(i + 1, nxt)
        return total & 1
    if any(c == 0 for c in zero_beta):
        raise ValueError('zero positions in beta must be positive')
    return go(0, counts)


def conditions(k):
    """Rows (w, ones_beta, zero_beta) for weights 1 <= w < k and orders |beta| < k - w."""
    rows = []
    for w in range(1, k):
        for t in range(k - w):
            for s1 in range(t + 1):
                for ob in multisets(s1, w):
                    for zb in partitions(t - s1):
                        rows.append((w, ob, zb))
    return rows


def rank_and_basis(vecs):
    """Row-reduce integer bitsets; returns pivot dictionary {pivot_bit: vector}."""
    piv = {}
    for v in vecs:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                break
    return piv


def solve(k, D):
    lams = [lam for s in range(D + 1) for lam in partitions(s)]
    # column order: low-degree (|lam| < k) columns in the HIGH bits so they are eliminated last
    low = [lam for lam in lams if sum(lam) < k]
    high = [lam for lam in lams if sum(lam) >= k]
    cols = high + low                          # bit index = position
    rows = conditions(k)
    mat = []
    for (w, ob, zb) in rows:
        v = 0
        for idx, lam in enumerate(cols):
            if placement_parity(lam, ob, zb):
                v |= 1 << idx
        mat.append(v)
    # Solutions with nonzero low part exist iff rank(all) < rank(high-only) + #low.
    mask_high = (1 << len(high)) - 1
    r_all = len(rank_and_basis(mat))
    r_high = len(rank_and_basis([v & mask_high for v in mat]))
    exists = r_all < r_high + len(low)
    sol = None
    if exists:
        sol = kernel_vector_with_low(mat, len(cols), len(high))
    return exists, cols, sol, len(rows)


def kernel_vector_with_low(mat, ncols, nhigh):
    """Gauss-Jordan over columns in index order; a free low column gives the witness."""
    rows = list(mat)
    pivcols = []
    r = 0
    for c in range(ncols):
        p = next((i for i in range(r, len(rows)) if rows[i] >> c & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> c & 1:
                rows[i] ^= rows[r]
        pivcols.append(c)
        r += 1
    pivset = set(pivcols)
    for f in range(nhigh, ncols):
        if f in pivset:
            continue
        x = 1 << f
        for i, pc in enumerate(pivcols):
            if rows[i] >> f & 1:
                x |= 1 << pc
        return x
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kmax', type=int)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = []
    for k in range(1, args.kmax + 1):
        t0 = time.time()
        m = int(math.log2(k)) + 2
        target = 2 * k - m
        exists, cols, sol, nrows = solve(k, target)
        rec = {'k': k, 'm': m, 'target_degree': target, 'symmetric_Q_exists': exists, 'rows': nrows,
               'unknowns': len(cols), 'seconds': round(time.time() - t0, 2)}
        if exists:
            rec['Q'] = [list(cols[i]) for i in range(len(cols)) if sol >> i & 1]
            rec['origin_order'] = min(sum(l) for l in rec['Q'])
        print(json.dumps({x: rec[x] for x in rec if x != 'Q'}), flush=True)
        out.append(rec)
        json.dump(out, open(args.out, 'w'), indent=1)        # after every k: a timeout keeps results


if __name__ == '__main__':
    main()
