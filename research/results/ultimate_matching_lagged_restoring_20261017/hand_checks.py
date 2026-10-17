"""No statement tested: two hand-step checks for the lagged restoring flow entry.
(1) The symmetric two-child model's optimal exchange, cost 2 psi(R - m) + psi(2m), for psi(x) = x^4 and
psi(x) = exp(x^4) - 1, at R = 0.5, 1, 1.5: the minimizer, against R/3.
(2) The variance baseline: for a Gaussian with variance ratio v to the dyadic flow, its fraction beyond t dyadic
standard deviations relative to the dyadic flow's, erfc(t/sqrt(2v))/erfc(t/sqrt 2), at v = 0.78 and 1.23."""
import math
import numpy as np
for name, psi in (('x^4', lambda x: x ** 4), ('exp(x^4)-1', lambda x: np.expm1(x ** 4))):
    for R in (0.5, 1.0, 1.5):
        ms = np.linspace(0, R, 200001)
        f = 2 * psi(R - ms) + psi(2 * ms)
        print(f'(1) psi={name} R={R}: argmin m={ms[f.argmin()]:.5f}, R/3={R / 3:.5f}')
for v in (0.78, 1.23):
    for t in (2.5, 3.0, 3.5):
        print(f'(2) variance ratio {v}, t={t}: Gaussian fraction ratio '
              f'{math.erfc(t / math.sqrt(2 * v)) / math.erfc(t / math.sqrt(2)):.4f}')
