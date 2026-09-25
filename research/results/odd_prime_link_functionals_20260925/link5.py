"""Single-clause degree-5 detection by link functionals (width-1 heptad clause), functional board.

Statement tested (single-clause local condition L5): for a heptad clause C (U = S u T, 4 + 3 cells on 7 rows, labels
4..10, tau = l_S^2 l_T), the contractions D_tau Omega of the link functionals Omega = omega_A (x) w (A a pattern: two
cells of S, one of T; omega_A = tensor_{x in A} (e_{label x} - e_{z_x}) with spares z from a set Z of non-U labels;
w a zero-marginal array on a row pair disjoint from rows(A), supported on labels outside labels(A) u Z) span
Ann(K_C) in K_2 = G_2^*, where K_C = l_S G_1 + F l_T^2 is the Taylor kernel.  The problem splits into independent
pieces: a far row pair (both rows outside rows(U)), an outside-row slice (row pairs (rho, r), rho in rows(U), r
outside), and the inside block (row pairs within rows(U)).  For each piece: undetected dimension
dim G_2(piece) - rank(functionals) must equal dim of K_C's component in the piece.
G_2 on a row pair: pairs (c, c') of distinct labels < L modulo their total sum (one relation q_rs).
Usage: python3 link5.py OUT.json N1 N2 ..."""
import itertools, json, os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_permutation_forms_20260923'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'odd_prime_alignment_mechanism_20260922'))
import gf3, gf3_prefix

def rank_mod3(rows, ncols):
    """GF(3) rank of a list of numpy vectors, by the compiled prefix-rank kernel (one block)."""
    if not rows:
        return 0
    M = np.zeros((len(rows), ncols), dtype=np.uint8)
    for i, v in enumerate(rows):
        M[i] = (v % 3).astype(np.uint8)
    Pk, W = gf3.pack(M)
    return gf3_prefix.prefix_ranks(Pk, W, ncols, [len(rows)])[0]

