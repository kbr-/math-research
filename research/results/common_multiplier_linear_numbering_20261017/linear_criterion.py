"""The two-pigeon dance criterion for linear errors at K=1, against the exact dance search.

Setting: the functional pigeonhole board with 6 pigeons and 5 holes, numberings as in numberings.py
(research/results/common_multiplier_functional_transfer_20261016), the property of lem:admissible-numbering-transfer
at K=1 for a set S of single edges (the matching monomials of linear errors): for every edge E in S and every t of
size <= 1 with a dance and t cup E a matching, t cup E has a dance.
Statement tested (the entry's criterion, derived by hand from Definition 2.3): under a numbering whose hole ranks
put hole of rank N-1 at the top, the property holds exactly when (i) no edge of S uses the top hole, (ii) every
edge of S at hole rank N-2 has its pigeon before every other pigeon, and (iii) every edge of S at hole rank N-3 has
its pigeon after every other pigeon. The extreme the question needs: an equivalence, so the script compares the
two truth values on every numbering it tries, in both directions.
Expected: agreement on every (S, numbering) pair tried.
Refuted by: one pair where the search and the criterion disagree, printed with S and the numbering.
Possible because: the hand derivation considered only two-pigeon matchings and might miss a case, such as t
using the hole of rank N-3 while E sits at rank N-2 with the same pigeon order reversed.
Control: the factors' monomials {x00,x11,x22,x33} under pigeons 3,0,1,4,5,2 (holes 0..4) pass, and under
pigeons 3,2,1,0,4,5 fail, as factor_numbering.json records.
Refuted by: either recorded outcome reversed.
Possible because: a wrong import or rank direction.
Forced by counts: no count forces agreement; each pair is decided by the exact search.
Positive control: a set with an edge at the top hole must fail under the search and the criterion alike.
Refuted by: the search passing it, which would mean the search lets a pigeon at the top hole stay put.
Possible because: an off-by-one in the hole ranks.
Baseline: the band review's necessary condition (a free top hole) decides only clause (i); nothing plainer decides
clauses (ii) and (iii).
Record checked: check:six-by-five-numberings (monomial sets, exact search), cor:nested-hole-joint-transfer (nested
hole sets), lem:ballot-dance-maps (dances for hole sets in every pigeon order); none states this criterion.
"""
import argparse
import importlib.util
import itertools
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    'numberings', ROOT / 'research/results/common_multiplier_functional_transfer_20261016/numberings.py')
nb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nb)
P, N = 6, 5


def ranks(order):
    return {x: k for k, x in enumerate(order)}


def criterion(S, prank, hrank):
    first = min(prank, key=prank.get)
    last = max(prank, key=prank.get)
    for p, h in S:
        r = hrank[h]
        if r == N - 1:
            return False
        if r == N - 2 and p != first:
            return False
        if r == N - 3 and p != last:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    F = [{0: 0}, {1: 1}, {2: 2}, {3: 3}]
    ident = ranks(range(N))
    assert not nb.failures(F, ranks((3, 0, 1, 4, 5, 2)), ident), 'control: the found numbering'
    assert nb.failures(F, ranks((3, 2, 1, 0, 4, 5)), ident), 'control: the reviewer numbering'
    assert nb.failures([{0: 4}], ranks(range(P)), ident), 'positive control'
    rng = random.Random(20261017)
    edges = [(p, h) for p in range(P) for h in range(N)]
    pairs = agree = holds = 0
    disagreements = []
    for trial in range(300):
        S = rng.sample(edges, rng.randint(1, 6))
        for _ in range(12):
            po = list(range(P)); rng.shuffle(po)
            ho = list(range(N)); rng.shuffle(ho)
            prank, hrank = ranks(po), ranks(ho)
            search = not nb.failures([{p: h} for p, h in S], prank, hrank)
            crit = criterion(S, prank, hrank)
            pairs += 1
            holds += search
            if search == crit:
                agree += 1
            else:
                disagreements.append({'S': S, 'pigeons': po, 'holes': ho, 'search': search})
    # sets built to satisfy the criterion, so that the 'holds' side is exercised too
    built = built_ok = 0
    for trial in range(300):
        po = list(range(P)); rng.shuffle(po)
        ho = list(range(N)); rng.shuffle(ho)
        top, second, third = ho[-1], ho[-2], ho[-3]
        low = [h for h in ho[:-3]]
        S = [(rng.randrange(P), rng.choice(low)) for _ in range(rng.randint(1, 4))]
        S += [(po[0], second)] * rng.randint(0, 1) + [(po[-1], third)] * rng.randint(0, 1)
        S = list(dict.fromkeys(S))
        prank, hrank = ranks(po), ranks(ho)
        assert criterion(S, prank, hrank)
        built += 1
        built_ok += not nb.failures([{p: h} for p, h in S], prank, hrank)
    out = {'random_pairs': pairs, 'agree': agree, 'property_held': holds, 'disagreements': disagreements[:5],
           'built_pairs': built, 'built_pass_search': built_ok}
    print(json.dumps({k: v for k, v in out.items() if k != 'disagreements'}), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
