#!/usr/bin/env python3
"""Closure of the peeling rules on {0,1}^3 (entry-2026-09-26-cube-product-peeling).

Statement tested.  For 1 <= rho <= d let B(d, rho) = sum (p_i^2 - 1) over the balanced partition of d into rho
parts (open statement 1's torsion-partition value in both regions).  A pair (d, rho) is *settled* when the solution
module at (d, rho) is proved free on witness solutions; its least generator excess E is then l_0(d+1, 4d+rho-1)
when E <= B (product bound).  Settled pairs arise from:
  * rho = 1: the boundary theorem, E = d^2 - 1;
  * the proved non-product bases (3,2) (E = 3) and (5,2) (E = 11), and the diagonal (e,e) (E = 0) and
    near-diagonal (d,d-1) (E = 3) of thm:cube-diagonal-near-diagonal;
  * product peeling (lem:cube-general-peeling): (d-p, rho-1) settled with least excess E', p >= 1, and a partition
    pi of d into rho positive parts, none equal to p, with sum (pi_i^2 - 1) = p(2d - p rho); then (d, rho) is settled
    with E = min(E' + p^2 - 1, p(2d - p rho));
  * the line theorem (thm:cube-peeling-lines): (2j, j) settled with E = 3j settles (j+rho, rho), rho >= j, E = 3j.
The script computes the closure for d <= DMAX.  It asserts E <= B for every settled pair (E > B would contradict
the product bound, so it would expose an error in a rule), reports pairs with E < B (settled, but giving only
l_0 >= E), and prints the settled and unsettled pairs with one route each.

With --assume-odd-two, the pairs (2e+1, 2) are added as settled with E = B (conj:cube-odd-invariant-generator), to
show what remains once that conjecture is proved.

Usage: bmd_cube_peeling_closure.py DMAX [--assume-odd-two] [--out PATH]
"""
import sys


def partitions(n, k, maxpart=None):
    """Partitions of n into exactly k positive parts, non-increasing."""
    if maxpart is None:
        maxpart = n
    if k == 0:
        if n == 0:
            yield ()
        return
    for first in range(min(n - (k - 1), maxpart), 0, -1):
        if first * k < n:
            break
        for rest in partitions(n - first, k - 1, first):
            yield (first,) + rest


def balanced(d, rho):
    p, r = divmod(d, rho)
    return (p + 1,) * r + (p,) * (rho - r)


def B(d, rho):
    return sum(x * x - 1 for x in balanced(d, rho))


def main():
    dmax = int(sys.argv[1])
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    E, route = {}, {}
    for d in range(1, dmax + 1):
        E[(d, 1)] = d * d - 1; route[(d, 1)] = 'boundary'
        E[(d, d)] = 0; route[(d, d)] = 'diagonal'
        if d >= 3:
            E[(d, d - 1)] = 3; route[(d, d - 1)] = 'near-diagonal'
    for key, val in (((3, 2), 3), ((5, 2), 11)):
        E[key] = val; route[key] = 'proved base'
    if '--assume-odd-two' in sys.argv:
        for d in range(7, dmax + 1, 2):
            E[(d, 2)] = B(d, 2); route[(d, 2)] = 'assumed (odd invariant generator)'
    parts_cache = {}
    changed = True
    while changed:
        changed = False
        for d in range(2, dmax + 1):
            for rho in range(2, d):
                if (d, rho) in E:
                    continue
                for p in range(1, d - rho + 2):
                    src = (d - p, rho - 1)
                    if src not in E:
                        continue
                    target = p * (2 * d - p * rho)
                    if (d, rho) not in parts_cache:
                        parts_cache[(d, rho)] = list(partitions(d, rho))
                    hit = next((pi for pi in parts_cache[(d, rho)]
                                if p not in pi and sum(x * x - 1 for x in pi) == target), None)
                    if hit is None:
                        continue
                    E[(d, rho)] = min(E[src] + p * p - 1, target)
                    route[(d, rho)] = f'P_{p}-peel from {src}, new generator prod P over {hit}'
                    changed = True
                    break
        for j in range(1, dmax // 2 + 1):
            start = (2 * j, j)
            if start in E and E[start] == 3 * j:
                for rho in range(j, dmax - j + 1):
                    if (j + rho, rho) not in E:
                        E[(j + rho, rho)] = 3 * j; route[(j + rho, rho)] = f'line j={j} from start {start}'
                        changed = True
    lines, bad, weak = [], [], []
    for d in range(2, dmax + 1):
        for rho in range(2, d):
            b = B(d, rho)
            if (d, rho) in E:
                if E[(d, rho)] > b:
                    bad.append((d, rho, E[(d, rho)], b))
                elif E[(d, rho)] < b:
                    weak.append((d, rho))
                lines.append(f'({d},{rho}) B={b} settled E={E[(d, rho)]}: {route[(d, rho)]}')
            else:
                lines.append(f'({d},{rho}) B={b} UNSETTLED')
    unsettled = [l for l in lines if 'UNSETTLED' in l]
    summary = [f'DMAX={dmax}: {len(lines) - len(unsettled)} of {len(lines)} pairs with 2 <= rho <= d-1 settled; '
               f'{len(bad)} with least excess > B; {len(weak)} with least excess < B: {weak}']
    text = '\n'.join(summary + lines + ['unsettled: ' + ', '.join(l.split(' ')[0] for l in unsettled)]) + '\n'
    print(text, end='')
    if out:
        with open(out, 'w') as f:
            f.write(text)
    assert not bad, bad


if __name__ == '__main__':
    main()
