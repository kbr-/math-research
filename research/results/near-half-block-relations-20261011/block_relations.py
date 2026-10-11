"""A check of the classification of linear relations between two pairs of a paired-pigeon subspace.

Statement checked (proved in the entry): for two pairs with d options each and conflict set K (the option
pairs that share a hole), the span of the rows alpha_a beta_b, (a, b) in K, contains a nonzero polynomial of
degree at most one exactly when K contains (S^c x R) u (S x R^c) for some subsets S, R of the options other
than S = R = empty and S = R = all.  The check compares that combinatorial test with the elimination test of
../near-half-block-free-pairing-20261011/block_free.py on every block of random pairings with three and four
options; a disagreement would refute the classification or the proof's reading of the rows.  It registers
nothing; it is the entry's verification of a proved statement.

Usage: python3 block_relations.py OUT.json
"""
import importlib.util
import json
import random
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'block_free', HERE.parent / 'near-half-block-free-pairing-20261011' / 'block_free.py')
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)


def patterns(d):
    """The supports (S^c x R) u (S x R^c) for the admissible (S, R), as frozensets of option pairs."""
    out = []
    for s_bits, r_bits in product(range(1 << d), repeat=2):
        if s_bits == r_bits and s_bits in (0, (1 << d) - 1):
            continue
        out.append(frozenset((a, b) for a in range(d) for b in range(d)
                             if (s_bits >> a & 1) != (r_bits >> b & 1)))
    return out


def conflicts(n, d, seed):
    """Conflict sets by block, rebuilt with the recorded generator's random choices."""
    rng = random.Random(seed)
    holes = {}
    for p in range(n // 2 + 1):
        chosen = rng.sample(range(n), 2 * d)
        for o in range(d):
            holes[(p, o)] = {chosen[2 * o], chosen[2 * o + 1]}
    blocks = {}
    for a, b in product(sorted(holes), repeat=2):
        if a[0] < b[0] and holes[a] & holes[b]:
            blocks.setdefault((a[0], b[0]), set()).add((a[1], b[1]))
    return blocks


def compare(n, d, seed, shapes):
    """(blocks, blocks with a relation by elimination, disagreements) for one pairing."""
    _, rows_by_block = bf.paired_rows_by_block(n, d, seed)
    by_conflicts = conflicts(n, d, seed)
    assert set(rows_by_block) == set(by_conflicts)
    eliminated = {key: bf.has_linear_relation(rows) for key, rows in rows_by_block.items()}
    combinatorial = {key: any(shape <= k for shape in shapes) for key, k in by_conflicts.items()}
    return len(eliminated), sum(eliminated.values()), sum(eliminated[k] != combinatorial[k] for k in eliminated)


def main(out):
    results = []
    for n, d in ((8, 3), (12, 3), (20, 3), (8, 4), (12, 4)):
        shapes = patterns(d)
        totals = [compare(n, d, seed, shapes) for seed in range(1, 201)]
        results.append({'holes': n, 'options': d, 'pairings': len(totals),
                        'blocks': sum(t[0] for t in totals), 'blocks_with_relation': sum(t[1] for t in totals),
                        'disagreements': sum(t[2] for t in totals)})
    with open(out, 'w') as handle:
        json.dump(results, handle, indent=1)
    print(json.dumps(results))


if __name__ == '__main__':
    main(sys.argv[1])
