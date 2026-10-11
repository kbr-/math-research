"""The blocking closure of a paired-pigeon instance: a combinatorial sufficient condition for degree three.

Statement behind it (proved in the entry): in a paired-pigeon subspace, call two options of different pairs
conflicting when their product is in the degree-3 closure, and an option dead when its form is.  Rows give the
first conflicts.  Rule: if every option of a pair p is dead, conflicts with b or conflicts with c, for options
b, c not of p, then b and c conflict (with b = c: b is dead).  If the rule's closure kills every option of
some pair, the system has a polynomial calculus refutation of degree three.

Part 1: on the fourteen instances of pairings-32.json (exact degree 3 at 24 to 44 holes), does the closure
refute?  If it does on all, it is the mechanism of their degree three; if on none, the mechanism is another.

Part 2: random pairings, three options, at 64 to 1024 holes, unfiltered.  Estimate written before the run: a
pair blocks a given two options when each of its three options meets one of their four holes, probability
about (8/n)^3, over about (n/2)(1.5 n)^2/2 choices: about 290 first derived conflicts whatever n, beside
about 3 n rows.  Prediction: the closure refutes while those are many against the rows and stops refuting at
some size in the hundreds or low thousands, where it stalls after a bounded number of derived conflicts; if
it refutes at every size run, the class has degree three at all of them and the estimate misses a cascade.

Added after review, the text above left as written before the run: the estimate's factor is wrong, a pair's
six holes being distinct (8 * 6 * 4 = 192 in place of 8^3 = 512, about 108 in place of 290); the output now
records the first-round count of each instance, the row count is asserted against the recorded one, and part
1b runs the closure on the 242 instances of the item's third entry (block-free.json).

Usage: python3 blocking.py RECORDED.json BLOCK_FREE.json OUT.json
"""
import json
import random
import sys


