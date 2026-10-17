"""Path rank saturation: distinct paths, words with zeros and nonpositive pieces, a failing control, and (1,-2,1).

Statement tested (lem:path-rank-saturation): for every word w with P_d = 0 and no part jumping across zero, the
construction (one-signed pieces split at the zeros of the partial sums, the unit-step sequence for a nonnegative
piece, the sequence of -v for a nonpositive piece v, markers for zero entries emitting once per enclosing copy)
gives a partial derivative matrix of integer determinant +1 or -1 (1 in the proof's orders; this script uses the
lexicographic orders of the digit tuples) and s(w) = sum_i 2^max(|P_(i-1)|, |P_i|) factors.
Cases: every distinct path of P_{k,d} (FLST TR23-191, 7.1.2: entries in [-k,k] minus 0, sum 0, partial sums in
[0,k] before the end) with k <= 3 and d <= 5 or k <= 2 and d = 6, each path counted once at its least k; the
word (2,0,-1,-1) and (1,-1,0,-1,1); the nonpositive word (-1,-1,2); the reviewer's 9-factor product for (1,-2,1).
Expected: |det| = 1 and the count formula exact on every word; the integer matrix of (2,-1,-1) printed; the
(1,-2,1) product of determinant +1 or -1.
Refuted by: a determinant other than +1 or -1 on a case, or a count differing from the formula.
Possible because: the proof's induction may mishandle markers or the transposed pieces, which no run tested.
Control: the sequence of (2,-1,-1) reversed, whose integer determinant must differ from +1 and -1.
Refuted by: the reversed control printing determinant +1 or -1, which would mean the determinant ignores order.
Possible because: a routine that counts all position triples, not increasing chains, is order-blind.
Forced by counts: the reversed sequence has 10 factors against a 4 by 4 matrix, so no count forces its
determinant; thm:affine-component-ranks allows rank up to 10 at this contiguous cut.
Positive control: (1,-1), whose matrix by hand is [[1,1],[0,1]], determinant 1.
Baseline: the plainest bound, rank at most the dimension, decides nothing; lem:nested-word-rank-saturation decides
the nested cases, which this script counts.
Record checked: the claims lem:nested-word-rank-saturation and imp:noncommutative-homogenization-lower-bound
were read; neither gives these determinants for the paths that are not nested.
"""
import argparse
import itertools
import json
from fractions import Fraction

import numpy as np


def paths(k, d):
    for p in itertools.product([x for x in range(-k, k + 1) if x], repeat=d):
        s, ok = 0, True
        for j, x in enumerate(p):
            s += x
            if j < d - 1 and not 0 <= s <= k:
                ok = False
                break
        if ok and s == 0:
            yield list(p)


def nonneg_sequence(w, offset):
    """Unit-step sequence of a nonnegative balanced word w; parts are numbered offset + i."""
    steps, markers_after = [], []
    for i, x in enumerate(w):
        if x == 0:
            steps.append((i, 0, 0, 0))
        for j in range(abs(x)):
            steps.append((i, j, abs(x), 1 if x > 0 else -1))
    partner, stack = {}, []
    for t, st in enumerate(steps):
        if st[3] > 0:
            stack.append(t)
        elif st[3] < 0:
            o = stack.pop()
            partner[o], partner[t] = t, o
    runs = {}
    for t, st in enumerate(steps):
        if st[3]:
            runs.setdefault(st[0], []).append(t)
    out = []

    def label(i, env):
        digits = tuple(env[min(u, partner[u])] for u in runs.get(i, []))
        out.append((offset + i, int(''.join(map(str, digits)), 2) if digits else 0))

    def emit(t, env):
        i, j, m, sign = steps[t]
        if (sign > 0 and j == m - 1) or (sign < 0 and j == 0):
            label(i, env)

    def gen(lo, hi, env):
        t = lo
        while t < hi:
            if steps[t][3] == 0:
                label(steps[t][0], env)
                t += 1
                continue
            c = partner[t]
            for b in (0, 1):
                env2 = dict(env)
                env2[t] = b
                emit(t, env2)
                gen(t + 1, c, env2)
                emit(c, env2)
            t = c + 1

    gen(0, len(steps), {})
    return out


