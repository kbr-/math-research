"""Window of the common-kernel step for coordinate blocks at l = 16, D = 107.

Statement tested (arithmetic for the route review entry-2026-10-16-joint-savings-review):
for proper coordinate blocks pinning at least r bits of the v = m*l old bits, the exact summed
count certifies a common row-linear kernel in L_k when
    ln M < -k ln(1 - r/v) - ln(rho x / (rho x - 1)),
with x = 1 - r/v and rho = (m - k + 1) l / k, while the ceiling family of prop:common-kernel-ceiling
at the same k and r has no kernel with ln M <= r k / (v - r - k) + ln(k ln(v+1) + 1).
At k = K_D = 303 (D = 107) and r = r_D = h(K_D+1)+1.
Expected: certified bound about 4.2, ceiling bound about 12.62, main terms 4.2 and 4.28.
Refuted by: rho x <= 1, which voids the geometric bound, or a certified bound above the ceiling.
Possible because: a wrong rho, x or k would change both bounds and could reverse their order.
"""
import argparse
import json
import math


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    ell = 16
    n = 2 ** ell
    m = n + 1
    v = m * ell
    h = 3 * ell
    degree = 107
    k = (n + 1) // (2 * (degree + 1))
    assert 2 * k * (degree + 1) - 1 <= n < 2 * (k + 1) * (degree + 1) - 1
    r = h * (k + 1) + 1
    x = 1 - r / v
    rho = (m - k + 1) * ell / k
    assert rho * x > 1
    main_certified = -k * math.log(x)
    certified = main_certified - math.log(rho * x / (rho * x - 1))
    main_ceiling = r * k / (v - r - k)
    ceiling = main_ceiling + math.log(k * math.log(v + 1) + 1)
    result = dict(ell=ell, n=n, m=m, v=v, D=degree, k=k, r=r, x=x, rho=rho, rho_x=rho * x,
                  certified_main=main_certified, certified_ln_M=certified,
                  ceiling_main=main_ceiling, ceiling_ln_M=ceiling, window=ceiling - certified,
                  rk_over_v=r * k / v)
    for key, value in result.items():
        print(f'{key} = {value}')
    assert certified < ceiling
    with open(args.out, 'w') as handle:
        json.dump(result, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()
