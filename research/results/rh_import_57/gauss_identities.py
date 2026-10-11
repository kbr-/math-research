"""Numerical control of the prime case of three identities read in the appendix of the import's intermediate
preprint (Reciprocity and Gauss sums), for primary Eisenstein primes p = a + b*omega of norm q <= 200, q = 1 mod 3
(primary: a = 1 mod 3, b = 0 mod 3).

Definitions, as read: chi_p the sextic residue character, chi_p(x) = x^((q-1)/6) mod p as a sixth root of unity;
gamma_j(p) = q^(-1/2) sum_{x mod p} chi_p(x)^j e(x/p), e(z) = exp(4 pi i Im z / sqrt 3); alpha(p) = p/|p|.

Statements tested:
 A. gamma_1 gamma_2 = conj(chi_p(4)) gamma_3 gamma_2^3.
 B. gamma_2^3 = -alpha(p).
 C. gamma_3(p) = (1 + i^(-b) + i^a + i^(b-a))/2, the quadratic Gauss value of p = a + b*omega.
Together A and B give gamma_1 gamma_2 = -conj(chi_p(4)) alpha(p) gamma_3: the Moebius sign of a prime.

Expected, written before the run: A, B and C hold to 1e-9 for every such prime.
Negative control: B with the non-primary generator omega*p in place of p.  The character and gamma_2^3 are those
of the same ideal (the script asserts gamma_2^3 is unchanged to 1e-9), while alpha(omega p) = omega alpha(p), so
the altered statement differs from the true one by |1 - omega| = sqrt 3 and is expected to fail for every prime.
The sums are computed from the definitions; nothing in them uses the identities.
"""
import cmath
import math

OMEGA = cmath.exp(2j * math.pi / 3)
TOL = 1e-9


def primes(limit):
    out = []
    for a in range(-20, 21):
        for b in range(-18, 19, 3):
            q = a * a - a * b + b * b
            if a % 3 == 1 and b != 0 and 1 < q <= limit and q % 3 == 1 and all(q % d for d in range(2, int(q ** 0.5) + 1)):
                out.append((q, a, b))
    return sorted(out)


def gauss(q, a, b, unit_power=0):
    """gamma_1, gamma_2, gamma_3 and chi(4) for the generator omega^unit_power * (a + b omega)."""
    r = (-a * pow(b, -1, q)) % q                       # omega mod p
    assert (r * r + r + 1) % q == 0
    roots = {1: 1, q - 1: -1, r: OMEGA, q - r: -OMEGA, r * r % q: OMEGA ** 2, q - r * r % q: -OMEGA ** 2}
    chi = [0] + [roots[pow(x, (q - 1) // 6, q)] for x in range(1, q)]
    a2, b2 = a, b
    for _ in range(unit_power):                        # multiply the generator by omega
        a2, b2 = -b2, a2 - b2
    # x / (a2 + b2 omega) = x (a2 - b2 - b2 omega)/q, with imaginary part -b2 x sqrt(3)/(2 q)
    e = [cmath.exp(-2j * math.pi * b2 * x / q) for x in range(q)]
    gammas = [sum(chi[x] ** j * e[x] for x in range(1, q)) / math.sqrt(q) for j in (1, 2, 3)]
    return gammas, chi[4 % q], complex(a2 + b2 * OMEGA) / math.sqrt(q)


def main():
    cases = primes(200)
    worst = {'A': 0.0, 'B': 0.0, 'C': 0.0}
    control_fails = 0
    for q, a, b in cases:
        (g1, g2, g3), chi4, alpha = gauss(q, a, b)
        worst['A'] = max(worst['A'], abs(g1 * g2 - chi4.conjugate() * g3 * g2 ** 3))
        worst['B'] = max(worst['B'], abs(g2 ** 3 + alpha))
        worst['C'] = max(worst['C'], abs(g3 - (1 + 1j ** (-b) + 1j ** a + 1j ** (b - a)) / 2))
        (_, h2, _), _, alpha_w = gauss(q, a, b, 1)
        assert abs(h2 ** 3 - g2 ** 3) < TOL, 'the control changes more than alpha'
        assert abs(alpha_w - OMEGA * alpha) < TOL
        control_fails += abs(h2 ** 3 + alpha_w) > 0.5
    print(f'{len(cases)} primary primes of norm at most 200: norms {[q for q, _, _ in cases]}')
    for name in 'ABC':
        print(f'{name}: largest deviation {worst[name]:.2e} against tolerance {TOL:.0e} (the quantities have modulus 1 or 2): '
              + ('holds' if worst[name] < TOL else 'FAILS'))
    print(f'negative control (B with a non-primary generator): fails in {control_fails} of {len(cases)}')


if __name__ == '__main__':
    main()
