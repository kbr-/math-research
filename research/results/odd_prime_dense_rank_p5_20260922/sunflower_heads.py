"""Exact check of Observation SH: leading monomials of the span of q_ij = 1 - (y_i + y'_j + z)^(p-1).

Polynomials are multilinear over F_p (Booleanity), stored as dicts frozenset(vars) -> coeff.
For each prime, size and monomial order, the script
  * expands every q_ij exactly,
  * checks the identity w_ij = -(y_i - y_1)(y'_j - y'_1) B(z),
  * row-reduces the span, reads off its leading monomials (heads) and its dimension,
  * reports how many heads contain none of m* = lm(B), n* = lm(A + y'_1 B), n'* = lm(A + y_1 B),
    how many miss m* itself, whether m* is the set of the p-3 largest Z-variables, and whether
    every head has degree p-1 (so the span has no affine element).
Orders: degree first, then lexicographic by a variable ranking (random rankings with a fixed seed,
plus rankings putting Z first and Z last); all are degree-compatible monomial orders on squarefree
monomials.
"""
import itertools, json, random, sys

def mul(P, Q, p):
    R = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = m1 | m2
            R[m] = (R.get(m, 0) + c1 * c2) % p
    return {m: c for m, c in R.items() if c}

def add(P, Q, p, s=1):
    R = dict(P)
    for m, c in Q.items():
        R[m] = (R.get(m, 0) + s * c) % p
    return {m: c for m, c in R.items() if c}

def power(P, e, p):
    R = {frozenset(): 1}
    for _ in range(e):
        R = mul(R, P, p)
    return R

def lin(vs, coeffs, const, p):
    P = {frozenset([v]): c % p for v, c in zip(vs, coeffs) if c % p}
    if const % p:
        P[frozenset()] = const % p
    return P

def lm(P, order):
    rank = {v: i for i, v in enumerate(order)}
    def better(m1, m2):  # True if m1 > m2
        if len(m1) != len(m2):
            return len(m1) > len(m2)
        a = sorted(rank[v] for v in m1); b = sorted(rank[v] for v in m2)
        return a < b  # contains a larger variable earlier
    best = None
    for m in P:
        if best is None or better(m, best):
            best = m
    return best

def heads_of_span(polys, order, p):
    """Gaussian elimination by leading monomials; returns list of heads (distinct)."""
    basis = {}  # head -> poly with that head (monic)
    rank = {v: i for i, v in enumerate(order)}
    for P in polys:
        P = dict(P)
        while P:
            h = lm(P, order)
            if h in basis:
                c = P[h]
                P = add(P, basis[h], p, -c)
            else:
                inv = pow(P[h], p - 2, p)
                basis[h] = {m: (c * inv) % p for m, c in P.items()}
                break
    return list(basis.keys())

def run(p, a, b, zsize, seed, n_orders):
    rng = random.Random(seed)
    d = p - 1
    ys = [f"y{i}" for i in range(a)]; yp = [f"u{j}" for j in range(b)]; Z = [f"z{t}" for t in range(zsize)]
    zc = [rng.randrange(1, p) for _ in Z]; z0 = rng.randrange(p)
    zpoly = lin(Z, zc, z0, p)
    q = {}
    for i in range(a):
        for j in range(b):
            L = add(add(lin([ys[i]], [1], 0, p), lin([yp[j]], [1], 0, p), p), zpoly, p)
            q[i, j] = add({frozenset(): 1}, power(L, d, p), p, -1)
    # B(z) and A(z)
    two = add(zpoly, {frozenset(): 2}, p); one = add(zpoly, {frozenset(): 1}, p)
    B = add(add(power(two, d, p), power(one, d, p), p, -2), power(zpoly, d, p), p)
    A = add(power(one, d, p), power(zpoly, d, p), p, -1)
    ok_identity = True
    for i in range(1, a):
        for j in range(1, b):
            w = add(add(add(q[i, j], q[i, 0], p, -1), q[0, j], p, -1), q[0, 0], p)
            dy = add(lin([ys[i]], [1], 0, p), lin([ys[0]], [1], 0, p), p, -1)
            du = add(lin([yp[j]], [1], 0, p), lin([yp[0]], [1], 0, p), p, -1)
            rhs = {m: (-c) % p for m, c in mul(mul(dy, du, p), B, p).items()}
            rhs = {m: c for m, c in rhs.items() if c}
            if w != rhs:
                ok_identity = False
    degB = max(len(m) for m in B) if B else -1
    allv = ys + yp + Z
    orders = []
    orders.append(Z + ys + yp); orders.append(ys + yp + Z)
    for _ in range(n_orders):
        o = allv[:]; rng.shuffle(o); orders.append(o)
    out = []
    for o in orders:
        H = heads_of_span(list(q.values()), o, p)
        mstar = lm(B, o)
        nstar = lm(add(A, mul(lin([yp[0]], [1], 0, p), B, p), p), o)
        npstar = lm(add(A, mul(lin([ys[0]], [1], 0, p), B, p), p), o)
        sets = [s for s in (mstar, nstar, npstar) if s]
        outside = [sorted(h) for h in H if not any(s <= h for s in sets)]
        pair_heads = sum(1 for h in H if len(h) == 2)
        miss_m = sum(1 for h in H if not mstar <= h)
        topZ = [v for v in o if v in Z][:p - 3]
        out.append({"dim": len(H), "outside": len(outside), "not_containing_mstar": miss_m,
                    "mstar_is_top_Z": sorted(mstar) == sorted(topZ), "max_head_degree_only": all(len(h) == p - 1 for h in H), "outside_heads": outside[:3],
                    "sizes": [len(mstar), len(nstar), len(npstar)], "pair_heads": pair_heads,
                    "head_degrees": sorted(set(len(h) for h in H))})
    return {"p": p, "a": a, "b": b, "zsize": zsize, "seed": seed, "identity": ok_identity,
            "degB": degB, "orders": out}

if __name__ == "__main__":
    res = []
    for (p, a, b, zs) in [(3, 4, 4, 4), (5, 4, 4, 4), (5, 5, 4, 5), (7, 3, 3, 5), (7, 4, 3, 6)]:
        res.append(run(p, a, b, zs, seed=20260922 + p + a, n_orders=6))
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    for r in res:
        print(r["p"], r["a"], r["b"], r["zsize"], "identity", r["identity"], "degB", r["degB"],
              "dims", sorted(set(o["dim"] for o in r["orders"])),
              "max outside", max(o["outside"] for o in r["orders"]),
              "heads missing m*", max(o["not_containing_mstar"] for o in r["orders"]),
              "m*=top(Z)", all(o["mstar_is_top_Z"] for o in r["orders"]),
              "all heads degree p-1", all(o["max_head_degree_only"] for o in r["orders"]),
              "set sizes", r["orders"][0]["sizes"], "pair heads", [o["pair_heads"] for o in r["orders"]])
