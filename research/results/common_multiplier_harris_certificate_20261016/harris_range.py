"""Range of the Harris kernel certificate for coordinate blocks, against the summed count and ceiling.

Statement tested (arithmetic for entry-2026-10-16-harris-certificate, lemma lem:harris-kernel-certificate):
for coordinate blocks pinning at least r bits, with pi = mu/m, J = floor(eps/pi) >= 1,
c0 = ceil(r/(2l)), y = (1 - eps/2) mu r / v, g(y) = -ln(1 - e^{-y}),
tail = e^{-eps c0} / (J (1 - e^{-pi c0})) and h(t) = t ln t - t + 1, a common row-linear kernel in
L_k exists when M e^{-r/(8l)} <= 1/2 and 2 M (g(y) + tail) < mu h(k/mu), mu < k. So the certified
ln M is ln(mu h(k/mu)) - ln 2 - ln(g(y) + tail), maximized over mu and eps; it is compared with the
summed count -k ln x - ln(rho x/(rho x - 1)) and the ceiling r k/(v-r-k) + ln(k ln(v+1)+1).
Expected: at l = 16, D = 107 the certificate exceeds the summed count (about 5.5 to 6 against
4.25); at minimal degree D = 6l+1 it falls below the summed count by l = 20 or 24.
Refuted by: a certified value above the ceiling, which would contradict the ceiling's construction.
Possible because: an error in g, the tail or the Chernoff term would inflate the certified range.
"""
import argparse
import json
import math


def certified(m, ell, k, r):
    v = m * ell
    c0 = math.ceil(r / (2 * ell))
    best = (-math.inf, None, None)
    for mu_step in range(1, 400):
        mu = k * mu_step / 400
        pi = mu / m
        h = (k / mu) * math.log(k / mu) - k / mu + 1
        mass = mu * h
        for eps_step in range(1, 100):
            eps = eps_step / 100
            jj = math.floor(eps / pi)
            if jj < 1:
                continue
            y = (1 - eps / 2) * mu * r / v
            g = -math.log(-math.expm1(-y))
            tail = math.exp(-eps * c0) / (jj * -math.expm1(-pi * c0))
            value = math.log(mass) - math.log(2) - math.log(g + tail)
            if value > best[0]:
                best = (value, mu, eps)
    cap = r / (8 * ell) - math.log(2)
    return min(best[0], cap), best[1], best[2], cap


def row(ell, degree):
    n = 2 ** ell
    m = n + 1
    v = m * ell
    h = 3 * ell
    k = (n + 1) // (2 * (degree + 1))
    r = h * (k + 1) + 1
    x = 1 - r / v
    rho = (m - k + 1) * ell / k
    summed = -k * math.log(x) - math.log(rho * x / (rho * x - 1))
    ceiling = r * k / (v - r - k) + math.log(k * math.log(v + 1) + 1)
    harris, mu, eps, cap = certified(m, ell, k, r)
    assert harris < ceiling, 'a certificate above the ceiling would contradict the ceiling family'
    return dict(ell=ell, D=degree, k=k, r=r, summed=summed, harris=harris, mu=mu, eps=eps,
                goodness_cap=cap, ceiling=ceiling, harris_minus_summed=harris - summed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    rows = [row(16, 107)] + [row(ell, 6 * ell + 1) for ell in (16, 18, 20, 24)]
    for item in rows:
        print(item)
    with open(args.out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()
