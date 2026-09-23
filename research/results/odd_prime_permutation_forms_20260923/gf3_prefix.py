"""ctypes wrapper for gf3_prefix.c: prefix ranks of a block-structured GF(3) matrix in one elimination.
Self-test: python3 gf3_prefix.py compares with the recorded gf3.rref on random blocks."""
import ctypes, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, '..', '..', 'logs', 'gf3build')
def _lib():
    os.makedirs(BUILD, exist_ok=True); so = os.path.join(BUILD, 'libgf3_prefix.so'); src = os.path.join(HERE, 'gf3_prefix.c')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
        subprocess.check_call(['gcc', '-O3', '-march=native', '-fopenmp', '-shared', '-fPIC', '-o', so, src])
    L = ctypes.CDLL(so); L.gf3_prefix_ranks.restype = ctypes.c_int
    vp, ci = ctypes.c_void_p, ctypes.c_int
    L.gf3_prefix_ranks.argtypes = [vp, ci, ci, ci, vp, ci, vp, vp, vp, ci]; return L
def prefix_ranks(P, W, cols, block_end, threads=12):
    """P: packed (rows, 2W) uint64 (modified in place); block_end: increasing row counts. Returns ranks per block."""
    P = np.ascontiguousarray(P, dtype=np.uint64); rows = P.shape[0]
    basis = np.zeros((min(rows, cols), 2 * W), dtype=np.uint64); piv = np.zeros(min(rows, cols), dtype=np.int32)
    be = np.array(block_end, dtype=np.int32); ranks = np.zeros(len(be), dtype=np.int32)
    _lib().gf3_prefix_ranks(P.ctypes.data, rows, W, cols, be.ctypes.data, len(be), basis.ctypes.data, piv.ctypes.data,
                            ranks.ctypes.data, threads)
    return ranks.tolist()
if __name__ == '__main__':
    sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_alignment_mechanism_20260922')); import gf3
    rng = np.random.default_rng(1)
    for trial in range(20):
        cols = int(rng.integers(5, 200)); nb = int(rng.integers(1, 6)); sizes = rng.integers(1, 40, size=nb)
        A = rng.integers(0, 3, size=(int(sizes.sum()), cols)).astype(np.uint8)
        if trial % 3 == 0: A[:, ::2] = 0                                   # rank-deficient cases
        Pk, W = gf3.pack(A)[:2]; ends = np.cumsum(sizes).tolist()
        got = prefix_ranks(Pk.copy(), W, cols, ends)
        want = [gf3.rank(np.ascontiguousarray(A[:e])) for e in ends]
        assert got == want, (trial, got, want)
    print('prefix ranks agree with gf3.rank on 20 random block matrices')
