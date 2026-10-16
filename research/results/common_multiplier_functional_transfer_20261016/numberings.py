"""Admissible numberings for the recorded six-by-five error sets (lem:admissible-numbering-transfer).

A numbering orders the pigeons and the holes. A matching admits a dance (Impagliazzo-Pudlak-Sgall, Definition
2.3) if its pigeons, taken in increasing order, can each move to a strictly larger hole unoccupied at that moment;
dance() searches all choices, so it decides existence exactly. The property of the lemma, for a set F at K=1:
for every matching E in F and every t of size <= 1 with a dance and t cup E a matching, t cup E has a dance.
Statement tested: the hand checks of the entry: the chain {x00x11,x11x22} has the property for holes ordered
1,0,2,3,4 and pigeons 0,3,4,5,1,2; the shared set {x00x11,x00x22} for holes 0,1,2,3,4 and pigeons 3,4,5,1,2,0;
the diagonal pair {x00x11,x22x33} for holes 0,1,2,3,4 and pigeons 3,2,1,0,4,5. Then, for the triple
{x00x11,x22x33,x34x43}, a search over all 5! hole orders and 6! pigeon orders for one with the property.
Expected: the three hand numberings pass; the triple's outcome is not predicted.
Refuted by: a printed failing (E, t) for one of the three hand numberings, which would withdraw that hand check.
Possible because: the hand checks chose each pigeon's target greedily and might have missed a blocking case.
Control: the corollary's crossing set {x00x11,x01x10} with holes 0,1,2,3,4 and pigeons 2,3,4,5,0,1 (its proof's
numbering) must pass.
Positive control: the single error {x04x13} (pigeon 0 at the top hole) with the identity numbering must fail,
since t empty gives a pigeon at the top hole, which cannot move.
Refuted by: the positive control passing, which would mean dance() accepts a pigeon that cannot move.
Possible because: an off-by-one in the hole positions would let the top pigeon stay put.
Baseline: the corollary's room condition decides none of the four sets (their hole sets are not nested), and
the bare count of holes does not decide whether a dance exists; nothing plainer decides them.
Record checked: lem:ballot-dance-maps gives dances for hole sets meeting a ballot condition in every pigeon
order; it does not decide these (E, t) pairs under one numbering. check:block-pair-kernels found excess 0 for all
four sets, which the property would explain but does not imply.
"""
import argparse
import itertools
import json

PIGEONS, HOLES = 6, 5


def dance(match, prank, hrank):
    """Whether the matching {pigeon: hole} admits a dance under the given pigeon and hole ranks."""
    order = sorted(match, key=lambda p: prank[p])

    def go(k, pos):
        if k == len(order):
            return True
        p = order[k]
        taken = set(pos.values())
        for h in range(HOLES):
            if hrank[h] > hrank[pos[p]] and h not in taken:
                if go(k + 1, {**pos, p: h}):
                    return True
        return False
    return go(0, dict(match))


def failures(F, prank, hrank):
    out = []
    singles = [{}] + [{p: h} for p in range(PIGEONS) for h in range(HOLES)]
    for E in F:
        for t in singles:
            if not dance(t, prank, hrank):
                continue
            u = {**t}
            ok = True
            for p, h in E.items():
                if (p in u and u[p] != h) or any(q != p and g == h for q, g in u.items()):
                    ok = False
                u[p] = h
            if ok and not dance(u, prank, hrank):
                out.append((E, t))
    return out


def ranks(order):
    return {x: i for i, x in enumerate(order)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    out = {}
    args = ap.parse_args()
    cases = {
        'chain': ([{0: 0, 1: 1}, {1: 1, 2: 2}], [1, 0, 2, 3, 4], [0, 3, 4, 5, 1, 2]),
        'shared': ([{0: 0, 1: 1}, {0: 0, 2: 2}], [0, 1, 2, 3, 4], [3, 4, 5, 1, 2, 0]),
        'diagonal pair': ([{0: 0, 1: 1}, {2: 2, 3: 3}], [0, 1, 2, 3, 4], [3, 2, 1, 0, 4, 5]),
        'crossing (control)': ([{0: 0, 1: 1}, {0: 1, 1: 0}], [0, 1, 2, 3, 4], [2, 3, 4, 5, 0, 1]),
    }
    for name, (F, holes, pigeons) in cases.items():
        bad = failures(F, ranks(pigeons), ranks(holes))
        out[name] = {'holes': holes, 'pigeons': pigeons, 'failures': [[list(E.items()), list(t.items())]
                                                                       for E, t in bad]}
        print(name, 'PASS' if not bad else f'FAIL {bad[:3]}', flush=True)
    top = failures([{0: 4, 1: 3}], ranks(range(PIGEONS)), ranks(range(HOLES)))
    print('positive control (must fail):', 'FAIL as required' if top else 'PASSED, error', flush=True)
    assert top, 'positive control'
    assert not out['crossing (control)']['failures'], 'control'
    triple = [{0: 0, 1: 1}, {2: 2, 3: 3}, {3: 4, 4: 3}]
    found, tried = None, 0
    for holes in itertools.permutations(range(HOLES)):
        hr = ranks(holes)
        for pigeons in itertools.permutations(range(PIGEONS)):
            tried += 1
            if not failures(triple, ranks(pigeons), hr):
                found = (list(holes), list(pigeons))
                break
        if found:
            break
    out['triple'] = {'numbering': found, 'numberings tried': tried}
    print('triple:', found, 'after', tried, 'numberings', flush=True)
    with open(args.out, 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
