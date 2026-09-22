"""Exact test of Conjecture C3 (ternary fresh-block conservativity) over a Boolean base.

Ring R = F_3[x_1..x_v, r_1..r_t]/(x^2-x, r^3-r).  PC closure C_D of a set of generators at degree
ceiling D: the smallest subspace of R_{<=D} containing the generators and closed under f -> y f
(reduced) for every variable y whenever deg f <= D-1.  (Working in the reduced ring is PC with
the Boolean and field axioms: an unreduced product of degree <= D is a PC line, and reducing it
subtracts axiom multiples of degree <= D.)

A block with affine forms L_1..L_h has inputs g_i = 1 - L_i^2, coefficients r_i (r^3 = r),
product P = 1 - sum r_i g_i, and companions g_i P (degree 5).  P itself is not an axiom.

Test: base = one or more blocks; fresh block B.  Existing variables = x and the base blocks'
coefficients.  Conservative iff dim(C_D(base+B) cap R[existing]) == dim(C_D(base)), the latter
computed in R[existing] (setting B's coefficients to 0 maps derivations to derivations).
"""
import itertools, json, os, sys, time, zlib
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3

# ---------- polynomial arithmetic on dicts {exponent tuple: coeff mod 3} ----------
def reduce_exp(e, nv):
    out = list(e)
    for k in range(len(out)):
        if k < nv:
            if out[k] > 1: out[k] = 1                      # x^2 = x
        else:
            while out[k] > 2: out[k] -= 2                  # r^3 = r
    return tuple(out)

def pmul(a, b, nv):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = reduce_exp(tuple(x + y for x, y in zip(ea, eb)), nv)
            out[e] = (out.get(e, 0) + ca * cb) % 3
    return {e: c for e, c in out.items() if c}

def padd(a, b, s=1):
    out = dict(a)
    for e, c in b.items():
        out[e] = (out.get(e, 0) + s * c) % 3
    return {e: c for e, c in out.items() if c}

def const(c, n): return {tuple([0] * n): c % 3} if c % 3 else {}
def var(k, n):
    e = [0] * n; e[k] = 1; return {tuple(e): 1}

def affine(coeffs, c0, n):
    p = const(c0, n)
    for k, a in coeffs.items():
        if a % 3: p = padd(p, {tuple(1 if j == k else 0 for j in range(n)): a % 3})
    return p

def block_generators(forms, rvars, nv, n):
    """forms: list of (coeff dict over x indices, constant); rvars: variable indices of coefficients."""
    g = []
    for coeffs, c0 in forms:
        L = affine(coeffs, c0, n)
        g.append(padd(const(1, n), pmul(L, L, nv), -1))
    P = const(1, n)
    for gi, rv in zip(g, rvars):
        P = padd(P, pmul(var(rv, n), gi, nv), -1)
    return [pmul(gi, P, nv) for gi in g]

def block_product(forms, rvars, nv, n):
    P = const(1, n)
    for (coeffs, c0), rv in zip(forms, rvars):
        L = affine(coeffs, c0, n)
        P = padd(P, pmul(var(rv, n), padd(const(1, n), pmul(L, L, nv), -1), nv), -1)
    return P

# ---------- monomial space ----------
def monomials(nv, nt, D):
    out = []
    for xs in itertools.product(range(2), repeat=nv):
        dx = sum(xs)
        if dx > D: continue
        for rs in itertools.product(range(3), repeat=nt):
            if dx + sum(rs) <= D: out.append(xs + rs)
    return out

def deg(e): return sum(e)

class Space:
    """Columns are ordered by decreasing degree (fresh monomials first within a degree), so that
    in an echelon basis the rows whose pivot has degree <= D-1 span the closure's part of degree
    <= D-1.  The existing-variable part is read off after permuting to fresh-first order."""
    def __init__(self, nv, nt, D, fresh_vars=()):
        self.nv, self.nt, self.D, self.n = nv, nt, D, nv + nt
        mons = monomials(nv, nt, D)
        fresh = set(fresh_vars)
        isf = lambda e: any(e[k] for k in fresh)
        mons.sort(key=lambda e: (-deg(e), 0 if isf(e) else 1, e))
        self.mons = mons; self.idx = {e: i for i, e in enumerate(mons)}
        self.cols = len(mons)
        self.deg = np.array([deg(e) for e in mons])
        self.isfresh = np.array([isf(e) for e in mons])
        self.nfresh = int(self.isfresh.sum())
        self.fresh_first = np.concatenate([np.nonzero(self.isfresh)[0], np.nonzero(~self.isfresh)[0]])
        self.mult = []                                   # sparse cols x cols map for y*
        for y in range(self.n):
            rows, cols = [], []
            for i, e in enumerate(mons):
                if deg(e) <= D - 1:
                    t = list(e); t[y] += 1
                    rows.append(i); cols.append(self.idx[reduce_exp(tuple(t), nv)])
            self.mult.append(sparse.csr_matrix((np.ones(len(rows), dtype=np.int64), (rows, cols)),
                                               shape=(self.cols, self.cols)))

    def vec(self, p):
        v = np.zeros(self.cols, dtype=np.uint8)
        for e, c in p.items():
            if deg(e) > self.D: raise ValueError('generator above ceiling')
            v[self.idx[e]] = c
        return v

