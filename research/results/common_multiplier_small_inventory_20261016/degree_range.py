"""Largest excluded degree for complete coordinate families, by the kernel certificate used.

Statement tested (arithmetic for entry-2026-10-16-small-inventory-exclusion, thm:small-inventory-coordinate-exclusion):
Braun's finite-parameter theorem excludes degree D for a k with 2k(D+1)-1 <= n, 4(k-1) < n, k <= m,
D >= 6l+1, given a nonzero common kernel in L_k for the proper blocks of rank > 3l(k+1). The best D for
a k is floor((n+1)/(2k)) - 1, decreasing in k, so each certificate's range is set by its smallest k:
- published count: m ln(4M) <= k^2;
- summed count (prop:coordinate-count-window, coordinate blocks of rank r = 3l(k+1)+1):
  ln M < -k ln(1-r/v) - ln(rho x/(rho x-1));
- greedy (lem:greedy-transversal-certificate, general pins V = 2v): some 0 <= t <= k-1 with
  ln M <= ln(k-t) - sum_{i<t} ln(1-(r-l i)/V); its t = 0 case is M <= k.
Expected: for M = 1, 2, 16 the greedy degree is about (n+1)/(2M) - 1, far above the published and
summed degrees (about sqrt(n)/(2 sqrt(ln 4M)) and sqrt(3n/ln M)/2); at M = n and n^2 the summed count
gives the largest degree and the greedy gain is small or none.
Refuted by: a greedy smallest k larger than M for M <= m, since t = 0 certifies k = M,
or the closed-form greedy value differing from the direct sum at l = 16 by more than 1e-6.
Possible because: an indexing error in the greedy scan would raise its smallest k above M.
Also refuted by: a non-monotone certificate in k on the full l = 16 scan, which would invalidate the
binary search used at larger l.
Possible because: the greedy optimum over t could in principle drop as r grows with k.
The baselines' smallest k is taken from a full scan of every allowed k, and the binary search is kept
only as a cross-check (it must return a certifying k at or above the scanned one).
Refuted by: a binary-search baseline k below the full-scan smallest k, which would mean a bad scan.
Possible because: an off-by-one in the vectorized scan would shift every scanned index by one.
"""
import argparse
import json
import math

import numpy as np


def params(ell):
    n = 2 ** ell
    m = n + 1
    return n, m, m * ell, 3 * ell


def published(ell, M, k):
    n, m, v, h = params(ell)
    return m * math.log(4 * M) <= k * k


def summed(ell, M, k):
    n, m, v, h = params(ell)
    r = h * (k + 1) + 1
    if r + k >= v:
        return False
    x = 1 - r / v
    rho = (m - k + 1) * ell / k
    if rho * x <= 1:
        return False
    return math.log(M) < -k * math.log(x) - math.log(rho * x / (rho * x - 1))


def greedy_value(ell, k):
    """max over 0 <= t <= k-1 of ln(k-t) - sum_{i<t} ln(1-(r-l i)/V), V = 2v, in closed form:
    prod_{i<t}(1-(r-l i)/V) = (l/V)^t Gamma(c+t)/Gamma(c), c = (V-r)/l.  The increment from t to t+1,
    ln(1-1/(k-t)) - ln(1-f_t), decreases in t (f_t falls, 1/(k-t) rises), so the optimum is the first t
    whose increment is not positive, found by binary search."""
    n, m, v, h = params(ell)
    V = 2 * v
    r = h * (k + 1) + 1
    assert r - ell * (k - 1) > 0 and r < V
    c = (V - r) / ell

    def gain(t):
        return -t * math.log(ell / V) - math.lgamma(c + t) + math.lgamma(c)

    def increment(t):
        f = (r - ell * t) / V
        return math.log1p(-1 / (k - t)) - math.log1p(-f)

    lo, hi = 0, k - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if increment(mid) > 0:
            lo = mid + 1
        else:
            hi = mid
    return math.log(k - lo) + gain(lo)


