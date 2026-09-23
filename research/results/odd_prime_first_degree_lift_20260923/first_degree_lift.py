"""First-degree symmetric lifting for r forms at p = 3 on the functional matching board.

Checks whether the polarized lift Lambda: K_3 -> K_1^A, w -> (D^alpha w)_{|alpha|=2}, is onto the
symmetric tuples, by exact GF(3) ranks.  K_s: arrays on injections from s-row sets to labels with
every ordinary row marginal zero.  D_j = sum_i delta_i^{f_i^(j)} (weighted marginals).  Symmetric
tuples: D_i zeta_alpha = D_j zeta_beta whenever alpha+e_i = beta+e_j, and D_i zeta_{2e_i} = 0.
(The unit factors m(alpha) are omitted, which does not change ranks.)

Modes:
  full   -- K_3 by an exact nullspace of the (row-independent) marginal map on each row triple.
  sample -- K_3 sampled by products of three two-label differences on disjoint labels; the rank is
            then a lower bound, and equality with dim Sym proves surjectivity for that instance.
Usage: python3 first_degree_lift.py OUT.json
"""
import itertools, json, os, random, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                                'odd_prime_alignment_mechanism_20260922'))
import gf3

P = 3
R_FORMS = 3
ALPHAS = [a for a in itertools.product(range(3), repeat=R_FORMS) if sum(a) == 2]

def op_seq(alpha):
    s = []
    for j, e in enumerate(alpha): s += [j] * e
    return s

def lam_columns(F, rows, labels):
    """Lambda of the basis array e at (rows[0]->labels[0], ...): returns dict coord -> value.
    Coordinates: (alpha index, row, label) in K_1."""
    out = {}
    for ai, alpha in enumerate(ALPHAS):
        ops = op_seq(alpha)          # apply ops[1] first, then ops[0]; order irrelevant (commute)
        # D_{j0} D_{j1} e: choose distinct rows i (for j1) and i' (for j0) among the three
        for x, y in itertools.permutations(range(3), 2):
            v = F[ops[1]][rows[x]][labels[x]] * F[ops[0]][rows[y]][labels[y]] % P
            if v:
                z = 3 - x - y
                key = (ai, rows[z], labels[z])
                out[key] = (out.get(key, 0) + v) % P
    return out

def coord_index(R, N):
    return lambda ai, i, w: (ai * R + i) * N + w

def sym_dim(F, R, N):
    """dim of symmetric tuples in K_1^A, computed as a nullity in full coordinates."""
    idx = coord_index(R, N); ncols = len(ALPHAS) * R * N
    eqs = []
    for ai in range(len(ALPHAS)):                  # row sums zero (tuple entries lie in K_1)
        for i in range(R):
            v = np.zeros(ncols, np.uint8); v[[idx(ai, i, w) for w in range(N)]] = 1; eqs.append(v)
    def Dvec(ai, j):
        v = np.zeros(ncols, np.uint8)
        for i in range(R):
            for w in range(N): v[idx(ai, i, w)] = F[j][i][w] % P
        return v
    groups = {}
    for ai, alpha in enumerate(ALPHAS):
        for j in range(R_FORMS):
            b = tuple(alpha[t] + (t == j) for t in range(R_FORMS))
            groups.setdefault(b, []).append(Dvec(ai, j))
    for b, vs in groups.items():
        if max(b) == 3: eqs += vs                    # pure moments vanish
        else: eqs += [(vs[0] + 2 * v) % P for v in vs[1:]]   # all preimages equal
    C = np.array(eqs, np.uint8)
    return ncols - gf3.rank(C), C

def nullspace_marginals(N):
    inj = list(itertools.permutations(range(N), 3))
    pos = {t: k for k, t in enumerate(inj)}
    pairs = list(itertools.permutations(range(N), 2)); ppos = {t: k for k, t in enumerate(pairs)}
    M = np.zeros((3 * len(pairs), len(inj)), np.uint8)
    for k, t in enumerate(inj):
        for x in range(3):
            rest = tuple(t[y] for y in range(3) if y != x)
            M[x * len(pairs) + ppos[rest], k] = 1
    E, W, piv = gf3.rref(M, full=True)
    U = gf3.unpack(E, W, len(inj)).astype(np.int64)
    piv = list(piv); free = [c for c in range(len(inj)) if c not in set(piv)]
    B = np.zeros((len(inj), len(free)), np.int64)
    for f_i, f in enumerate(free):
        B[f, f_i] = 1
        for r, pc in enumerate(piv): B[pc, f_i] = (-U[r, f]) % P
    assert not ((M.astype(np.int64) @ B) % P).any()
    return inj, B

def width(F, R, N):
    best = None
    for u in itertools.product(range(3), repeat=R_FORMS):
        if not any(u) or next(x for x in u if x) != 1: continue   # projective points
        act = 0
        for i in range(R):
            g = [sum(u[j] * F[j][i][w] for j in range(R_FORMS)) % P for w in range(N)]
            act += len(set(g)) > 1
        best = act if best is None else min(best, act)
    return best

