"""Falsification test: min over l of Phi(n,k,l) = n + 2l + sum_{j<n} floor((k-l-1)/2^j) must equal
the verified complete formula D(n,k) (thm:binary-multiplicity-degree-complete):
2k+n-2-floor(log2 k) for k < 2^(n-1), and 2k - floor(k/2^(n-1)) for k >= 2^(n-1).
Usage: bmd_phi_vs_complete.py NMAX KMAX
"""
import sys


def phi(n, k, l):
    c = k - l - 1
    return n + 2 * l + sum(c >> j for j in range(n))


def complete(n, k):
    return 2 * k + n - 2 - (k.bit_length() - 1) if k < 2 ** (n - 1) else 2 * k - k // 2 ** (n - 1)


nmax, kmax = int(sys.argv[1]), int(sys.argv[2])
pairs = [(n, k) for n in range(1, nmax + 1) for k in range(1, kmax + 1)]
bad = [(n, k) for n, k in pairs if min(phi(n, k, l) for l in range(k)) != complete(n, k)]
print(f'checked {len(pairs)} pairs (n <= {nmax}, k <= {kmax}); mismatches {len(bad)} {bad[:20]}')