def echelon(M, par):
    E, W, piv = gf3.rref(M, full=False, parallel=par)
    return gf3.unpack(E, W, M.shape[1]), piv

def closure(space, gens, par=False, log=None, chunk=300):
    """Echelon basis of the degree-D PC closure: iterate V <- V + y*(V cap R_{<=D-1}).
    The basis is kept bit-packed; only chunks of `chunk` low rows are unpacked and multiplied by
    every variable at once, so peak memory stays near a few packed basis copies."""
    cols = space.cols
    P, W, piv = gf3.rref(np.array([space.vec(g) for g in gens], dtype=np.uint8), parallel=par)
    mult = [My.astype(np.int32) for My in space.mult]
    rounds = 0
    while True:
        rounds += 1
        old = P.shape[0]
        lowrows = np.nonzero(space.deg[piv] <= space.D - 1)[0]
        Pold = P                                           # multiply this round's low part
        for s in range(0, len(lowrows), chunk):
            L = sparse.csr_matrix(gf3.unpack(Pold[lowrows[s:s + chunk]], W, cols), dtype=np.int32)
            prod = np.vstack([(L @ My).toarray() % 3 for My in mult]).astype(np.uint8)
            Q, _ = gf3.pack(prod)
            P, W, piv = gf3.rref(None, parallel=par, packed=(np.vstack([P, Q]), W, cols))
        if log: log(f'  {cols} cols, round {rounds}: dim {old} -> {P.shape[0]}')
        if P.shape[0] == old: return P, W, piv

def existing_dim(space, P, W, par=False):
    """dim(V cap F3[existing]): echelon in fresh-first column order, done in row chunks."""
    cols = space.cols
    acc = None
    for s in range(0, P.shape[0], 2000):
        M = gf3.unpack(P[s:s + 2000], W, cols)[:, space.fresh_first]
        Q, W2 = gf3.pack(M)
        acc = Q if acc is None else np.vstack([acc, Q])
        acc, W2, pv = gf3.rref(None, parallel=par, packed=(acc, W2, cols))
    return int((pv >= space.nfresh).sum())

def dense(P, W, space): return gf3.unpack(P, W, space.cols)

def contains_one(space, P, W):
    Q, _ = gf3.pack(space.vec(const(1, space.n))[None, :])
    r = gf3.rref(None, packed=(np.vstack([P, Q]), W, space.cols))[2].shape[0]
    return r == P.shape[0]

# ---------- instances ----------

PAR = os.environ.get('C3_PAR') == '1'                    # OpenMP elimination for single large jobs

def run(inst, log=None):
    v, D = inst['v'], inst['D']
    base_forms, fresh_forms = inst['base'], inst['fresh']
    tA = sum(len(b) for b in base_forms); tB = len(fresh_forms)
    t0 = time.time()
    sp0 = Space(v, tA, D)                                 # existing ring: x and base coefficients
    gens0, k = [], v
    for b in base_forms:
        gens0 += block_generators(b, list(range(k, k + len(b))), v, v + tA); k += len(b)
    P0, W0, _ = closure(sp0, gens0, par=PAR, log=log)
    freshvars = list(range(v + tA, v + tA + tB))
    sp1 = Space(v, tA + tB, D, fresh_vars=freshvars)
    lift = lambda p: {e + (0,) * tB: c for e, c in p.items()}
    gens1 = [lift(g) for g in gens0]
    gens1 += block_generators(fresh_forms, freshvars, v, v + tA + tB)
    if inst.get('axiomP'):                                # control: P_B as an axiom (not a block)
        gens1.append(block_product(fresh_forms, freshvars, v, v + tA + tB))
    for mono in inst.get('fake', []):                     # sanity control: an extra old axiom
        e = [0] * (v + tA + tB)
        for j in mono: e[j] = 1
        gens1.append({tuple(e): 1})
    P1, W1, _ = closure(sp1, gens1, par=PAR, log=log)
    dim_base = P0.shape[0]
    dim_exist = existing_dim(sp1, P1, W1, par=PAR)
    res = dict(name=inst['name'], v=v, D=D, base_inputs=[len(b) for b in base_forms], fresh_inputs=tB,
               cols_base=sp0.cols, cols_full=sp1.cols, dim_base=dim_base, dim_full=P1.shape[0],
               dim_existing_after=dim_exist, conservative=(dim_exist == dim_base),
               one_in_base=bool(contains_one(sp0, P0, W0)), one_in_full=bool(contains_one(sp1, P1, W1)),
               seconds=round(time.time() - t0, 2), base=base_forms, fresh=fresh_forms)
    return res

