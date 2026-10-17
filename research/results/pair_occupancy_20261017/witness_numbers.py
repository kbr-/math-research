"""No statement tested: evaluates the hypotheses and bounds of the pair occupancy lemma, and of the recorded
counts it is compared with, on the entry's Nonvacuity witness: the complete graph K_n, n = 64 (edge expansion 33,
the largest valid constant), window D = 2n, K = 32, and s = 80 pairs taken from five perfect matchings of a
round-robin 1-factorization, each pair two consecutive edges of one matching. Every graph quantity (the pairs'
disjointness, pi, the expansion) is computed here from the edge list.
"""
import math

n = 64
D, K = 2 * n, 32
eps = min(n - x for x in range(1, n // 2))

# Round-robin 1-factorization of K_64: matching r pairs vertex n-1 with r and i with j, i + j = 2r mod (n-1).
def matching(r):
    out = [(min(r, n - 1), max(r, n - 1))]
    for i in range(n - 1):
        j = (2 * r - i) % (n - 1)
        if i < j:
            out.append((i, j))
    return out

matchings = [matching(r) for r in range(5)]
assert all(len(mt) == n // 2 and len({v for e in mt for v in e}) == n for mt in matchings)
pairs = [(mt[2 * i], mt[2 * i + 1]) for mt in matchings for i in range(len(mt) // 2)]
paired = [e for p in pairs for e in p]
assert len(paired) == len(set(paired)), 'pairs disjoint as edge sets'
s = len(pairs)
m = n * (n - 1) // 2
pi = max(sum(1 for e in paired if v in e) for v in range(n))

def ball(j, k):
    return sum(2 ** i * math.comb(j, i) for i in range(k + 1))

beta = 2 * math.sqrt(K / (m - s))
eta_w = math.expm1(n * math.log1p(2 * beta ** (eps - pi)))   # (1 + x)^n - 1 without underflow to zero
print(f'n = {n}, m = {m}, eps = {eps}, D = {D}, K = {K}, s = {s} pairs ({2 * s} edges), pi = {pi}')
print(f'2K + 2s = {2 * K + 2 * s} <= 2D = {2 * D}: {2 * K + 2 * s <= 2 * D}; 4K = {4 * K} < m - s = {m - s}: '
      f'{4 * K < m - s}; 2s = {2 * s} > D = {D}: {2 * s > D}; K + 2s = {K + 2 * s} > D: {K + 2 * s > D}')
print(f'window: max(4, 2(n-1)) = {2 * (n - 1)} <= D = {D} < eps n / 8 = {eps * n / 8}')
print(f'beta_W = {beta:.4f}; eps - pi = {eps - pi}; eta_W = {eta_w:.3g}')
print(f'lemma: q_W(K) >= {1 - eta_w:.6f} B_(m-s)(K), and q_W(K) <= B_(m-s)(K)')
tau = 2 * s
beta_t = 2 * math.sqrt(K / (m - tau))
eta_t = math.expm1(n * math.log1p(2 * beta_t ** (eps - pi)))
r1 = ball(m - s, K) / ball(m - tau, K)
print(f'edge-set count (lem:exposed-degree-occupancy, V_hi empty, T the paired edges, 2K + tau = {2 * K + tau} <= 2D): '
      f'q_T(K) >= {1 - eta_t:.6f} B_(m-2s)(K); B_(m-s)(K) / B_(m-2s)(K) = {r1:.4f}')
r2 = ball(m, K) / ball(m - s, K)
print(f'B_m(K) / B_(m-s)(K) = {r2:.4f} (the average number of cut-code classes per coset of B + W is at most this '
      f'over 1 - eta_W); 3^s = 3^{s} = {3 ** s:.3e}')
