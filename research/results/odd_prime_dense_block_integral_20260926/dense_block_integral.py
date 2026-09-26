"""Do 3-integral certificates survive one dense constraint? (odd-prime thread, 26 Sept 2026)

Tested statement (the 3-integrality lead at a block): for weak PHP^{n+1}_n plus one axiom q_L saying L != 0
mod 3, with L = c0 + sum_e a_e x_e a random dense form over F_3 lifted to integers a_e, c0 in {0,1,2}, and the
integer lift q_L = (L - 1)(L - 2) (which is L^2 - 1 mod 3), is the constant monomial e_1 outside
Sat(L_d) + 3 Z_(3)^N, where L_d is the Z-lattice of multilinear degree-<=d multiples of all axioms?
Reported first, as the decision conditions: whether F_3 refutes at NS degree d (then no certificate can exist
and the case is uninformative), whether Z^N / L_d has 3-torsion (without it a certificate exists iff F_3 does
not refute), and whether Q refutes (then no rational certificate exists for this lift).
Ranks: rank_modp (small primes), FLINT (word-size primes, left kernels). Saturation by one exact lifting step,
iterated while the F_3 rank is below the rational-rank estimate (as in hensel_saturation.py).
Usage: dense_block_integral.py --n 5 --d 3 --seeds 0,1,2,3 --density 0.7 --out FILE"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ('odd_prime_hensel_saturation_20260926', 'odd_prime_closed_routes_review_20260926'):
    sys.path.insert(0, os.path.join(HERE, '..', sub))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from hensel_saturation import left_kernel_mod3, rank_large, rank3, LARGE_PRIMES
from php_lattice_torsion import lattice_rows, monomials, mul
from rank_modp import rank_mod_p


def q_poly(nv, a, c0):
    """Multilinear (L - 1)(L - 2) with L = c0 + sum a_e x_e, over Z (x_e^2 = x_e)."""
    lin = {frozenset(): c0}
    lin.update({frozenset([e]): int(a[e]) for e in range(nv) if a[e]})
    out = {}
    for m1, c1 in lin.items():
        for m2, c2 in lin.items():
            k = m1 | m2
            out[k] = out.get(k, 0) + c1 * c2
    for m, c in lin.items():                                  # - 3 L
        out[m] = out.get(m, 0) - 3 * c
    out[frozenset()] = out.get(frozenset(), 0) + 2
    return {m: c for m, c in out.items() if c}


def run_case(n, d, seed, density):
    nv = (n + 1) * n
    rng = np.random.default_rng(seed)
    a = np.where(rng.random(nv) < density, rng.integers(1, 3, nv), 0)
    c0 = int(rng.integers(0, 3))
    rows, cols = lattice_rows(n, d)
    q = q_poly(nv, a, c0)
    rows = rows + [mul(q, mono) for mono in monomials(nv, d - 2)]
    idx = {m: i for i, m in enumerate(cols)}
    G = np.zeros((len(rows), len(cols)), dtype=np.float64)
    fill_rows(G, rows, idx)
    one = idx[frozenset()]
    small = {p: rank_mod_p(sparse_mod(G, p), len(cols), p) for p in (3, 5, 7, 11, 13, 37)}
    refuted = {p: rank_mod_p(sparse_mod(G, p) + [[(one, 1)]], len(cols), p) == small[p] for p in (3, 5, 7)}
    rq = max(v for p, v in small.items() if p != 3)
    large = {str(p): rank_large(G, p) for p in LARGE_PRIMES}
    res = dict(n=n, pigeons=n + 1, d=d, seed=seed, density=density, support=int((a > 0).sum()), c0=c0,
               rows=G.shape[0], cols=G.shape[1], rank_F3=small[3], rank_Q_estimate=rq, ranks_large=large,
               refuted_F3=refuted[3], refuted_F5=refuted[5], refuted_F7=refuted[7], torsion3=rq - small[3])
    if refuted[3]:
        res['certificate'] = 'none (F_3 refutes)'
        return res
    S, hist = G, [small[3]]
    while hist[-1] < rq and len(hist) < 5:
        P = left_kernel_mod3(S) @ S
        assert np.all(np.mod(P, 3) == 0) and np.abs(P).max() < 2 ** 52
        S = np.vstack([S, P / 3]); hist.append(rank3(S))
    res['f3_rank_history'] = hist
    res['e1_in_saturation_mod3'] = rank3(S, extra=[(one, 1)]) == hist[-1]
    res['certificate'] = ('exists' if not res['e1_in_saturation_mod3'] else 'none for this lift') if hist[-1] >= rq else 'undecided'
    return res


def fill_rows(G, rows, idx):
    for i, r in enumerate(rows):
        for m, c in r.items():
            G[i, idx[m]] += c


def sparse_mod(G, p):
    Gp = np.mod(G, p).astype(np.int64)
    return [list(zip(np.nonzero(r)[0].tolist(), r[np.nonzero(r)[0]].tolist())) for r in Gp]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=5); ap.add_argument('--d', type=int, default=3)
    ap.add_argument('--seeds', default='0,1,2,3'); ap.add_argument('--density', type=float, default=0.7)
    ap.add_argument('--out', required=True)
    a = ap.parse_args(); out = []
    for seed in map(int, a.seeds.split(',')):
        t0 = time.time(); res = run_case(a.n, a.d, seed, a.density); res['seconds'] = round(time.time() - t0, 1)
        out.append(res); print(json.dumps(res), flush=True)
        with open(a.out, 'w') as fh:
            json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
