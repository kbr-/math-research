#!/usr/bin/env python3
"""Enumeration check of Lemma C's count (cycle 207): |Phi_k(S)| = C(n+1-e, N+1+k-e) C(n-N, k) (n-N-k)! for the
family with an e-set S of rows residual, and the ratio |Phi_{e-s}(S)|/|Phi_e(S)| = prod_{i<s} (N+1-i)(e-i)/(n-N-e+1+i),
against theta_A^s with theta_A = (N+1)e/(n-N-e+1).  Rows 0..n; S = rows 0..e-1; holes of Q = the first N labels."""
import itertools, math
def count(n, N, k, e):
    rows = range(n + 1); total = 0
    for R in itertools.combinations(rows, N + 1 + k):
        if any(r >= e for r in R[:e]) or set(range(e)) - set(R): continue   # S must be residual
        total += math.comb(n - N, k) * math.factorial(n - N - k)
    return total
def formula(n, N, k, e):
    return math.comb(n + 1 - e, N + 1 + k - e) * math.comb(n - N, k) * math.factorial(n - N - k)
ok = True
for (n, N, e) in [(7, 2, 2), (8, 2, 3), (9, 3, 2), (9, 3, 3), (9, 2, 3)]:
    for s in range(1, e + 1):
        a1, f1 = count(n, N, e, e), formula(n, N, e, e)
        a2, f2 = count(n, N, e - s, e), formula(n, N, e - s, e)
        ratio = a2 / a1
        prod = math.prod((N + 1 - i) * (e - i) / (n - N - e + 1 + i) for i in range(s))
        bound = ((N + 1) * e / (n - N - e + 1)) ** s
        good = a1 == f1 and a2 == f2 and abs(ratio - prod) < 1e-12 and prod <= bound + 1e-12
        ok &= good
        print(f'n={n} N={N} e={e} s={s}: |Phi_e(S)|={a1} |Phi_(e-s)(S)|={a2} formula ok={a1 == f1 and a2 == f2} ratio={ratio:.6f} product={prod:.6f} theta_A^s={bound:.6f} ok={good}')
print('ALL OK' if ok else 'MISMATCH')
