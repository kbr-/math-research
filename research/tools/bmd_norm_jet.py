"""Test: does the origin jet v = (1+N)^(-1) mod m^c attain delta(n,c,0) = Phi(n,c,0)?

N is the norm form of F_(2^n)/F_2 in the polynomial basis: N(x) = prod_{i<n} L_i(x), with
L_i(x) = sum_j beta^(j 2^i) x_j.  It has F_2 coefficients, degree n, and N(a) = 1 for a != 0 in F_2^n,
so 1+N vanishes on F_2^n minus 0 and is 1 at the origin.  P(v) is computed by bmd_jet_orders --jet.
Tested statement: deg P((1+N)^(-1) mod m^c) = n + sum_{j<n} floor((c-1)/2^j).
Usage: bmd_norm_jet.py BIN OUTDIR NMAX CMAX [power]   (power: the jet (1+N)^c mod m^c instead)
"""
import json, subprocess, sys
from pathlib import Path

IRRED = {1: 0b11, 2: 0b111, 3: 0b1011, 4: 0b10011, 5: 0b100101, 6: 0b1000011}


def gmul(a, b, n):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a ^= IRRED[n]
    return r


def gpow(a, e, n):
    r = 1
    for _ in range(e):
        r = gmul(r, a, n)
    return r


def polymul(p, q, n, gf):
    """Multiply polynomials {exponent tuple: coefficient}; coefficients in GF(2^n) (gf) or F_2."""
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(a + b for a, b in zip(m1, m2))
            r[m] = r.get(m, 0) ^ (gmul(c1, c2, n) if gf else (c1 & c2))
    return {m: c for m, c in r.items() if c}


def norm_form(n):
    beta = 2 if n > 1 else 1
    prod = {tuple([0] * n): 1}
    for i in range(n):
        lin = {tuple(int(t == j) for t in range(n)): gpow(beta, j * 2 ** i, n) for j in range(n)}
        prod = polymul(prod, lin, n, True)
    assert all(c == 1 for c in prod.values()), 'norm form must have F_2 coefficients'
    return prod


def inverse_jet(N, n, c):
    jet, power = {}, {tuple([0] * n): 1}
    while power and sum(next(iter(power))) < c:
        for m in power:
            jet[m] = jet.get(m, 0) ^ 1
        power = polymul(power, N, n, False)
    return [m for m, v in jet.items() if v]


def power_jet(N, n, c):
    """(1+N)^c mod m^c."""
    one = {tuple([0] * n): 1}
    base = dict(N); base[tuple([0] * n)] = 1
    r = one
    for _ in range(c):
        r = {m: v for m, v in polymul(r, base, n, False).items() if sum(m) < c}
    return list(r)


def main():
    global JET
    JET = power_jet if sys.argv[5:] == ['power'] else inverse_jet
    binary, outdir, nmax, cmax = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    outdir.mkdir(parents=True, exist_ok=True)
    bad = 0
    for n in range(1, nmax + 1):
        N = norm_form(n)
        for c in range(1, cmax + 1):
            jf = outdir / f'jet-n{n}-c{c}.txt'
            jf.write_text(''.join(' '.join(map(str, m)) + '\n' for m in JET(N, n, c)))
            res = json.loads(subprocess.run([binary, str(n), str(c), '--jet', str(jf)], check=True,
                                            capture_output=True, text=True).stdout)
            phi = n + sum((c - 1) >> j for j in range(n))
            bad += res['degree'] != phi
            print(f'n={n} c={c}: deg P((1+N)^-1) = {res["degree"]}, Phi = {phi}'
                  f'{"" if res["degree"] == phi else "  DIFFERENT"}', flush=True)
    print(f'cases differing from Phi: {bad}')


if __name__ == '__main__':
    main()
