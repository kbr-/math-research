"""Symmetry of a printed threshold generator under S_4 and under the branch-point involution (bmd-r110).

Reads the first 'top 0:' polynomial from a bmd_cube_thresholds_m2 output (over F_32003), and checks
invariance up to sign under the transpositions of y_1..y_4 and under psi(y) = (y_1, y_1-y_2, y_1-y_3,
y_1-y_4) of thm:cube-branch-point-symmetry; also reports its total degree.
Usage: bmd_cube_top_symmetry.py OUTPUT
"""
import re
import sys
import sympy as sp

P = 32003
y1, y2, y3, y4 = Y = sp.symbols('y_1 y_2 y_3 y_4')
text = open(sys.argv[1]).read()
m = re.search(r'top 0: (.*)', text)
s = m.group(1).strip()
s = re.sub(r'\)\*\(-?\d+\)$', ')', s)
f = sp.Poly(sp.sympify(s.replace('^', '**'), locals={'y_1': y1, 'y_2': y2, 'y_3': y3, 'y_4': y4}), *Y, modulus=P)
print('degree', f.total_degree())


def same_up_to_sign(g):
    return g == f or g == -f


for i in range(4):
    for j in range(i + 1, 4):
        sub = {Y[i]: Y[j], Y[j]: Y[i]}
        g = sp.Poly(f.as_expr().subs(sub, simultaneous=True), *Y, modulus=P)
        print(f'swap y{i + 1},y{j + 1}:', 'invariant up to sign' if same_up_to_sign(g) else 'NOT invariant')
psi = {y2: y1 - y2, y3: y1 - y3, y4: y1 - y4}
g = sp.Poly(f.as_expr().subs(psi, simultaneous=True), *Y, modulus=P)
print('psi:', 'invariant up to sign' if same_up_to_sign(g) else 'NOT invariant')
