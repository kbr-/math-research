"""Paired-pigeon subspaces without linear relations in degree two: exact refutation degrees.

Queue check pigeonhole-affine-restriction, third entry.  Class and rows as in
../near-half-paired-pigeons-20261011/paired_pigeons.py (imported): n holes, n/2 + 1 pairs of pigeons, d = 3
options to a pair, free dimension N = n + 2.

Part 1, the cause of degree two.  Hypothesis (the last reviewer's, in the author's checkable form): a recorded
instance has refutation degree two exactly when the span of its rows contains a nonzero polynomial of degree
at most one, a linear relation among the forms; and such a relation already lies in the span of the rows
between some two pairs.  Checked on the 21 recorded instances, whose degrees are read from the recorded output.

Part 2.  Pairings drawn at random and kept only when the span of all rows contains no nonzero polynomial of
degree at most one ("relation-free"), at n = 14, 16, 18, 20, three each, with the graph control at n = 8, 9, 10
(N = 18, 20, 22).  Prediction written before the run: if the degree of the class grows like n/2, no refutation
is found through degree 6 at n = 14 and above (n/2 = 7 to 10); if it stays near the recorded values, the degree
is 3 or 4 at every size.  Relation-free instances have degree at least 3 by construction of the filter, so a
degree of exactly 3 at all sizes would be the filter's floor and say only that it is attained.

Usage: python3 block_free.py KERNEL_BINARY SCRATCH_DIR RECORDED.json OUT.json
"""
import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'paired_pigeons', HERE.parent / 'near-half-paired-pigeons-20261011' / 'paired_pigeons.py')
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)


def has_linear_relation(rows):
    """Whether the span of the polynomials (lists of monomial masks) has a nonzero element of degree <= 1."""
    quadratic = sorted({t for r in rows for t in r if bin(t).count('1') == 2})
    low = sorted({t for r in rows for t in r if bin(t).count('1') < 2})
    bit = {t: i for i, t in enumerate(quadratic + low)}
    limit = 1 << len(quadratic)
    pivots = {}
    for r in rows:
        v = sum(1 << bit[t] for t in r)
        while v:
            p = v & -v
            if p >= limit:
                return True                       # no quadratic monomial left, and not zero
            if p not in pivots:
                pivots[p] = v
                break
            v ^= pivots[p]
    return False


def paired_rows_by_block(n, d, seed):
    """The paired instance of the recorded generator, with its rows grouped by the two pairs they join."""
    rng = random.Random(seed)
    groups, holes_of = [], {}
    for p in range(n // 2 + 1):
        chosen = rng.sample(range(n), 2 * d)
        groups.append(list(range(d)))
        for o in range(d):
            holes_of[(p, o)] = {chosen[2 * o], chosen[2 * o + 1]}
    form, free = {}, 0
    for g, options in enumerate(groups):
        bits = [1 << (free + k) for k in range(len(options) - 1)]
        for k, o in enumerate(options[:-1]):
            form[(g, o)] = [bits[k]]
        form[(g, options[-1])] = [0] + bits
        free += len(options) - 1
    keys = sorted(form)
    blocks = {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a[0] != b[0] and holes_of[a] & holes_of[b]:
                blocks.setdefault((a[0], b[0]), []).append(pp.product(form[a], form[b]))
    return free, blocks


def all_rows(blocks):
    return [row for block in blocks.values() for row in block]


def cause_of(r):
    free, blocks = paired_rows_by_block(r['holes'], r['options'], r['seed'])
    rows = all_rows(blocks)
    assert free == r['free_dimension'] and len(rows) == r['rows']
    return {'holes': r['holes'], 'options': r['options'], 'seed': r['seed'], 'degree': r['degree'],
            'linear_relation_in_span': has_linear_relation(rows),
            'linear_relation_in_one_block': any(map(has_linear_relation, blocks.values()))}


def relation_free(n, skip):
    """The next seed after `skip` whose pairing has no linear relation in the span of its rows."""
    seed = skip
    while True:
        seed += 1
        free, blocks = paired_rows_by_block(n, 3, seed)
        rows = all_rows(blocks)
        if not has_linear_relation(rows):
            return seed, free, rows


def main(binary, scratch, recorded, out):
    cause = [cause_of(r) for r in json.load(open(recorded)) if r['kind'] == 'paired']
    results = []
    last = {}
    cases = [('paired', n, k) for n in (14, 16, 18, 20) for k in range(3)] + [
        ('graph', n, seed) for n in (8, 9, 10) for seed in (1, 2)]
    for kind, n, k in cases:
        if kind == 'paired':
            seed, free, rows = relation_free(n, last.get(n, 100 * n))
            last[n] = seed
            label, extra = 'paired, relation-free', {'seeds_tried_so_far': seed - 100 * n}
        else:
            seed = k
            free, rows = pp.graph(n, 3, seed)
            label, extra = 'graph', {}
        got = pp.degree(binary, scratch, free, rows, 6)
        results.append({'kind': label, 'holes': n, 'seed': seed, 'free_dimension': free, 'rows': len(rows),
                        'degree': got['degree'], 'half_holes': n / 2, 'quarter_dimension': free / 4, **extra})
        with open(out, 'w') as handle:
            json.dump({'cause': cause, 'runs': results}, handle, indent=1)
    # Part 3, added after part 2 gave degree 3 in all twelve relation-free instances: is 3 the degree of every
    # random relation-free pairing, or only of the first few?  A survey: 200 at n = 20 searched through degree
    # 5, and 30 at n = 24 (N = 26) searched through degree 4.  Prediction: all 3 if the class has constant
    # degree at these sizes; some null (no refutation within the search) if harder pairings exist.
    survey = []
    for n, count, dmax in ((20, 200, 5), (24, 30, 4)):
        degrees = survey_degrees(binary, scratch, n, count, dmax)
        survey.append({'holes': n, 'free_dimension': n + 2, 'instances': count, 'searched_through': dmax,
                       'degree_counts': {str(d): degrees.count(d) for d in sorted(set(degrees), key=str)}})
        with open(out, 'w') as handle:
            json.dump({'cause': cause, 'runs': results, 'survey': survey}, handle, indent=1)
    print(len(cause), 'recorded instances checked,', len(results), 'new runs and', len(survey), 'surveys written')


def survey_degrees(binary, scratch, n, count, dmax):
    degrees, seed = [], 1000 * n
    while len(degrees) < count:
        seed, free, rows = relation_free(n, seed)
        degrees.append(pp.degree(binary, scratch, free, rows, dmax)['degree'])
    return degrees


if __name__ == '__main__':
    main(*sys.argv[1:5])
