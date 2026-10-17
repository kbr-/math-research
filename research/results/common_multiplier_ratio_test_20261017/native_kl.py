"""Native count of a variable error at general K and L, through the reduced board (lem:native-restriction).

Setting: by lem:native-restriction (b) and (c), for the functional pigeonhole system with D <= ceil(N/2) and
1+K+L <= D, the least number of old functionals detecting a variable error's kernel is the least number of
functionals lam_j on A_{K+L} with {u in A_K : lam_j(u v) = 0 for all v in A_L, all j} = 0, A_k = V_k(B)/W_k(B) on
the reduced board B modulo C (W_k the span of the x_s Q_i with |s|+1 <= k), A_k = V_k(B) modulo H. Over F_2.
Statement tested (the conjecture of the native-restriction entry, here at K = 3, L = 1): random functionals attain
the ratio lower bound ceil(dim A_K / dim A_L) in both models, on the reduced boards with 8 holes and 3, 4
pigeons (the boards with 4, 5 pigeons and 9 holes at D = 5 = ceil(9/2)); also run at K = L = 2 on the same boards
and as a validation at K = 2, L = 1 on six holes.
The extreme the question needs: m_min is a minimum over choices, so the least number of random functionals that
detect, minimized over seeds, is an upper bound, set beside the ratio lower bound.
Expected: the least number equals the ratio bound in both models on every board run (the conjecture).
Refuted by: on some board and model, no seed among twenty detecting with as many functionals as the ratio bound.
(Corrected after the runs: that criterion was met at K = L = 2, three pigeons, modulo the closure, and was badly
formed, a count being an existence claim that random seeds can miss; the rerun with 200 seeds found detecting
functionals, and total_eval.py's embedding explains them. Recorded in the entry.)
Possible because: on the cube the record has the count known only up to its ratio at K = 3, L = 1, and a slack
smaller than K - 1 leaves each functional's map A_K -> A_L^* structured (lem:native-functional-growth).
Control: with one functional fewer than the ratio bound no seed may detect.
Refuted by: a seed detecting below the ratio bound, which would mean the rank code or the dimensions are wrong.
Possible because: a wrong product table or W would change the rank the rows reach.
Forced by counts: this control is forced by the row count c dim A_L < dim A_K, and checks only the routine;
the assertion that no rank exceeds dim A_K is the control that can fail (W_K V_L in W_{K+L}, the annihilator).
No positive control: no instance of these models is known with a count above its ratio.
Baseline: the ratio bound from below and dim A_K from above (lem:native-restriction (d)); neither decides whether
the ratio is attained.
Record checked: lem:native-restriction and check:reduced-native-counts (K = 2, L = 1 only), lem:native-detection-
count (the bounds), lem:native-functional-growth and check:native-upper-ranks (the cube, where at K = 3, L = 1
the record gives only upper bounds by ball translates); none decides these counts.
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
    def __init__(self, m, n, top):
        self.m, self.n, self.top = m, n, top
        self.edges = [(i, h) for i in range(m) for h in range(n)]
        self.bit = {e: 1 << k for k, e in enumerate(self.edges)}
        mats = {0: [0]}
        for k in range(1, top + 1):
            mats[k] = [sum(self.bit[(i, h)] for i, h in zip(ps, hs))
                       for ps in itertools.combinations(range(m), k) for hs in itertools.permutations(range(n), k)]
        self.upto = {k: [mm for j in range(k + 1) for mm in mats[j]] for k in range(top + 1)}
        self.index = {k: {mm: i for i, mm in enumerate(self.upto[k])} for k in range(top + 1)}
        self.rows, self.holes = {}, {}
        for mm in self.upto[top]:
            es = [e for e in self.edges if mm & self.bit[e]]
            self.rows[mm] = {e[0] for e in es}
            self.holes[mm] = {e[1] for e in es}

    def W(self, k):
        """Generators x_s Q_i with |s|+1 <= k, s a matching avoiding row i, as vectors over V_k (Q_i = 1 + sum)."""
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


def run(m, holes, K, L, seeds, extra):
    t0 = time.time()
    b = Board(m, holes, K + L)
    nK, nL, nT = (len(b.upto[k]) for k in (K, L, K + L))
    WK, WL = Span(b.W(K)) if K else Span(), Span(b.W(L)) if L else Span()
    AK, AL = nK - len(WK), nL - len(WL)
    # for each b in V_L, the pairs (index of a in V_K, index of x_a x_b in V_{K+L}) with x_a x_b a matching
    table = []
    for bm in b.upto[L]:
        pairs = []
        for ai, am in enumerate(b.upto[K]):
            common = am & bm
            rest = bm & ~common
            if not (b.rows[am] & b.rows[rest] or b.holes[am] & b.holes[rest]):
                pairs.append((ai, b.index[K + L][am | bm]))
        table.append(pairs)
    gens = b.W(K + L)
    images = [0] * nT
    for g, w in enumerate(gens):
        bits = w
        while bits:
            low = bits & -bits
            images[low.bit_length() - 1] |= 1 << g
            bits ^= low
    perp = kernel(nT, images)
    out = {'pigeons': m, 'holes': holes, 'K': K, 'L': L, 'dim_VK': nK, 'dim_VL': nL, 'dim_VT': nT,
           'dim_WK': len(WK), 'dim_WL': len(WL), 'dim_perp_WT': len(perp)}
    for model, (target, dimAL, draw) in {
            'H': (nK, nL, lambda rng: rng.getrandbits(nT)),
            'C': (AK, AL, lambda rng: xor_combination(perp, rng))}.items():
        lower = -(-target // dimAL)
        least = []
        for seed in range(seeds):
            rng = random.Random(10000 * m + 100 * K + seed + (0 if model == 'H' else 5000))
            s = Span()
            got = None
            for c in range(1, lower + extra + 1):
                lam = draw(rng)
                for pairs in table:
                    row = 0
                    for ai, ci in pairs:
                        if lam >> ci & 1:
                            row |= 1 << ai
                    s.add(row)
                assert len(s) <= target, 'rank above dim A_K'
                if c == lower - 1:
                    assert len(s) < target, 'control: detection below the ratio bound'
                if len(s) == target:
                    got = c
                    break
            least.append(got)
        out[model] = {'dim_AK': target, 'dim_AL': dimAL, 'lower': lower, 'least_by_seed': least,
                      'upper': min((c for c in least if c is not None), default=None)}
    out['seconds'] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--pigeons', default='3,4')
    ap.add_argument('--holes', type=int, default=8)
    ap.add_argument('--K', type=int, default=3)
    ap.add_argument('--L', type=int, default=1)
    ap.add_argument('--seeds', type=int, default=20)
    ap.add_argument('--extra', type=int, default=12)
    args = ap.parse_args()
    res = []
    for m in [int(t) for t in args.pigeons.split(',')]:
        res.append(run(m, args.holes, args.K, args.L, args.seeds, args.extra))
        print(json.dumps(res[-1]), flush=True)
        pathlib.Path(args.out).write_text(json.dumps(res, indent=1) + '\n')


if __name__ == '__main__':
    main()
