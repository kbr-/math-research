"""Check the capped Catalan bound on the cube against saved exact values.

Statement tested.  On {0,1}^n over F_p, every polynomial with multiplicity >= k at the nonzero
points and origin order exactly l has savings h = n + 2(k-1) - delta <= rho_{<=n}(m+1), m = k-l-1,
where rho_{<=n}(c) is the least number of allowed parts summing to c-1; a part a is allowed when
C_{a-1} != 0 mod p and nu(a) = #{1 <= j <= a : C_{j-1} != 0 mod p} <= n (a linear form in n root-curve
coordinates then has order exactly a).  When n >= m, h = rho_{<=n}(m+1) (Menezes' formula, extended from n >= k-1 to n >= k-l-1).
Reads the kernel JSONs of research/results/bmd-r9-odd-cube/pP and reports violations and equality.
Usage: bmd_cube_rho_cap_check.py RESULTS_DIR p
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


def main():
    root, p = Path(sys.argv[1]), int(sys.argv[2])
    above, eq_fail, eq_ok, total, eq_all, beyond, beyond_eq = [], [], 0, 0, 0, 0, 0
    for f in sorted(root.glob('cube-p%d-n*-k*.json' % p)):
        d = json.loads(f.read_text())
        n, k = d['n'], d['k']
        best = rho_capped(p, n, k)
        for l, v in enumerate(d['delta']):
            m = k - l - 1
            h = n + 2 * (k - 1) - v
            total += 1
            if h > best[m]:
                above.append((n, k, l, h, best[m]))
            eq_all += h == best[m]
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
    print(f'p={p}: values with n >= m and n < k-1 (beyond Menezes range): {beyond}, equalities: {beyond_eq}')


if __name__ == '__main__':
    main()
