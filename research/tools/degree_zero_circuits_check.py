"""Degree-zero circuits check (entry-2026-09-27-degree-zero-circuits).

Statement tested (prop:degree-zero-circuits (b)): in the truncated algebra T = F_3[y_1..y_6]/(y_i^3), which the
group sums of a 12-cell row generate inside the square-free algebra, the tops A_b^2 B_b with (A_b, B_b) a basis of
the F_3-plane of a point of PG(2, 9) (a Desarguesian spread of F_3^6 into 91 planes) are pairwise non-proportional,
and 51 of them are linearly dependent since dim T_3 = 50.  At multiplier degree 0 there are no Taylor syzygies, so
the dependency space is the Taylor defect.  Also printed: rank of all 91 tops, the dependency dimension of the
first 51, and whether any three of those 51 are dependent.  Also part (a): tops y_1^2 y_{i+1} (i < r) and
y_1^2 (-(y_2 + ... + y_r)) form a circuit of size r (r = 2..6).  Small exact computation over F_3 in pure Python
(matrices of at most 91 x 50), a few seconds.
Usage: python3 degree_zero_circuits_check.py OUT.json
"""
import itertools
import json
import sys

D = 6
MONS = [m for m in itertools.product(range(3), repeat=D) if sum(m) == 3]
IDX = {m: i for i, m in enumerate(MONS)}
assert len(MONS) == 50


def mul(p, q):
    """Product of polynomials {exponent tuple: coefficient} in T, dropping exponents >= 3."""
    out = {}
    for ea, ca in p.items():
        for eb, cb in q.items():
            e = tuple(x + y for x, y in zip(ea, eb))
            if max(e) < 3:
                out[e] = (out.get(e, 0) + ca * cb) % 3
    return {e: c for e, c in out.items() if c}


def linear(v):
    return {tuple(1 if j == i else 0 for j in range(D)): c % 3 for i, c in enumerate(v) if c % 3}


def top(a, b):
    la = linear(a)
    p = mul(mul(la, la), linear(b))
    vec = [0] * len(MONS)
    for e, c in p.items():
        vec[IDX[e]] = c
    return vec


def rank(rows):
    rows = [r[:] for r in rows]
    rk, ncol = 0, len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = rows[rk][c]  # 1 or 2, self-inverse mod 3
        rows[rk] = [(x * inv) % 3 for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % 3 for x, y in zip(rows[i], rows[rk])]
        rk += 1
    return rk


# F_9 = F_3[i]/(i^2 + 1); a vector of F_9^3 is a vector of F_3^6 (real parts, then imaginary parts).
def f9_times_i(v):  # (x + y i) i = -y + x i
    return [(-v[3 + j]) % 3 for j in range(3)] + [v[j] for j in range(3)]


points = []
for v in itertools.product(range(3), repeat=6):
    if any(v):
        # normalize: first nonzero F_9 coordinate equal to 1
        z = [(v[j], v[3 + j]) for j in range(3)]
        k = next(j for j in range(3) if z[j] != (0, 0))
        if z[k] == (1, 0):
            points.append(list(v))
assert len(points) == 91
tops = [top(p, f9_times_i(p)) for p in points]
spans = [rank([p, f9_times_i(p)]) for p in points]
assert all(s == 2 for s in spans)
pairwise_forms_independent = all(
    rank([points[a], f9_times_i(points[a]), points[b], f9_times_i(points[b])]) == 4
    for a, b in itertools.combinations(range(91), 2))
pairwise_tops_independent = all(rank([tops[a], tops[b]]) == 2 for a, b in itertools.combinations(range(91), 2))
first = tops[:51]
rank_first = rank(first)
triples_dependent = sum(1 for t in itertools.combinations(range(51), 3) if rank([first[i] for i in t]) < 3)
result = {
    "dim_T3": len(MONS), "spread_planes": len(points), "rank_all_91": rank(tops),
    "pairwise_forms_independent": pairwise_forms_independent, "pairwise_tops_independent": pairwise_tops_independent,
    "rank_first_51": rank_first, "defect_first_51": 51 - rank_first, "dependent_triples_among_51": triples_dependent,
}
circuits = []
for r in range(2, 7):
    y = [[1 if j == i else 0 for j in range(D)] for i in range(D)]
    bs = [y[i] for i in range(1, r)] + [[(-sum(y[i][j] for i in range(1, r))) % 3 for j in range(D)]]
    ts = [top(y[0], b) for b in bs]
    proper_ranks = [rank([ts[i] for i in range(r) if i != skip]) for skip in range(r)]
    circuits.append({"r": r, "rank": rank(ts), "proper_subfamily_ranks": proper_ranks})
result["shared_square_circuits"] = circuits
with open(sys.argv[1], "w") as f:
    json.dump(result, f, indent=1)
print(json.dumps(result))
