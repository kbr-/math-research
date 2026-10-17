"""The smallest unmatched path (2,-1,-1) over F_2: two constructions, every choice.

Statement tested: the reviewer's report that (i) the segment construction, factors in segments a = 1..4 of
the form x_(1,a), x_(2,beta(a)), x_(3,gamma(a)), has F_2 rank distribution {1: 16, 2: 108, 3: 116, 4: 16}
over all 256 maps beta, gamma: [4] -> [2], with beta = (0,0,1,1), gamma = (0,0,0,1) of full rank; and
(ii) the draft's hand claim that FLST's H_p at t = 1 for p = (2,-1,-1), k = 2, has rows a = 00 and 01 both
equal to (0,0,1,1) over F_2. H_p (FLST TR23-191, Section 7.1.5): one leaf, columns w in {0,1}^2 in lex
order, H_(1,w) = x_(1,w[1:2]), H_(2,w) = x_(2,w[2]), H_(3,w) = x_(3,w[1]) at t = 1, and H_p = BE(H), the
sum over nondecreasing sigma_1 <= sigma_2 <= sigma_3 of H_(1,sigma_1) H_(2,sigma_2) H_(3,sigma_3).
Expected: (i) the distribution {1: 16, 2: 108, 3: 116, 4: 16}; (ii) rank 3 with rows 00 and 01 equal.
Refuted by: any other rank distribution in (i), or rows 00 and 01 differing in (ii).
Possible because: the reviewer's enumeration and the draft's hand computation were neither saved nor rerun.
Baseline: the plainest bound is rank at most 4, the matrix dimension, which decides neither count.
Record checked: the claims lem:nested-word-rank-saturation (draft) and imp:noncommutative-homogenization-lower-bound
were read; neither decides these small F_2 ranks.
"""
import argparse
import itertools
import json

import numpy as np


def rank2(m):
    m = [int(''.join(str(int(b)) for b in row), 2) for row in m]
    r = 0
    pivots = []
    for row in m:
        for p in pivots:
            row = min(row, row ^ p)
        if row:
            pivots.append(row)
            r += 1
    return r


def segment_matrix(beta, gamma):
    seq = []
    for a in range(4):
        seq += [(0, a), (1, beta[a]), (2, gamma[a])]
    m = np.zeros((4, 4), dtype=np.int64)
    for i, j, l in itertools.combinations(range(len(seq)), 3):
        (t1, a), (t2, b), (t3, c) = seq[i], seq[j], seq[l]
        if (t1, t2, t3) == (0, 1, 2):
            m[a, 2 * b + c] += 1
    return m % 2


def flst_matrix():
    cols = [(0, 0), (0, 1), (1, 0), (1, 1)]
    m = np.zeros((4, 4), dtype=np.int64)
    for s1, s2, s3 in itertools.combinations_with_replacement(range(4), 3):
        a = 2 * cols[s1][0] + cols[s1][1]
        b, c = cols[s2][1], cols[s3][0]
        m[a, 2 * b + c] += 1
    return m % 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    dist, witness = {}, None
    for beta in itertools.product(range(2), repeat=4):
        for gamma in itertools.product(range(2), repeat=4):
            r = rank2(segment_matrix(beta, gamma))
            dist[r] = dist.get(r, 0) + 1
    full = segment_matrix((0, 0, 1, 1), (0, 0, 0, 1))
    print('segment construction rank distribution over 256 maps:', dict(sorted(dist.items())))
    print('beta=(0,0,1,1), gamma=(0,0,0,1):', full.tolist(), 'rank', rank2(full))
    f = flst_matrix()
    print('FLST H_p at t=1, rows a=00,01,10,11:', f.tolist(), 'rank', rank2(f))
    with open(args.out, 'w') as h:
        json.dump(dict(segment_distribution=dist, segment_witness=full.tolist(),
                       flst_t1=f.tolist(), flst_t1_rank=rank2(f)), h)


if __name__ == '__main__':
    main()
