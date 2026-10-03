"""Saturation of the plane minor ideal by msolve instead of Macaulay2 (cycle bmd-20261009-dg).

Macaulay2's saturation ran over five minutes on the d = 4 minors (29 generators of degree about 140 in two
variables); msolve's F4 handles it.  Two modes:
  to-msolve IN.m2 P OUT.ms     the stripped minors of research/tools/bmd_plane_minors.cpp, plus the Rabinowitsch
                               generator t * prod(collision forms) - 1, in variables t, x, y (run msolve -e 1 -g 2,
                               which returns the reduced Groebner basis of the saturated ideal in x, y)
  to-m2 GB.txt P OUT.m2        that basis as `gbList = {...}` for research/tools/bmd_plane_section_betti.m2"""
import re
import sys


def parse_poly(text, p):
    poly = {}
    for term in text.replace('-', '+-').split('+'):
        term = term.strip()
        if not term:
            continue
        coeff, e, b = 1, 0, 0
        for factor in term.split('*'):
            factor = factor.strip()
            if factor.startswith('x'):
                e = int(factor[2:]) if '^' in factor else 1
            elif factor.startswith('y'):
                b = int(factor[2:]) if '^' in factor else 1
            else:
                coeff *= int(factor)
        poly[(e, b)] = (poly.get((e, b), 0) + coeff) % p
    return {k: v for k, v in poly.items() if v}


def multiply(f, g, p):
    out = {}
    for (e1, b1), c1 in f.items():
        for (e2, b2), c2 in g.items():
            key = (e1 + e2, b1 + b2)
            out[key] = (out.get(key, 0) + c1 * c2) % p
    return {k: v for k, v in out.items() if v}


def show(poly, prefix=''):
    return '+'.join(f'{c}*{prefix}x^{e}*y^{b}' for (e, b), c in sorted(poly.items())) or '0'


def to_msolve(source, p, target):
    text = open(source).read()
    body = text[text.index('minorList = {') + len('minorList = {'):text.index('};')]
    minors = [parse_poly(m, p) for m in body.split(',\n')]
    minors = [m for m in minors if m]
    forms = text[text.index('collisionForms = {') + len('collisionForms = {'):]
    forms = forms[:forms.index('}')].split(',')
    product = {(0, 0): 1}
    for form in forms:
        product = multiply(product, parse_poly(form, p), p)
    lines = [show(m) for m in minors] + [show(product, 't*') + f'+{p - 1}']
    with open(target, 'w') as out:
        out.write('t,x,y\n' + str(p) + '\n' + ',\n'.join(lines) + '\n')
    print(f'{len(minors)} minors, collision product of degree {max(e + b for e, b in product)}, written to {target}')


def to_m2(source, p, target):
    text = open(source).read()
    body = text[text.index('[') + 1:text.rindex(']')]
    polys = [x.strip() for x in body.split(',') if x.strip() and 't' not in x]   # the elimination ideal: free of t
    with open(target, 'w') as out:
        out.write('gbList = {\n' + ',\n'.join(polys) + '\n};\n')
    print(f'{len(polys)} basis elements written to {target}')


def basis_to_msolve(source, p, target):
    """msolve's saturated basis (t-free part) as an msolve input in x, y, for msolve -P 1 (reducedness check)."""
    text = open(source).read()
    body = text[text.index('[') + 1:text.rindex(']')]
    polys = [x.strip() for x in body.split(',') if x.strip() and 't' not in x]
    with open(target, 'w') as out:
        out.write('x,y\n' + str(p) + '\n' + ',\n'.join(polys) + '\n')
    print(f'{len(polys)} basis elements written to {target}')


if __name__ == '__main__':
    mode, source, p, target = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    {'to-msolve': to_msolve, 'to-m2': to_m2, 'basis-to-msolve': basis_to_msolve}[mode](source, p, target)
