"""Local-fall test: degree split of the degree-D PC closure of weak unary PHP^{n+1}_n over F_3 plus k planted
satisfiable pencils (four selectors 1-L^2 on L1, L2, L1+L2+c3, L1-L2+c4 with (c3,c4) != (0,0)) and then M random
selectors (the recorded sequence of seed 9000+10n), against the additive prediction: the recorded no-fall split
for the random selectors plus each pencil's own change in split.  One incremental closure (gf3_basis.c: persistent
fully reduced basis; each product row inserted once) gives every checkpoint.
Usage: --n N --D D --pencils k1,k2,... --Ms 0,10,... --seed S --out PATH"""
import argparse, ctypes, json, os, subprocess, sys, time
import numpy as np
from scipy import sparse
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
for d in ('odd_prime_one_count_20260922', 'odd_prime_alignment_mechanism_20260922', 'odd_prime_selector_sr_20260923'):
    sys.path.insert(0, os.path.join(RES, d))
import gf3
from random_conditioning_fast import QSpace, base_rows
from random_conditioning import random_eq
from selector_threshold_lib import selector
def lib():
    b = os.path.join(RES, '..', 'logs', 'gf3build'); os.makedirs(b, exist_ok=True); so = os.path.join(b, 'libgf3_basis.so')
    src = os.path.join(HERE, 'gf3_basis.c')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
        subprocess.check_call(['gcc', '-O3', '-march=native', '-fopenmp', '-shared', '-fPIC', '-o', so, src])
    L = ctypes.CDLL(so); vp, ci = ctypes.c_void_p, ctypes.c_int
    L.gf3_insert.argtypes = [vp, vp, vp, vp, ci, ci, ci]; L.gf3_insert.restype = ci; return L
class Closure:
    def __init__(self, sp, threads):
        self.sp, self.th, self.L = sp, threads, lib()
        self.W = (sp.cols + 63) // 64
        self.basis = np.zeros((sp.cols, 2 * self.W), dtype=np.uint64); self.piv = np.zeros(sp.cols, dtype=np.int32)
        self.rank = ctypes.c_int(0); self.done = 0
        self.const = sp.idx[()]
    def insert(self, U8):
        if len(U8) == 0: return
        P = np.ascontiguousarray(gf3.pack(U8)[0], dtype=np.uint64)
        self.L.gf3_insert(self.basis.ctypes.data, ctypes.byref(self.rank), self.piv.ctypes.data, P.ctypes.data,
                          P.shape[0], self.W, self.th)
    def add(self, polys):
        self.insert(np.array([self.sp.vec(p) for p in polys], dtype=np.uint8)); self.close()
    def close(self):
        processed = getattr(self, 'processed', set())
        while True:
            r = self.rank.value; low = [k for k in range(r) if k not in processed and self.sp.deg[self.piv[k]] <= self.sp.D - 1]
            if not low: break
            for s in range(0, len(low), 200):
                idx = low[s:s + 200]
                X = sparse.csr_matrix(gf3.unpack(self.basis[idx], self.W, self.sp.cols), dtype=np.int32)
                prod = np.vstack([(X @ My).toarray() % 3 for My in self.sp.mult]).astype(np.uint8)
                self.insert(prod); processed.update(idx)
        self.processed = processed
    def split(self):
        r = self.rank.value; dg = self.sp.deg[self.piv[:r]]
        return dict(rank=int(r), top=int((dg == self.sp.D).sum()), low=int((dg < self.sp.D).sum()),
                    refuted=bool((self.piv[:r] == self.const).any()))
def add_forms(*terms):
    out = {}
    for c, L in terms:
        for m, a in L.items(): out[m] = (out.get(m, 0) + c * a) % 3
    return {m: a for m, a in out.items() if a}
def sel(L):
    sq = {}
    for m1, a1 in L.items():
        for m2, a2 in L.items():
            mon = tuple(sorted(set(m1 + m2))); sq[mon] = (sq.get(mon, 0) + a1 * a2) % 3
    p = {(): 1}
    for mon, c in sq.items(): p[mon] = (p.get(mon, 0) - c) % 3
    return {m: c for m, c in p.items() if c}
def pencil(rng, v):
    L1, L2 = random_eq(rng, v), random_eq(rng, v)
    c3, c4 = [(0, 1), (1, 0), (1, 1), (2, 2), (1, 2), (2, 1), (0, 2), (2, 0)][int(rng.integers(0, 8))]
    L3 = add_forms((1, L1), (1, L2), (1, {(): c3})); L4 = add_forms((1, L1), (2, L2), (1, {(): c4}))
    return [sel(L) for L in (L1, L2, L3, L4)]
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--D', type=int, default=3)
    ap.add_argument('--pencils', default='0,1,2,4,8'); ap.add_argument('--Ms', default='0,20,40,60,70'); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--threads', type=int, default=12); ap.add_argument('--out'); a = ap.parse_args()
    t0 = time.time(); sp = QSpace(a.n, a.D); v = sp.v
    Ms = [int(x) for x in a.Ms.split(',')]; ks = [int(x) for x in a.pencils.split(',')]
    rng = np.random.default_rng(9000 + 10 * a.n); rand = [selector(rng, v) for _ in range(max(Ms))]   # recorded sequence
    prng = np.random.default_rng(a.seed); pens = [pencil(prng, v) for _ in range(max(ks))]
    C = Closure(sp, a.threads); C.add(base_rows(a.n)); base = C.split(); print('base', base, f'({time.time()-t0:.0f}s)', flush=True)
    own = []
    for p in pens:                                  # each pencil's own change in split
        Cp = Closure(sp, a.threads); Cp.add(base_rows(a.n) + p); s = Cp.split()
        own.append(dict(low=s['low'] - base['low'], top=s['top'] - base['top'], refuted=s['refuted']))
    print('own pencil deltas', own, f'({time.time()-t0:.0f}s)', flush=True)
    res = dict(n=a.n, D=a.D, seed=a.seed, base=base, own=own, runs=[])
    for k in ks:
        C = Closure(sp, a.threads); C.add(base_rows(a.n) + [c for p in pens[:k] for c in p]); done = 0
        for M in Ms:
            C.add(rand[done:M]); done = M; s = C.split()
            pred_low = base['low'] + M + sum(o['low'] for o in own[:k]); pred_top = base['top'] + 34 * M + sum(o['top'] for o in own[:k])
            row = dict(k=k, M=M, **s, pred_low=pred_low, pred_top=pred_top, excess_low=s['low'] - pred_low)
            res['runs'].append(row); print(row, f'({time.time()-t0:.0f}s)', flush=True)
            if a.out: json.dump(res, open(a.out, 'w'), indent=1)
            if s['refuted']: break
