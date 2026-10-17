"""No statement tested: evaluates the hypotheses and bounds of the exposed degree occupancy lemma and its tuple
ratio corollary, and of the recorded bounds they are compared with, on the entry's Nonvacuity witness: the
complete graph K_n, n = 64 (edge expansion n/2, maximum degree n - 1), window D = 2n, K = n, V_hi = {v1, v2},
T = 32 edges from v1 to u_1..u_32 and 32 edges from v2 to u_31..u_62 (the u_i the other 62 vertices), tau = 64.
Every graph quantity (theta(u), mu(u), the margins s(x) - kappa(x), the closure size) is computed from the edge
list below, not typed in.
"""
import math

n = 64
D, K = 2 * n, n
eps = min(n - s for s in range(1, n // 2))    # |dS| = s(n - s) >= 33 s for s < n/2: the largest valid constant
v1, v2 = 0, 1
others = list(range(2, n))                    # u_1..u_62
edges = [(a, b) for a in range(n) for b in range(a + 1, n)]
T = {(v1, u) for u in others[:32]} | {(v2, u) for u in others[30:62]}
m, tau = len(edges), len(T)
V_hi = {v1, v2}
off = [e for e in edges if e not in T]

nu = max(sum(1 for e in T if u in e) + 2 * sum(1 for e in off if u in e and (set(e) - {u}) & V_hi)
         for u in range(n) if u not in V_hi)
theta = max(sum(1 for e in T if u in e) for u in range(n) if u not in V_hi)
mu = max(sum(1 for e in off if u in e and (set(e) - {u}) & V_hi) for u in range(n) if u not in V_hi)
exposed = [x for x in V_hi if any(x in e for e in off)]
margins = [sum(1 for e in off if x in e) - sum(1 for e in off if x in e and (set(e) - {x}) <= V_hi)
           for x in exposed]
closure = T | {e for e in off if set(e) & V_hi}

beta = 2 * math.sqrt(K / (m - tau))
eta_ex = (1 + 2 * beta ** (eps - nu)) ** n * math.prod(1 + 2 * beta ** g for g in margins) - 1
eta_hi = 3 ** len(V_hi) * ((1 + 2 * beta ** (eps - theta - mu)) ** n - 1)
print(f'm = {m}; tau = {tau}; window max(4, 2(n-1)) = {2 * (n - 1)} <= D = {D} < eps n / 8 = {eps * n / 8}')
print(f'2K + tau = {2 * K + tau} <= 2D = {2 * D}; K + tau = {K + tau} <= D (corollary, gamma = 0); '
      f'4K = {4 * K} < m - tau = {m - tau}')
print(f'theta = {theta}, mu = {mu}, nu = max(theta(u) + 2 mu(u)) = {nu}; exposed h\' = {len(exposed)}, '
      f'margins s(x) - kappa(x) = {margins}')
print(f'star closure of V_hi: tau^A = {len(closure)}, K + tau^A = {K + len(closure)} > D = {D}: '
      f'{K + len(closure) > D}')
print(f'beta_T = {beta:.4f}; eta_ex = {eta_ex:.3g}; new occupancy factor 1 - eta_ex = {1 - eta_ex:.6f}')
print(f'lem:exposed-vertex-occupancy (and lem:high-incidence-occupancy, h = 2): eta = {eta_hi:.3g}, '
      f'factor 3^(-2)(1 - eta) = {(1 - eta_hi) / 9:.6f}')
print(f'ratio factor over the off-T ball ratio: corollary 1/(1 - eta_ex) = {1 / (1 - eta_ex):.6f}; '
      f'lem:local-tuple-ratio 3^2/(1 - eta_hi) = {9 / (1 - eta_hi):.6f}')

# The bounds that need no exceptional set, at this expansion: lem:off-support-occupancy (theta(T) < eps) and
# cor:star-closure-ratio with A empty (theta^A = theta(T)), both with eta = (1 + 2 beta^(eps - theta(T)))^n - 1.
theta_T = max(sum(1 for e in T if u in e) for u in range(n))
eta_empty = (1 + 2 * beta ** (eps - theta_T)) ** n - 1
print(f'eps = {eps}; theta(T) = {theta_T} < eps: {theta_T < eps}; eta with no exceptional set = {eta_empty:.3g}')

# The lemma with Y = all of V_hi closed (the hybrid at its other end), under its hypothesis 2K + tau' <= 2D.
def ball(j, k):
    return sum(2 ** i * math.comb(j, i) for i in range(k + 1))

tc = len(closure)
nu_c = max(sum(1 for e in closure if u in e) for u in range(n) if u not in V_hi)
beta_c = 2 * math.sqrt(K / (m - tc))
eta_c = (1 + 2 * beta_c ** (eps - nu_c)) ** n - 1
print(f'closed end: 2K + tau\' = {2 * K + tc} <= 2D: {2 * K + tc <= 2 * D}; nu\' = {nu_c}; eta\' = {eta_c:.3g}; '
      f'factor on B_(m-tau)(K) = {(1 - eta_c) * ball(m - tc, K) / ball(m - tau, K):.4f}')

# Corollary (ii): lambda of lem:ball-ratio-comparison at n = m, tau, k = K.
q = K / (2 * (m - K + 1))
rho = 1 + tau / (m - tau - K + 1)
lam = rho * (1 + q * (rho - 1) / ((1 - q * rho) * (1 - q)))
print(f'lem:ball-ratio-comparison at n = m, tau, k = K: q = {q:.5f}, rho = {rho:.5f}, q rho < 1: {q * rho < 1}, '
      f'lambda = {lam:.5f}')

# Second witness, for the converse non-implication: on the same K_64, x a vertex, z and y two others, T the 61
# edges at x other than xz and xy, V_hi = {x, z}; window D = 200, K = 128. Then g(x) = 1 (xz ends in V_hi).
D2, K2 = 200, 128
x, z, y = 0, 1, 2
T2 = {(x, u) for u in range(3, n)}
off2 = [e for e in edges if e not in T2]
V2 = {x, z}
theta2 = max(sum(1 for e in T2 if u in e) for u in range(n) if u not in V2)
mu2 = max(sum(1 for e in off2 if u in e and (set(e) - {u}) & V2) for u in range(n) if u not in V2)
nu2 = max(sum(1 for e in T2 if u in e) + 2 * sum(1 for e in off2 if u in e and (set(e) - {u}) & V2)
          for u in range(n) if u not in V2)
exp2 = [w for w in V2 if any(w in e for e in off2)]
marg2 = {w: sum(1 for e in off2 if w in e) - sum(1 for e in off2 if w in e and (set(e) - {w}) <= V2) for w in exp2}
tau2 = len(T2)
beta2 = 2 * math.sqrt(K2 / (m - tau2))
eta_new2 = (1 + 2 * beta2 ** (eps - nu2)) ** n * math.prod(1 + 2 * beta2 ** g for g in marg2.values()) - 1
eta_old2 = 3 ** len(exp2) * ((1 + 2 * beta2 ** (eps - theta2 - mu2)) ** n - 1)
print(f'second witness: tau = {tau2}, 2K + tau = {2 * K2 + tau2} <= 2D = {2 * D2}; 4K = {4 * K2} < m - tau = '
      f'{m - tau2}; window {2 * (n - 1)} <= D = {D2} < {eps * n / 8}; theta = {theta2}, mu = {mu2}, nu = {nu2}; '
      f'margins {sorted(marg2.values())}; beta_T = {beta2:.4f}')
print(f'second witness: eta_ex = {eta_new2:.3g} (vacuous: {eta_new2 >= 1}); lem:exposed-vertex-occupancy eta = '
      f'{eta_old2:.3g}, factor {(1 - eta_old2) / 3 ** len(exp2):.6f}')

# The entry's Remark at Y = {x} on the second witness (its reviewer's third pass): close x's off-T edges.
TY = T2 | {e for e in off2 if x in e}
offY = [e for e in edges if e not in TY]
nuY = max(sum(1 for e in TY if u in e) + 2 * sum(1 for e in offY if u in e and (set(e) - {u}) & V2)
          for u in range(n) if u not in V2)
margY = [sum(1 for e in offY if w in e) - sum(1 for e in offY if w in e and (set(e) - {w}) <= V2)
         for w in V2 if any(w in e for e in offY)]
tauY = len(TY)
betaY = 2 * math.sqrt(K2 / (m - tauY))
etaY = (1 + 2 * betaY ** (eps - nuY)) ** n * math.prod(1 + 2 * betaY ** g for g in margY) - 1
print(f'Remark at Y = {{x}}: tau_Y = {tauY}, 2K + tau_Y = {2 * K2 + tauY} <= 2D; nu_Y = {nuY}; margins {margY}; '
      f'eta_Y = {etaY:.3g}; factor on B_(m-tau)(K) = {(1 - etaY) * ball(m - tauY, K2) / ball(m - tau2, K2):.4f}')
