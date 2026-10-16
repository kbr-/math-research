"""Harris certificate against the exact summed count on evenly spread coordinate families.

Statement tested (arithmetic for entry-2026-10-16-harris-certificate, thm:spread-correlation-saving):
fix l, D, K = K_D = floor((n+1)/(2(D+1))), r = 3l(K+1)+1 <= m. For coordinate blocks each pinning r
bits, at most one per row, every exact restriction rank in L_k' (k' <= K) is at least
a_k' (1-1/l)^{k' r/m}, so the exact summed count fails at every k' <= K once
ln M >= L_E = -(K r/m) ln(1-1/l) + ln(rho/(rho-1)), rho = (m-K+1) l/K; while the Harris certificate
(computed as in harris_range.py) gives a kernel in L_K for ln M < L_H. We take D so that K is
about sqrt(m): D = max(6l+1, floor((n+1)/(2 floor(sqrt(m)))) - 1).
Expected: L_H - L_E is positive at every l from 16 to 32 and grows roughly like ln K.
Refuted by: L_H <= L_E at some l in the sweep, or r > m (evenly spread sets impossible).
Possible because: the gain is a few units at these sizes, and the constants in L_H could eat it.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harris_range import certified


def row(ell, degree=None):
    n = 2 ** ell
    m = n + 1
    v = m * ell
    h = 3 * ell
    if degree is None:
        degree = max(6 * ell + 1, (n + 1) // (2 * math.isqrt(m)) - 1)
    k = (n + 1) // (2 * (degree + 1))
    assert 2 * k * (degree + 1) - 1 <= n and 4 * (k - 1) < n and degree >= 2 * h + 1
    r = h * (k + 1) + 1
    assert r <= m, 'evenly spread pinned sets need r <= m'
    rho = (m - k + 1) * ell / k
    exact_fails = -(k * r / m) * math.log(1 - 1 / ell) + math.log(rho / (rho - 1))
    harris, mu, eps, cap = certified(m, ell, k, r)
    ceiling = r * k / (v - r - k) + math.log(k * math.log(v + 1) + 1)
    return dict(ell=ell, D=degree, K=k, r=r, exact_fails_at=exact_fails, harris=harris,
                gain=harris - exact_fails, ceiling=ceiling, mu=mu, eps=eps)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    rows = [row(16, 107)] + [row(ell) for ell in (16, 20, 24, 28, 32)]
    for item in rows:
        print(item)
        assert item['gain'] > 0, 'the Harris certificate must beat the exact-count failure point'
    with open(args.out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()
