"""Native rectangle upper bound on a subcube: ball-translate functionals detect degree-K functions.

Setting: over F_2, functions on the cube F_2^a (the support A of one error E, in affine coordinates; on the cube
u -> [E u] has kernel {u : u|_A = 0}, as in lem:native-functional-growth's proof). For a point set S, the
functional lambda_S = sum_{x in S} delta_x gives, in rectangle form at slack L, the conditions
f -> sum_{x in S} f(x) v(x) for v in P_L (polynomials of degree <= L). Detection of degree-<=K f by functionals
lambda_S1..lambda_Sm means: the rows (S_j, v) span the dual of P_K (rank N_a(K)).
Statement tested: the drafted lemma: with S_y = y + B_L (the Hamming ball of radius L translated by y) for the
N_a(K-L) points y of weight <= K-L, the rank is N_a(K); and at K=2, L=1 the explicit sets (a simplex and edge
sets) give rank N_a(2) with 2 functionals at a=3 and 3 at a=4, meeting the lower bound ceil(N_a(2)/N_a(1)).
Expected: rank N_a(K) for every (a, K, L) listed and for both explicit constructions.
Refuted by: a rank below N_a(K) for some listed case, which would refute the drafted lemma.
Possible because: the covering argument could be wrong, or P_L-independence of a translated ball could fail.
Control: removing one functional from the a=4 explicit construction must drop the rank below N_4(2) = 11.
Refuted by: rank 11 with two of the three functionals.
Possible because: a rank computation that ignores some rows would hide it.
Positive control: with m = ceil(N_a(2)/N_a(1)) - 1 functionals at a = 4 (two), the row count 2*5 = 10 < 11, so
any choice must fail; the script checks this on 200 random pairs of point sets.
Baseline: the recorded lower bound m >= N_a(K)/N_a(L) (lem:native-detection-count (a)) and the trivial upper
bound N_a(K) point evaluations; the drafted lemma sits between.
Record checked: the claims read were lem:native-detection-count, lem:native-functional-growth and
lem:coordinate-radical-realization; none gives an upper bound of order a^{K-L}.
"""
import argparse
import itertools
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import f2_span


def monomials(a, d):
    return [sum(1 << c for c in cs) for k in range(d + 1) for cs in itertools.combinations(range(a), k)]


def value(mono, x):
    return int(mono & x == mono)


def rank(a, K, L, sets):
    PK, PL = monomials(a, K), monomials(a, L)
    span = f2_span.Span()
    for S in sets:
        for v in PL:
            row = 0
            for k, f in enumerate(PK):
                if sum(value(f, x) & value(v, x) for x in S) & 1:
                    row |= 1 << k
            span.add(row)
    return len(span)


def ball_translates(a, K, L):
    ball = [x for x in range(1 << a) if bin(x).count('1') <= L]
    centers = [y for y in range(1 << a) if bin(y).count('1') <= K - L]
    return [[y ^ b for b in ball] for y in centers]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {'ball_translates': [], 'explicit': {}}
    for a, K, L in [(a, K, L) for a in range(3, 8) for K, L in ((1, 0), (2, 0), (2, 1), (3, 1), (3, 2))
                    if K <= a]:
        sets = ball_translates(a, K, L)
        r = rank(a, K, L, sets)
        NK = len(monomials(a, K))
        out['ball_translates'].append({'a': a, 'K': K, 'L': L, 'functionals': len(sets), 'rank': r, 'N_K': NK,
                                       'lower_bound': -(-NK // len(monomials(a, L)))})
        assert r == NK, (a, K, L)
    e = lambda *ix: sum(1 << i for i in ix)
    a3 = [[0, e(0), e(1), e(2)], [e(0, 1), e(1, 2), e(0, 2)]]
    a4 = [[0, e(0), e(1), e(2), e(3)], [e(0, 1), e(1, 2), e(2, 3)], [e(0, 2), e(0, 3), e(1, 3)]]
    out['explicit']['a=3'] = {'functionals': 2, 'rank': rank(3, 2, 1, a3), 'N_2': 7}
    out['explicit']['a=4'] = {'functionals': 3, 'rank': rank(4, 2, 1, a4), 'N_2': 11}
    assert out['explicit']['a=3']['rank'] == 7 and out['explicit']['a=4']['rank'] == 11
    drop = [rank(4, 2, 1, a4[:k] + a4[k + 1:]) for k in range(3)]
    out['control_drop_one'] = drop
    assert max(drop) < 11, 'control'
    rng = random.Random(17)
    pairs = [rank(4, 2, 1, [rng.sample(range(16), rng.randint(1, 16)) for _ in range(2)]) for _ in range(200)]
    out['positive_control_two_functionals_max_rank'] = max(pairs)
    assert max(pairs) < 11, 'positive control'
    print(json.dumps(out, indent=1), flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
