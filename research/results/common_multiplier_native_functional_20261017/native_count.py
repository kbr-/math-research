"""Native count of a single-variable error on the functional pigeonhole system, through its reduced board.

Setting (the entry's restriction lemma): for the functional pigeonhole system with m pigeons and N >= 7 holes,
D = 4 <= ceil(N/2), an error x_e, K = 2 and L = 1, the least number m_min(C) of old functionals modulo C whose
rectangle forms (u, v) -> mu(x_e u v) detect Ann_C(x_e) cap V_2 equals the least number of linear functionals
lam_j on A_3 = V_3(B)/W_3(B) with {u in A_2 : lam_j(u v) = 0 for all v in A_1, all j} = 0, where B is the reduced
board (m-1 pigeons, N-1 holes) and W_k(B) the span of the x_s Q_i of degree <= k modulo H; m_min(H) is the same
count with W replaced by 0 (the matching domain). Over F_2, Q_i = 1 + sum_h x_ih.
Statement tested (a conjecture of the entry, written before the run): random functionals attain the ratio lower
bound ceil(dim A_2 / dim A_1) of lem:native-detection-count in both models, on the reduced boards with 6 holes
and 3..7 pigeons, so that m_min(C) and m_min(H) over F_2 equal those bounds there.
The extreme the question needs: m_min is a minimum over choices of functionals, so a random choice that detects
gives an upper bound and the lower bound is the ratio; the script reports the least number of random functionals
that detected, over seeds (the minimum over seeds is the upper bound used), beside the lower bound.
Expected: the least number equals the lower bound in both models on every board run.
Refuted by: on some board and model, no seed detecting with as many functionals as the lower bound.
Possible because: rectangle forms of one functional are structured (one functional's map A_2 -> A_1^* need not
have full rank, and the maps of several functionals can share kernel), as lem:native-functional-growth shows on
the cube, where the count grows past the ratio.
Control: with one functional fewer than the lower bound no seed may detect.
Refuted by: a seed detecting below the ratio bound, which would mean the rank code or the dimensions are wrong.
Possible because: a wrong product table or a wrong W would change the rank the rows reach.
Forced by counts: this control is forced, c dim A_1 < dim A_2 rows cannot reach rank dim A_2; it tests only the
routine's row count, and is reported so.
No positive control: no recorded instance of these models has a known native count above its ratio bound to
check that the code would see one; the check is that ranks are compared with dim A_2 computed independently as
dim V_2 - dim W_2 and against the hand count of dancing matchings (36 and 435 at seven pigeons).
Baseline: the ratio bound ceil(dim A_2 / dim A_1) from below and dim A_2 (one functional per dual basis vector,
lem:native-detection-count with c = 1) from above; neither decides whether the ratio is attained.
Record checked: lem:native-detection-count (the bounds above), lem:native-rectangle-upper-bound and
lem:native-functional-growth (the cube), prop:top-degree-native-count (product system), check:native-upper-ranks
(cube ranks); none gives these counts on the functional system or its reduced boards.
Decisive at these sizes: the outcomes differ by at least one functional at each board, and over five seeds the
least detecting count either equals the bound or exceeds it, with no spread to average over.
Parallel use: one process; the boards are small and the run takes about a minute, below the cost of
splitting it into processes.
"""
import argparse
import itertools
import json
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from f2_span import Span


def kernel(n, images):
    """A basis of {c in F_2^n : sum c_k images[k] = 0}, as rows of [image | identity] with zero image part."""
    s = Span()
    for k, img in enumerate(images):
        s.add((img << n) | (1 << k))
    return [row for h, row in s.piv.items() if h < n]


def xor_combination(vectors, rng):
    """A uniformly random F_2 combination of the given vectors (an XOR, not an integer sum)."""
    out = 0
    for v in vectors:
        if rng.getrandbits(1):
            out ^= v
    return out


