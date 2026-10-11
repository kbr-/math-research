"""Exact polynomial-calculus degrees of the recorded parity 2-clause instances, by the committed closure kernel.

Queue build entry-2026-10-09-exact-degree-tool:s1 asked for a compiled truncated completion, validated against
tools/truncated_buchberger.py, to obtain exact degrees of the parity 2-clause instances at n = 20 to 32.  The
kernel tools/f2_closure_degree.cpp computes the degree-D closure and is tested against that reference; this
script is its use on those instances: m = 3n products of two random affine forms, the generator of
../near-half-span-kernel-20261009/gen_instances.py (same seeds, same draws), three instances at each size.

What the recorded data predict.  The recorded static degrees (1 in the span of the products x_T f_i with
|T| <= D - 2) are 3, 3, 4, 4, 4 at n = 12, 16, 20, 24, 28 and "none through 4" at n = 32.  The closure contains
that span, so the exact degree is at most the static one: at n <= 28 it is 3 or 4 and can only be lower than
recorded; at n = 32 the two outcomes are a refutation at 4, which the static span does not have (polynomial
calculus then beats the static span on these instances), or none through 4, as for the span.

Usage: python3 closure_series.py KERNEL_BINARY SCRATCH_DIR OUT.jsonl DMAX N ...
"""
import json
import random
import subprocess
import sys
import time


def affine(n, rng):
    while True:
        mask = rng.getrandbits(n)
        if mask:
            return mask, rng.getrandbits(1)


def form_terms(n, mask, const):
    return [1 << i for i in range(n) if mask >> i & 1] + ([0] if const else [])


def product(first, second):
    """The multilinear product: each pair of monomials is added separately, so that x * 1 + x * x cancels."""
    pairs = [a | b for a in first for b in second]
    return sorted(t for t in set(pairs) if pairs.count(t) % 2)


def evaluate(poly, point):
    return sum(point & t == t for t in poly) % 2


def check_product(n, f, g, rng):
    """The product as a function: at random points it equals the product of the two forms' values."""
    poly = product(form_terms(n, *f), form_terms(n, *g))
    for _ in range(8):
        x = rng.getrandbits(n)
        value = lambda form: (bin(form[0] & x).count('1') + form[1]) % 2
        assert evaluate(poly, x) == value(f) * value(g)
    return poly


def instance(n, seed):
    """The rows of gen_instances.py for (n, seed), each as the monomials of the product of its two forms."""
    rng = random.Random(1000 * n + seed)
    points = random.Random(7)                    # a separate stream: the instance's draws are the recorded ones
    rows = []
    for _ in range(3 * n):
        f = affine(n, rng)
        g = affine(n, rng)
        while g[0] == f[0]:
            g = affine(n, rng)
        rows.append(check_product(n, f, g, points))
    return rows


def degree(binary, scratch, n, seed, dmax):
    rows = instance(n, seed)
    path = f'{scratch}/parity_{n}_{seed}.txt'
    with open(path, 'w') as handle:
        handle.write(f'{n} {len(rows)}\n' + ''.join(f'{len(r)} ' + ' '.join(map(str, r)) + '\n' for r in rows))
    start = time.time()
    got = json.loads(subprocess.run([binary, path, str(dmax)], check=True, capture_output=True, text=True).stdout)
    return {'n': n, 'm': len(rows), 'seed': seed, 'searched_through': dmax, 'exact_degree': got['degree'],
            'closure_dimensions': got['dimensions'], 'seconds': round(time.time() - start, 1)}


def main(binary, scratch, out, dmax, sizes):
    cases = [(int(n), seed) for n in sizes for seed in (1, 2, 3)]
    with open(out, 'a') as handle:
        for n, seed in cases:
            result = degree(binary, scratch, n, seed, int(dmax))
            handle.write(json.dumps(result) + '\n')
            handle.flush()
            print(json.dumps({k: result[k] for k in ('n', 'seed', 'exact_degree', 'seconds')}))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
