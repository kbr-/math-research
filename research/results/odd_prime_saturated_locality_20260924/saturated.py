"""Saturated locality in form space over F_3.
Budget clauses: disjunctions of literals (l = 0), l an affine form on F_3^s (allowed: some literal true).
Resolution rule: from clauses C_1..C_r (r <= rmax) and literals l_i = 0 in C_i that are jointly inconsistent,
derive the union of the remaining literals; closure with subsumption (a clause whose literal set contains another's
is dropped).  Tested statement (saturated-locality conjecture, form-space version): if the closure does not contain
the empty clause, the closed family is local in every degree (I_e(Z) = sum_b I_e(U_b)).  Also reports the defect of
the original family.  Usage: python3 saturated.py OUT.json s:k:M:rmax:trials:seed [...]"""
import itertools, json, random, sys, time
import numpy as np
exec(open(__file__.replace('odd_prime_saturated_locality_20260924/saturated.py',
                           'odd_prime_t_wise_locality_20260924/form_locality.py')).read().split('out = sys.argv[1]')[0])
def norm(v):  # affine form (coeffs..., const) scaled so the first nonzero coefficient is 1
    v = [x % p for x in v]
    for x in v[:-1]:
        if x: inv = 1 if x == 1 else 2; return tuple((y * inv) % p for y in v)
    return tuple(v)
def inconsistent(forms):
    A = np.array([f[:-1] for f in forms], dtype=np.int64); Ab = np.array([list(f[:-1]) + [(-f[-1]) % p] for f in forms], dtype=np.int64)
    return rank(Ab) > rank(A)
def saturate(clauses, rmax, cap=400):
    cl = set(frozenset(c) for c in clauses)
    changed = True
    while changed:
        changed = False; cur = sorted(cl, key=len)
        for r in range(1, rmax + 1):
            for combo in itertools.combinations(cur, r):
                for lits in itertools.product(*[sorted(c) for c in combo]):
                    if inconsistent(list(lits)):
                        new = frozenset().union(*[c - {l} for c, l in zip(combo, lits)])
                        if any(o <= new for o in cl): continue
                        cl = {o for o in cl if not new <= o} | {new}; changed = True
                        if len(cl) > cap: return None
            if changed: break
    return cl
def defects(clauses, s, pts, Efull, degs):
    forb = []
    for c in clauses:
        f = np.ones(len(pts), bool)
        for l in c: f &= ((pts @ np.array(l[:-1]) + l[-1]) % p != 0)
        forb.append(f)
    forb = np.stack(forb, axis=1); Z = ~forb.any(axis=1); out = []
    for e in range(0, 2 * s + 1):
        E = Efull[degs <= e]
        IZ = null_left(E[:, Z]) if Z.any() else np.eye(len(E), dtype=np.int64)
        parts = [null_left(E[:, ~forb[:, b]]) for b in range(forb.shape[1])]; parts = [q for q in parts if len(q)]
        out.append(len(IZ) - (rank(np.vstack(parts)) if parts else 0))
    return out, int(Z.sum())
out = sys.argv[1]; res = []
for case in sys.argv[2:]:
    s, k, M, rmax, trials, seed = map(int, case.split(':')); rnd = random.Random(seed); t0 = time.time()
    pts = np.array(list(itertools.product(range(p), repeat=s)), dtype=np.int64)
    mons_all = sorted(itertools.product(range(p), repeat=s), key=sum); degs = np.array([sum(m) for m in mons_all])
    Efull = np.ones((len(mons_all), len(pts)), dtype=np.int64)
    for i, m in enumerate(mons_all):
        for j in range(s):
            if m[j]: Efull[i] = Efull[i] * (pts[:, j] ** m[j]) % p
    for tr in range(trials):
        clauses = []
        while len(clauses) < M:
            c = frozenset(norm([rnd.randrange(p) for _ in range(s)] + [rnd.randrange(p)]) for _ in range(k))
            if len(c) == k and all(any(l[:-1]) for l in c): clauses.append(c)
        sat = saturate(clauses, rmax)
        d0, zs = defects(clauses, s, pts, Efull, degs)
        if sat is None: row = dict(case=case, trial=tr, allowed=zs, orig=d0, saturated=None, note='cap'); 
        elif frozenset() in sat: row = dict(case=case, trial=tr, allowed=zs, orig=d0, saturated='empty clause')
        else:
            d1, _ = defects(sorted(sat, key=len), s, pts, Efull, degs)
            row = dict(case=case, trial=tr, allowed=zs, n_sat=len(sat), sat_widths=sorted(len(c) for c in sat), orig=d0, saturated=d1)
        res.append(row); print(json.dumps(row), flush=True); json.dump(res, open(out, 'w'), indent=1)
    print('done', case, round(time.time() - t0, 1), flush=True)
