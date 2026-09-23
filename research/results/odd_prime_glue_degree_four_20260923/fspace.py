"""Functional quotient space for the all-C closure (gf3_closure.c): monomials in the cells x_{i,j} (variable i*n+j,
pigeon i < n+1, hole j < n) of degree <= D with distinct pigeons and distinct holes.  Row collisions x_{ij}x_{ij'} and
hole collisions are zero, Booleanity x^2 = x.  PC closure in this quotient equals the closure of the weak base plus the
row-collision axioms, modulo the collision monomials (all their multiples of degree <= D are derivable).
Self-test: python3 fspace.py  (n=6, D=3: codimension of the functional base plus the seed-1 selector prefixes equals the
recorded QSpace-based computation, and the first refuted M is 49)."""
import itertools, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_local_falls_n7_20260923'))
import closure3
from closure3 import Closure
class FSpace:
    def __init__(self, n, D):
        self.n, self.D, self.v = n, D, n * (n + 1); R = n + 1
        blocks = []                                          # monomials of degree k: k pigeons x injective holes
        for k in range(D, -1, -1):
            P = np.array(list(itertools.combinations(range(R), k)), dtype=np.int64).reshape(-1, k) if k else np.zeros((1, 0), dtype=np.int64)
            H = np.array(list(itertools.permutations(range(n), k)), dtype=np.int64).reshape(-1, k) if k else np.zeros((1, 0), dtype=np.int64)
            blocks.append(np.sort((P[:, None, :] * n + H[None, :, :]).reshape(len(P) * len(H), k), axis=1))
        mons = [tuple(r) for blk in blocks for r in blk.tolist()]
        self.mons = mons; self.idx = {m: i for i, m in enumerate(mons)}; self.cols = len(mons)
        self.W = (self.cols + 63) // 64; self.deg = np.array([len(m) for m in mons], dtype=np.int8); self.const = self.idx[()]
        # product table by numpy: monomials as bit masks (v <= 63), located by searchsorted; no loop over monomials
        bit = np.concatenate([(np.int64(1) << blk).sum(axis=1) for blk in blocks])
        pm = np.concatenate([(np.int64(1) << (blk // n)).sum(axis=1) for blk in blocks]); hm = np.concatenate([(np.int64(1) << (blk % n)).sum(axis=1) for blk in blocks])
        order = np.argsort(bit); sb = bit[order]
        mul = -np.ones((self.v, self.cols), dtype=np.int32); low = self.deg <= D - 1
        for y in range(self.v):                                  # v iterations, vectorized over monomials
            inm = (bit >> y) & 1 == 1; free = ((pm >> (y // n)) & 1 == 0) & ((hm >> (y % n)) & 1 == 0)
            mul[y, low & inm] = np.nonzero(low & inm)[0]
            sel_ = low & free; tgt = bit[sel_] | (1 << y); pos = np.searchsorted(sb, tgt); assert (sb[pos] == tgt).all()
            mul[y, sel_] = order[pos]
        self.mul = np.ascontiguousarray(mul); self.q = self
    def vec(self, p):
        out = np.zeros(self.cols, dtype=np.uint8)
        for m, c in p.items():
            m = tuple(sorted(set(m)))
            if m in self.idx: out[self.idx[m]] = (int(out[self.idx[m]]) + c) % 3
        return out
def base_rows(n):
    return [dict([((i * n + j,), 1) for j in range(n)] + [((), 2)]) for i in range(n + 1)]
if __name__ == '__main__':
    import json
    sys.path.insert(0, os.path.join(RES, 'odd_prime_local_falls_20260923'))
    from local_falls import random_eq, sel
    rec = json.load(open(os.path.join(RES, 'odd_prime_glued_theorem_20260923', 'glued_n6_s1.json')))
    sp = FSpace(6, 3); C = Closure(sp); C.add(base_rows(6)); s = C.split()
    qcols = 7638; codim_rec = qcols - rec['base']['rank']
    print('functional cols', sp.cols, 'base codim', sp.cols - s['rank'], 'recorded', codim_rec, flush=True)
    assert sp.cols - s['rank'] == codim_rec
    rng = np.random.default_rng(500 + 1); v = sp.v; first = None
    forms = []
    while len(forms) < 60:
        L = random_eq(rng, v); arr = np.zeros((7, 6), dtype=np.int64)
        for m, c in L.items():
            if m: arr[m[0] // 6, m[0] % 6] = c
        if all(len(set(arr[x])) > 1 for x in range(7)): forms.append(L)
    for M, L in enumerate(forms, 1):
        C.add([sel(L)]); r = rec['rows'][M - 1] if M <= len(rec['rows']) else None
        if r: assert sp.cols - C.split()['rank'] == qcols - r['rank'], M
        if C.split()['refuted']: first = M; break
    print('first refuted', first, 'recorded', rec['first_refuted_M'], flush=True); assert first == rec['first_refuted_M']
    print('self-test passed')
