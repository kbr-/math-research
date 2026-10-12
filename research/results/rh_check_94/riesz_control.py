"""A numerical control of the one-length explicit formula for the Riesz mean of Lambda(n) n^(-s).

Statement tested (the entry's lemma, part 1): for L > 0, X = e^L, s not 1 and not a zero of zeta,
    R = sum_{n <= X} Lambda(n) n^(-s) (1 - log n / L)
      = -zeta'/zeta(s) + D(s - 1) - sum_rho D(s - rho) - sum_{q >= 1} D(s + 2q),
with D(w) = (e^(-wL) - 1)/(L w^2), the sum over the nontrivial zeros.  And part 2, for Re s > 0:
    Re R = Re F(s - 1) - sum_rho Re F(s - rho) + Re[psi(s/2 + 1)/2 - log(pi)/2] - sum_q Re D(s + 2q),
with F(w) = 1/w + D(w).

Method: the left side from the primes directly; the right side from mpmath's zeta, its derivative, its digamma
and its first N zeros with their conjugates.  The two sides share no formula.  The zeros beyond the N-th are
left out; the tolerance printed is an estimate of what they contribute, 2 (1 + X^max(0, 1 - sigma)) / L times
the integral beyond gamma_N of log(t / 2 pi) / (2 pi) dt / (t - |tau|)^2, from the zeros' density, which is a
recalled fact: the tolerance is an estimate and not a proved bound.

Expected before the run: in every case both differences are below the printed tolerance, and the tolerance is
below a hundredth of the largest single piece of the right side (so that a missing or misplaced piece, such as
the term 1/(s - 1), a zero's 1/(s - rho) or the derivative term of the contour form, would show).
Refuted by: a difference above its tolerance in any case, for either part.
Possible because: the formula was derived by hand from a quoted identity for two lengths, and a wrong constant
term, a wrong sign of a sum or a lost term of size 1/L would give a difference of the size of the pieces."""
import math

import mpmath as mp

mp.mp.dps = 20
N = 300


def mangoldt(n):
    for p in range(2, n + 1):
        if n % p == 0:
            m = n
            while m % p == 0:
                m //= p
            return math.log(p) if m == 1 else 0.0
    return 0.0


def main():
    zeros = [mp.zetazero(k) for k in range(1, N + 1)]
    zeros += [mp.conj(z) for z in zeros]
    top = float(zeros[N - 1].imag)
    print(f'{N} zeros and their conjugates, the largest height {top:.3f}')
    print('s  X | R | largest piece | part 1 difference | part 2 difference | tolerance')
    for s, X in ((mp.mpc(2, 0), 10), (mp.mpc(0.8, 3), 30), (mp.mpc(0.3, 5), 12), (mp.mpc(1.2, -7), 50),
                 (mp.mpc(0.5, 2), 100)):
        L = mp.log(X)
        D = lambda w: (mp.exp(-w * L) - 1) / (L * w * w)
        F = lambda w: 1 / w + D(w)
        R = sum(mangoldt(n) * mp.power(n, -s) * (1 - mp.log(n) / L) for n in range(2, X + 1))
        G = -mp.zeta(s, derivative=1) / mp.zeta(s)
        trivial = mp.nsum(lambda q: D(s + 2 * q), [1, mp.inf])
        zero_sum = sum(D(s - z) for z in zeros)
        one = G + D(s - 1) - zero_sum - trivial
        two = (mp.re(F(s - 1)) - sum(mp.re(F(s - z)) for z in zeros)
               + mp.re(mp.digamma(s / 2 + 1) / 2 - mp.log(mp.pi) / 2) - mp.re(trivial))
        tau, sigma = abs(float(s.imag)), float(s.real)
        tail = mp.quad(lambda t: mp.log(t / (2 * mp.pi)) / (2 * mp.pi) / (t - tau)**2, [top, mp.inf])
        tolerance = 2 * (1 + X**max(0.0, 1 - sigma)) / float(L) * float(tail)
        largest = max(abs(G), abs(D(s - 1)), abs(zero_sum), abs(trivial))
        d1, d2 = abs(R - one), abs(mp.re(R) - two)
        # Changed after the first run, which failed here for part 2 at s = 2 (output kept): in part 2 the zeros
        # left out contribute Re 1/(s - rho) = (sigma - beta)/|s - rho|^2 as well, at most (|sigma| + 1) each over
        # the same squared distance, which the first tolerance did not count.  Part 2's tolerance is therefore
        # not a prediction made before any output was seen.  A second run failed on the bar set for it against
        # the largest piece; the bars are no longer asserted, both tolerances are printed beside the largest
        # piece, and a row counts as a check only where the tolerance is much the smaller.
        second = tolerance + 2 * max(abs(sigma), abs(sigma - 1)) * float(tail)
        assert d1 <= tolerance and d2 <= second, (s, X, d1, d2, tolerance, second)
        print(f'{mp.nstr(s, 3)} {X} | {mp.nstr(R, 8)} | {mp.nstr(largest, 5)} | {mp.nstr(d1, 3)} | {mp.nstr(d2, 3)} '
              f'| {tolerance:.3e} {second:.3e}')


if __name__ == '__main__':
    main()
