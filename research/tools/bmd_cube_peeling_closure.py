#!/usr/bin/env python3
"""Closure of the peeling rules on {0,1}^3 (entry-2026-09-26-cube-product-peeling and its route review).

Statement tested.  For 1 <= rho <= d let B(d, rho) = sum (p_i^2 - 1) over the balanced partition of d into rho
parts (open statement 1's torsion-partition value in both regions).  A pair (d, rho) is *settled* when the solution
module at (d, rho) is proved free on witness solutions; M(d, rho) is then the multiset of generator excesses, and its
least element E gives l_0(d+1, 4d+rho-1) >= E, with equality when E = B (product bound).  Settled pairs arise from:
  * rho = 1: the boundary theorem, M = {d^2 - 1};
  * the proved bases (3,2) (M = {3,4}) and (5,2) (M = {11,12}), the diagonal (e,e) (M = {0,2,...,e}) and the
    near-diagonal (d,d-1) (M = {3,...,d+1}) of thm:cube-diagonal-near-diagonal;
  * peeling (lem:cube-general-peeling): (d-p, rho-1) settled, p >= 1, and a witness solution h at (d, rho) of excess
    p(2d - p rho) whose function is nonzero at q_p; then M = (M(d-p, rho-1) + p^2 - 1) + {p(2d - p rho)};
  * the line theorem (thm:cube-peeling-lines): (2j, j) settled with E = 3j settles (j+rho, rho), rho >= j.
h is searched among products of *atoms*, witness solutions known to be nonzero at given q_p:
  * boundary: P_n at (n,1), excess n^2 - 1, nonzero at q_p for p != n (lem:cube-general-peeling, part 1);
  * extended (--atoms extended): also u_4 at (3,2), excess 4, nonzero at q_1 and q_2 (the P_1- and P_2-hyperplanes at
    (3,2) are both the line of P_1 P_2); w_12 at (5,2), excess 12, nonzero at q_2 and q_3 (both hyperplanes are the
    line of P_2 P_3); and the diagonal generators g_s at (s,s), s >= 2, excess s, nonzero at q_1.
Falsification check: when several routes settle one pair, the generator degrees of a free graded module are unique,
so all routes must give the same M; the script counts disagreements, and asserts E <= B.

Usage: bmd_cube_peeling_closure.py DMAX [--atoms boundary|extended] [--assume-odd-two] [--out PATH]
With --assume-odd-two, the pairs (2e+1, 2), e >= 3, are added as settled with M = {B, B+1}
(conj:cube-odd-invariant-generator), and their new generators are added as atoms, nonzero at q_e and q_{e+1}.
"""
import sys
from collections import Counter


def balanced(d, rho):
    p, r = divmod(d, rho)
    return (p + 1,) * r + (p,) * (rho - r)


def B(d, rho):
    return sum(x * x - 1 for x in balanced(d, rho))


