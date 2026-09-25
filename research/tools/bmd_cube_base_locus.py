"""Base locus of computed degree-l parts of the threshold ideal on {0,1}^3.

Parses blocks printed by bmd_cube_dual_order_zero.py LOWEST (coefficients are residues mod p, read
as symmetric integers). For each block it reports the least multiplicity over the basis at each of
the seven multiple points of the braid arrangement y_i = 0, y_i = y_j, and the common zeros of the
basis on each line of L_2. These are computed modulo p, so they are exact for any coefficients.
The printed gcd and factorizations use the integer lifts and are only indicative when a
coefficient is not a small integer (e.g. 500001 = -1/2 mod 1000003). The data are in the dual
variables u = -y up to sign, which fixes these points and lines.
Usage: bmd_cube_base_locus.py LOWEST_OUTPUT_FILE [L ...]   (degrees to analyse; default: first block)
"""
import re, sys
import sympy as sp

p = 1000003
u1, u2, u3 = sp.symbols('u1 u2 u3')
U = (u1, u2, u3)
t = sp.symbols('t')
L = [u1 + u2 - u3, u1 - u2 + u3, -u1 + u2 + u3]
PTS = [(1, 1, 0), (1, 0, 1), (0, 1, 1), (0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)]


def parse(line):
    poly = 0
    for c, e in re.findall(r'(-?\d+)\*u\^\((\d+, \d+, \d+)\)', line):
        c = int(c) % p
        if c > p // 2:
            c -= p
        ex = tuple(int(x) for x in e.split(','))
        poly += c * u1**ex[0] * u2**ex[1] * u3**ex[2]
    return sp.expand(poly)


def analyse(block):
    polys = [parse(l) for l in block[1:] if 'u^' in l]
    print(block[0])
    g = polys[0]
    for q in polys[1:]:
        g = sp.gcd(g, q)
    print('gcd (integer lifts):', sp.factor(g))
    for q in polys:
        print('factor (integer lift):', sp.factor(q))
    for P in PTS:
        sub = dict(zip(U, P))
        mults = []  # least k with some k-th partial derivative nonzero mod p at P
        for q in polys:
            k, ds = 0, [q]
            while not any(int(f.subs(sub)) % p for f in ds):
                ds = [sp.diff(f, v) for f in ds for v in U]
                k += 1
            mults.append(k)
        print('point', P, 'min multiplicity over basis', min(mults), mults)
    for Lf, par in [(L[0], (t, 1 - t, 1)), (L[1], (t, 1, 1 - t)), (L[2], (1, t, 1 - t))]:
        sub = dict(zip(U, par))
        gg = None
        for q in polys:
            r = sp.Poly(sp.expand(q.subs(sub)), t, modulus=p)
            gg = r if gg is None else sp.gcd(gg, r)
        print('line', Lf, 'common restriction gcd mod p:', gg.monic().as_expr() if not gg.is_zero else 0)


def main():
    lines = open(sys.argv[1]).read().splitlines()
    for want in (sys.argv[2:] or [None]):
        start = 0 if want is None else next(i for i, l in enumerate(lines) if f' l={want}:' in l)
        end = next((i for i in range(start + 1, len(lines)) if 'dimension' in lines[i]), len(lines))
        analyse(lines[start:end])


if __name__ == '__main__':
    main()
