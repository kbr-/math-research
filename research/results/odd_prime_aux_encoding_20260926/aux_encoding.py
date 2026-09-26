"""3-integral designs with the auxiliary-variable encoding of one dense block (odd-prime thread, 26 Sept 2026).

Tested statement (integrality review, next step): weak PHP^{n+1}_n (rows sum_j x_ij - 1, collisions) plus the
linear equation E = L - 1 - y - 3 sum_{i<r} 2^i b_i over fresh Boolean y, b_i, where L = c0 + sum_e a_e x_e is a
random dense form with integer coefficients in {0,1,2} and r is the least with 3(2^r - 1) >= max L - 1.
On 0-1 points E has a solution iff L != 0 mod 3; mod 3 it is L = 1 + y. Question: at NS degree d, is the
constant monomial outside Sat(L_d) + 3 Z_(3)^N (a 3-integral design exists)? Decision conditions reported
first: F_3 refutation, rational refutation (estimated at p = 5, 7), 3-torsion.
Ranks: rank_modp.cpp, FLINT (rank_large.c, nullspace_mod.c). Lattice: multilinear multiples of every axiom by
monomials over all variables (cells and auxiliaries), degree <= d.
Usage: aux_encoding.py --n 5 --d 3 --seeds 0 --out FILE"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ('odd_prime_hensel_saturation_20260926',):
    sys.path.insert(0, os.path.join(HERE, '..', sub))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from hensel_saturation import left_kernel_mod3, rank_large, rank3
from rank_modp import rank_mod_p


def monos(nv, d):
    return [frozenset(c) for j in range(d + 1) for c in itertools.combinations(range(nv), j)]


def mul(poly, mono):
    out = {}
    for m, c in poly.items():
        k = m | mono
        out[k] = out.get(k, 0) + c
    return {m: c for m, c in out.items() if c}


def axioms(n, a, c0, r):
    ncell = (n + 1) * n; y = ncell; b = [ncell + 1 + i for i in range(r)]
    var = lambda i, j: i * n + j
    ax = [{**{frozenset([var(i, j)]): 1 for j in range(n)}, frozenset(): -1} for i in range(n + 1)]
    pairs = itertools.product(range(n), itertools.combinations(range(n + 1), 2))
    ax += [{frozenset([var(i, j), var(k, j)]): 1} for j, (i, k) in pairs]
    E = {frozenset([e]): int(a[e]) for e in range(ncell) if a[e]}
    E[frozenset()] = c0 - 1
    E[frozenset([y])] = -1
    E.update({frozenset([b[i]]): -3 * 2 ** i for i in range(r)})
    return ax + [E], ncell + 1 + r


def build(n, d, a, c0, r):
    ax, nv = axioms(n, a, c0, r)
    cols = monos(nv, d); idx = {m: i for i, m in enumerate(cols)}
    rows = []
    for A in ax:
        da = max(len(m) for m in A)
        rows.extend(mul(A, mono) for mono in monos(nv, d - da))
    rows = [q for q in rows if q and max(len(m) for m in q) <= d]
    G = np.zeros((len(rows), len(cols)), dtype=np.float64)
    fill(G, rows, idx)
    return G, idx[frozenset()]


def fill(G, rows, idx):
    for i, q in enumerate(rows):
        for m, c in q.items():
            G[i, idx[m]] += c


def sparse_mod(G, p):
    Gp = np.mod(G, p).astype(np.int64)
    return [list(zip(np.nonzero(q)[0].tolist(), q[np.nonzero(q)[0]].tolist())) for q in Gp]


def run_case(n, d, seed, density):
    ncell = (n + 1) * n
    rng = np.random.default_rng(seed)
    a = np.where(rng.random(ncell) < density, rng.integers(1, 3, ncell), 0); c0 = int(rng.integers(0, 3))
    maxL = c0 + int(a.sum()); r = 0
    while 3 * (2 ** r - 1) < maxL - 1:
        r += 1
    G, one = build(n, d, a, c0, r)
    res = dict(n=n, pigeons=n + 1, d=d, seed=seed, support=int((a > 0).sum()), c0=c0, r=r, rows=G.shape[0], cols=G.shape[1])
    ranks, refuted = {}, {}
    for p in (3, 5, 7):
        sp = sparse_mod(G, p); ranks[p] = rank_mod_p(sp, G.shape[1], p)
        refuted[p] = rank_mod_p(sp + [[(one, 1)]], G.shape[1], p) == ranks[p]
    rq = max(ranks[5], ranks[7], rank_large(G, 1000000007))
    res.update(rank_F3=ranks[3], rank_F5=ranks[5], rank_F7=ranks[7], rank_Q_estimate=rq, torsion3=rq - ranks[3],
               refuted_F3=refuted[3], refuted_F5=refuted[5], refuted_F7=refuted[7])
    if refuted[3]:
        res['design'] = 'none (F_3 refutes)'; return res
    S, hist = G, [ranks[3]]
    while hist[-1] < rq and len(hist) < 5:
        P = left_kernel_mod3(S) @ S
        assert np.all(np.mod(P, 3) == 0) and np.abs(P).max() < 2 ** 52
        S = np.vstack([S, P / 3]); hist.append(rank3(S))
    res['f3_rank_history'] = hist
    res['e1_in_saturation_mod3'] = rank3(S, extra=[(one, 1)]) == hist[-1]
    res['design'] = ('3-integral design exists' if not res['e1_in_saturation_mod3'] else 'none (e1 in saturation)') if hist[-1] >= rq else 'undecided'
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=5); ap.add_argument('--d', type=int, default=3)
    ap.add_argument('--seeds', default='0'); ap.add_argument('--density', type=float, default=0.7)
    ap.add_argument('--out', required=True)
    o = ap.parse_args(); out = []
    for seed in map(int, o.seeds.split(',')):
        t0 = time.time(); res = run_case(o.n, o.d, seed, o.density); res['seconds'] = round(time.time() - t0, 1)
        out.append(res); print(json.dumps(res), flush=True)
        with open(o.out, 'w') as fh:
            json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