class Board:
    def __init__(self, m, n):
        self.m, self.n = m, n
        self.edges = [(i, h) for i in range(m) for h in range(n)]
        self.bit = {e: 1 << k for k, e in enumerate(self.edges)}
        self.mats = {k: [] for k in range(4)}
        self.mats[0] = [0]
        for k in range(1, 4):
            for es in itertools.combinations(self.edges, k):
                if len({e[0] for e in es}) == k and len({e[1] for e in es}) == k:
                    self.mats[k].append(sum(self.bit[e] for e in es))
        self.upto = {k: [mm for j in range(k + 1) for mm in self.mats[j]] for k in range(4)}
        self.index = {k: {mm: i for i, mm in enumerate(self.upto[k])} for k in range(4)}
        self.rows = {mm: {e[0] for e in self.edges if mm & self.bit[e]} for mm in self.upto[3]}
        self.holes = {mm: {e[1] for e in self.edges if mm & self.bit[e]} for mm in self.upto[3]}

    def W(self, k):
        """Generators x_s Q_i of degree <= k, s a matching avoiding row i, as vectors over V_k."""
        idx = self.index[k]
        gens = []
        for i in range(self.m):
            for s in self.upto[k - 1]:
                if i in self.rows[s]:
                    continue
                v = 1 << idx[s]
                for h in range(self.n):
                    if h not in self.holes[s]:
                        v ^= 1 << idx[s | self.bit[(i, h)]]
                gens.append(v)
        return gens


def run(m, seeds, extra):
    t0 = time.time()
    b = Board(m, 6)
    n1, n2, n3 = (len(b.upto[k]) for k in (1, 2, 3))
    W1, W2, W3 = (Span(b.W(k)) for k in (1, 2, 3))
    A1, A2 = n1 - len(W1), n2 - len(W2)
    # products: for each a in V_2 and b in V_1, the V_3 index of the matching a | b, or None
    table = []
    for bm in b.upto[1]:
        pairs = []
        for ai, am in enumerate(b.upto[2]):
            # x_a x_b in the multilinear ring modulo H: x_a when b is the constant or an edge of a, x_{a|b} when
            # b shares no pigeon or hole with a, and 0 (a non-matching monomial) otherwise
            if bm == 0 or am & bm == bm or not (b.rows[am] & b.rows[bm] or b.holes[am] & b.holes[bm]):
                pairs.append((ai, b.index[3][am | bm]))
        table.append(pairs)
    # W_3's annihilator: functionals lam with lam . w = 0 for every generator w of W_3
    gens3 = b.W(3)
    images = [0] * n3
    for g, w in enumerate(gens3):
        bits = w
        while bits:
            low = bits & -bits
            images[low.bit_length() - 1] |= 1 << g
            bits ^= low
    perp = kernel(n3, images)
    out = {'pigeons': m, 'holes': 6, 'dim_V1': n1, 'dim_V2': n2, 'dim_V3': n3, 'dim_W1': len(W1),
           'dim_W2': len(W2), 'dim_W3': len(W3), 'dim_perp_W3': len(perp)}
    assert len(perp) == n3 - len(W3)
    for model, (target, dimA1, draw) in {
            'H': (n2, n1, lambda rng: rng.getrandbits(n3)),
            'C': (A2, A1, lambda rng: xor_combination(perp, rng))}.items():
        lower = -(-target // dimA1)
        least = []
        for seed in range(seeds):
            rng = random.Random(1000 * m + seed + (0 if model == 'H' else 500))
            s = Span()
            got = None
            for c in range(1, lower + extra + 1):
                lam = draw(rng) & ((1 << n3) - 1)
                for pairs in table:
                    row = 0
                    for ai, ci in pairs:
                        if lam >> ci & 1:
                            row |= 1 << ai
                    s.add(row)
                assert len(s) <= target, 'rank above dim A_2'
                if c == lower - 1:
                    assert len(s) < target, 'control: detection below the ratio bound'
                if len(s) == target:
                    got = c
                    break
            least.append(got)
        out[model] = {'dim_A2': target, 'dim_A1': dimA1, 'lower': lower, 'least_by_seed': least,
                      'upper': min((c for c in least if c is not None), default=None)}
    out['seconds'] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--pigeons', default='3,4,5')
    ap.add_argument('--seeds', type=int, default=5)
    ap.add_argument('--extra', type=int, default=12)
    args = ap.parse_args()
    res = []
    for m in [int(t) for t in args.pigeons.split(',')]:
        res.append(run(m, args.seeds, args.extra))
        print(json.dumps(res[-1]), flush=True)
        pathlib.Path(args.out).write_text(json.dumps(res, indent=1) + '\n')
    if res and res[-1]['pigeons'] == 7:
        assert res[-1]['C']['dim_A2'] == 435 and res[-1]['C']['dim_A1'] == 36, 'hand counts of dancing matchings'


if __name__ == '__main__':
    main()
