"""The reviewer's unit-step construction for paths of P_{k,d}, over F_2, small cases.

Statement tested (the reviewer's unverified suggestion): for every path p in P_{k,d} (entries in [-k,k] minus 0,
partial sums in [0,k] before the end, total 0), refine each entry p_i into |p_i| unit steps of its sign, a Dyck word
matched by the stack; run the segment recursion of lem:nested-word-rank-saturation on the refined word (a matched
unit pair (o, W', c) gives, for b = 0, 1 in turn, o's slot, the sequence of W', c's slot), but emit a factor 1 + x
only at the innermost open step of each positive run (the run's last step) and at the innermost close step of each
negative run (the run's first step), the letter's index being the run's digits, the current b for its own step and
the enclosing segments' digits for the run's other steps. Then the ordered set-multilinear projection's partial
derivative matrix (|X_i| = 2^|p_i|, rows the positive parts) is invertible over F_2.
Expected: full rank for every path with k <= 2, d <= 6 and k = 3, d <= 5, and the matrix
[[1,0,1,0],[0,1,1,0],[0,1,0,1],[0,0,0,1]] with 10 factors for (2,-1,-1), as the reviewer reported.
Refuted by: some path printing a rank below its dimension, or a different matrix or count for (2,-1,-1).
Possible because: the reviewer's description could differ from what it ran, and no proof was written.
Baseline: the plainest bound is rank at most the dimension; lem:nested-word-rank-saturation decides only the paths
that are nested words before refinement, such as (2,-2), and this run counts how many paths are not.
Record checked: the claims lem:nested-word-rank-saturation (draft) and imp:noncommutative-homogenization-lower-bound
were read; the second decides every path over large integral domains, not over F_2.
"""
import argparse
import itertools
import json
import sys

import numpy as np

sys.path.insert(0, 'tools')
from f2_span import Span  # noqa: E402


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


def sequence(p):
    steps = []  # (part, position in run, run length, sign)
    for i, x in enumerate(p):
        for j in range(abs(x)):
            steps.append((i, j, abs(x), 1 if x > 0 else -1))
    partner, stack = {}, []
    for t, st in enumerate(steps):
        if st[3] > 0:
            stack.append(t)
        else:
            o = stack.pop()
            partner[o], partner[t] = t, o
    run_steps = {}
    for t, st in enumerate(steps):
        run_steps.setdefault(st[0], []).append(t)
    out = []

    def pair_of(t):
        return min(t, partner[t])

    def emit(t, env):
        i, j, m, sign = steps[t]
        if (sign > 0 and j == m - 1) or (sign < 0 and j == 0):
            digits = tuple(env[pair_of(u)] for u in run_steps[i])
            out.append((i, int(''.join(map(str, digits)), 2)))

    def gen(lo, hi, env):
        t = lo
        while t < hi:
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


def pdm(p, seq):
    sizes = [2 ** abs(x) for x in p]
    levels = [np.ones(1, dtype=np.uint8)]
    for t in range(len(p)):
        levels.append(np.zeros(int(np.prod(sizes[:t + 1])), dtype=np.uint8))
    for (t, a) in seq:
        prev = levels[t]
        levels[t + 1].reshape(len(prev), sizes[t])[:, a] ^= prev
    coef = levels[len(p)].reshape(sizes)
    pos = [i for i, x in enumerate(p) if x > 0]
    neg = [i for i, x in enumerate(p) if x < 0]
    rows = int(np.prod([sizes[i] for i in pos]))
    return np.transpose(coef, pos + neg).reshape(rows, -1)


def rank(m):
    span = Span()
    for r in m:
        span.add(int(''.join('1' if b else '0' for b in r), 2))
    return len(span)


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
    seq = sequence([2, -1, -1])
    m = pdm([2, -1, -1], seq)
    print('(2,-1,-1):', len(seq), 'factors, matrix', m.tolist(), 'rank', rank(m))
    rows = []
    for k, dmax in ((1, 6), (2, 6), (3, 5)):
        for d in range(2, dmax + 1):
            for p in paths(k, d):
                seq = sequence(p)
                m = pdm(p, seq)
                r = rank(m)
                rows.append(dict(k=k, path=p, factors=len(seq), dim=m.shape[0], rank=r,
                                 full=(r == m.shape[0] == m.shape[1]), nested=nested(p)))
    print('paths:', len(rows), 'full rank:', sum(r['full'] for r in rows),
          'not nested before refinement:', sum(not r['nested'] for r in rows),
          'max factors / (k d 2^k):', max(r['factors'] / (r['k'] * len(r['path']) * 2 ** r['k']) for r in rows))
    print('not full:', [r['path'] for r in rows if not r['full']])
    with open(args.out, 'w') as f:
        json.dump(dict(example=dict(path=[2, -1, -1], matrix=m.tolist()), rows=rows), f)


if __name__ == '__main__':
    main()
