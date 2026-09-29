"""Linear relations among the roots at the F_p-rational points of the six-root repeated factor (29 September 2026;
cycle bmd-20260929-zzd). The line certificate bmd_cube_wronskian_discriminant.c draws alpha_i, beta_i (i < N,
interleaved) by splitmix64 from the seed and restricts to a(u) = alpha + u beta over F_p, p = 2^61 - 1. Its JSON dumps
the repeated factor of Delta_W^nc (exponent 4, degree 45 at N = 6). Tested statement: at each F_p-rational root u0 of
that factor, the configuration a(u0) satisfies a translation-invariant linear relation sum c_i a_i = 0 (sum c_i = 0)
with small integer coefficients |c_i| <= C; the relation found names the component. With p ~ 2.3e18 a chance hit
among (2C+1)^N candidates has probability about (2C+1)^N / p per point. Control: the same search at 20 random points of
the line (random u) must find nothing. Usage: python3 bmd_cube_repeated_factor_relations.py OUT C JSON...
"""
import itertools
import json
import random
import subprocess
import sys

P = 2305843009213693951


def splitmix(seed):
    state = seed
    while True:
        state = (state + 0x9E3779B97F4A7C15) & (2**64 - 1)
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & (2**64 - 1)
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & (2**64 - 1)
        z ^= z >> 31
        yield z % P


def rational_roots(coeffs):
    gp = "print(apply(r -> lift(r), polrootsmod(Polrev([%s]), %d)))" % (",".join(coeffs), P)
    out = subprocess.run(["gp", "-q"], input=gp + "\n", capture_output=True, text=True, check=True).stdout
    return [int(x) for x in out.strip().strip("[]~").split(",") if x.strip()]


def relations(a, C):
    """All primitive c with |c_i| <= C, sum c = 0, c != 0, first nonzero entry positive, and sum c_i a_i = 0 mod P."""
    n = len(a)
    found = []
    for c in itertools.product(range(-C, C + 1), repeat=n - 1):
        last = -sum(c)
        if abs(last) > C:
            continue
        cc = c + (last,)
        nz = [x for x in cc if x]
        if not nz or nz[0] < 0:
            continue
        g = 0
        for x in nz:
            g = abs(x) if g == 0 else __import__("math").gcd(g, abs(x))
        if g != 1:
            continue
        if sum(ci * ai for ci, ai in zip(cc, a)) % P == 0:
            found.append(cc)
    return found


def omega_relations(a):
    """Relations sum c_i a_i = 0 mod P with c_i in {0, +-1, +-w, +-w^2}, w a primitive cube root of unity in F_P
    (P = 1 mod 3), sum c_i = 0, normalized by first nonzero entry 1; includes equilateral triples
    a_i + w a_j + w^2 a_k = 0."""
    w = next(x for x in (pow(g, (P - 1) // 3, P) for g in range(2, 100)) if x != 1)
    assert pow(w, 3, P) == 1
    vals = [0, 1, P - 1, w, P - w, w * w % P, (P - w * w) % P]
    names = ["0", "1", "-1", "w", "-w", "w2", "-w2"]
    n, found = len(a), []
    for idx in itertools.product(range(7), repeat=n):
        nz = [k for k in idx if k]
        if not nz or nz[0] != 1:
            continue
        c = [vals[k] for k in idx]
        if sum(c) % P or sum(ci * ai for ci, ai in zip(c, a)) % P:
            continue
        found.append(tuple(names[k] for k in idx))
    return found


def main():
    if sys.argv[1] == "--omega":
        out, files = sys.argv[2], sys.argv[3:]
        lines = []
        for f in files:
            d = json.load(open(f))
            N, seed = d["N"], int(d["seed"])
            g = splitmix(seed)
            alpha, beta = [], []
            for _ in range(N):
                alpha.append(next(g)); beta.append(next(g))
            for part in d["squarefree_decomposition"]:
                if part["exponent"] == 1:
                    continue
                roots = rational_roots(part["monic_coefficients_low_to_high"])
                hits = [omega_relations([(x + u * y) % P for x, y in zip(alpha, beta)]) for u in roots]
                lines.append(f"seed {seed}: {len(roots)} rational roots; omega-relations per root: {[len(h) for h in hits]}")
                lines.extend(f"  {h}" for h in hits if h)
            rng = random.Random(seed)
            ctl = sum(len(omega_relations([(x + y * u) % P for x, y in zip(alpha, beta)]))
                      for u in [rng.randrange(P) for _ in range(5)])
            lines.append(f"  control: omega-relations at 5 random points of the line: {ctl}")
        open(out, "w").write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return
    out, C, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
    lines = []
    for f in files:
        d = json.load(open(f))
        N, seed = d["N"], int(d["seed"])
        g = splitmix(seed)
        alpha, beta = [], []
        for _ in range(N):
            alpha.append(next(g)); beta.append(next(g))
        for part in d["squarefree_decomposition"]:
            if part["exponent"] == 1:
                continue
            roots = rational_roots(part["monic_coefficients_low_to_high"])
            lines.append(f"seed {seed} exponent {part['exponent']} degree {part['degree']}: {len(roots)} F_p-rational roots")
            for u in roots:
                a = [(x + u * y) % P for x, y in zip(alpha, beta)]
                rel = relations(a, C)
                lines.append(f"  u0: relations with |c| <= {C}: {rel}")
        rng = random.Random(seed)
        hits = 0
        for _ in range(20):
            u = rng.randrange(P)
            hits += len(relations([(x + u * y) % P for x, y in zip(alpha, beta)], C))
        lines.append(f"  control: relations at 20 random points of the line: {hits}")
        # positive control: at the collision parameter u_01 (a_0 = a_1) the relation (1,-1,0,...) must be found
        u01 = (-(alpha[0] - alpha[1]) * pow(beta[0] - beta[1], P - 2, P)) % P
        rel01 = relations([(x + u01 * y) % P for x, y in zip(alpha, beta)], C)
        want = (1, -1) + (0,) * (N - 2)
        lines.append(f"  positive control: at u_01 relations {rel01}; contains {want}: {want in rel01}")
    open(out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