def robustness(F, R, N):
    """Largest L such that deleting any L labels keeps the rank of [1; f^(1..3)] on every row."""
    best = None
    for i in range(R):
        cols = [(1,) + tuple(F[j][i][w] for j in range(R_FORMS)) for w in range(N)]
        rk = gf3.rank(np.array(cols, np.uint8).T)
        # rank drops iff the kept columns lie in a subspace of dim rk-1 of the column span:
        # L_max = min over hyperplanes H of the span of #{cols outside H} - 1.
        span_basis = np.array(cols, np.uint8)
        worst = None
        for h in itertools.product(range(3), repeat=R_FORMS + 1):
            if not any(h): continue
            vals = [sum(a * b for a, b in zip(h, c)) % P for c in cols]
            if all(v == 0 for v in vals): continue       # h vanishes on the span: not a hyperplane
            out = sum(1 for v in vals if v)
            worst = out if worst is None else min(worst, out)
        L = worst - 1
        best = L if best is None else min(best, L)
    return best

def make_forms(kind, R, N, rng):
    F = [[[0] * N for _ in range(R)] for _ in range(R_FORMS)]
    for i in range(R):
        if kind == 'generic':
            for j in range(R_FORMS):
                F[j][i] = [rng.randrange(3) for _ in range(N)]
        elif kind == 'rowdep':                         # f3 = a_i f1 + b_i f2 on each row
            a, b = rng.randrange(3), rng.randrange(3)
            F[0][i] = [rng.randrange(3) for _ in range(N)]
            F[1][i] = [rng.randrange(3) for _ in range(N)]
            F[2][i] = [(a * x + b * y) % P for x, y in zip(F[0][i], F[1][i])]
        elif kind == 'affine4':                        # labels F_3^4, random linear row maps
            lab = list(itertools.product(range(3), repeat=4))
            while True:
                Lm = [[rng.randrange(3) for _ in range(4)] for _ in range(R_FORMS)]
                if gf3.rank(np.array(Lm, np.uint8)) == R_FORMS: break
            for j in range(R_FORMS):
                F[j][i] = [sum(Lm[j][t] * lab[w][t] for t in range(4)) % P for w in range(N)]
    return F

def run_full(kind, R, N, seed, inj_B):
    rng = random.Random(seed); F = make_forms(kind, R, N, rng)
    inj, B = inj_B; idx = coord_index(R, N); ncoord = len(ALPHAS) * R * N
    blocks = []
    for S in itertools.combinations(range(R), 3):
        L = np.zeros((ncoord, len(inj)), np.int64)
        for k, t in enumerate(inj):
            for (ai, i, w), v in lam_columns(F, S, t).items(): L[idx(ai, i, w), k] = v
        blocks.append(((L @ B) % P).astype(np.uint8))
    img = np.concatenate(blocks, axis=1).T
    rk = gf3.rank(np.ascontiguousarray(img))
    sd, C = sym_dim(F, R, N)
    assert not ((C.astype(np.int64) @ img.T.astype(np.int64)) % P).any()   # image is symmetric
    return dict(mode='full', kind=kind, rows=R, labels=N, seed=seed, width=width(F, R, N),
                robustness=robustness(F, R, N), rank_lambda=int(rk), dim_sym=int(sd),
                onto=bool(rk == sd))

def run_sample(kind, R, N, seed, nsamp):
    rng = random.Random(seed); F = make_forms(kind, R, N, rng)
    idx = coord_index(R, N); ncoord = len(ALPHAS) * R * N
    rows = []
    for _ in range(nsamp):
        S = sorted(rng.sample(range(R), 3)); labs = rng.sample(range(N), 6)
        v = np.zeros(ncoord, np.int64)
        for signs in itertools.product((0, 1), repeat=3):
            t = tuple(labs[2 * x + signs[x]] for x in range(3)); c = (-1) ** sum(signs)
            for (ai, i, w), val in lam_columns(F, S, t).items(): v[idx(ai, i, w)] += c * val
        rows.append((v % P).astype(np.uint8))
    img = np.array(rows, np.uint8)
    rk = gf3.rank(img); sd, C = sym_dim(F, R, N)
    assert not ((C.astype(np.int64) @ img.T.astype(np.int64)) % P).any()
    return dict(mode='sample', kind=kind, rows=R, labels=N, seed=seed, samples=nsamp,
                width=width(F, R, N), robustness=robustness(F, R, N),
                rank_lambda_lower=int(rk), dim_sym=int(sd), onto=bool(rk == sd))

if __name__ == '__main__':
    out = sys.argv[1]; res = []; t0 = time.time()
    for N in (6, 9):
        ib = nullspace_marginals(N)
        for kind in ('generic', 'rowdep'):
            for R in range(3, 8):
                for seed in (1, 2):
                    r = run_full(kind, R, N, seed, ib); res.append(r); print(r, flush=True)
    for R in (6, 7):
        r = run_sample('affine4', R, 81, 1, 3 * 6 * R * 81 // 2); res.append(r); print(r, flush=True)
    json.dump(dict(results=res, seconds=time.time() - t0), open(out, 'w'), indent=1)