def options(n, d, seed):
    """Holes of each option, as the recorded generator draws them: option index = d * pair + choice."""
    rng = random.Random(seed)
    holes = []
    for _ in range(n // 2 + 1):
        chosen = rng.sample(range(n), 2 * d)
        holes += [{chosen[2 * o], chosen[2 * o + 1]} for o in range(d)]
    return holes


def first_conflicts(holes, d):
    """Bit sets: bit c of result[b] when options b and c of different pairs share a hole."""
    users = {}
    for o, pair_holes in enumerate(holes):
        for hole in pair_holes:
            users.setdefault(hole, []).append(o)
    conflict = [0] * len(holes)
    for sharing in users.values():
        mask = sum(1 << o for o in sharing)
        for o in sharing:
            own = ((1 << d) - 1) << (o // d * d)
            conflict[o] |= mask & ~own
    return conflict


def blocked_by(conflict, dead, pair, d, everything):
    """New conflicts forced by one pair: for each b, the c such that every option of the pair is dead or
    conflicts with b or with c.  Returns a list of (b, set of c as bits)."""
    live = [o for o in range(pair * d, pair * d + d) if not dead >> o & 1]
    own = ((1 << d) - 1) << (pair * d)
    candidates = 0
    for o in live:
        candidates |= conflict[o]
    candidates &= ~own
    found = []
    while candidates:
        low = candidates & -candidates
        b = low.bit_length() - 1
        candidates ^= low
        partners = everything & ~own
        for o in live:
            if not conflict[o] >> b & 1:
                partners &= conflict[o]
        found.append((b, partners))
    return found


def closure(holes, d):
    """(refuted, derived conflicts, rounds) of the blocking closure."""
    count = len(holes)
    everything = (1 << count) - 1
    conflict = first_conflicts(holes, d)
    start = sum(bin(c).count('1') for c in conflict) // 2
    dead, rounds, changed = 0, 0, True
    while changed:
        changed, rounds = False, rounds + 1
        for pair in range(count // d):
            if (dead >> (pair * d)) & ((1 << d) - 1) == (1 << d) - 1:
                return True, sum(bin(c).count('1') for c in conflict) // 2 - start, rounds, start
            changed |= apply(conflict, blocked_by(conflict, dead, pair, d, everything))
        newly = sum(1 << b for b in range(count) if conflict[b] >> b & 1) & ~dead
        if newly:
            dead |= newly
            changed = True
            spread(conflict, newly, everything, d)
    return False, sum(bin(c).count('1') for c in conflict) // 2 - start, rounds, start


def first_round(holes, d):
    """The conflicts rule (ii) derives from the rows alone, each pair applied once to the first conflicts."""
    conflict = first_conflicts(holes, d)
    everything = (1 << len(holes)) - 1
    fresh = set()
    for pair in range(len(holes) // d):
        for b, partners in blocked_by(conflict, 0, pair, d, everything):
            fresh |= members(b, partners & ~conflict[b])
    return len(fresh)


def members(b, mask):
    return {frozenset((b, c)) for c in range(mask.bit_length()) if mask >> c & 1}


def apply(conflict, found):
    changed = False
    for b, partners in found:
        fresh = partners & ~conflict[b]
        if fresh:
            conflict[b] |= fresh
            changed = True
            mark(conflict, fresh, b)
    return changed


def mark(conflict, fresh, b):
    while fresh:
        low = fresh & -fresh
        conflict[low.bit_length() - 1] |= 1 << b
        fresh ^= low


def spread(conflict, newly, everything, d):
    """A dead option conflicts with every option."""
    for b in range(len(conflict)):
        if newly >> b & 1:
            conflict[b] = everything
            mark(conflict, everything, b)


def run(n, seed, rows=None):
    holes = options(n, 3, seed)
    refuted, derived, rounds, start = closure(holes, 3)
    assert rows is None or rows == start, (n, seed, rows, start)     # the recorded instance, by its row count
    return {'holes': n, 'seed': seed, 'rows': start, 'refuted_by_blocking': refuted,
            'derived_conflicts_at_exit': derived, 'first_round_conflicts': first_round(holes, 3), 'rounds': rounds}


def earlier_seeds(bf, n, count):
    """The seeds of the recorded survey at n holes: the first `count` relation-free ones after 1000 n."""
    seeds, seed = [], 1000 * n
    while len(seeds) < count:
        seed = bf.relation_free(n, seed)[0]
        seeds.append(seed)
    return seeds


def main(recorded, earlier, out):
    """Part 1 on the run's fourteen instances; part 1b on the 242 of the item's third entry (the twelve listed
    in its output and its two surveys, regenerated); part 2 at larger sizes."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        'block_free', Path(__file__).resolve().parent.parent / 'near-half-block-free-pairing-20261011' / 'block_free.py')
    bf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bf)
    part1 = [dict(run(r['holes'], r['seed'], r['rows']), exact_degree=r['degree']) for r in json.load(open(recorded))]
    listed = [r for r in json.load(open(earlier))['runs'] if r['kind'] == 'paired, relation-free']
    part1b = [dict(run(r['holes'], r['seed'], r['rows']), exact_degree=r['degree']) for r in listed]
    part1b += [dict(run(20, seed), exact_degree=3) for seed in earlier_seeds(bf, 20, 200)]
    part1b += [dict(run(24, seed), exact_degree=3) for seed in earlier_seeds(bf, 24, 30)]
    cases = [(n, 1000 * n + k) for n in (64, 128, 256, 512, 1024) for k in (1, 2, 3, 4, 5)]
    part2 = [run(n, seed) for n, seed in cases]
    with open(out, 'w') as handle:
        json.dump({'recorded': part1, 'earlier': part1b, 'larger': part2}, handle, indent=1)
    print(json.dumps({'earlier_refuted': sum(r['refuted_by_blocking'] for r in part1b), 'earlier': len(part1b),
                      'rest': [[r['holes'], r['refuted_by_blocking'], r['derived_conflicts_at_exit'],
                                r['first_round_conflicts'], r['rounds']] for r in part1 + part2]}))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
