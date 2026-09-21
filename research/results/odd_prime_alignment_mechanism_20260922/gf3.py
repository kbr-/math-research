"""ctypes wrapper for gf3.c (bit-sliced GF(3) elimination). Builds a parallel (OpenMP) and a
serial library into research/logs/gf3build/ on first use. Run this file to self-test against
exhaustive addition cases and the NumPy reference implementation."""
import ctypes, os, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, '..', '..', 'logs', 'gf3build')
def _lib(parallel):
    os.makedirs(BUILD, exist_ok=True)
    so = os.path.join(BUILD, 'libgf3_par.so' if parallel else 'libgf3_ser.so')
    src = os.path.join(HERE, 'gf3.c')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
        flags = ['-fopenmp'] if parallel else []
        subprocess.check_call(['gcc', '-O3', '-march=native', *flags, '-shared', '-fPIC', '-o', so, src])
    L = ctypes.CDLL(so)
    L.gf3_rref.restype = ctypes.c_int
    L.gf3_rref.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
    return L
_L = {}
def lib(parallel=False):
    if parallel not in _L: _L[parallel] = _lib(parallel)
    return _L[parallel]

def pack(M):
    """uint8 matrix (values 0..2) -> (rows, 2W) uint64 bit-planes."""
    M = np.asarray(M, dtype=np.uint8) % 3
    rows, cols = M.shape; W = (cols + 63) // 64
    out = np.zeros((rows, 2, W * 8), dtype=np.uint8)
    for plane, val in ((0, 1), (1, 2)):
        bits = np.packbits((M == val), axis=1, bitorder='little')
        out[:, plane, :bits.shape[1]] = bits
    return out.view(np.uint64).reshape(rows, 2 * W), W

def unpack(P, W, cols):
    B = P.reshape(P.shape[0], 2, W).view(np.uint8)
    a = np.unpackbits(B[:, 0, :], axis=1, bitorder='little')[:, :cols]
    b = np.unpackbits(B[:, 1, :], axis=1, bitorder='little')[:, :cols]
    return (a + 2 * b).astype(np.uint8)

def rref(M, full=False, parallel=False, packed=None):
    """Returns (echelon rows as packed uint64, W, pivots)."""
    if packed is None: P, W = pack(M); cols = M.shape[1]
    else: P, W, cols = packed
    P = np.ascontiguousarray(P); piv = np.zeros(max(1, P.shape[0]), dtype=np.int32)
    r = lib(parallel).gf3_rref(P.ctypes.data, P.shape[0], W, cols, int(full), piv.ctypes.data)
    return P[:r].copy(), W, piv[:r].copy()

def rank(M, parallel=False):
    if M.shape[0] == 0: return 0
    return rref(M, parallel=parallel)[2].shape[0]

if __name__ == '__main__':
    import itertools, sys
    sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_kernel_alignment_20260921'))
    import alignment as A
    for v, w in itertools.product(range(3), repeat=2):          # addition and scaling, all cases
        M = np.array([[1, v], [1, w]], dtype=np.uint8)           # row2 - row1 -> w - v
        E, W, piv = rref(M, full=True)
        U = unpack(E, W, 2)
        exp = A.rref3(M)
        assert rank(M) == exp.shape[0], (v, w)
    rng = np.random.default_rng(1)
    for trial in range(60):
        r, c = int(rng.integers(1, 300)), int(rng.integers(1, 300))
        M = rng.integers(0, 3, size=(r, c)).astype(np.uint8)
        if trial % 3 == 0: M[:, rng.integers(0, c, size=c // 2)] = 0
        if trial % 3 == 1: M[r // 2:] = (M[:r - r // 2] * 2) % 3 if r > 1 else M[r // 2:]
        E, W, piv = rref(M, full=True, parallel=trial % 2 == 0)
        U = unpack(E, W, c)
        assert len(piv) == A.rref3(M).shape[0]
        assert all(U[i, p] == 1 and (U[:, p] != 0).sum() == 1 for i, p in enumerate(piv))
        # row space equality: stacking must not raise the rank
        assert A.rref3(np.vstack([M, U])).shape[0] == len(piv)
    print('gf3 self-test passed')
