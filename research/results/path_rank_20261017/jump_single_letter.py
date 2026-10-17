"""(2,-1,-2,1) with products of single-letter factors 1 + x over F_2: random search.

Hypothesis tested: some product of factors 1 + x, each x one letter of one part (the lemma's class of products,
not the general affine factors of jump_search.py), has an ordered set-multilinear projection of (2,-1,-2,1) with an
invertible 8 by 8 partial derivative matrix over F_2 (rows parts 1 and 4, sizes 4 and 2; columns parts 2 and 3,
sizes 2 and 4).
Prediction: none expected; the reviewer reported no odd determinant in 30000 random sequences of 24 factors,
unsaved.
Refuted by: a full-rank sequence among the trials, which would decide the smallest case by a single-letter product.
Possible because: the reviewer's run covered one length only, and longer sequences give more chains.
Baseline: rank at most 8; the general affine search found full rank in 241 of 2000 16-factor products, which says
nothing about single-letter products.
Record checked: the claims lem:path-rank-saturation (draft) and lem:nested-word-rank-saturation were read; neither
covers this word.
"""
import argparse
import json
import sys

import numpy as np

sys.path.insert(0, 'research/results/path_rank_20261017')
sys.path.insert(0, 'tools')
from check import integer_pdm  # noqa: E402
from f2_span import Span  # noqa: E402


def rank2(m):
    span = Span()
    for r in m:
        span.add(int(''.join(str(int(x) % 2) for x in r), 2))
    return len(span)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    w = [2, -1, -2, 1]
    letters = [(i, a) for i, x in enumerate(w) for a in range(2 ** abs(x))]
    rng = np.random.default_rng(20261017)
    out = []
    for L in (24, 32, 48):
        full, witness = 0, None
        for _ in range(4000):
            seq = [letters[j] for j in rng.integers(0, len(letters), L)]
            if rank2(integer_pdm(w, seq)) == 8:
                full += 1
                witness = witness or seq
        out.append(dict(word=w, factors=L, trials=4000, full_rank=full, witness=witness))
        print({k: v for k, v in out[-1].items() if k != 'witness'}, 'witness' if witness else 'no witness')
    with open(args.out, 'w') as f:
        json.dump(out, f)


if __name__ == '__main__':
    main()
