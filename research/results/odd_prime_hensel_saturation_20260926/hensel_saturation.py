"""3-saturation criterion for the Hensel lead (odd-prime thread, 26 Sept 2026).

Tested statement (closed-routes review): for the degree-d lattice L_d of weak PHP^{n+1}_n (Z-span of the
multilinear degree-<=d multiples of rows sum_j x_ij - 1 and collisions x_ij x_i'j), a rational dual functional
with 3-integral values and l(1) = 1 exists iff e_1 (the constant monomial) is not in Sat(L_d) + 3 Z_(3)^N,
where Sat(L_d) = (L_d (x) Q) cap Z_(3)^N. This script computes Sat(L_d) mod 3 by iterated lifting:
S_0 = generator matrix G; S_{t+1} = S_t plus (y~ S_t)/3 for a lifted basis y~ of the F_3 left kernel of S_t;
stop when the F_3 rank reaches the rational rank (estimated as the max rank over the primes 5..37, as in
php_lattice_torsion.py, and checked modulo three word-size primes by FLINT, rank_large.c). Then it reports whether e_1 lies in the F_3 span of the saturation.
Left kernels by FLINT's nmod_mat_nullspace (nullspace_mod.c); products in float64 BLAS (exact: entries < 2^53);
ranks by research/tools/rank_modp.py.
Usage: hensel_saturation.py --cases 4:3,5:3 --out FILE"""
import argparse, hashlib, json, os, struct, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_closed_routes_review_20260926'))
from rank_modp import rank_mod_p
from php_lattice_torsion import lattice_rows, to_sparse

BUILD = os.path.join(HERE, '..', '..', 'tmp', 'hensel_build')
SRC = os.path.join(HERE, 'nullspace_mod.c')
SRC_RANK = os.path.join(HERE, 'rank_large.c')
LARGE_PRIMES = [1000000007, 998244353, 2305843009213693951]


def binary(src=SRC, name='nullspace_'):
    exe = os.path.join(BUILD, name + hashlib.sha256(open(src, 'rb').read()).hexdigest()[:12])
    if not os.path.exists(exe):
        os.makedirs(BUILD, exist_ok=True)
        subprocess.run(['gcc', '-O2', '-o', exe, src, '-lflint', '-lgmp'], check=True)
    return exe


def rank_large(G, p):
    """Rank of the integer matrix G modulo a word-size prime (FLINT), a check on the rational rank."""
    os.makedirs(BUILD, exist_ok=True)
    fi = tempfile.NamedTemporaryFile(dir=BUILD, delete=False)
    assert np.abs(G).max() < 128
    fi.write(struct.pack('<2i', *G.shape)); fi.write(G.astype(np.int8).tobytes()); fi.close()
    r = int(subprocess.run([binary(SRC_RANK, 'rank_large_'), fi.name, str(p)], check=True, capture_output=True, text=True).stdout)
    os.remove(fi.name)
    return r


def left_kernel_mod3(M):
    """Basis (rows) of {y : y M = 0 mod 3}, via the right nullspace of M^T."""
    A = np.ascontiguousarray((M.T % 3).astype(np.uint8))
    os.makedirs(BUILD, exist_ok=True)
    fi = tempfile.NamedTemporaryFile(dir=BUILD, delete=False); fo = fi.name + '.out'
    fi.write(struct.pack('<3i', A.shape[0], A.shape[1], 3)); fi.write(A.tobytes()); fi.close()
    subprocess.run([binary(), fi.name, fo], check=True)
    with open(fo, 'rb') as fh:
        r, nul = struct.unpack('<2i', fh.read(8))
        X = np.frombuffer(fh.read(), dtype=np.uint8).reshape(r, nul)
    os.remove(fi.name); os.remove(fo)
    return X.T.astype(np.float64)


def rank3(M, extra=None):
    rows = [[(j, int(v)) for j, v in zip(np.nonzero(r)[0], r[np.nonzero(r)[0]])] for r in (M % 3).astype(np.int64)]
    if extra is not None:
        rows.append(extra)
    return rank_mod_p(rows, M.shape[1], 3)


def run(n, d, max_iter=4):
    rows, cols = lattice_rows(n, d)
    idx = {m: i for i, m in enumerate(cols)}
    sp = to_sparse(rows, idx)
    G = np.zeros((len(sp), len(cols)), dtype=np.float64)
    for i, r in enumerate(sp):
        for j, c in r:
            G[i, j] += c
    rq = max(rank_mod_p([[(j, c % p) for j, c in r if c % p] for r in sp], len(cols), p) for p in (5, 7, 11, 13, 37))
    assert np.abs(G).max() < 100
    large = {str(p): rank_large(G, p) for p in LARGE_PRIMES}
    one = idx[frozenset()]
    S = G.copy(); hist = []
    for it in range(max_iter + 1):
        r3 = rank3(S)
        hist.append(r3)
        if r3 >= rq or it == max_iter:
            break
        Y = left_kernel_mod3(S)
        P = Y @ S
        assert np.all(np.mod(P, 3) == 0) and np.abs(P).max() < 2 ** 52
        S = np.vstack([S, P / 3])   # exact integers (asserted below 2^52): added rows lie in Sat(L_d)
        assert np.abs(S).max() < 2 ** 52
    lifted_rank_large = rank_large(S, LARGE_PRIMES[0]) if len(hist) > 1 else None  # added rows stay in L (x) Q
    r_e = rank3(S, extra=[(one, 1)])
    return dict(n=n, pigeons=n + 1, d=d, rows=G.shape[0], cols=G.shape[1], rank_Q_estimate=rq, ranks_large_primes=large, lifted_rank_mod_1e9p7=lifted_rank_large, f3_rank_history=hist,
                saturated=(hist[-1] >= rq), e1_in_saturation_mod3=(r_e == hist[-1]),
                integral_certificate_exists=(hist[-1] >= rq and r_e > hist[-1]))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cases', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args(); out = []
    for case in a.cases.split(','):
        n, d = map(int, case.split(':')); t0 = time.time()
        res = run(n, d); res['seconds'] = round(time.time() - t0, 1)
        out.append(res); print(json.dumps(res), flush=True)
        with open(a.out, 'w') as fh:
            json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