def rand_form(rng, v, density):
    coeffs = {k: int(rng.integers(1, 3)) for k in range(v) if rng.random() < density}
    if not coeffs: coeffs = {int(rng.integers(v)): 1}
    return (coeffs, int(rng.integers(0, 3)))

def independent(forms, v):
    M = np.array([[f[0].get(k, 0) for k in range(v)] for f in forms], dtype=np.uint8)
    return gf3.rank(M) == len(forms)

def make(tag, v, D, hA, hB, seed, mode='random', nbase=1, density=0.6):
    rng = np.random.default_rng(zlib.crc32(f'{tag}-{mode}-{seed}'.encode()))
    while True:
        base = [[rand_form(rng, v, density) for _ in range(hA)] for _ in range(nbase)]
        if mode == 'dependent':                           # forms A, B, A+B (three-selector shape)
            (ca, a0), (cb, b0) = rand_form(rng, v, density), rand_form(rng, v, density)
            cs = {k: (ca.get(k, 0) + cb.get(k, 0)) % 3 for k in set(ca) | set(cb)}
            fresh = [(ca, a0), (cb, b0), ({k: c for k, c in cs.items() if c}, (a0 + b0) % 3)]
            if independent(fresh[:2], v) and fresh[2][0]: break
            continue
        if mode == 'shared':
            fresh = [base[0][0]] + [rand_form(rng, v, density) for _ in range(hB - 1)]
        else:
            fresh = [rand_form(rng, v, density) for _ in range(hB)]
        if all(independent(b, v) for b in base) and independent(fresh, v): break
    inst = dict(name=f'{tag}-{mode}-s{seed}', v=v, D=D, base=base, fresh=fresh)
    if mode == 'fake': inst['fake'] = [(0, 1, 2)]
    if mode == 'axiomP': inst['axiomP'] = True
    return inst

CONFIGS = {
    'tiny': [('tiny', 4, 5, 2, 2, s, m) for s in range(2) for m in ('random', 'fake')],
    'small': [('small', 6, D, 2, 2, s, m) for D in (6, 7, 8) for s in range(4)
              for m in ('random', 'shared', 'fake')] +
             [('small', 6, D, 2, 3, s, 'dependent') for D in (6, 7) for s in range(4)] +
             [('small3', 6, D, 3, 3, s, 'random') for D in (6, 7) for s in range(3)],
    'axiomP': [('axp', 6, D, 2, h, s, 'axiomP') for D in (6, 7, 8) for h in (2, 3) for s in range(3)],
    'twobase2': [('twobase2', 6, D, 2, 2, s, 'random', 2) for D in (6, 7, 8) for s in range(12)],
    'threebase': [('threebase', 5, D, 2, 2, s, 'random', 3) for D in (6, 7) for s in range(8)],
    'lag': [('twobase2', 6, D, 2, 2, s, 'random', 2) for D in (8,) for s in range(12)] +
           [('twobase3', 6, D, 2, 2, s, 'random', 2) for D in (7,) for s in range(24)],
    'rerun': [('twobase2', 6, D, 2, 2, s, 'random', 2) for D in (6, 7) for s in range(12)] +
             [('threebase', 5, 6, 2, 2, s, 'random', 3) for s in range(8)],
    'threebase7': [('threebase', 5, 7, 2, 2, s, 'random', 3) for s in (0, 2, 4, 7)],
    'd8': [('threebase', 5, 8, 2, 2, 4, 'random', 3)],
    'threebase8': [('threebase', 5, 8, 2, 2, s, 'random', 3) for s in range(8)],
    'twobase': [('twobase', 6, D, 2, 2, s, 'random', 2) for D in (6, 7) for s in range(6)],
}

def work(args):
    return run(make(*args), log=(lambda m: print(m, flush=True)) if PAR else None)

if __name__ == '__main__':
    from multiprocessing import Pool
    cfg = sys.argv[1]
    jobs = CONFIGS[cfg]
    for j in jobs[:1]:
        i = make(*j); tA = sum(len(b) for b in i['base']); tB = len(i['fresh'])
        print(cfg, len(jobs), 'jobs; columns', len(monomials(i['v'], tA + tB, i['D'])), flush=True)
    out = []
    workers = int(os.environ.get('C3_WORKERS', '14'))
    with Pool(min(workers, len(jobs))) as pool:
        for r in pool.imap_unordered(work, jobs):
            print({k: r[k] for k in ('name', 'D', 'cols_full', 'dim_base', 'dim_existing_after',
                                     'conservative', 'one_in_full', 'seconds')}, flush=True)
            out.append(r)
    out.sort(key=lambda r: r['name'])
    with open(os.path.join(HERE, f'c3_{cfg}.json'), 'w') as f: json.dump(out, f, indent=1)
