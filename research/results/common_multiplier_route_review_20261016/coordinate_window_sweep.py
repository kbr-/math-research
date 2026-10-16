"""Sweep of the coordinate-count window over l at the minimal degree D = 2h+1 = 6l+1.

Statement tested (arithmetic for the route review entry-2026-10-16-joint-savings-review): with
K_D = floor((n+1)/(2(D+1))), r = 3l(K_D+1)+1, x = 1-r/v, the certified main term -K_D ln x of
prop:coordinate-count-window and the ceiling main term r K_D/(v-r-K_D) of prop:common-kernel-ceiling
differ by about (r K_D/v)(r/(2v)+K_D/v), which grows with l at minimal D; the logarithmic term
ln(K_D ln(v+1)+1) grows only linearly in l.
Expected: at l = 16 (and also D = 107) the main-term gap is below 0.1; by l = 32 at minimal D it
exceeds the logarithmic term by far (hundreds against about 20).
Refuted by: a printed main-term gap that is negative, or one that stays below the log term at l=32.
Possible because: the gap's growth depends on K_D/m and r/v, which a wrong K_D formula would change.
"""
import argparse
import json
import math


def row(ell, degree):
    n = 2 ** ell
    m = n + 1
    v = m * ell
    h = 3 * ell
    k = (n + 1) // (2 * (degree + 1))
    assert k >= 1 and 2 * k * (degree + 1) - 1 <= n < 2 * (k + 1) * (degree + 1) - 1
    r = h * (k + 1) + 1
    assert r + k < v
    x = 1 - r / v
    certified = -k * math.log(x)
    ceiling = r * k / (v - r - k)
    log_term = math.log(k * math.log(v + 1) + 1)
    return dict(ell=ell, D=degree, K_D=k, r=r, certified_main=certified, ceiling_main=ceiling,
                main_gap=ceiling - certified, log_term=log_term, published=k * k / m)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    rows = [row(16, 107)] + [row(ell, 6 * ell + 1) for ell in (16, 20, 24, 28, 32)]
    for item in rows:
        print(item)
        assert item['main_gap'] > 0
    assert rows[-1]['main_gap'] > rows[-1]['log_term']
    with open(args.out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()
