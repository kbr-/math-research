"""Write the symmetric power-of-two factor Q_K = g_K / prod(1+x_i) of the Catalan truncation construction.

Over F_2, g_K = prod(1+x_i) * sum over S and powers of two a_i (i in S), sum a_i <= K-1, of
prod_{i in S} x_i^{a_i} (1+x_i)^{a_i-1}.  A part e of a monomial comes from x^a (1+x)^(a-1) only when
a <= e <= 2a-1, i.e. a = 2^floor(log2 e), with coefficient binom(a-1, e-a) mod 2; coordinates with
exponent 0 lie outside S.  So the coefficient of m_lambda is [sum_i a(lambda_i) <= K-1] times
prod_i [e_i - a_i is a bit-submask of a_i - 1].  Output: one partition per line (bmd_recheck format).
Usage: bmd_catalan_certificate.py K OUT_TXT
"""
import sys

def partitions(total, maxpart):
    if total == 0:
        yield ()
        return
    for p in range(min(total, maxpart), 0, -1):
        for rest in partitions(total - p, p):
            yield (p,) + rest

def coefficient(lam, K):
    a = [1 << (e.bit_length() - 1) for e in lam]
    return sum(a) <= K - 1 and all(((e - ai) & ~(ai - 1)) == 0 for e, ai in zip(lam, a))

K, out = int(sys.argv[1]), sys.argv[2]
j = K.bit_length() - 1
deg = 2 ** (j + 1) - j - 2
terms = [lam for size in range(deg + 1) for lam in partitions(size, size) if coefficient(lam, K)]
with open(out, 'w') as f:
    f.write(''.join(' '.join(map(str, lam)) + '\n' for lam in terms))
print(f'K={K} degree bound {deg}: {len(terms)} terms, max size {max(sum(l) for l in terms)}')
