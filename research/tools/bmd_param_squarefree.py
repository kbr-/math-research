"""Squarefreeness of msolve's eliminating polynomial (cycle bmd-20261009-df).

Reads an msolve -P 1 output, takes the eliminating polynomial (the first coefficient list of the parametrization,
lowest degree first) over F_p, and prints its degree and deg gcd(f, f').  If the gcd is constant and the degree equals
the ideal's length, the zero-dimensional scheme is reduced: its points are distinct and as many as its length.
Usage: python3 bmd_param_squarefree.py PARAM.txt OUT.txt"""
import re
import sys


def gcd_degree(f, g, p):
    def trim(a):
        while a and a[-1] == 0:
            a.pop()
        return a
    a, b = trim([x % p for x in f]), trim([x % p for x in g])
    while b:
        inv = pow(b[-1], p - 2, p)
        while len(a) >= len(b):
            c = a[-1] * inv % p
            shift = len(a) - len(b)
            for i, v in enumerate(b):
                a[shift + i] = (a[shift + i] - c * v) % p
            trim(a)
            if not a:
                break
        a, b = b, a
    return len(a) - 1


text = open(sys.argv[1]).read()
numbers = re.findall(r'-?\d+', text)
p, length = int(numbers[1]), int(numbers[3])
start = text.index('[[') + 2
degree = int(re.match(r'\s*(\d+)', text[start:]).group(1))
coeffs = [int(x) for x in re.search(r'\[([-\d,\s]+)\]', text[start:]).group(1).split(',')]
derivative = [i * c for i, c in enumerate(coeffs)][1:]
g = gcd_degree(coeffs, derivative, p)
result = (f'p = {p}; ideal length (msolve) = {length}; eliminating polynomial degree {degree} '
          f'({len(coeffs)} coefficients); deg gcd(f, f\') = {g}\n')
open(sys.argv[2], 'w').write(result)
print(result, end='')
