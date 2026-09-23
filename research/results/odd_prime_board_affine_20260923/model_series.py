"""Hilbert series of the column-subalgebra model R = F_3[t_1..t_n]/(t_j^2, sum t_j) through degree K, and HS_R/(1+t+t^2)^2
(sizing count for the model scaling test).  Usage: python3 model_series.py n K"""
import sys, itertools, numpy as np
sys.path.insert(0, 'research/results/odd_prime_alignment_mechanism_20260922'); import gf3
from math import comb
n = int(sys.argv[1]); K = int(sys.argv[2])
def rank_z(k):   # z = sum t_j from degree k-1 subsets to degree k subsets
    Bk = list(itertools.combinations(range(n), k)); idx = {b: i for i, b in enumerate(Bk)}
    M = np.zeros((comb(n, k - 1), len(Bk)), dtype=np.uint8)
    for r, S in enumerate(itertools.combinations(range(n), k - 1)):
        for j in range(n):
            if j not in S: M[r, idx[tuple(sorted(S + (j,)))]] = 1
    return gf3.rank(M)
HR = [1] + [comb(n, k) - rank_z(k) for k in range(1, K + 1)]
inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]; c = [1] + [0] * K
for _ in range(2): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(K + 1)]
print(n, 'HR', HR, 'W_R r=2', [sum(HR[i] * c[k - i] for i in range(k + 1)) for k in range(K + 1)])
