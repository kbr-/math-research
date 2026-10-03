"""Cheap arithmetic tests of the goal-level review of cycle bmd-20261009-df (no heavy computation).

1. Power-law (Prony-type) fit of the triple window's large-m error: the relative errors |scaled + B|/|B| recorded in
   research/results/bmd-20261009-cy/route-review32-tests.txt, multiplied by m^2, should approach a constant if the
   error is c/m^2.
2. Ehrhart test of the reflection hypothesis: under H, P(d) = lambda(lambda+1)/2 - 8(d - 1/2)(d - 2)(d + 1)
   (beta = -16 from deg T_3 = 1460).  An Ehrhart polynomial of a lattice polytope has constant term 1.
Usage: python3 bmd_route_review33_tests.py OUT"""
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
lines = (ROOT / 'research/results/bmd-20261009-cy/route-review32-tests.txt').read_text().splitlines()
out = []
for line in lines:
    r = re.match(r'r = (\S+): .*?\[(.*?)\]', line)
    if not r:
        continue
    rel = [float(x) for x in r.group(2).split(',')]
    scaled = [round(m * m * e, 3) for m, e in zip(range(4, 15), rel)]
    out.append(f'r = {r.group(1)}: m^2 * relative error for m = 4..14: {scaled}')


def lam(d):
    return 10 * d * d - 10 * d - 5


def P(d):
    d = Fraction(d)
    return Fraction(lam(d) * (lam(d) + 1), 2) - 8 * (d - Fraction(1, 2)) * (d - 2) * (d + 1)


out.append('P(d) under H, d = -2..5: ' + str([str(P(d)) for d in range(-2, 6)]))
out.append(f'checks: P(2) = {P(2)} (120), P(3) = {P(3)} (1460), P(-1) + P(2) = {P(-1) + P(2)} (240), '
           f'P(0) = {P(0)} (Ehrhart constant term would be 1)')
Path(sys.argv[1]).write_text('\n'.join(out) + '\n')