def greedy_value_direct(ell, k):
    n, m, v, h = params(ell)
    r = h * (k + 1) + 1
    i = np.arange(0, k)
    f = (r - ell * i) / (2 * v)
    g = np.concatenate([[0.0], np.cumsum(-np.log1p(-f))[:-1]])
    return float(np.max(np.log(k - i) + g))


def greedy(ell, M, k):
    return math.log(M) <= greedy_value(ell, k) + 1e-9


METHODS = {'published': published, 'summed': summed, 'greedy': greedy}


def smallest_k(ell, M, test):
    n, m, v, h = params(ell)
    # Only k with D = floor((n+1)/(2k)) - 1 >= 2h+1 matter: k <= (n+1)/(2(2h+2)).  There r = h(k+1)+1 is
    # below v/4, inside every certificate's hypotheses; beyond, the summed count stops being monotone.
    hi = (n + 1) // (2 * (2 * h + 2))
    if not test(ell, M, hi):
        return None
    lo = 1
    while lo < hi:
        mid = (lo + hi) // 2
        if test(ell, M, mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def exact_baseline_k(ell, M, name):
    """The smallest k at which a baseline certifies, by a full scan of every allowed k (vectorized), with
    no monotonicity assumption: the binary search can return a certifying k above the smallest one, and
    an understated baseline would overstate the greedy gain (review of 16 October 2026)."""
    n, m, v, h = params(ell)
    hi = (n + 1) // (2 * (2 * h + 2))
    k = np.arange(1, hi + 1, dtype=np.float64)
    if name == 'published':
        ok = m * math.log(4 * M) <= k * k
    else:
        r = h * (k + 1) + 1
        x = 1 - r / v
        rho = (m - k + 1) * ell / k
        rx = rho * x
        valid = (r + k < v) & (rx > 1)
        rhs = np.where(valid, -k * np.log(x) - np.log(np.where(valid, rx / (rx - 1), 2.0)), -np.inf)
        ok = math.log(M) < rhs
    hits = np.flatnonzero(ok)
    return int(hits[0]) + 1 if hits.size else None


def degree(ell, k):
    n, m, v, h = params(ell)
    if k is None or k > m or 4 * (k - 1) >= n:
        return None
    D = (n + 1) // (2 * k) - 1
    return D if D >= 2 * h + 1 else None


def monotone_check(ell, M, test, kmax):
    seen = False
    for k in range(1, kmax + 1):
        ok = test(ell, M, k)
        assert not (seen and not ok), f'non-monotone at l={ell}, M={M}, k={k}'
        seen = seen or ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    for M in (1, 2, 16, 256, 65537):
        for test in METHODS.values():
            monotone_check(16, M, test, 1500)
    # The closed form against the direct sum, an independent route, on every k to 1500 at l = 16.
    worst = max(abs(greedy_value(16, k) - greedy_value_direct(16, k)) for k in range(1, 1501))
    print('closed form vs direct sum, largest difference', worst, 'tolerance 1e-6')
    assert worst < 1e-6
    rows = []
    for ell in (16, 20, 24, 28, 32):
        n = 2 ** ell
        for label, M in (('1', 1), ('2', 2), ('16', 16), ('n^(1/4)', round(n ** 0.25)), ('n^(1/2)', round(n ** 0.5)),
                         ('n', n), ('n^2', n * n)):
            row = dict(ell=ell, M_label=label, M=M)
            for name, test in METHODS.items():
                k = smallest_k(ell, M, test)
                if name != 'greedy':
                    exact = exact_baseline_k(ell, M, name)
                    row[name + '_k_search'] = k
                    assert (k is None) == (exact is None) and (k is None or exact <= k)
                    k = exact
                row[name + '_k'] = k
                row[name + '_D'] = degree(ell, k)
            if M <= (n + 1) // (2 * (6 * ell + 2)):
                assert row['greedy_k'] is not None and row['greedy_k'] <= M, 'the t = 0 case certifies k = M'
            rows.append(row)
            print(row)
    with open(args.out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()
