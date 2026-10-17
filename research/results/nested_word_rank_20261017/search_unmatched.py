"""Unmatched words: random products of affine factors over F_2, small cases.

Hypothesis tested: for the balanced words below, which have no non-crossing matching of equal and
opposite entries (so lem:nested-word-rank-saturation does not apply), some product over F_2 of L
factors 1 + l_j, each l_j a linear form in all the variables, has an ordered set-multilinear
projection with invertible partial derivative matrix (|X_i| = 2^|w_i|, rows over the parts with
w_i > 0). Random factors are drawn with each variable present with probability 1/2.

The coefficient of x_(1,a_1)...x_(d,a_d) is the sum over j_1 < ... < j_d of the product of the
coefficients of x_(t,a_t) in l_(j_t); each factor is processed from the last part down, so that
one factor supplies at most one letter of a chain.

Prediction: for (2,-1,-1) and (1,1,-2), a positive fraction of 2000 trials at L = 16 is full rank.
Refuted by: zero full-rank trials among the 2000 at every L run for a word.
Possible because: products of affine forms could have an F_2 parity obstruction on such words,
as the first hand construction for (2,-1,-1) had rank at most 3.
Baseline: the plainest bound is rank at most 4, the matrix dimension; thm:affine-component-ranks
bounds contiguous cuts by L, and these cuts are not contiguous, so neither decides full rank.
Record checked: the claims thm:affine-component-ranks and imp:noncommutative-homogenization-lower-bound
were read (FLST Proposition 24 needs paths with nonnegative partial sums and large fields; (2,-1,-1) is
such a path with k = 2 but F_2 is too small for its count); none decides these ranks.
Decisive at these sizes: exact ranks; a found full-rank product is a witness, not an estimate.
"""
import argparse
import json
import sys

import numpy as np

sys.path.insert(0, 'tools')
from f2_span import Span  # noqa: E402


def coefficients(w, forms):
    sizes = [2 ** abs(x) for x in w]
    levels = [np.ones(1, dtype=np.uint8)]
    for t in range(len(w)):
        levels.append(np.zeros(int(np.prod(sizes[:t + 1])), dtype=np.uint8))
    for form in forms:  # form[t] is a 0/1 vector over X_t
        for t in reversed(range(len(w))):
            prev = levels[t]
            cur = levels[t + 1].reshape(len(prev), sizes[t])
            cur ^= np.outer(prev, form[t]).astype(np.uint8) & 1
    return levels[len(w)].reshape(sizes)


def rank(w, coef):
    pos = [i for i, x in enumerate(w) if x > 0]
    neg = [i for i, x in enumerate(w) if x < 0]
    rows = int(np.prod([coef.shape[i] for i in pos]))
    m = np.transpose(coef, pos + neg).reshape(rows, -1)
    span = Span()
    for r in m:
        span.add(int(''.join('1' if b else '0' for b in r), 2))
    return len(span), rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(20261017)
    out = []
    for w in ([2, -1, -1], [1, 1, -2], [1, -2, 1]):
        for L in (8, 16, 32):
            full, witness = 0, None
            for _ in range(2000):
                forms = [[rng.integers(0, 2, 2 ** abs(x)).astype(np.uint8) for x in w]
                         for _ in range(L)]
                r, dim = rank(w, coefficients(w, forms))
                if r == dim:
                    full += 1
                    if witness is None:
                        witness = [[f.tolist() for f in form] for form in forms]
            row = dict(word=w, factors=L, trials=2000, full_rank=full, dim=dim)
            print(row)
            out.append(dict(row, witness=witness))
    with open(args.out, 'w') as f:
        json.dump(out, f)


if __name__ == '__main__':
    main()
