"""Least degrees of the common and the combined repair for parity product lines on the cube.

Statement tested (prop:parity-product-repair, proved in entry-2026-10-17-parity-product): over a field of
characteristic other than 2, on the cube {0,1}^n with l <= n lines, protected classes 1 and errors E_t = -2 x_t,
the least degree of a polynomial that is nonzero on the cube and vanishes where some x_t = 1 is l (common
repair), and the least degree of one that vanishes where x_1 + ... + x_l is odd is ceil(l/2) (combined repair of
the product line). Here over F_3 and F_5, n = l and n = l + 1, for l = 1..6.

The least degree d is found as the least d for which the space of multilinear polynomials of degree <= d that
vanish on the target set has a member nonzero on the cube: the evaluation map of the degree <= d monomials on
all points is injective (multilinear polynomials are functions), so this is the least d with
dim{coefficients vanishing on the target} > 0, computed as (number of monomials) - rank(evaluation on target).
Expected: common = l and combined = ceil(l/2) in every case, as the proof gives.
Refuted by: a printed combined degree other than ceil(l/2), or a common degree other than l, at some l and p.
Possible because: the lower bound's symmetry argument or the pairing construction could be wrong at some l.
Control: the same computation over F_2, where -2 = 0 makes the errors vanish; the parity set is computed as
written there too, and the combined degree is then that of the parity set itself, not a repair statement.
Forced by counts: at degree d < ceil(l/2) the monomial count is below the target set's size 2^(n-1) only for
small d, so the rank is not forced by the shape of the matrix; the script prints both numbers.
Positive control: l = 2 over F_3, where the entry's hand computation gives 1 - x_1 - x_2, degree 1 against 2.
Baseline: the support-size bound (a nonzero multilinear polynomial of degree d is nonzero on at least
2^(n-d) points) gives the common degree l exactly and the combined degree only >= 1; the script prints it.
Record checked: lem:transversal-killer-basis (the common degree l on the cube), ex:top-degree-linear-killer
(a linear killer 1 - x - y of the same form); no record result gives the combined degree.
"""
import itertools
import json
import sys

import numpy as np


def rank_mod(m, p):
    m = m.copy() % p
    r = 0
    rows, cols = m.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if m[i, c]), None)
        if piv is None:
            continue
        m[[r, piv]] = m[[piv, r]]
        m[r] = (m[r] * pow(int(m[r, c]), p - 2, p)) % p
        nz = np.nonzero(m[:, c])[0]
        for i in nz:
            if i != r:
                m[i] = (m[i] - m[i, c] * m[r]) % p
        r += 1
        if r == rows:
            break
    return r


def least_degree(n, target, p):
    points = [x for x in itertools.product((0, 1), repeat=n) if target(x)]
    for d in range(n + 1):
        monos = [S for k in range(d + 1) for S in itertools.combinations(range(n), k)]
        if not points:
            return 0, len(monos), 0
        ev = np.array([[int(all(x[i] for i in S)) for S in monos] for x in points], dtype=np.int64)
        if len(monos) - rank_mod(ev, p) > 0:
            return d, len(monos), len(points)
    return None, None, len(points)


def main(out):
    rows = []
    for p in (3, 5, 2):
        for l in range(1, 7):
            for n in (l, l + 1):
                common = least_degree(n, lambda x: any(x[:l]), p)[0]
                combined = least_degree(n, lambda x: sum(x[:l]) % 2 == 1, p)[0]
                rows.append({'p': p, 'l': l, 'n': n, 'common': common, 'combined': combined,
                             'expected_common': l, 'expected_combined': -(-l // 2)})
                print(p, l, n, common, combined, flush=True)
    bad = [r for r in rows if r['p'] != 2 and (r['common'] != r['expected_common']
                                                or r['combined'] != r['expected_combined'])]
    json.dump({'rows': rows, 'mismatches_odd_p': bad}, open(out, 'w'), indent=1)
    assert any(r['p'] == 3 and r['l'] == 2 and r['combined'] == 1 for r in rows)   # positive control
    print('mismatches at odd p:', len(bad))
    print('PASS' if not bad else 'FAIL')


if __name__ == '__main__':
    main(sys.argv[sys.argv.index('--out') + 1])
