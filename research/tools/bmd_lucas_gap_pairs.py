"""Review bmd-20261004-zo cheap test: for the interval [0, 24] with two exponents removed (the N = 7 two-cluster limit
has S = [0,24] minus {2, 23}), the rank modulo 3 of (binom(e, k))_(e in S, k < 23); which removed pairs give full rank.
Small exact computation (25 choose 2 = 300 matrices of size 23), Gaussian elimination mod 3."""
from math import comb
from itertools import combinations
def rank_mod3(rows):
    rows = [r[:] for r in rows]; rk = 0; ncol = len(rows[0])
    for c in range(ncol):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c] % 3), None)
        if piv is None: continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = 1 if rows[rk][c] % 3 == 1 else 2
        rows[rk] = [(v * inv) % 3 for v in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c] % 3:
                f = rows[i][c]; rows[i] = [(a - f * b) % 3 for a, b in zip(rows[i], rows[rk])]
        rk += 1
    return rk
D, top = 23, 24
good, bad = [], []
for a, b in combinations(range(top + 1), 2):
    S = [e for e in range(top + 1) if e not in (a, b)]
    r = rank_mod3([[comb(e, k) % 3 for k in range(D)] for e in S])
    (good if r == D else bad).append((a, b))
print('pairs removed from [0,24]:', len(good) + len(bad), 'full rank:', len(good), 'deficient:', len(bad))
print('the N = 7 limit gap pair (2, 23) is', 'good' if (2, 23) in good else 'deficient')
print('good pairs with a = 2:', [p for p in good if p[0] == 2][:12])
print('good pairs containing 23 or 24:', [p for p in good if 23 in p or 24 in p][:20])
# residue rule: full rank iff the residue counts mod 3 of S equal those of [0, 22] (8, 8, 7)
target = [sum(1 for e in range(D) if e % 3 == r) for r in range(3)]
pred = lambda p: [sum(1 for e in range(top + 1) if e not in p and e % 3 == r) for r in range(3)] == target
mism = [p for p in good if not pred(p)] + [p for p in bad if pred(p)]
print('residue-count rule', target, 'agrees with the rank on', 300 - len(mism), 'of 300 pairs; mismatches:', mism[:10])
