"""Sanity check (scratch): symmetric f = g(|x|) on n variables, rows = subcubes fixing w coordinates.
A static barrier at D exists iff some g has odd weight sum_k C(n,k) g(k) and, for a set J of shifts j such
that every weight k has a j in J with max(0,k-n+w) <= j <= min(w,k), the (e+1)-th difference of g vanishes on
each window [j, j+n-w], e = n-D-1.  Compare with: exists u in [D, 2w-2] with C(u, w-1) odd."""
from math import comb
from itertools import product


def good(g, j, n, w, e):
    L = n - w
    if e >= L:
        return True
    for a in range(j, j + L - e):
        if sum(comb(e + 1, i) * g[a + i] for i in range(e + 2)) % 2:
            return False
    return True


bad = 0
for n in range(4, 12):
    for w in range(1, n // 2 + 1):
        for D in range(0, n - w + 1):
            e = n - D - 1
            found = False
            for g in product((0, 1), repeat=n + 1):
                if sum(comb(n, k) * g[k] for k in range(n + 1)) % 2 == 0:
                    continue
                ok = [good(g, j, n, w, e) for j in range(w + 1)]
                if all(any(ok[j] for j in range(max(0, k - n + w), min(w, k) + 1)) for k in range(n + 1)):
                    found = True
                    break
            pred = any(comb(u, w - 1) % 2 for u in range(D, 2 * w - 1))
            if found != pred:
                bad += 1
                print('MISMATCH', n, w, D, found, pred)
print('mismatches', bad)