def sequence(w):
    """Split at zeros of the partial sums into one-signed pieces; a nonpositive piece uses the sequence of -v."""
    out, start, s = [], 0, 0
    for i, x in enumerate(w):
        s += x
        if s == 0 and (i == len(w) - 1 or True):
            piece = w[start:i + 1]
            if any(v < 0 for v in itertools.accumulate(piece)) and any(v > 0 for v in itertools.accumulate(piece)):
                raise ValueError(f'part jumps across zero in {piece}')
            neg = any(v < 0 for v in itertools.accumulate(piece))
            out += nonneg_sequence([-v for v in piece] if neg else piece, start)
            start = i + 1
    assert start == len(w) and s == 0
    return out


def integer_pdm(w, seq):
    sizes = [2 ** abs(x) for x in w]
    levels = [np.ones(1, dtype=object)]
    for t in range(len(w)):
        levels.append(np.zeros(int(np.prod(sizes[:t + 1])), dtype=object))
    for (t, a) in seq:
        prev = levels[t]
        levels[t + 1].reshape(len(prev), sizes[t])[:, a] += prev
    coef = levels[len(w)].reshape(sizes)
    pos = [i for i, x in enumerate(w) if x > 0]
    neg = [i for i, x in enumerate(w) if x < 0]
    rows = int(np.prod([sizes[i] for i in pos]))
    return np.transpose(coef, pos + neg).reshape(rows, -1)


def det(m):
    a = [[Fraction(int(x)) for x in row] for row in m]
    n, d = len(a), Fraction(1)
    if n != len(a[0]):
        return None
    for c in range(n):
        piv = next((r for r in range(c, n) if a[r][c] != 0), None)
        if piv is None:
            return 0
        if piv != c:
            a[c], a[piv] = a[piv], a[c]
            d = -d
        d *= a[c][c]
        for r in range(c + 1, n):
            f = a[r][c] / a[c][c]
            if f:
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return int(d)


def formula(w):
    s, prev = 0, 0
    for x in w:
        cur = prev + x
        s += 2 ** max(abs(prev), abs(cur))
        prev = cur
    return s


def nested(p):
    stack = []
    for x in p:
        if stack and stack[-1] == -x:
            stack.pop()
        else:
            stack.append(x)
    return not stack


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    pos = integer_pdm([1, -1], sequence([1, -1]))
    assert pos.tolist() == [[1, 1], [0, 1]], pos.tolist()
    seq = sequence([2, -1, -1])
    m = integer_pdm([2, -1, -1], seq)
    rev = det(integer_pdm([2, -1, -1], list(reversed(seq))))
    print('positive control (1,-1):', pos.tolist())
    print('(2,-1,-1):', len(seq), 'factors, integer matrix', m.tolist(), 'det', det(m))
    print('reversed control (2,-1,-1): det', rev)
    assert rev not in (1, -1)
    seen, rows = set(), []
    for k, d in [(k, d) for k in (1, 2, 3) for d in range(2, 6)] + [(1, 6), (2, 6)]:
        for p in paths(k, d):
            if tuple(p) in seen:
                continue
            seen.add(tuple(p))
            s = sequence(p)
            rows.append(dict(path=p, k=max(itertools.accumulate(p)), det=det(integer_pdm(p, s)),
                             factors=len(s), formula=formula(p), nested=nested(p)))
    print('distinct paths:', len(rows), 'nested:', sum(r['nested'] for r in rows),
          'not nested:', sum(not r['nested'] for r in rows),
          '|det| = 1:', sum(abs(r['det']) == 1 for r in rows),
          'count = formula:', sum(r['factors'] == r['formula'] for r in rows))
    extra = []
    for w in ([2, 0, -1, -1], [1, -1, 0, -1, 1], [-1, -1, 2], [1, -1, -1, 1]):
        s = sequence(w)
        extra.append(dict(word=w, det=det(integer_pdm(w, s)), factors=len(s), formula=formula(w)))
        print('word', w, extra[-1])
    rev_seq = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (1, 2), (0, 0), (1, 3), (2, 1)]
    m121 = integer_pdm([1, -2, 1], rev_seq)
    print('reviewer (1,-2,1), 9 factors:', m121.tolist(), 'det', det(m121))
    with open(args.out, 'w') as f:
        json.dump(dict(example=dict(word=[2, -1, -1], factors=len(seq), matrix=m.tolist(), det=det(m)),
                       reversed_control_det=rev, paths=rows, extra=extra,
                       reviewer_121=dict(sequence=rev_seq, matrix=m121.tolist(), det=det(m121))), f)


if __name__ == '__main__':
    main()
