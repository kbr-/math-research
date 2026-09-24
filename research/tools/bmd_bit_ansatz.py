"""Search for power-of-two factors Q_K (K = 2^j) inside a subalgebra of symmetric functions.

Statement tested.  Is there Q = sum_gamma c_gamma prod_i g_i^gamma_i, with generators g_i taken
from a given list of elementary symmetric functions e_r (default e_1, e_2, e_4, ...), of degree
<= 2K - j - 2, with Q(0) = 1 and Hasse multiplicity >= K - |a| at every point of weight
1 <= |a| < K, in every dimension?  Each product of e's is e_mu, expanded as sum_lambda M(mu,lambda)
m_lambda with M the parity of 0-1 matrices; the conditions are the dimension-free placement parities
of bmd_symmetric_q.  Small linear algebra over F_2 (seconds for K <= 8).
Usage: bmd_bit_ansatz.py K [--gens 1,2,4] --out PATH
"""
import argparse, itertools, json, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmd_symmetric_q import conditions, placement_parity, partitions, rank_and_basis
from bmd_ebasis import matrices


def exponent_vectors(gens, D):
    def rec(i, left):
        if i == len(gens):
            yield ()
            return
        for g in range(left // gens[i] + 1):
            for rest in rec(i + 1, left - g * gens[i]):
                yield (g,) + rest
    return list(rec(0, D))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('K', type=int)
    ap.add_argument('--gens', default=None)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    K = a.K; j = int(math.log2(K)); D = 2 * K - j - 2
    gens = [int(x) for x in a.gens.split(',')] if a.gens else [2 ** i for i in range(j + 1) if 2 ** i <= D]
    t0 = time.time()
    cols = exponent_vectors(gens, D)
    rows = conditions(K)
    # m-expansion of each column e_mu, then its value on each condition row
    lam_cache = {}
    def m_expansion(mu):
        s = sum(mu)
        if mu not in lam_cache:
            lam_cache[mu] = [lam for lam in partitions(s) if matrices(mu, lam)]
        return lam_cache[mu]
    mat = [0] * len(rows)
    for ci, gam in enumerate(cols):
        mu = tuple(sorted([g for g, e in zip(gens, gam) for _ in range(e)], reverse=True))
        lams = m_expansion(mu)
        for ri, (w, ob, zb) in enumerate(rows):
            if sum(placement_parity(l, ob, zb) for l in lams) & 1:
                mat[ri] |= 1 << ci
    # need the constant column (gam = 0) coefficient 1: solve mat * c = 0 with c_0 = 1
    const = cols.index(tuple(0 for _ in gens))
    r_all = len(rank_and_basis(mat))
    r_wo = len(rank_and_basis([v & ~(1 << const) for v in mat]))
    exists = r_all == r_wo            # constant column dependent on the others => some solution has c_0 = 1
    rec = {'K': K, 'degree_bound': D, 'generators': gens, 'columns': len(cols), 'rows': len(rows),
           'exists': exists, 'seconds': round(time.time() - t0, 2)}
    print(json.dumps(rec), flush=True)
    json.dump(rec, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
