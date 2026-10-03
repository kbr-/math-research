"""Hilbert function of a plane section from the leading monomials of msolve's grevlex basis (cycle bmd-20261009-dg).

For an ideal I of k[x, y] with a Groebner basis for a degree-compatible order, the homogenization of that basis is a
Groebner basis of the projective closure, so the Hilbert function of the section, H(k) = dim (S/I^h)_k, counts the
standard monomials of total degree at most k.  Its length is their number, and the initial degree of I^h is the least
k with C(k+2, 2) > H(k).  It is compared with general points, H(k) = min(C(k+2, 2), length).
(Statement: indeg of the section ideal is a lower bound for l_0; bmd_plane_section_betti.m2.)
Usage: python3 bmd_section_hilbert.py GB.txt [GB.txt ...] > OUT"""
import re
import sys


def leading(poly):
    term = poly.split('+')[0]
    e = re.search(r'x\^(\d+)', term) or (re.search(r'\bx\b', term) and ['', '1'])
    b = re.search(r'y\^(\d+)', term) or (re.search(r'\by\b', term) and ['', '1'])
    return int(e[1]) if e else 0, int(b[1]) if b else 0


for path in sys.argv[1:]:
    text = open(path).read()
    body = text[text.index('[') + 1:text.rindex(']')]
    leads = [leading(p.strip()) for p in body.split(',') if p.strip() and 't' not in p]
    top = max(a + b for a, b in leads) + 2
    standard = [(a, b) for a in range(top + 1) for b in range(top + 1 - a)
                if not any(a >= la and b >= lb for la, lb in leads)]
    length = len(standard)
    H = [sum(1 for a, b in standard if a + b <= k) for k in range(top + 1)]
    choose = [(k + 1) * (k + 2) // 2 for k in range(top + 1)]
    alpha = next(k for k in range(top + 1) if choose[k] > H[k])
    general = next(k for k in range(top + 1) if choose[k] > min(choose[k], length))
    gens_alpha = choose[alpha] - H[alpha]
    deviations = [k for k in range(top + 1) if H[k] != min(choose[k], length)]
    print(f'{path}: length {length}; initial degree {alpha} ({gens_alpha} forms); general points: initial degree '
          f'{general}; Hilbert function equals that of general points: {not deviations}'
          + (f' (differs at degrees {deviations[:5]}...)' if deviations else ''))
