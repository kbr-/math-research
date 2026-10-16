"""Strip versus hypograph discrepancy along adaptively chosen slope-one grid paths.

Statement tested (the fourth route review's Hammersley lead): for N uniform points in [0,1]^2 and
paths choosing one row per column of an M x M grid (M = sqrt(N)/2, about 4 points per cell) with
row changes of at most one, the maximal excess over N * area of a strip of q rows above the path
grows with q but not with N at fixed q (strips see no coarse scales), while the maximal excess of
the hypograph below the path grows with N like Leighton-Shor's (log N)^(3/4).

Expected outcome, written before the run: at q = 4 the strip maximum over sqrt(N) changes by less
than 30% from N = 2^12 to N = 2^22 (median over seeds); the hypograph maximum over sqrt(N) grows by
a factor of at least 1.3 over the same range (Leighton-Shor predicts about 1.57).
Refuted by: a strip maximum over sqrt(N) at q = 4 growing by more than 30% across the range.
Possible because: if strips inherited the coarse-scale gains of hypographs, they would follow the
(log N)^(3/4) growth, a factor of about 1.57 across this range.
Positive control: the hypograph maximum, which must grow by at least 1.3 across the range.
Refuted by: a hypograph ratio below 1.3, which would mean the grid paths cannot show the growth.
Possible because: slope-one paths at about two points per cell side may not realize the
Leighton-Shor tents at these sizes.
"""
import argparse
import json

import numpy as np


def path_max(weights):
    """Maximum over paths (one row per column, row change at most one) of the summed weights."""
    value = weights[0].copy()
    for col in range(1, weights.shape[0]):
        best = value.copy()
        best[1:] = np.maximum(best[1:], value[:-1])
        best[:-1] = np.maximum(best[:-1], value[1:])
        value = best + weights[col]
    return float(value.max())


def run(log2n, seed, widths):
    n = 1 << log2n
    m = 1 << (log2n // 2 - 1)
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2))
    counts = np.zeros((m, m))
    np.add.at(counts, (np.minimum((pts[:, 0] * m).astype(int), m - 1),
                       np.minimum((pts[:, 1] * m).astype(int), m - 1)), 1)
    excess = counts - n / m ** 2
    cum = np.concatenate([np.zeros((m, 1)), np.cumsum(excess, axis=1)], axis=1)
    row = {'log2N': log2n, 'seed': seed, 'M': m,
           'hypograph': path_max(cum) / np.sqrt(n)}
    for q in widths:
        strip = cum[:, q:] - cum[:, :-q]
        row[f'strip_q{q}'] = path_max(strip) / np.sqrt(n)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    widths = [1, 2, 4, 8, 16]
    rows = [run(k, s, widths) for k in range(12, 23, 2) for s in range(4)]
    with open(args.out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    keys = ['hypograph'] + [f'strip_q{q}' for q in widths]
    medians = {k: {key: float(np.median([r[key] for r in rows if r['log2N'] == k])) for key in keys}
               for k in range(12, 23, 2)}
    for k, med in medians.items():
        print(k, ' '.join(f'{key}={val:.3f}' for key, val in med.items()))
    ratio = {key: medians[22][key] / medians[12][key] for key in keys}
    print('ratio 2^22/2^12:', ' '.join(f'{key}={val:.3f}' for key, val in ratio.items()))
    print('strip q4 prediction', 'held' if abs(ratio['strip_q4'] - 1) < 0.3 else 'failed')
    print('positive control', 'held' if ratio['hypograph'] >= 1.3 else 'failed')


if __name__ == '__main__':
    main()
