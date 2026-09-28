"""Reference check of absorbable_classes.cpp on one instance (N = 8, seed 1, E = 2): the lift criterion.

Reproduces std::mt19937 draws, builds the square-free algebra, and computes dim Syz_E(R'), dim Syz_E(R),
dim Syz_{E-1}(R) and the dimension of the liftable syzygies {z in Syz_E(R): z.dtau in I_R} directly, by
brute-force linear algebra over F_3 (plain elimination; all spaces have dimension below 200).
"""
import itertools, sys
sys.path.insert(0, '/home/kbr/dev/math-auxiliary/research/tools')
from value_space_lift import rank_mod3


class MT:
    def __init__(self, seed):
        self.mt = [0] * 624; self.i = 624; self.mt[0] = seed & 0xffffffff
        for k in range(1, 624):
            self.mt[k] = (1812433253 * (self.mt[k - 1] ^ (self.mt[k - 1] >> 30)) + k) & 0xffffffff
    def __call__(self):
        if self.i >= 624:
            for k in range(624):
                y = (self.mt[k] & 0x80000000) | (self.mt[(k + 1) % 624] & 0x7fffffff)
                self.mt[k] = self.mt[(k + 397) % 624] ^ (y >> 1) ^ (0x9908b0df if y & 1 else 0)
            self.i = 0
        y = self.mt[self.i]; self.i += 1
        y ^= y >> 11; y ^= (y << 7) & 0x9d2c5680; y ^= (y << 15) & 0xefc60000; y ^= y >> 18
        return y & 0xffffffff


N, seed, E = 8, 1, 2
rng = MT(seed)
coef = [[0] * N for _ in range(4)]
for b in range(2):
    for w in range(2):
        for col in range(N):
            coef[2 * b + w][col] = rng() % 3
rng2 = MT((seed * 7919 + E) & 0xffffffff)
l = [rng2() % 3 for _ in range(4)]
print('coef', coef, 'l', l)


def monos(n, d):
    return [frozenset(c) for c in itertools.combinations(range(n), d)]


def mul(a, b):
    out = {}
    for ca, xa in a.items():
        for cb, xb in b.items():
            if ca & cb:
                continue
            c = ca | cb; out[c] = (out.get(c, 0) + xa * xb) % 3
    return {c: x for c, x in out.items() if x}


def tops(n, cfs):
    F = [{frozenset([i]): cf[i] for i in range(n) if cf[i]} for cf in cfs]
    return F, mul(mul(F[0], F[0]), F[1]), mul(mul(F[2], F[2]), F[3])


def matrix(n, polys_by_slot, e, target_deg):
    """columns: (slot, monomial of degree e); rows: monomials of target_deg; entry = coefficient of slot poly * monomial"""
    src = monos(n, e); tgt = {m: i for i, m in enumerate(monos(n, target_deg))}
    cols = []
    for p in polys_by_slot:
        for r in src:
            col = [0] * len(tgt)
            for c, x in p.items():
                if r & c:
                    continue
                col[tgt[r | c]] = (col[tgt[r | c]] + x) % 3
            cols.append(col)
    return cols, len(tgt)


def syz_dim(n, tau, sig, e):
    cols, nt = matrix(n, [tau, sig], e, e + 3)
    if not cols:
        return 0
    rows = [list(x) for x in zip(*cols)] if nt else []
    return len(cols) - (rank_mod3(rows) if rows else 0)


F, tau, sig = tops(N, coef)
F2, tau2, sig2 = tops(N + 1, [c + [l[i]] for i, c in enumerate(coef)])
AB = mul(F[0], F[1]); A2 = mul(F[0], F[0]); CD = mul(F[2], F[3]); C2 = mul(F[2], F[2])
def lin(*terms):
    out = {}
    for s, p in terms:
        for c, x in p.items():
            out[c] = (out.get(c, 0) + s * x) % 3
    return {c: x for c, x in out.items() if x}
dt = lin((2 * l[0], AB), (l[1], A2)); ds = lin((2 * l[2], CD), (l[3], C2))
# liftable: (z, w) with z.(tau, sig) = 0 in degree E+3 and z.(dt, ds) + w.(tau, sig) = 0 in degree E+2
cz1, n1 = matrix(N, [tau, sig], E, E + 3)
cz2, n2 = matrix(N, [dt, ds], E, E + 2)
cw2, _ = matrix(N, [tau, sig], E - 1, E + 2)
cols = [a + b for a, b in zip(cz1, cz2)] + [[0] * n1 + b for b in cw2]
nz = len(cz1)
rows = [list(x) for x in zip(*cols)]
rank_all = rank_mod3(rows)
# dimension of the projection of the solution space onto z = nullity(all) - nullity(w-only part with z = 0)
null_all = len(cols) - rank_all
w_rows = [list(x) for x in zip(*[[0] * n1 + b for b in cw2])]
null_w = len(cw2) - rank_mod3(w_rows)
liftable = null_all - null_w
print('syz_E_ext', syz_dim(N + 1, tau2, sig2, E), 'syz_E_R', syz_dim(N, tau, sig, E), 'syz_low_R', syz_dim(N, tau, sig, E - 1),
      'liftable_dim', liftable)
