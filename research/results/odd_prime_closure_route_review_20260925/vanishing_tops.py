#!/usr/bin/env python3
"""Vanishing-top modules of column members and their Jordan types (one explicit row, p = 3).

Statement tested (lem:free-vanishing-tops, prop:link-criterion, u = 1). For a set Z of occupancy
patterns in the slice sum(c) = m mod 3 on N holes, the link Z_Y = {c in Z : c_Y = 1} (patterns on the
other holes) has vanishing tops a_{Y,e}: degree-e parts of multilinear polynomials of degree <= e in the
occupancies C_j (j not in Y) vanishing on Z_Y. A_e = sum_Y x_Y a_{Y,e} (|Y| = d - e in total degree d),
inside tV_e = sum_Y x_Y Mon_e(Y^c). The row sum r acts by x_Y g -> sum_{j not in Y} x_{Y+j} g|_{C_j = 0}.
Reported per (member, e, d):
  short_A[d]  = dim ker(r on A_e,d) - rank(r^2: A_e,d-2 -> A_e,d): Jordan strings of length < 3 ending
                at d. A_e is free through t iff short_A[d] = 0 for d <= t-1.
  short_V[d]  = the same for V_e = tV_e / A_e (closed row freeness is short_V = 0, given tV_e free).
  mayer_vs_ordinary: dims of the ordinary cohomology of the signed coboundary
                delta(x_Y g) = sum_j (-1)^{#(Y below j)} x_{Y+j} g|_{C_j=0} on A_e (absurd-bridge test).
All ranks are exact over GF(3) (fflas-ffpack RowRankProfile via ctypes); nullspaces by exact numpy reduction mod 3.
Sizes: N = 10, e <= 2, d <= 4: at most C(10,2)^2 = 2025 basis vectors per degree.
"""
import ctypes, itertools, json, os, subprocess, sys, tempfile
import numpy as np

P = 3


def _load_rrp():
    """Build rrp.cpp (next to this script) into a temporary shared library once, and load it."""
    lib = os.environ.get('RRP_LIB') or os.path.join(tempfile.gettempdir(), 'librrp_gf3_%d.so' % os.getuid())
    if not os.path.exists(lib):
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rrp.cpp')
        flags = subprocess.check_output(['pkg-config', '--cflags', 'fflas-ffpack'], text=True).split()
        subprocess.check_call(['g++', '-O2', '-fPIC', '-shared', src, '-o', lib, *flags,
                               '-lgivaro', '-lgmpxx', '-lgmp', '-lopenblas'])
    return ctypes.CDLL(lib)


LIB = _load_rrp()
LIB.gf3_row_rank_profile.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.POINTER(ctypes.c_float),
                                     ctypes.POINTER(ctypes.c_long)]
LIB.gf3_row_rank_profile.restype = ctypes.c_long


def rank3(M):
    M = np.asarray(M, dtype=np.int64) % P
    if M.size == 0 or M.shape[0] == 0 or M.shape[1] == 0:
        return 0
    A = np.ascontiguousarray(M, dtype=np.float32)
    prof = (ctypes.c_long * max(1, min(A.shape)))()
    return int(LIB.gf3_row_rank_profile(A.shape[0], A.shape[1],
                                        A.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), prof))


def rref3(M):
    A = np.array(M, dtype=np.int64) % P
    r = 0
    piv = []
    for c in range(A.shape[1]):
        nz = np.nonzero(A[r:, c])[0]
        if nz.size == 0:
            continue
        p = r + nz[0]
        A[[r, p]] = A[[p, r]]
        A[r] = (A[r] * (1 if A[r, c] == 1 else 2)) % P
        rows = np.nonzero(A[:, c])[0]
        rows = rows[rows != r]
        A[rows] = (A[rows] - np.outer(A[rows, c], A[r])) % P
        piv.append(c)
        r += 1
        if r == A.shape[0]:
            break
    return A[:r], piv


def nullspace3(M):
    """Basis (rows) of {v : M v = 0} over GF(3)."""
    ncol = M.shape[1]
    R, piv = rref3(M)
    free = [c for c in range(ncol) if c not in piv]
    basis = []
    for f in free:
        v = np.zeros(ncol, dtype=np.int64)
        v[f] = 1
        for i, c in enumerate(piv):
            v[c] = (-R[i, f]) % P
        basis.append(v)
    return np.array(basis, dtype=np.int64).reshape(len(basis), ncol)


