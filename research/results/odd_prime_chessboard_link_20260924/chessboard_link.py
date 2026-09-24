"""Check of the chessboard link for the row sums on the weak algebra without row sums, over F_3.

Tested statements. A = F_3[x_bj]/(x_bj x_b'j) on d rows and N columns, r_b = sum_j x_bj, content c in N^d.
(P1) Multilinear strand: for c = (1^k), dim H_i(r; A)_c = dim H~^{k-i-1}(Delta_{k,N}; F_3) for every i, where
     Delta_{k,N} is the k x N chessboard complex, computed separately with standard simplicial signs.
(P2) Light contents (every c_b <= 2 < p): H_i(r; A)_c = 0 for i >= 1 when N >= 2|c| - 1, and in all cases
     dim H_i(r; A)_c <= dim H_i(r; A)_{(1^k)} (the retract), k = |c|.
Koszul differential: e_U x_P -> sum_l (-1)^l e_{U - u_l} r_{u_l} x_P (U sorted, l from 0). Exact ranks mod 3.
Usage: python3 chessboard_link.py OUT.json"""
import itertools, json, sys, time
import numpy as np
p = 3

def rank_mod3(M):
    M = (M % p).astype(np.int8); r = 0; rows, cols = M.shape
    for c in range(cols):
        if r == rows: break
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0: continue
        piv = r + nz[0]
        if piv != r: M[[r, piv]] = M[[piv, r]]
        if M[r, c] == 2: M[r] = (M[r] * 2) % p
        below = np.nonzero(M[:, c])[0]; below = below[below != r]
        if len(below): M[below] = (M[below] - np.outer(M[below, c], M[r])) % p
        r += 1
    return r

def placements(N, c):
    """Column-injective placements with row content c, as sorted tuples of (column, row)."""
    rows = [b for b, cb in enumerate(c) for _ in range(cb)]
    out = set()
    for cols in itertools.permutations(range(N), len(rows)):
        out.add(tuple(sorted(zip(cols, rows))))
    return sorted(out)

def koszul_terms(N, c):
    d = len(c); terms = {}
    for i in range(d + 1):
        B = []
        for U in itertools.combinations(range(d), i):
            cc = list(c)
            for u in U: cc[u] -= 1
            if min(cc) < 0: continue
            B += [(U, P) for P in placements(N, tuple(cc))]
        terms[i] = B
    return terms

def koszul_diff(N, src, dst):
    idx = {b: n for n, b in enumerate(dst)}
    M = np.zeros((len(src), len(dst)), dtype=np.int64)
    for s, (U, P) in enumerate(src):
        used = {j for j, _ in P}
        for l, u in enumerate(U):
            V = U[:l] + U[l + 1:]
            for j in range(N):
                if j in used: continue
                M[s, idx[(V, tuple(sorted(P + ((j, u),))))]] += (-1) ** l
    return M

def koszul_homology(N, c):
    T = koszul_terms(N, c); d = len(c)
    rk = {i: (rank_mod3(koszul_diff(N, T[i], T[i - 1])) if T[i] and T[i - 1] else 0) for i in range(1, d + 1)}
    rk[0] = 0; rk[d + 1] = 0
    return {i: len(T[i]) - rk[i] - rk[i + 1] for i in range(d + 1)}

def chessboard_cohomology(k, N):
    """Reduced (co)homology dimensions over F_3 of Delta_{k,N}, by degree q = -1..k-1."""
    faces = {q: [] for q in range(-1, k)}
    for s in range(k + 1):
        for R in itertools.combinations(range(k), s):
            for cols in itertools.permutations(range(N), s):
                faces[s - 1].append(tuple(zip(R, cols)))
    rk = {}
    for q in range(0, k):
        idx = {f: n for n, f in enumerate(faces[q - 1])}
        M = np.zeros((len(faces[q]), len(faces[q - 1])), dtype=np.int64)
        for a, f in enumerate(faces[q]):
            for pos in range(len(f)):
                M[a, idx[f[:pos] + f[pos + 1:]]] += (-1) ** pos
        rk[q] = rank_mod3(M) if len(faces[q]) and len(faces[q - 1]) else 0
    rk[-1] = 0; rk[k] = 0
    return {q: len(faces[q]) - rk[q] - rk[q + 1] for q in range(-1, k)}

def main():
    out = {'p1': [], 'p2': [], 'failures': []}; t0 = time.time()
    for k in range(1, 5):
        for N in range(k, 8):
            if k == 4 and N > 7: continue
            kh = koszul_homology(N, (1,) * k); ch = chessboard_cohomology(k, N)
            row = {'k': k, 'N': N, 'koszul_H': kh, 'chessboard_H': {str(q): v for q, v in ch.items()}}
            for i in range(k + 1):
                if kh[i] != ch[k - i - 1]: out['failures'].append(('P1', k, N, i))
            out['p1'].append(row); print('P1', k, N, kh, flush=True)
    multi = {(r['k'], r['N']): r['koszul_H'] for r in out['p1']}
    lights = sorted({tuple(sorted(x, reverse=True)) for n in range(1, 5) for x in itertools.product((1, 2), repeat=n)
                     if sum(x) <= 4 and 2 in x})
    for c in lights:
        k = sum(c)
        for N in range(max(k, 2), 8):
            kh = koszul_homology(N, c)
            ok_zero = N < 2 * k - 1 or all(kh[i] == 0 for i in range(1, len(c) + 1))
            ok_retract = all(kh[i] <= multi[(k, N)][i] for i in range(1, len(c) + 1))
            if not (ok_zero and ok_retract): out['failures'].append(('P2', c, N))
            out['p2'].append({'c': c, 'N': N, 'koszul_H': kh}); print('P2', c, N, kh, flush=True)
    out['seconds'] = round(time.time() - t0, 2)
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
    print('failures', out['failures'], 'seconds', out['seconds'])

if __name__ == '__main__':
    main()
