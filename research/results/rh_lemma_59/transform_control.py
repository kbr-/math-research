"""Numerical control of the two computed ingredients of the one-sided equivalence for infinite configurations.

Statements tested:
 T. For complex w and Re s > |Im w|:  int_0^infty  2(1 - cos(L w))/w^2 * exp(-s L) dL  =  2/(s (s^2 + w^2)).
 R. The function 2 m/(s (s^2 + w^2)) has at s0 = i w (and at s0 = -i w) a simple pole with residue m/s0^2;
    for the two points z = gamma + i delta and z' = (2 tau - gamma) - i delta, seen from tau, the poles at
    s0 = delta + i (tau - gamma) coincide and their residues m/s0^2 and m'/s0^2 add without cancelling.

Method: T by adaptive quadrature of the real and imaginary parts on [0, X] with X chosen so that the neglected
tail is below 1e-12 (the script prints its bound), against the closed form, which the quadrature does not use.
R by evaluating (s - s0) * (sum of the two terms) at s = s0 + 1e-6 e^{i phi} for four directions phi, against
(m + m')/s0^2, with tolerance 1e-4 times its modulus (the next term of the expansion is of relative size 1e-6
divided by the distance to the nearest other pole, which the script prints).

Expected, written before the run: T holds in all cases to 1e-8 relative; R holds in all cases to 1e-4 relative.
Negative control for T: the closed form with s^2 - w^2 in place of s^2 + w^2; the script asserts that the two
closed forms differ by more than 1e-3 relative in each case, and the altered one is expected to fail in all.
"""
import cmath
import math

from scipy.integrate import quad

CASES = [  # (w, s): Re s > |Im w|
    (1.3 - 0.4j, 0.9 + 0.0j), (0.2 - 0.45j, 1.0 + 2.0j), (5.0 + 0.3j, 0.8 - 1.5j), (0.05 - 0.1j, 0.6 + 0.3j),
    (2.0 + 0.0j, 0.5 + 0.0j), (-3.1 - 0.25j, 0.75 + 4.0j), (0.7 - 0.49j, 1.2 - 0.6j), (12.0 - 0.2j, 0.7 + 0.1j),
]


def transform(w, s):
    margin = s.real - abs(w.imag)
    assert margin > 0
    upper = 60.0 / margin                                    # tail below 4 e^{-60}/(|w|^2 margin)
    tail = 4 * math.exp(-60.0) / (abs(w) ** 2 * margin)
    f = lambda t: 2 * (1 - cmath.cos(t * w)) / w ** 2 * cmath.exp(-s * t)
    re = quad(lambda t: f(t).real, 0, upper, limit=4000, epsabs=1e-13, epsrel=1e-12)[0]
    im = quad(lambda t: f(t).imag, 0, upper, limit=4000, epsabs=1e-13, epsrel=1e-12)[0]
    return complex(re, im), tail


def main():
    worst = worst_control = 0.0
    for w, s in CASES:
        value, tail = transform(w, s)
        closed = 2 / (s * (s * s + w * w))
        altered = 2 / (s * (s * s - w * w))
        assert abs(closed - altered) > 1e-3 * abs(closed), 'the control does not differ here'
        worst = max(worst, abs(value - closed) / abs(closed))
        worst_control = max(worst_control, 0.0) if abs(value - altered) / abs(closed) > 1e-3 else float('inf')
        print(f'T  w={w}  s={s}  quadrature {value:.12g}  closed form {closed:.12g}  '
              f'relative deviation {abs(value - closed) / abs(closed):.1e} (tail bound {tail:.1e}); '
              f'altered form off by {abs(value - altered) / abs(closed):.1e}')
    print(f'T: largest relative deviation {worst:.1e} against 1e-8: ' + ('holds' if worst < 1e-8 else 'FAILS')
          + '; the altered form ' + ('fails in all cases' if worst_control == 0.0 else 'PASSES SOMEWHERE'))

    worst = 0.0
    for tau, gamma, delta, m, m2 in [(0.3, 1.7, 0.4, 2, 3), (10.0, 9.2, 0.1, 1, 0), (-2.0, 5.5, 0.49, 4, 1)]:
        u = tau - gamma
        s0 = complex(delta, u)
        points = [(complex(gamma, delta), m), (complex(2 * tau - gamma, -delta), m2)]
        total = lambda s: sum(2 * mult / (s * (s * s + (tau - z) ** 2)) for z, mult in points)
        other = min(abs(s0 - p) for p in (0, complex(-delta, u), complex(delta, -u), complex(-delta, -u)))
        for k in range(4):
            eps = 1e-6 * cmath.exp(1j * (0.3 + k * math.pi / 2))
            got = eps * total(s0 + eps)
            want = (m + m2) / s0 ** 2
            worst = max(worst, abs(got - want) / abs(want))
        print(f'R  tau={tau} gamma={gamma} delta={delta} m={m} m\'={m2}: residue {(m + m2) / s0 ** 2:.8g}, '
              f'nearest other pole at distance {other:.2g}')
    print(f'R: largest relative deviation {worst:.1e} against 1e-4: ' + ('holds' if worst < 1e-4 else 'FAILS'))


if __name__ == '__main__':
    main()
