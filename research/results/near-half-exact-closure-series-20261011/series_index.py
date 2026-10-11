"""The two series indices for m = 3n products of two affine forms, at the sizes of closure_series.py.

generic: first non-positive coefficient of (1+z)^n / (1+z^2)^m (conj:parity-clause-semiregular-degree).
product: first non-positive coefficient of (1+z)^(n-2m) ((1+z)^2 - z^2)^m (conj:parity-clause-regular-index).
Exact integer arithmetic on truncated power series.

Usage: python3 series_index.py OUT.json
"""
import json
import sys

TOP = 40


def multiply(a, b):
    out = [0] * (TOP + 1)
    for i, x in enumerate(a):
        if x:
            for j in range(TOP + 1 - i):
                out[i + j] += x * b[j]
    return out


def power(base, exponent):
    out = [1] + [0] * TOP
    for _ in range(exponent):
        out = multiply(out, base)
    return out


def inverse(a):
    out = [0] * (TOP + 1)
    out[0] = 1
    for d in range(1, TOP + 1):
        out[d] = -sum(a[i] * out[d - i] for i in range(1, d + 1))
    return out


def pad(coefficients):
    return coefficients + [0] * (TOP + 1 - len(coefficients))


def first_nonpositive(series):
    return next(d for d, c in enumerate(series) if c <= 0)


def indices(n):
    m = 3 * n
    generic = multiply(power(pad([1, 1]), n), inverse(power(pad([1, 0, 1]), m)))
    product = multiply(power(pad([1, 2]), m), inverse(power(pad([1, 1]), 2 * m - n)))
    return {'n': n, 'm': m, 'generic_index': first_nonpositive(generic), 'product_index': first_nonpositive(product)}


if __name__ == '__main__':
    results = [indices(n) for n in (12, 16, 20, 24, 28, 32)]
    with open(sys.argv[1], 'w') as handle:
        json.dump(results, handle, indent=1)
    print(json.dumps(results))
