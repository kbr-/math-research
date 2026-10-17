"""Words with a part jumping across zero whose neighbouring pieces hold rows and columns: random F_2 search.

Hypothesis tested: for (2,-1,-2,1) (P = 2, 1, -1, 0; part 3 jumps from 1 to -1, and the positive piece before it
holds a row part and a column part), some product over F_2 of affine factors 1 + l_j has an ordered set-multilinear
projection with an invertible 8 by 8 partial derivative matrix (rows parts 1 and 4, columns parts 2 and 3).
Prediction: a positive fraction of 2000 random products of 16 or 32 factors is full rank.
Refuted by: zero full-rank products among the 2000 trials at both lengths.
Possible because: the reviewer's staircase for one jumping part needs L and R vectors, and here they are matrices.
Baseline: the plainest bound is rank at most 8, which decides nothing; thm:affine-component-ranks does not apply
since the cut, parts 1 and 4 against parts 2 and 3, is not contiguous.
Record checked: the claims lem:path-rank-saturation (draft) and lem:nested-word-rank-saturation were read; the
word is neither nested nor free of jumps, so neither decides it.
"""
import argparse
import json
import sys

import numpy as np

sys.path.insert(0, 'research/results/nested_word_rank_20261017')
from search_unmatched import coefficients, rank  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(20261017)
    w, out = [2, -1, -2, 1], []
    for L in (16, 32):
        full = 0
        for _ in range(2000):
            forms = [[rng.integers(0, 2, 2 ** abs(x)).astype(np.uint8) for x in w] for _ in range(L)]
            r, dim = rank(w, coefficients(w, forms))
            full += r == dim
        out.append(dict(word=w, factors=L, trials=2000, full_rank=int(full), dim=dim))
        print(out[-1])
    with open(args.out, 'w') as f:
        json.dump(out, f)


if __name__ == '__main__':
    main()