def atoms(dmax, extended, assume_odd=False):
    """(name, d, rho, excess, predicate p -> nonzero at q_p)."""
    out = [(f'P{n}', n, 1, n * n - 1, (lambda p, n=n: p != n)) for n in range(1, dmax + 1)]
    if assume_odd:
        # the assumed odd generator at (2e+1,2), excess B+1: both hyperplanes there are the line of P_e P_{e+1}
        out += [(f'w{2*e+1}', 2 * e + 1, 2, B(2 * e + 1, 2) + 1, (lambda p, e=e: p in (e, e + 1)))
                for e in range(3, (dmax - 1) // 2 + 1)]
    if extended:
        out.append(('u4', 3, 2, 4, lambda p: p in (1, 2)))
        out.append(('w12', 5, 2, 12, lambda p: p in (2, 3)))
        out += [(f'g{s}', s, s, s, lambda p: p == 1) for s in range(2, dmax + 1)]
    return out


def reach(dmax, emax, alist):
    """mask[d][rho]: bit e set if some product of the atoms lies at (d, rho) with excess e."""
    mask = [[0] * (dmax + 1) for _ in range(dmax + 1)]
    mask[0][0] = 1
    lim = (1 << (emax + 1)) - 1
    for (_, ad, ar, ae, _) in alist:
        for d in range(ad, dmax + 1):
            for r in range(ar, d + 1):
                src = mask[d - ad][r - ar]
                if src:
                    mask[d][r] |= (src << ae) & lim
    return mask


def witness(alist, d, r, e):
    """One product (list of atom names) at (d, r) with excess e."""
    def rec(i, d, r, e):
        if d == 0 and r == 0 and e == 0:
            return []
        if i == len(alist) or d < 0 or r < 0 or e < 0:
            return None
        _, ad, ar, ae, _ = alist[i]
        if ad <= d and ar <= r and ae <= e:
            got = rec(i, d - ad, r - ar, e - ae)
            if got is not None:
                return [alist[i][0]] + got
        return rec(i + 1, d, r, e)
    return rec(0, d, r, e)


def main():
    dmax = int(sys.argv[1])
    extended = '--atoms' in sys.argv and sys.argv[sys.argv.index('--atoms') + 1] == 'extended'
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    emax = dmax * dmax
    alls = atoms(dmax, extended, '--assume-odd-two' in sys.argv)
    masks, lists = {}, {}
    for p in range(1, dmax + 1):
        lists[p] = [a for a in alls if a[4](p)]
        masks[p] = reach(dmax, emax, lists[p])
    M, route = {}, {}
    for d in range(1, dmax + 1):
        M[(d, 1)] = Counter([d * d - 1]); route[(d, 1)] = 'boundary'
        if d >= 2:
            M[(d, d)] = Counter([0] + list(range(2, d + 1))); route[(d, d)] = 'diagonal'
        if d >= 3:
            M[(d, d - 1)] = Counter(range(3, d + 2)); route[(d, d - 1)] = 'near-diagonal'
    M[(3, 2)] = Counter([3, 4]); M[(5, 2)] = Counter([11, 12])
    route[(3, 2)] = route[(5, 2)] = 'proved base'
    if '--assume-odd-two' in sys.argv:
        for d in range(7, dmax + 1, 2):
            M[(d, 2)] = Counter([B(d, 2), B(d, 2) + 1]); route[(d, 2)] = 'assumed (odd invariant generator)'
    conflicts, checked = [], 0
    changed = True
    while changed:
        changed = False
        for d in range(2, dmax + 1):
            for rho in range(2, d):
                for p in range(1, d - rho + 2):
                    src = (d - p, rho - 1)
                    if src not in M:
                        continue
                    t = p * (2 * d - p * rho)
                    if t < 0 or t > emax or not (masks[p][d][rho] >> t) & 1:
                        continue
                    new = Counter({e + p * p - 1: c for e, c in M[src].items()})
                    new[t] += 1
                    if (d, rho) in M:
                        checked += 1
                        if M[(d, rho)] != new:
                            conflicts.append(((d, rho), p, sorted(M[(d, rho)].elements()), sorted(new.elements())))
                        continue
                    M[(d, rho)] = new
                    route[(d, rho)] = f'P_{p}-peel from {src}, h = {"*".join(witness(lists[p], d, rho, t))}'
                    changed = True
        for j in range(1, dmax // 2 + 1):
            start = (2 * j, j)
            if start in M and min(M[start].elements()) == 3 * j:
                for rho in range(j + 1, dmax - j + 1):
                    if (j + rho, rho) not in M:
                        M[(j + rho, rho)] = M[start] + Counter(range(3 * j + 1, 2 * j + rho + 1))
                        route[(j + rho, rho)] = f'line j={j} from start {start}'
                        changed = True
    lines, bad, weak = [], [], []
    region = settled_region = 0
    for d in range(2, dmax + 1):
        for rho in range(2, d):
            b = B(d, rho)
            below = 2 * rho < d
            region += below
            if (d, rho) in M:
                E = min(M[(d, rho)].elements())
                settled_region += below
                if E > b:
                    bad.append((d, rho))
                elif E < b:
                    weak.append((d, rho))
                lines.append(f'({d},{rho}) B={b} settled M={sorted(M[(d, rho)].elements())}: {route[(d, rho)]}')
            else:
                lines.append(f'({d},{rho}) B={b} UNSETTLED')
    unsettled = [l.split(' ')[0] for l in lines if 'UNSETTLED' in l]
    summary = [f'DMAX={dmax} atoms={"extended" if extended else "boundary"}: {settled_region} of {region} pairs with '
               f'2 <= rho < d/2 settled; {len(unsettled)} unsettled; least excess > B: {len(bad)}; < B: {weak}; '
               f'second routes checked for equal degree multisets: {checked}, conflicts: {len(conflicts)}']
    text = '\n'.join(summary + lines + ['unsettled: ' + ', '.join(unsettled)]
                     + [f'CONFLICT {c}' for c in conflicts]) + '\n'
    print(text, end='')
    if out:
        with open(out, 'w') as f:
            f.write(text)
    assert not bad, bad


if __name__ == '__main__':
    main()
