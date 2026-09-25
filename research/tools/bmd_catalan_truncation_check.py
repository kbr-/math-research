"""Exact check of the Catalan truncation over F_p on the cube {0,1}^n.

Statement tested.  With y_i = x_i^2 - x_i, N_s(x) = (x - 1) - sum_{a=1}^{s-1} (-1)^(a-1) C_{a-1} y^a, and
g_s the part of prod_i N_s(x_i) of total y-degree <= s-1 (the product expanded as a sum over
subsets S and exponents a_i >= 1 for i in S, factors (x_j - 1) for j not in S), the polynomial
P = y_1^l g_{k-l} has Hasse multiplicity >= k at every nonzero cube point, origin order exactly l,
and degree <= n + 2k - 2 - rho_F(k-l).  The script builds P exactly over F_p (dict polynomials),
computes multiplicities by shifting to each cube point, and checks all three claims.
With --wrong-sign the Catalan signs are flipped, as a negative control that must fail.
Usage: bmd_catalan_truncation_check.py p NMAX KMAX [--wrong-sign]
"""
import itertools, sys


def main():
    p, nmax, kmax = map(int, sys.argv[1:4])
    control = '--wrong-sign' in sys.argv[4:]  # negative control: flip the Catalan signs
    cat = [1]
    for j in range(1, kmax + 2):
        cat.append(cat[-1] * 2 * (2 * j - 1) // (j + 1))

    def mul(f, g):
        h = {}
        for a, u in f.items():
            for b, v in g.items():
                e = tuple(i + j for i, j in zip(a, b))
                h[e] = (h.get(e, 0) + u * v) % p
        return {e: c for e, c in h.items() if c}

    def add(f, g, c=1):
        h = dict(f)
        for e, v in g.items():
            h[e] = (h.get(e, 0) + c * v) % p
        return {e: x for e, x in h.items() if x}

    def rho(c):
        parts = [a for a in range(1, c) if cat[a - 1] % p]
        best = [0] + [10 ** 9] * c
        for v in range(1, c):
            best[v] = min(best[v - a] + 1 for a in parts if a <= v)
        return best[c - 1]

    def mult_at(f, pt, n):
        # multiplicity of f at pt: lowest total degree of f(pt + z); expand via binomials mod p
        low = None
        shifted = {}
        for e, c in f.items():
            terms = [{}]
            for i in range(n):
                # (pt_i + z_i)^e_i = sum_j C(e_i, j) pt_i^(e_i - j) z_i^j
                opts = []
                for j in range(e[i] + 1):
                    from math import comb
                    coef = comb(e[i], j) * (pt[i] ** (e[i] - j)) % p
                    if coef:
                        opts.append((j, coef))
                terms = [dict(t, **{str(i): (j, coef)}) for t in terms for (j, coef) in opts]
            for t in terms:
                key = tuple(t[str(i)][0] for i in range(n))
                c2 = c
                for i in range(n):
                    c2 = c2 * t[str(i)][1] % p
                shifted[key] = (shifted.get(key, 0) + c2) % p
        degs = [sum(e) for e, c in shifted.items() if c]
        return min(degs) if degs else 10 ** 9

    fails = 0
    count = 0
    for n in range(1, nmax + 1):
        unit = [0] * n
        xs = []
        for i in range(n):
            e = [0] * n
            e[i] = 1
            xs.append(tuple(e))
        one = {tuple(unit): 1}
        for k in range(1, kmax + 1):
            for l in range(k):
                s = k - l
                # g_s: sum over S, a
                g = {}
                for S in itertools.product([0, 1], repeat=n):
                    idx = [i for i in range(n) if S[i]]
                    for a in itertools.product(range(1, s), repeat=len(idx)):
                        if sum(a) > s - 1:
                            continue
                        coef = 1
                        for ai in a:
                            sign = (-1) ** (ai - 1) if control else -(-1) ** (ai - 1)
                            coef = coef * (sign * cat[ai - 1]) % p
                        if coef == 0:
                            continue
                        term = {tuple(unit): coef}
                        for i, ai in zip(idx, a):
                            y = add({tuple(2 * (j == i) for j in range(n)): 1}, {xs[i]: 1}, -1)
                            for _ in range(ai):
                                term = mul(term, y)
                        for j in range(n):
                            if not S[j]:
                                term = mul(term, add({xs[j]: 1}, one, -1))
                        g = add(g, term)
                P = dict(g)
                y1 = add({tuple(2 * (j == 0) for j in range(n)): 1}, {xs[0]: 1}, -1)
                for _ in range(l):
                    P = mul(P, y1)
                deg = max((sum(e) for e in P), default=-1)
                ok_deg = deg <= n + 2 * k - 2 - rho(s)
                ok_mult = all(mult_at(P, pt, n) >= k for pt in itertools.product([0, 1], repeat=n) if any(pt))
                ok_origin = mult_at(P, tuple(unit), n) == l
                count += 1
                if not (ok_deg and ok_mult and ok_origin):
                    fails += 1
                    print(f'FAIL p={p} n={n} k={k} l={l}: deg {deg} bound {n + 2 * k - 2 - rho(s)} mult {ok_mult} origin {ok_origin}', flush=True)
    print(f'p={p}: {count} cases (n <= {nmax}, k <= {kmax}), {fails} failures', flush=True)


if __name__ == '__main__':
    main()
