"""Orchestration for gf3_closure.c: the whole degree-D closure runs in C (table-driven products, persistent reduced
basis).  Closure objects copy in O(basis) so a shared prefix (base, base plus random selectors) is computed once.
Self-test: python3 closure3.py compares splits with the recorded Python-orchestrated closure at n=5, D=3."""
import ctypes, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
for d in ('odd_prime_one_count_20260922', 'odd_prime_alignment_mechanism_20260922', 'odd_prime_local_falls_20260923'):
    sys.path.insert(0, os.path.join(RES, d))
import gf3
from random_conditioning_fast import QSpace, base_rows
def _lib():
    b = os.path.join(RES, '..', 'logs', 'gf3build'); os.makedirs(b, exist_ok=True); so = os.path.join(b, 'libgf3_closure.so')
    src = os.path.join(HERE, 'gf3_closure.c')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
        subprocess.check_call(['gcc', '-O3', '-march=native', '-fopenmp', '-shared', '-fPIC', '-o', so, src])
    L = ctypes.CDLL(so); vp, ci = ctypes.c_void_p, ctypes.c_int
    L.gf3_insert.argtypes = [vp, vp, vp, vp, ci, ci]; L.gf3_insert.restype = ci
    L.gf3_close.argtypes = [vp, vp, vp, vp, vp, ci, vp, ci, ci, ci, ci, ci]; L.gf3_close.restype = ci
    return L
LIB = None
class Space:
    def __init__(self, n, D):
        self.q = QSpace(n, D); q = self.q; self.D, self.v, self.cols = D, q.v, q.cols
        self.W = (q.cols + 63) // 64; self.deg = q.deg.astype(np.int8); self.const = q.idx[()]
        hole = lambda u: u % n
        mul = -np.ones((q.v, q.cols), dtype=np.int32)
        for c, m in enumerate(q.mons):
            if len(m) > D - 1: continue
            hs = {hole(u) for u in m}
            for y in range(q.v):
                if y in m: mul[y, c] = c
                elif hole(y) not in hs: mul[y, c] = q.idx[tuple(sorted(m + (y,)))]
        self.mul = np.ascontiguousarray(mul)
class Closure:
    def __init__(self, sp, threads=12, other=None):
        global LIB
        if LIB is None: LIB = _lib()
        self.sp, self.th = sp, threads
        if other is None:
            self.basis = np.zeros((sp.cols, 2 * sp.W), dtype=np.uint64); self.piv = np.zeros(sp.cols, dtype=np.int32)
            self.proc = np.zeros(sp.cols, dtype=np.uint8); self.rank = ctypes.c_int(0)
        else:
            self.basis, self.piv, self.proc = other.basis.copy(), other.piv.copy(), other.proc.copy()
            self.rank = ctypes.c_int(other.rank.value)
    def copy(self): return Closure(self.sp, self.th, self)
    def add(self, polys):
        if polys:
            P = np.ascontiguousarray(gf3.pack(np.array([self.sp.q.vec(p) for p in polys], dtype=np.uint8))[0], dtype=np.uint64)
            LIB.gf3_insert(self.basis.ctypes.data, ctypes.byref(self.rank), self.piv.ctypes.data, P.ctypes.data, P.shape[0], self.sp.W)
        LIB.gf3_close(self.basis.ctypes.data, ctypes.byref(self.rank), self.piv.ctypes.data, self.proc.ctypes.data,
                      self.sp.deg.ctypes.data, self.sp.D, self.sp.mul.ctypes.data, self.sp.v, self.sp.W, self.sp.cols, 256, self.th)
        return self
    def split(self):
        r = self.rank.value; dg = self.sp.deg[self.piv[:r]]
        return dict(rank=int(r), top=int((dg == self.sp.D).sum()), low=int((dg < self.sp.D).sum()),
                    refuted=bool((self.piv[:r] == self.sp.const).any()))
if __name__ == '__main__':
    import local_falls as old
    from selector_threshold_lib import selector
    sp = Space(5, 3); rng = np.random.default_rng(1); cons = [selector(rng, sp.v) for _ in range(12)]
    for M in (0, 4, 8, 12):
        a = Closure(sp).add(base_rows(5) + cons[:M]).split()
        o = old.Closure(sp.q, 12); o.add(base_rows(5) + cons[:M]); b = o.split()
        assert a == b, (M, a, b)
    print('C closure agrees with the recorded-machinery closure at n=5, D=3, M=0,4,8,12')
