"""Check the capped Catalan bound on the cube against saved exact values.

Statement tested.  On {0,1}^n over F_p, every polynomial with multiplicity >= k at the nonzero
points and origin order exactly l has savings h = n + 2(k-1) - delta <= rho_{<=n}(m+1), m = k-l-1,
where rho_{<=n}(c) is the least number of allowed parts summing to c-1; a part a is allowed when
C_{a-1} != 0 mod p and nu(a) = #{1 <= j <= a : C_{j-1} != 0 mod p} <= n (a linear form in n root-curve
coordinates then has order exactly a).  When n >= m, h = rho_{<=n}(m+1) (Menezes' formula, extended from n >= k-1 to n >= k-l-1).
Also checks the uncapped side h >= rho_F(m+1) (the Catalan-truncation upper bound on delta).
Reads the kernel JSONs of research/results/bmd-r9-odd-cube/pP and reports violations and equality.
With --kappa it instead compares each value with kappa_n(m) from the refined initial-segment law
(kappa = 0 at m = 0, 1 for the n-allowed parts, otherwise max(2, min{d : N_{2,n}(d) > m})), which is
proved for n <= 3 and for the recorded n = 4 range: it reports any h > kappa (a contradiction with the
stable law) and, for each (n, m), the least l from which h = kappa holds in the data.
Usage: bmd_cube_rho_cap_check.py RESULTS_DIR p [--kappa]
"""
import json, sys
from pathlib import Path


def catalan_mod(p, count):
    c = [1]
    for j in range(1, count):
        c.append(c[-1] * 2 * (2 * j - 1) // (j + 1))
    return [x % p for x in c]


def rho_capped(p, n, top):
    cat = catalan_mod(p, top + 2)
    nu, parts = 0, []
    for a in range(1, top + 1):
        if cat[a - 1] != 0:
            nu += 1
            if nu <= n:
                parts.append(a)
    INF = 10 ** 9
    best = [0] + [INF] * top
    for v in range(1, top + 1):
        best[v] = min((best[v - a] + 1 for a in parts if a <= v), default=INF)
    return best  # best[m] = rho_{<=n}(m+1)


def n2(n, d):
    from math import comb
    return sum(comb(n, i) for Q in range(d // 2 + 1) for i in range(n + 1) if 2 * Q + i <= d)


def kappa_refined(p, n, m):
    if m == 0:
        return 0
    cat = catalan_mod(p, m + 2)
    nu, allowed = 0, set()
    for a in range(1, m + 1):
        if cat[a - 1] != 0:
            nu += 1
            if nu <= n:
                allowed.add(a)
    if m in allowed:
        return 1
    d = 2
    while n2(n, d) <= m:
        d += 1
    return d


def kappa_mode(root, p):
    above, total, eq = [], 0, 0
    series = {}  # (n, m) -> list of (l, h)
    for f in sorted(root.glob('cube-p%d-n*-k*.json' % p)):
        d = json.loads(f.read_text())
        n, k = d['n'], d['k']
        for l, v in enumerate(d['delta']):
            m = k - l - 1
            h = n + 2 * (k - 1) - v
            kap = kappa_refined(p, n, m)
            total += 1
            eq += h == kap
            if h > kap:
                above.append((n, k, l, h, kap))
            series.setdefault((n, m), []).append((l, h, kap))
    print(f'p={p}: {total} values; h > kappa: {above}; h = kappa: {eq}')
    late = []
    for (n, m), rows in sorted(series.items()):
        rows.sort()
        below = [l for l, h, kap in rows if h < kap]
        if below:
            late.append((n, m, max(below) + 1, max(l for l, _, _ in rows)))
    print(f'p={p}: (n, m, least l with h = kappa from then on in the data, largest l recorded) where some h < kappa:')
    print(late)


def main():
    root, p = Path(sys.argv[1]), int(sys.argv[2])
    if '--kappa' in sys.argv:
        kappa_mode(root, p)
        return
    above, eq_fail, eq_ok, total, eq_all, beyond, beyond_eq = [], [], 0, 0, 0, 0, 0
    below_uncapped, above_uncapped = [], 0
    for f in sorted(root.glob('cube-p%d-n*-k*.json' % p)):
        d = json.loads(f.read_text())
        n, k = d['n'], d['k']
        best = rho_capped(p, n, k)
        free = rho_capped(p, 10 ** 6, k)  # uncapped rho_F
        for l, v in enumerate(d['delta']):
            m = k - l - 1
            h = n + 2 * (k - 1) - v
            total += 1
            if h > best[m]:
                above.append((n, k, l, h, best[m]))
            eq_all += h == best[m]
            if h < free[m]:
                below_uncapped.append((n, k, l, h, free[m]))
            above_uncapped += h > free[m]
            if n >= m and n < k - 1:  # beyond Menezes' range n >= k-1
                beyond += 1
                beyond_eq += h == best[m]
            if n >= m:
                if h == best[m]:
                    eq_ok += 1
                else:
                    eq_fail.append((n, k, l, h, best[m]))
    print(f'p={p}: {total} values; savings above rho_<=n: {above}')
    print(f'p={p}: n >= m cases with h = rho: {eq_ok}; failures: {eq_fail}')
    print(f'p={p}: equalities overall: {eq_all} of {total}')
    print(f'p={p}: savings below rho_F(m+1) (Catalan-truncation upper bound violated): {below_uncapped}')
    print(f'p={p}: values with savings strictly above rho_F(m+1): {above_uncapped} of {total}')
    print(f'p={p}: values with n >= m and n < k-1 (beyond Menezes range): {beyond}, equalities: {beyond_eq}')


if __name__ == '__main__':
    main()
