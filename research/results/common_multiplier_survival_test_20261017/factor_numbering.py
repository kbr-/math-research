"""Does one admissible numbering serve the collapsed two-factor form on the six-by-five board?

The two factors 1+q1 = 1+x00+x11 and 1+q2 = 1+x22+x33 have the matching monomials {}, {0:0}, {1:1}, {2:2},
{3:3}. The band review's polynomial extension of lem:admissible-numbering-transfer (an unregistered argument of
that review's Decision) gives their joint transfer when all these matchings share a numbering with the property
of the lemma: for every matching E and every t of size <= 1 with a dance and t cup E a matching, t cup E has a
dance (Impagliazzo-Pudlak-Sgall, Definition 2.3, as numberings.py implements it). The empty matching always
passes. The extreme the question needs: existence of one numbering, so the script tries the reviewer's numbering
(holes 0..4, pigeons 3,2,1,0,4,5) and then, if it fails, all 5! hole orders and 6! pigeon orders.
Statement tested: the reviewer's suggestion (unverified) that this numbering has the property.
Expected: not predicted; the reviewer's hand reasoning says it passes.
Refuted by: a printed failing (E, t) for the reviewer's numbering, which would withdraw the suggestion's step.
Possible because: the reviewer did not read the dance definition beyond one quotation.
Control: numberings.py's diagonal pair {x00x11, x22x33} with this same numbering passes, as check:six-by-five-
numberings records.
Refuted by: the control failing, which would mean this script calls the search wrongly.
Possible because: the import or the rank maps could be built in the wrong direction.
Forced by counts: no count forces either outcome; the search decides existence exactly.
Positive control: {x04x13} under the identity numbering fails (pigeon 0 at the top hole cannot move).
Refuted by: it passing, which would mean the search accepts a pigeon that cannot move.
Possible because: an off-by-one in the hole ranks.
Baseline: the free top hole is necessary for a numbering, not sufficient (band review), so the free hole 4 of
these monomials decides nothing.
Record checked: check:six-by-five-numberings (the diagonal pair passes under this numbering, which does not
imply its sub-matchings pass), lem:functional-killer-transfer (single monomials), cor:nested-hole-joint-transfer
(nested hole sets; these hole sets {0},{1},{2},{3} are not nested); none decides this set.
"""
import argparse
import importlib.util
import itertools
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    'numberings', ROOT / 'research/results/common_multiplier_functional_transfer_20261016/numberings.py')
nb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nb)


def ranks(pigeon_order, hole_order):
    return {p: k for k, p in enumerate(pigeon_order)}, {h: k for k, h in enumerate(hole_order)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    F = [{}, {0: 0}, {1: 1}, {2: 2}, {3: 3}]
    prank, hrank = ranks((3, 2, 1, 0, 4, 5), (0, 1, 2, 3, 4))
    assert not nb.failures([{0: 0, 1: 1}, {2: 2, 3: 3}], prank, hrank), 'control: the recorded diagonal pair'
    ip, ih = ranks(range(6), range(5))
    assert nb.failures([{0: 4, 1: 3}], ip, ih), 'positive control'
    bad = nb.failures(F, prank, hrank)
    out = {'reviewer_numbering': {'pigeons': [3, 2, 1, 0, 4, 5], 'holes': [0, 1, 2, 3, 4],
                                  'failures': [str(b) for b in bad]}}
    if bad:
        found = None
        for hs in itertools.permutations(range(5)):
            for ps in itertools.permutations(range(6)):
                pr, hr = ranks(ps, hs)
                if not nb.failures(F, pr, hr):
                    found = (ps, hs)
                    break
            if found:
                break
        out['search'] = {'found': found}
    print(json.dumps(out), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
