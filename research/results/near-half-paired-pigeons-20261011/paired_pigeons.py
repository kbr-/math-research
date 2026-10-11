"""Exact refutation degree of pigeonhole hole clauses on affine subspaces with forms shared by pairs of pigeons.

Statement tested (queue check pigeonhole-affine-restriction, second entry): is there an affine subspace inside
the pigeon equations, of free dimension N < 2n, on which the hole clauses need degree near n/2?  Candidate
class.  n holes, n even; P = n/2 + 1 pairs of pigeons, so m = n + 2 pigeons; each pair has d options, an option
placing its first pigeon in one hole and its second in another, the 2d holes of a pair distinct and chosen at
random (seeded).  The subspace: x_{i,h} = x_{i',h'} = y_{p,o} for the two pigeons i, i' of pair p and its
option o with holes (h, h'); all other variables of the pair zero; sum_o y_{p,o} = 1.  It lies inside the pigeon
equations, each pigeon's variables summing to one, and its free dimension is N = (d-1) P.  Rows: for options of
different pairs that share a hole, the product of their two forms (a free variable, or one plus the sum of a
pair's free variables for its eliminated option).  Unsatisfiable: at every point each pigeon occupies an odd
number of holes and no hole holds two pigeons, with m > n.
Control: the graph principle with n + 1 pigeons of three random holes each, no forms shared, N = 2 (n + 1).
Predictions written before the run are in the entry.  Degrees by tools/f2_closure_degree.cpp, compiled into a
scratch directory given on the command line.  One-off job of 11 October 2026.

Usage: python3 paired_pigeons.py KERNEL_BINARY SCRATCH_DIR OUT.json
"""
import json
import random
import subprocess
import sys


def product(first, second):
    out = set()
    for a in first:
        for b in second:
            out ^= {a | b}
    return sorted(out)


def instance(groups, holes_of):
    """groups: per chooser, its options; holes_of[(g, o)]: the holes option o of chooser g occupies.
    Returns (free dimension, rows) with the last option of each chooser eliminated by its affine row."""
    form, free = {}, 0
    for g, options in enumerate(groups):
        bits = [1 << (free + k) for k in range(len(options) - 1)]
        for k, o in enumerate(options[:-1]):
            form[(g, o)] = [bits[k]]
        form[(g, options[-1])] = [0] + bits
        free += len(options) - 1
    keys = sorted(form)
    rows = [product(form[a], form[b]) for i, a in enumerate(keys) for b in keys[i + 1:]
            if a[0] != b[0] and holes_of[a] & holes_of[b]]
    return free, [r for r in rows if r]


def paired(n, d, seed):
    rng = random.Random(seed)
    groups, holes_of = [], {}
    for p in range(n // 2 + 1):
        chosen = rng.sample(range(n), 2 * d)
        groups.append(list(range(d)))
        for o in range(d):
            holes_of[(p, o)] = {chosen[2 * o], chosen[2 * o + 1]}
    return instance(groups, holes_of)


def graph(n, d, seed):
    rng = random.Random(seed)
    groups, holes_of = [], {}
    for p in range(n + 1):
        chosen = rng.sample(range(n), d)
        groups.append(list(range(d)))
        for o in range(d):
            holes_of[(p, o)] = {chosen[o]}
    return instance(groups, holes_of)


def degree(binary, scratch, free, rows, dmax):
    path = f'{scratch}/instance.txt'
    with open(path, 'w') as handle:
        handle.write(f'{free} {len(rows)}\n' + ''.join(f'{len(r)} ' + ' '.join(map(str, r)) + '\n' for r in rows))
    return json.loads(subprocess.run([binary, path, str(dmax)], check=True, capture_output=True, text=True).stdout)


def main(binary, scratch, out):
    cases = ([('paired', n, 3, s) for n in (8, 10, 12, 14, 16) for s in (1, 2, 3)]
             + [('paired', n, 4, s) for n in (8, 10, 12) for s in (1, 2)]
             + [('graph', n, 3, s) for n in (6, 7, 8) for s in (1, 2)])
    built = sorted(((paired if kind == 'paired' else graph)(n, d, seed), kind, n, d, seed)
                   for kind, n, d, seed in cases)                      # smallest free dimension first
    results = []
    for (free, rows), kind, n, d, seed in built:
        found = degree(binary, scratch, free, rows, min(n // 2 + 1, 6))
        results.append({'kind': kind, 'holes': n, 'options': d, 'seed': seed, 'free_dimension': free,
                        'rows': len(rows), 'half_holes': n / 2, 'quarter_dimension': free / 4,
                        'degree': found['degree'], 'dimensions': found['dimensions']})
        with open(out, 'w') as handle:
            json.dump(results, handle, indent=1)
    print(len(results), 'cases written')


if __name__ == '__main__':
    main(*sys.argv[1:4])
