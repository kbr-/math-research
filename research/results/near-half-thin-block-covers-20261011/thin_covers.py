"""Exact refutation degree over F_2 of block covers with a minimal set of tuples.

Statement tested (queue check entry-2026-10-10-block-cover-witness:s1): the block cover on n = r g variables in
r groups of g has axioms Y_j = prod_{i in G_j} (1 + x_i), one per group, and F_t = prod_j l_{t,j} for tuples
t of nonzero linear forms, one on each group, whose sets {l_{t,j} = 1 for all j} cover the points with every
group nonzero.  With all tuples (the product form) the degree is g + r - 1.  Every cover is a subsystem of the
product form, so its degree is at least g + r - 1.  Question: does a minimal cover, from which no tuple can
be removed, need degree above g + r - 1?

Covers: random tuples are added while each covers a new point, until the points are covered; then tuples are
removed in random order while the rest still covers.  The result is checked to be a cover and minimal.
Controls: the product form at each size with at most 30000 tuples (expected degree g + r - 1), whose closure
dimensions at each degree are compared with those of the minimal covers, and for every minimal cover on at
most 12 variables a brute-force check that the axioms have no common zero.
Degrees by tools/f2_closure_degree.cpp, compiled into a scratch directory given on the command line; the
search stops at DMAX = g + r + EXTRA and reports null beyond it.  One-off job of 11 October 2026.

Usage: python3 thin_covers.py KERNEL_BINARY SCRATCH_DIR OUT.json EXTRA SEEDS R,G [R,G ...]
"""
import itertools
import json
import random
import subprocess
import sys


def form_terms(mask, offset, g):
    return [1 << (offset + i) for i in range(g) if mask >> i & 1]


def product(first, second):
    out = set()
    for a in first:
        for b in second:
            out ^= {a | b}
    return sorted(out)


def polys(r, g, tuples):
    rows = []
    for j in range(r):
        row = [0]
        for i in range(g):
            row = product(row, [0, 1 << (j * g + i)])
        rows.append(row)
    for t in tuples:
        row = [0]
        for j, mask in enumerate(t):
            row = product(row, form_terms(mask, j * g, g))
        rows.append(row)
    return rows


def covered(t, g, ones):
    """Bit set, over the points with all groups nonzero in mixed radix 2^g - 1, of the points tuple t covers."""
    bits = 0
    for point in itertools.product(*(ones[mask] for mask in t)):
        index = 0
        for a in point:
            index = index * ((1 << g) - 1) + (a - 1)
        bits |= 1 << index
    return bits


def minimal_cover(r, g, rng):
    ones = {mask: [a for a in range(1, 1 << g) if bin(a & mask).count('1') & 1] for mask in range(1, 1 << g)}
    full = (1 << ((1 << g) - 1) ** r) - 1
    chosen, sets, union = [], [], 0
    while union != full:
        t = tuple(rng.randrange(1, 1 << g) for _ in range(r))
        s = covered(t, g, ones)
        if s & ~union:
            chosen.append(t)
            sets.append(s)
            union |= s
    order = list(range(len(chosen)))
    rng.shuffle(order)
    keep = set(order)
    for k in order:
        rest = 0
        for i in keep:
            if i != k:
                rest |= sets[i]
        if rest == full:
            keep.discard(k)
    kept = sorted(keep)
    total = 0
    for i in kept:
        total |= sets[i]
    assert total == full
    for k in kept:
        rest = 0
        for i in kept:
            if i != k:
                rest |= sets[i]
        assert rest != full
    return [chosen[i] for i in kept]


def unsatisfiable(n, rows):
    """No point of the cube is a common zero.  Each row's truth table is a 2^n-bit integer, obtained from its
    coefficients by the subset-sum transform over F_2, one shift per variable."""
    size = 1 << n
    low = []
    for i in range(n):
        block = (1 << (1 << i)) - 1                      # positions with bit i equal to zero
        low.append(sum(block << (k << (i + 1)) for k in range(size >> (i + 1))))
    some_one = 0
    for row in rows:
        table = sum(1 << m for m in row)
        for i in range(n):
            table ^= (table & low[i]) << (1 << i)
        some_one |= table
    return some_one == (1 << size) - 1


def degree(binary, scratch, n, rows, dmax):
    path = f'{scratch}/thin_cover_instance.txt'
    with open(path, 'w') as f:
        f.write(f'{n} {len(rows)}\n')
        for row in rows:
            f.write(f'{len(row)} ' + ' '.join(map(str, row)) + '\n')
    out = subprocess.run([binary, path, str(dmax)], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main():
    binary, scratch, out_path, extra, seeds = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    results = []
    with open(out_path, 'w') as out:
        for size in sys.argv[6:]:
            r, g = map(int, size.split(','))
            n, dmax = r * g, min(r * g, r + g + extra)
            if ((1 << g) - 1) ** r <= 30000:
                tuples = list(itertools.product(range(1, 1 << g), repeat=r))
                res = degree(binary, scratch, n, polys(r, g, tuples), dmax)
                rec = {'r': r, 'g': g, 'n': n, 'kind': 'product', 'tuples': len(tuples), 'product_value': g + r - 1,
                       'dmax': dmax, 'kernel': res}
                out.write(json.dumps(rec) + '\n')
                out.flush()
            for seed in range(seeds):
                tuples = minimal_cover(r, g, random.Random(1000 * r + 100 * g + seed))
                rows = polys(r, g, tuples)
                unsat = unsatisfiable(n, rows) if n <= 12 else None
                res = degree(binary, scratch, n, rows, dmax)
                rec = {'r': r, 'g': g, 'n': n, 'kind': 'minimal', 'seed': seed, 'tuples': len(tuples),
                       'row_bound': (2 - 2 ** (1 - g)) ** r, 'unsatisfiable_checked': unsat,
                       'product_value': g + r - 1, 'dmax': dmax, 'kernel': res}
                out.write(json.dumps(rec) + '\n')
                out.flush()
                results.append(rec)
    print(len(results), 'minimal covers')


if __name__ == '__main__':
    main()
