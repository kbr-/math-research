"""Private-heptad design for (b4) of prop:width-one-degree-four-glue, functional board R = n+1, N = n, L = N-1.
Statement checked: the clauses U = S u T (S = positions 1..4, T = positions 5..7) on rows (i-1)N0 + x + (i-1)a
(7 N0 <= R, x + 6a <= N0-1) and labels 4 + alpha + (i-1)beta (beta >= 1, alpha + 6 beta <= L-5) are 7-matchings
with labels >= 4 that pairwise share at most one cell.  Prints M against the degree-4 capacity
gamma_4/(gamma_1-1), gamma_4 = C(R,4) delta_4(N)."""
import itertools, json, math, sys
def delta(t, N): return sum((-1) ** j * math.comb(t, j) * math.perm(N, t - j) for j in range(t + 1))
out = []
for n in [12, 16, 20, 24, 32, 40, 48, 64]:
    R, N = n + 1, n; L = N - 1; N0 = R // 7
    clauses = []
    for a in range(N0):
        for x in range(N0 - 6 * a):
            rows = [(i) * N0 + x + i * a for i in range(7)]
            for beta in range(1, L):
                for alpha in range(L - 4 - 6 * beta):
                    clauses.append(tuple((rows[i], 4 + alpha + i * beta) for i in range(7)))
    ok = all(len({c[0] for c in U}) == 7 and len({c[1] for c in U}) == 7 and min(c[1] for c in U) >= 4
             and max(c[1] for c in U) <= L - 1 and max(c[0] for c in U) < R for U in clauses)
    seen = set(); shared = 0
    for U in clauses:
        for p in itertools.combinations(sorted(U), 2):
            if p in seen: shared += 1
            seen.add(p)
    g1 = R * L; g4 = math.comb(R, 4) * delta(4, N); cap = g4 / (g1 - 1)
    out.append(dict(n=n, M=len(clauses), matchings_ok=ok, shared_pairs=shared, gamma1=g1, gamma4=g4,
                    capacity=round(cap, 1), fraction=round(len(clauses) / cap, 6), M_over_n4=len(clauses) / n ** 4))
    print(json.dumps(out[-1]), flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