def run_member(name, N, m, allowed, e_max, d_max):
    pts = np.array([c for c in itertools.product((0, 1), repeat=N) if sum(c) % P == m % P and allowed(c)],
                   dtype=np.int64)
    info = {'member': name, 'N': N, 'm': m, 'points': int(len(pts)),
            'slice_points': int(sum(1 for c in itertools.product((0, 1), repeat=N) if sum(c) % P == m % P))}
    holes = range(N)
    # a_{Y,e}: for each Y with |Y| <= d_max + 1 - e, basis of vanishing tops (as dict mu -> coeff rows)
    tops = {}
    for e in range(e_max + 1):
        for ysz in range(0, d_max + 2 - e):
            for Y in itertools.combinations(holes, ysz):
                rest = [j for j in holes if j not in Y]
                sel = pts[np.all(pts[:, list(Y)] == 1, axis=1)] if Y else pts
                mons = [mu for k in range(e + 1) for mu in itertools.combinations(rest, k)]
                top_idx = [i for i, mu in enumerate(mons) if len(mu) == e]
                if len(sel) == 0:
                    ker = np.eye(len(mons), dtype=np.int64)
                else:
                    E = np.array([[int(np.all(sel[s, list(mu)] == 1)) if mu else 1 for mu in mons]
                                  for s in range(len(sel))], dtype=np.int64)
                    ker = nullspace3(E)
                T = ker[:, top_idx] if len(ker) else np.zeros((0, len(top_idx)), dtype=np.int64)
                Tb, _ = rref3(T) if len(T) else (T, [])
                tops[(e, Y)] = ([mons[i] for i in top_idx], Tb)
    res = []
    for e in range(e_max + 1):
        # coordinates of tV_e in total degree d: pairs (Y, mu), |Y| = d - e, mu an e-set disjoint from Y
        def coords(d):
            out = []
            for Y in itertools.combinations(holes, d - e):
                for mu in itertools.combinations([j for j in holes if j not in Y], e):
                    out.append((Y, mu))
            return out, {c: i for i, c in enumerate(out)}
        C = {d: coords(d) for d in range(e, d_max + 2)}

        def basisA(d):
            idx = C[d][1]
            rows = []
            for Y in itertools.combinations(holes, d - e):
                mus, Tb = tops[(e, Y)]
                for t in Tb:
                    v = np.zeros(len(idx), dtype=np.int64)
                    for mu, cf in zip(mus, t):
                        if cf:
                            v[idx[(Y, mu)]] = cf
                    rows.append(v)
            return np.array(rows, dtype=np.int64).reshape(len(rows), len(idx))

        def rmat(d, signed=False):
            src, sidx = C[d]
            tgt, tidx = C[d + 1]
            R = np.zeros((len(src), len(tgt)), dtype=np.int64)
            for (Y, mu), i in sidx.items():
                for j in holes:
                    if j in Y or j in mu:
                        continue
                    Y2 = tuple(sorted(Y + (j,)))
                    sgn = (-1) ** sum(1 for y in Y if y < j) if signed else 1
                    R[i, tidx[(Y2, mu)]] = (R[i, tidx[(Y2, mu)]] + sgn) % P
            return R
        B = {d: basisA(d) for d in range(e, d_max + 2)}
        Rm = {d: rmat(d) for d in range(e, d_max + 1)}
        Sm = {d: rmat(d, True) for d in range(e, d_max + 1)}
        dimA = {d: int(len(B[d])) for d in B}
        dimV = {d: len(C[d][0]) for d in C}
        rA = {d: rank3(B[d] @ Rm[d]) for d in range(e, d_max + 1)}
        r2A = {d: rank3(B[d] @ Rm[d] @ Rm[d + 1]) for d in range(e, d_max)}
        # ranks on tV and on V = tV/A: rank(r on V_d) = rank([B_{d+1}; image]) - dimA_{d+1}
        rV = {}
        r2V = {}
        for d in range(e, d_max + 1):
            I = np.eye(dimV[d], dtype=np.int64) @ Rm[d]
            rV[d] = rank3(np.vstack([B[d + 1], I])) - rank3(B[d + 1])
        for d in range(e, d_max):
            I = Rm[d] @ Rm[d + 1]
            rV2 = rank3(np.vstack([B[d + 2], I])) if d + 2 in B else rank3(I)
            r2V[d] = rV2 - (rank3(B[d + 2]) if d + 2 in B else 0)
        shortA, shortV, ordA = {}, {}, {}
        for d in range(e, d_max + 1):
            kerA = dimA[d] - rA[d]
            imA = r2A.get(d - 2, 0)
            shortA[d] = kerA - imA
            dV = dimV[d] - rank3(B[d])
            kerV = dV - rV[d]
            shortV[d] = kerV - r2V.get(d - 2, 0)
            sA = rank3(B[d] @ Sm[d])
            sprev = rank3(B[d - 1] @ Sm[d - 1]) if d - 1 >= e else 0
            ordA[d] = dimA[d] - sA - sprev
        res.append({'e': e, 'dimA': dimA, 'short_A': shortA, 'short_V': shortV,
                    'ordinary_H_A': ordA})
    info['by_e'] = res
    return info


def main():
    N, m = 10, 11
    rng = np.random.default_rng(20260925)
    phi = rng.integers(0, 3, size=(4, N))       # four dense column forms

    def form(c, b):
        return int(np.dot(phi[b], c) % 3)

    def clause(c, i, S, consts):   # normalized W clause chi_{a_i}(l_i) prod (l_j - a_j): nonzero = forbidden
        return form(c, i) == consts[i] and all(form(c, j) != consts[j] for j in S)
    members = [
        ('slice', lambda c: True),
        ('low-weight (at most 2 occupied)', lambda c: sum(c) <= 2),
        ('one clause, k=1', lambda c: not clause(c, 0, [1], {0: 0, 1: 0})),
        ('two-block pair, k=1, i=i\'', lambda c: not clause(c, 0, [1], {0: 0, 1: 0})
         and not clause(c, 0, [1], {0: 1, 1: 1})),
        ('three clauses on four forms', lambda c: not clause(c, 0, [1], {0: 0, 1: 0})
         and not clause(c, 2, [3], {2: 1, 3: 2}) and not clause(c, 1, [2], {1: 2, 2: 0})),
    ]
    out = []
    path = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    for name, allowed in members:
        info = run_member(name, N, m, allowed, e_max=2, d_max=4)
        print(json.dumps(info), flush=True)
        out.append(info)
        if path:
            json.dump({'phi': phi.tolist(), 'members': out}, open(path, 'w'), indent=1)


if __name__ == '__main__':
    main()
