"""Nested-word rank saturation over F_2, small cases.

Statement tested (lem:nested-word-rank-saturation, part (a)): for a word w in (Z minus 0)^d whose
positions have a non-crossing perfect matching into pairs u < v with w_u = -w_v, the product of
factors (1 + x) in the order S(w) built below has an ordered set-multilinear projection whose
partial derivative matrix (rows: monomials over the parts i with w_i > 0, |X_i| = 2^|w_i|;
columns: over the parts with w_i < 0) is invertible over F_2.

S(w): the empty word gives the empty sequence; a concatenation gives the concatenation of the
sequences; a matched pair (u, W', v) with q = 2^|w_u| gives, for a = 1..q in turn,
[x_(u,a)] + S(W') + [x_(v,a)].

The coefficient of x_(1,a_1) ... x_(d,a_d) in the product is the number, mod 2, of increasing
chains j_1 < ... < j_d of factor positions whose variables are x_(t,a_t). It is computed by
processing the factors in order: a factor x_(t,a) adds the level-(t-1) prefix counts to the
level-t counts with a_t = a (numpy XOR over prefix arrays).

Expected: full rank 2^(sum of positive |w_i|) for every nested word run below.
Refuted by: any nested word below printing a rank below its matrix dimension over F_2.
Possible because: the triangular block argument could be wrong, for example cancellation mod 2 in
the diagonal blocks, which the proof claims are copies of the inner matrix.
Control: the pair word (1,-1) with its factor sequence reversed, whose matrix by hand is
[[0,0],[1,0]], so rank 1; the routine must print rank 1 there.
Refuted by: the reversed control printing rank 2, which would mean the chain count ignores order.
Possible because: a chain counter that sums over all position pairs, not increasing ones, gives 2.
Forced by counts: on (1,-1) the matrix is 2 by 2 and the product has 4 factors, so the counts
allow rank 0, 1 or 2 for both orders (thm:affine-component-ranks gives at most 4 at this
contiguous cut); neither control's outcome is forced by a count.
Positive control: the pair word (1,-1) in the order of S, whose matrix by hand is [[1,1],[0,1]];
the routine must print exactly these entries.
Baseline: the plainest bound is rank at most the matrix dimension, which decides nothing about
full rank; thm:affine-component-ranks bounds contiguous cuts of such products by the number of
factors, and the cuts here are not contiguous, so it does not apply; the dimension is printed
beside the number of factors, so a case where the dimension exceeds the factor count shows the
non-contiguous rank above the contiguous-cut bound.
Record checked: thm:affine-component-ranks (contiguous cuts only), prop:binary-word-rank-witness
(a certificate, not these products), imp:noncommutative-homogenization-lower-bound (FLST
Proposition 24, full rank over integral domains with at least d^2 2^(k(d+1)) elements, not F_2);
none decides these F_2 ranks.
Decisive at these sizes: the outcome is exact rank over F_2, not an estimate.
"""
import argparse
import json
import sys

import numpy as np

sys.path.insert(0, 'tools')
from f2_span import Span  # noqa: E402


def matching(w):
    """Greedy stack matching of equal-and-opposite entries; None if the word is not nested."""
    stack, pairs = [], {}
    for i, x in enumerate(w):
        if stack and w[stack[-1]] == -x:
            pairs[stack.pop()] = i
        else:
            stack.append(i)
    return pairs if not stack else None


def sequence(w, lo, hi, pairs):
    """S(w[lo:hi]) as a list of (part, value) labels."""
    out, i = [], lo
    while i < hi:
        j = pairs[i]
        inner = sequence(w, i + 1, j, pairs)
        for a in range(2 ** abs(w[i])):
            out.append((i, a))
            out.extend(inner)
            out.append((j, a))
        i = j + 1
    return out


def coefficients(w, seq):
    """Array over (a_1..a_d) of chain counts mod 2."""
    sizes = [2 ** abs(x) for x in w]
    levels = [np.ones(1, dtype=np.uint8)]
    for t in range(len(w)):
        levels.append(np.zeros(int(np.prod(sizes[:t + 1])), dtype=np.uint8))
    for (t, a) in seq:
        prev = levels[t]
        cur = levels[t + 1].reshape(len(prev), sizes[t])
        cur[:, a] ^= prev
    return levels[len(w)].reshape(sizes)


def pdm_rank(w, coef):
    pos = [i for i, x in enumerate(w) if x > 0]
    neg = [i for i, x in enumerate(w) if x < 0]
    m = np.transpose(coef, pos + neg)
    rows = int(np.prod([coef.shape[i] for i in pos]))
    cols = int(np.prod([coef.shape[i] for i in neg]))
    m = m.reshape(rows, cols)
    span = Span()
    for r in m:
        span.add(int(''.join('1' if b else '0' for b in r), 2))
    return len(span), rows, cols, m


def tls_word(k, r, depth):
    """The word w_depth of TLS Proposition 15, eq. (5), for d = r^depth - 1, r odd >= 3."""
    w = [k, -k] * ((r - 1) // 2)
    for _ in range(depth - 1):
        b = 0
        for lo in range(len(w)):
            b = max(b, abs(sum(w[:lo + 1])), abs(sum(w[lo:])))
        e = b + k
        new = list(w)
        for c in range(r - 1):
            new += [e if c % 2 == 0 else -e] + w
        w = new
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    results = []
    # Positive and negative controls on (1,-1).
    w = [1, -1]
    seq = sequence(w, 0, 2, matching(w))
    rank, _, _, m = pdm_rank(w, coefficients(w, seq))
    assert m.tolist() == [[1, 1], [0, 1]], m.tolist()
    rank_rev, _, _, m_rev = pdm_rank(w, coefficients(w, list(reversed(seq))))
    assert m_rev.tolist() == [[0, 0], [1, 0]] and rank_rev == 1, m_rev.tolist()
    print('positive control (1,-1):', m.tolist(), 'rank', rank)
    print('reversed control (1,-1):', m_rev.tolist(), 'rank', rank_rev)
    cases = [
        ('pair', [1, -1]),
        ('pair k=2', [2, -2]),
        ('nested', [1, 1, -1, -1]),
        ('negative first', [-1, 2, -2, 1]),
        ('tls w1 k=1 r=5', tls_word(1, 5, 1)),
        ('tls w2 k=1 r=3', tls_word(1, 3, 2)),
        ('tls w2 k=2 r=3', tls_word(2, 3, 2)),
        ('flst path from w2 k=1 r=3', [1] + tls_word(1, 3, 2) + [-1]),
    ]
    for name, w in cases:
        pairs = matching(w)
        assert pairs is not None, (name, w)
        seq = sequence(w, 0, len(w), pairs)
        rank, rows, cols, _ = pdm_rank(w, coefficients(w, seq))
        row = dict(name=name, word=w, factors=len(seq), rows=rows, cols=cols, rank=rank,
                   full=(rank == rows == cols))
        print(row)
        results.append(row)
    assert all(r['full'] for r in results)
    print('all nested cases full rank:', len(results))
    with open(args.out, 'w') as f:
        json.dump(dict(controls=dict(positive=m.tolist(), reversed=m_rev.tolist()),
                       cases=results), f, indent=1)


if __name__ == '__main__':
    main()
