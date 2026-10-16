"""Common-kernel certificates for coordinate families: trivial, greedy transversal, Harris, summed count.

Statements tested (arithmetic for entry-2026-10-16-harris-certificate):
- small inventory: M <= k always gives a common kernel (one pinned literal per block, fresh rows),
  because each block pins at least r > l(k-1) bits; certified ln M = ln k.
- lem:greedy-transversal-certificate: with f_i = (r - l i)/V (V = v when every bit has one pinned
  constant across the family, V = 2v in general), a kernel exists when
  ln M <= ln(k-t) - sum_{i<t} ln(1-f_i) for some 0 <= t <= k-1.
- lem:harris-kernel-certificate in the literal model: harris_range.certified with l (consistent pins)
  or 2l (general pins) in place of l.
Compared with the summed count -k ln x - ln(rho x/(rho x-1)) and the ceiling rk/(v-r-k)+ln(k ln(v+1)+1).
Expected: greedy > trivial > Harris at every row; greedy (consistent pins) about 7.1 at l=16, D=107;
every certificate below the ceiling.
Refuted by: a certificate value above the ceiling, which the ceiling family forbids for all pins.
Possible because: an error in the greedy fraction or the finishing step would inflate its range.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harris_range import certified


def greedy(ell, v_eff, k, r):
    t = np.arange(0, k)
    f = (r - ell * np.arange(0, k)) / v_eff
    assert (f > 0).all() and (f < 1).all()
    gain = np.concatenate([[0.0], np.cumsum(-np.log1p(-f))[:-1]])
    value = np.log(k - t) + gain
    best = int(np.argmax(value))
    return float(value[best]), best


def row(ell, degree):
    n = 2 ** ell
    m = n + 1
    v = m * ell
    k = (n + 1) // (2 * (degree + 1))
    r = 3 * ell * (k + 1) + 1
    assert k >= 1 and r > ell * (k - 1) and r + k < v
    x = 1 - r / v
    rho = (m - k + 1) * ell / k
    summed = -k * math.log(x) - math.log(rho * x / (rho * x - 1))
    ceiling = r * k / (v - r - k) + math.log(k * math.log(v + 1) + 1)
    g_cons, t_cons = greedy(ell, v, k, r)
    g_gen, t_gen = greedy(ell, 2 * v, k, r)
    h_cons = certified(m, ell, k, r)[0]
    h_gen = certified(m, 2 * ell, k, r)[0]
    out = dict(ell=ell, D=degree, k=k, r=r, summed=summed, trivial=math.log(k),
               greedy_consistent=g_cons, greedy_t_consistent=t_cons,
               greedy_general=g_gen, greedy_t_general=t_gen,
               harris_consistent=h_cons, harris_general=h_gen, ceiling=ceiling)
    for name in ('summed', 'trivial', 'greedy_consistent', 'greedy_general', 'harris_consistent', 'harris_general'):
        assert out[name] < ceiling, f'{name} above the ceiling at {ell}, {degree}'
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    cases = [(16, 107), (16, 97), (16, 127)] + [(ell, 6 * ell + 1) for ell in (18, 20, 24)]
    cases += [(ell, (2 ** ell + 1) // (2 * math.isqrt(2 ** ell + 1)) - 1) for ell in (20, 24)]
    rows = [row(*case) for case in cases]
    for item in rows:
        print({key: (round(val, 3) if isinstance(val, float) else val) for key, val in item.items()})
    with open(args.out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()