def run(N):
    L = N - 1                      # y-labels 0..L-1, label L eliminated
    Ulab = list(range(4, 11))       # 7 labels of the support
    assert L - 1 >= 10
    # rows: U on rows 0..6 (cell i: row i, label Ulab[i]); S = cells 0..3, T = cells 4..6
    S = [0, 1, 2, 3]; T = [4, 5, 6]
    lab = {i: Ulab[i] for i in range(7)}
    pats = [(a, b, c) for a, b in itertools.combinations(S, 2) for c in T]
    nonU = [c for c in range(N) if c not in Ulab]
    Zsets = list(itertools.combinations(nonU[:6], 3))   # every two of the first six non-U labels are avoided by some Z
    rng = np.random.default_rng(N)
    pairs_lab = [(c, d) for c in range(L) for d in range(L) if c != d]   # G_2 coordinates on one row pair
    pidx = {p: i for i, p in enumerate(pairs_lab)}
    P = len(pairs_lab)

    budget = {}
    def four_cycles(allowed, key):
        """All 4-cycles on the allowed labels, or a random sample of budget[key] of them."""
        al = sorted(allowed); m = len(al)
        total = (m * (m - 1) // 2) * ((m - 2) * (m - 3) // 2)
        k = budget.get(key)
        if k is None or total <= k:
            for c, d in itertools.combinations(al, 2):
                for c2, d2 in itertools.combinations(al, 2):
                    if len({c, d, c2, d2}) == 4:
                        yield (c, d, c2, d2)
        else:
            for _ in range(k):
                q = rng.choice(al, size=4, replace=False)
                yield tuple(int(t) for t in q)

    def warr(cyc):  # w = (e_c - e_d) (x) (e_c2 - e_d2) as dict {(label_row1, label_row2): value}
        c, d, c2, d2 = cyc
        return {(c, c2): 1, (c, d2): -1, (d, c2): -1, (d, d2): 1}

    npat, nZ = len(pats), len(Zsets)
    budget["far"] = max(4, 9 * P // (npat * nZ))
    budget["slice"] = max(4, 9 * 7 * P // (npat * nZ * 4))
    budget["inside"] = max(4, 9 * 21 * P // (npat * nZ * 6))
    def blocks(cells):
        """True if every pattern A conflicts (shares a row or a label) with one of the given cells."""
        for A in pats:
            ok = True
            for (rw, lb) in cells:
                if any(rw == x or lb == lab[x] for x in A):
                    ok = False; break
            if ok:
                return False
        return True
    out = {}
    # ---------- piece 1: far row pair (r, s outside rows(U)) ----------
    vecs = []
    for A in pats:
        for Z in Zsets:
            allowed = [c for c in range(N) if c not in {lab[x] for x in A} and c not in Z]
            for cyc in four_cycles(allowed, 'far'):
                v = np.zeros(P, dtype=np.int64)
                for (c, c2), val in warr(cyc).items():
                    if c < L and c2 < L:
                        v[pidx[(c, c2)]] += 2 * val
                vecs.append(v)
    rk = rank_mod3(vecs, P)
    out['far'] = dict(dimG2=P - 1, rank=rk, undetected=P - 1 - rk, taylor=0)
    # ---------- piece 2: outside-row slice; coordinates (rho, pair) for rho in rows 0..6, r outside ----------
    ncol = 7 * P
    def col(rho, c_rho, c_r):
        return rho * P + pidx[(c_rho, c_r)]
    vecs = []
    for A in pats:
        rowsA = set(A)
        for Z in Zsets:
            zmap = {x: Z[k] for k, x in enumerate(A)}
            allowed = [c for c in range(N) if c not in {lab[x] for x in A} and c not in Z]
            for rho in range(7):
                if rho in rowsA:
                    continue
                for cyc in four_cycles(allowed, 'slice'):
                    w = warr(cyc)          # first index: label on row rho, second: label on row r
                    v = np.zeros(ncol, dtype=np.int64)
                    for (c, c2), val in w.items():
                        if c < L and c2 < L:
                            v[col(rho, c, c2)] += 2 * val
                    # corrections: x = U-cell on row rho, A'' = A - a_j + x a pattern
                    x = rho
                    for aj in A:
                        A2 = tuple(sorted([y for y in A if y != aj] + [x]))
                        if A2 not in pats:
                            continue
                        for (c, c2), val in w.items():
                            if c != lab[x] or c2 >= L:
                                continue
                            # tuple: row aj carries p (label lab[aj] -> +1, zmap[aj] -> -1), row r carries c2
                            for plab, sgn in ((lab[aj], 1), (zmap[aj], -1)):
                                if plab < L and plab != c2:
                                    v[col(aj, plab, c2)] += 2 * sgn * val
                    vecs.append(v)
    rk = rank_mod3(vecs, ncol)
    # Taylor part: l_S y_v for v = (r, c), c < L: sum_{a in S} y_a y_v, a on row a with label lab[a]
    tay = []
    for c in range(L):
        v = np.zeros(ncol, dtype=np.int64)
        for a in S:
            if c != lab[a]:
                v[col(a, lab[a], c)] += 1
        tay.append(v)
    # rank of Taylor part in G_2(slice) = rank of [tay; relations] - rank(relations)
    rel = []
    for rho in range(7):
        v = np.zeros(ncol, dtype=np.int64); v[rho * P:(rho + 1) * P] = 1; rel.append(v)
    tr = rank_mod3(rel + tay, ncol) - 7
    blk = []
    for rho in range(7):
        for (c, c2) in pairs_lab:
            if blocks([(rho, c), (99, c2)]):
                v = np.zeros(ncol, dtype=np.int64); v[col(rho, c, c2)] = 1; blk.append(v)
    tb = rank_mod3(rel + tay + blk, ncol) - 7
    out['slice_blocking'] = dict(count=len(blk), taylor_plus_blocking=tb)
    out['slice'] = dict(dimG2=7 * (P - 1), rank=rk, undetected=7 * (P - 1) - rk, taylor=tr)
    # ---------- piece 3: inside block; row pairs (i < j) within rows 0..6 ----------
    rp = list(itertools.combinations(range(7), 2)); rpi = {p: k for k, p in enumerate(rp)}
    ncol = len(rp) * P
    def colin(i, ci, j, cj):
        if i > j:
            i, j, ci, cj = j, i, cj, ci
        return rpi[(i, j)] * P + pidx[(ci, cj)]
    vecs = []
    for A in pats:
        rowsA = set(A)
        for Z in Zsets:
            zmap = {x: Z[k] for k, x in enumerate(A)}
            allowed = [c for c in range(N) if c not in {lab[x] for x in A} and c not in Z]
            others = [r for r in range(7) if r not in rowsA]
            for rho, rho2 in itertools.combinations(others, 2):
                for cyc in four_cycles(allowed, 'inside'):
                    w = warr(cyc)   # (label on rho, label on rho2)
                    v = np.zeros(ncol, dtype=np.int64)
                    for (c, c2), val in w.items():
                        if c < L and c2 < L:
                            v[colin(rho, c, rho2, c2)] += 2 * val
                    for (c, c2), val in w.items():
                        # one U-cell seen: x on rho (c == lab[rho]) or x on rho2 (c2 == lab[rho2])
                        for x, other_row, other_lab, is_first in ((rho, rho2, c2, True), (rho2, rho, c, False)):
                            xl = c if is_first else c2
                            if xl != lab[x] or other_lab >= L:
                                continue
                            for aj in A:
                                A2 = tuple(sorted([y for y in A if y != aj] + [x]))
                                if A2 not in pats:
                                    continue
                                for plab, sgn in ((lab[aj], 1), (zmap[aj], -1)):
                                    if plab < L and plab != other_lab:
                                        v[colin(aj, plab, other_row, other_lab)] += 2 * sgn * val
                        # two U-cells seen: c == lab[rho] and c2 == lab[rho2]
                        if c == lab[rho] and c2 == lab[rho2]:
                            for aj, ak in itertools.combinations(A, 2):
                                A2 = tuple(sorted([y for y in A if y not in (aj, ak)] + [rho, rho2]))
                                if A2 not in pats:
                                    continue
                                for pl, s1 in ((lab[aj], 1), (zmap[aj], -1)):
                                    for ql, s2 in ((lab[ak], 1), (zmap[ak], -1)):
                                        if pl < L and ql < L and pl != ql:
                                            v[colin(aj, pl, ak, ql)] += 2 * s1 * s2 * val
                    vecs.append(v)
    rk = rank_mod3(vecs, ncol)
    tay = []
    for v_row in range(7):
        for c in range(L):
            if c == lab[v_row]:
                continue
            v = np.zeros(ncol, dtype=np.int64)
            for a in S:
                if a != v_row and c != lab[a]:
                    v[colin(a, lab[a], v_row, c)] += 1
            tay.append(v)
    v = np.zeros(ncol, dtype=np.int64)
    for t1, t2 in itertools.combinations(T, 2):
        v[colin(t1, lab[t1], t2, lab[t2])] += 2
    tay.append(v)
    rel = []
    for k in range(len(rp)):
        v = np.zeros(ncol, dtype=np.int64); v[k * P:(k + 1) * P] = 1; rel.append(v)
    tr = rank_mod3(rel + tay, ncol) - len(rp)
    blk = []
    for (i, j) in rp:
        for (c, c2) in pairs_lab:
            if blocks([(i, c), (j, c2)]):
                v = np.zeros(ncol, dtype=np.int64); v[colin(i, c, j, c2)] = 1; blk.append(v)
    tb = rank_mod3(rel + tay + blk, ncol) - len(rp)
    out['inside_blocking'] = dict(count=len(blk), taylor_plus_blocking=tb)
    out['inside'] = dict(dimG2=len(rp) * (P - 1), rank=rk, undetected=len(rp) * (P - 1) - rk, taylor=tr)
    out['N'] = N
    ok = all(out[k]['undetected'] == out[k]['taylor'] for k in ('far', 'slice', 'inside'))
    out['matches_taylor_plus_blocking'] = (out['slice']['undetected'] == out['slice_blocking']['taylor_plus_blocking'] and out['inside']['undetected'] == out['inside_blocking']['taylor_plus_blocking'])
    out['L5_holds'] = ok
    return out

res = []
for N in map(int, sys.argv[2:]):
    r = run(N); res.append(r); print(json.dumps(r), flush=True)
json.dump(res, open(sys.argv[1], 'w'), indent=1)
