"""Check the explicit parameters of the shell corollary for zeta at x = 1/4.

Statement tested: with a = 2, b = 1, x = 1/4, t = 0.6, r = 0.08, mu = x/r, R1 = mu + 1/4 + x/2,
R2 = mu + 3/4, kappa = 0.02, eps = 0.02, lambda = a mu / t, l = log(8e(lambda + kappa + 1)/kappa),
the strict inequalities of the corollary in parameters hold:
  kappa l + (lambda + kappa) log(1+r) < min(b, lambda h(t), lambda log(1 + 1/mu)),
  kappa l < lambda log(R1/(mu + x)),   kappa l < eps lambda,
and mu + x < R1 < mu + 1/2 < R2.  Also prints the Jensen-type count constant M0/log(R2/R1), M0 = 2.
Also asserts the two geometric facts the proof uses: e^eps (mu + x) < R1 and 1 + mu - R2 >= 1/4.
Arithmetic only, in floating point; the rational lines only confirm that the three rational inputs
(mu, R1, lambda) were formed as intended and are not an independent check of any inequality.
"""
import json
import sys
from fractions import Fraction
from math import e, log

a, b, x, t, r, kappa, eps, M0 = 2, 1, 0.25, 0.6, 0.08, 0.02, 0.02, 2
mu = x / r
R1 = mu + 0.25 + x / 2
R2 = mu + 0.75
lam = a * mu / t
ell = log(8 * e * (lam + kappa + 1) / kappa)
h = t - 1 - log(t)
left = kappa * ell + (lam + kappa) * log(1 + r)
out = {
    'mu': mu, 'R1': R1, 'R2': R2, 'lambda': lam, 'l': ell, 'h(t)': h,
    'kappa*l': kappa * ell, 'left': left,
    'b': b, 'lambda*h(t)': lam * h, 'lambda*log(1+1/mu)': lam * log(1 + 1 / mu),
    'lambda*log(theta)': lam * log(R1 / (mu + x)), 'eps*lambda': eps * lam,
    'real part of the disk at least': 1 + mu - R1,
    'count constant M0/log(R2/R1)': M0 / log(R2 / R1),
    'threshold exp(1/kappa)': f'exp({1 / kappa:.0f})',
}
from math import exp
assert exp(eps) * (mu + x) < R1 and 1 + mu - R2 >= 0.25
out['shell outer radius e^eps (mu+x)'] = exp(eps) * (mu + x)
out['bracket step needs (M0/log(R2/R1)) L <= tau^(eps*lambda - kappa*l), exponent'] = eps * lam - kappa * ell
out['margin of the first inequality'] = min(b, lam * h, lam * log(1 + 1 / mu)) - left
# The three rational inputs formed in exact rationals, to confirm the floats above.
xq, rq, tq = Fraction(1, 4), Fraction(2, 25), Fraction(3, 5)
muq = xq / rq
for exact, value in ((muq, mu), (muq + Fraction(1, 4) + xq / 2, R1), (2 * muq / tq, lam)):
    assert abs(float(exact) - value) < 1e-12, (exact, value)
assert mu + x < R1 < mu + 0.5 < R2
assert left < min(b, lam * h, lam * log(1 + 1 / mu))
assert kappa * ell < lam * log(R1 / (mu + x)) and kappa * ell < eps * lam
out['all inequalities hold'] = True
json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
print(json.dumps(out, indent=1))
