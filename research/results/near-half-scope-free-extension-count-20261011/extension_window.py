"""Scope-free extension window for random k-CNF: evaluation of two closed formulas.

Statement evaluated (entry-2026-10-11-scope-free-extension-window).  For m = d*v uniformly random
k-clause scopes on v variables, a set S is scope-free if it contains no scope, and x outside S is a
scope-free extension if S + x is scope-free.

upper(k, d): the least c in (0, 1/2] from which
    f(c) = H(c) + (1-c) H(c/(1-c)) + d ln(1 - c^k - k c^k) < 0     (natural logarithms)
holds on [c, 1/2]: the first-moment exponent of pairs (S, X), |S| = |X| = c v, S scope-free and every
x in X an extension.  Above it, with high probability every scope-free set has fewer scope-free
extensions than elements.

lower(k, d): the largest sigma = c - d c^k over c with (1-c) exp(-d k c^(k-1)) > sigma: a random set
of size c v, pruned by one variable for each scope inside it, is scope-free of size at least sigma v
and has more than sigma v extensions.

The table repeats the rows of the calibration of 9 October (typical_extension_cutoff.txt) and prints
its thin thresholds beside the window; those are copied constants, not recomputed here.
"""
import argparse
import math

ROWS = [(3, 4.27, 0.341), (3, 10.0, 0.275), (4, 9.93, 0.3555), (5, 21.1, 0.37), (7, 87.8, 0.3925),
        (10, 708.0, 0.414)]
STEP = 1e-4


def entropy(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log(p) - (1 - p) * math.log(1 - p)


def exponent(c, k, d):
    inside = 1 - c ** k - k * c ** k
    if inside <= 0:
        return -math.inf
    return entropy(c) + (1 - c) * entropy(c / (1 - c)) + d * math.log(inside)


def upper(k, d):
    grid = [i * STEP for i in range(1, int(0.5 / STEP) + 1)]
    last_nonnegative = max((c for c in grid if exponent(c, k, d) >= 0), default=0.0)
    return last_nonnegative + STEP


def lower(k, d):
    best = (0.0, 0.0)
    for i in range(1, int(0.5 / STEP) + 1):
        c = i * STEP
        sigma = c - d * c ** k
        if sigma > best[0] and (1 - c) * math.exp(-d * k * c ** (k - 1)) > sigma:
            best = (sigma, c)
    return best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    lines = ['k\tdensity\tlower\tat_c\tupper\tthin_threshold_copied\tthin_inside_window']
    for k, d, thin in ROWS:
        low, at = lower(k, d)
        up = upper(k, d)
        lines.append(f'{k}\t{d}\t{low:.4f}\t{at:.4f}\t{up:.4f}\t{thin}\t{low < thin < up}')
    with open(args.out, 'w') as out:
        out.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
