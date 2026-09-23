"""Compare gamma_k of the weak unary PHP top algebra A (n holes) with the Hilbert function of T/(rows) predicted by free
row action, HS_T(t)/(1+t+t^2)^(n+1), where T = tensor product over holes of C_j = F_3 + V_j (square-zero, dim V_j = n+1),
T_k = C(n,k)(n+1)^k.  gamma values from research/results/odd_prime_degree_four_20260923/gammas.txt."""
import ast, os
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, '..', 'odd_prime_degree_four_20260923', 'gammas.txt')
for line in open(src):
    d = ast.literal_eval(line); n = d['n']; g = d['gamma']; K = len(g) - 1
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(K + 1)]         # 1/(1+t+t^2)
    c = [1] + [0] * K
    for _ in range(n + 1): c = [sum(c[i] * inv[k - i] for i in range(k + 1)) for k in range(K + 1)]
    T = [comb(n, k) * (n + 1) ** k for k in range(K + 1)]
    pred = [sum(T[i] * c[k - i] for i in range(k + 1)) for k in range(K + 1)]
    print(dict(n=n, gamma=g, free_row_prediction=pred, agree_through=max(k for k in range(K + 1) if all(g[i] == pred[i] for i in range(k + 1)))))
