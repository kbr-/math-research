"""Content-graded Tor over u(W) = F_3[R_1..R_d]/(R_b^3) of the weak algebra without row sums.

Tested statement (thm:tensor-power-freeness): for every content c, i >= 1 and N >= 2|c| - i,
Tor_i^{u(W)}(F_3, A~)_c = 0, where A~ = F_3[x_bj]/(x_bj x_b'j) on d = len(c) rows and N columns, u(W)
acting through the row sums. Tor is computed from the minimal resolution of F_3 over u(W): the tensor
product of the periodic resolutions u <-r- u(-1) <-r^2- u(-3) <-r- u(-4) ..., generator g_n in degree
delta(n) = n + floor(n/2) per row, differential sum_b (-1)^{n_1+..+n_{b-1}} r_b^{1 if n_b odd else 2}.
C_i(c) = (+)_{sum n = i} A~_{c - sum delta(n_b) e_b}; dim Tor_i = dim C_i - rank d_i - rank d_{i+1}.
Validation: d = 1 against the graded Clebsch-Gordan decomposition of J_2^{(x)N}; content (1,1,1)
against the chessboard values of check.json in odd_prime_chessboard_link_20260924.
Ranks: research/tools/rank_modp.cpp (OpenMP). Usage: python3 tor_contents.py OUT.json"""
import itertools, json, sys, time
sys.path.insert(0, 'research/tools')
from rank_modp import rank_mod_p

def delta(n): return n + n // 2

def placements(N, c):
    """Placements of content c into N columns, as tuples (row or -1 per column), generated directly."""
    if min(c) < 0 or sum(c) > N: return []
    out = []
    def rec(b, free, cur):
        if b == len(c): out.append(tuple(cur)); return
        for S in itertools.combinations(free, c[b]):
            for j in S: cur[j] = b
            rec(b + 1, [j for j in free if j not in S], cur)
            for j in S: cur[j] = -1
    rec(0, list(range(N)), [-1] * N)
    return sorted(out)

def apply_r(vec, b, N):
    out = {}
    for P, v in vec.items():
        for j in range(N):
            if P[j] == -1:
                Q = P[:j] + (b,) + P[j + 1:]; out[Q] = (out.get(Q, 0) + v) % 3
    return {k: v for k, v in out.items() if v}

def terms(N, c, i):
    d = len(c); out = []
    for n in itertools.product(range(i + 1), repeat=d):
        if sum(n) != i: continue
        cc = tuple(c[b] - delta(n[b]) for b in range(d))
        if min(cc) < 0: continue
        out += [(n, P) for P in placements(N, cc)]
    return out

def diff_rows(N, c, i):
    src = terms(N, c, i); dst = terms(N, c, i - 1)
    idx = {t: k for k, t in enumerate(dst)}; rows = []
    for n, P in src:
        row = {}; sgn = 1
        for b in range(len(c)):
            if n[b] > 0:
                vec = {P: 1}
                for _ in range(1 if n[b] % 2 else 2): vec = apply_r(vec, b, N)
                m = n[:b] + (n[b] - 1,) + n[b + 1:]
                for Q, v in vec.items():
                    k = idx[(m, Q)]; row[k] = (row.get(k, 0) + sgn * v) % 3
            if n[b] % 2: sgn = -sgn
        rows.append({k: v for k, v in row.items() if v})
    return rows, len(src), len(dst)

def tor_dims(N, c, imax):
    """dim Tor_i at content c for i = 1..imax, one rank per differential d_1..d_{imax+1}."""
    rk = {}; dim = {}
    for k in range(1, imax + 2):
        rows, nsrc, ndst = diff_rows(N, c, k)
        rk[k] = rank_mod_p(rows, ndst, 3); dim[k] = nsrc
    return {i: dim[i] - rk[i] - rk[i + 1] for i in range(1, imax + 1)}

def cg_prediction(N, h, i):
    """dim Tor_i(J_2^{(x)N}) in degree h over F_3[r]/(r^3), from the graded Clebsch-Gordan rule."""
    if N % 2 == 0: return 1 if h == N // 2 + (3 * i) // 2 else 0
    return 1 if h == (N - 1) // 2 + (3 * i + 1) // 2 else 0

def main():
    out = {'validation': [], 'tests': [], 'failures': []}; t0 = time.time()
    for N in range(1, 8):
        for h in range(0, N + 1):
            dims = tor_dims(N, (h,), 3)
            for i in (1, 2, 3):
                got = dims[i]; want = cg_prediction(N, h, i)
                out['validation'].append({'kind': 'd=1', 'N': N, 'c': [h], 'i': i, 'tor': got, 'want': want})
                if got != want: out['failures'].append(('CG', N, h, i, got, want))
    chess = {(r['k'], r['N']): r['koszul_H'] for r in
             json.load(open('research/results/odd_prime_chessboard_link_20260924/check.json'))['p1']}
    for N in (3, 4, 5):
        dims = tor_dims(N, (1, 1, 1), 2)
        for i in (1, 2):
            got = dims[i]; want = chess[(3, N)][str(i)]
            out['validation'].append({'kind': 'multilinear', 'N': N, 'c': [1, 1, 1], 'i': i, 'tor': got, 'want': want})
            if got != want: out['failures'].append(('chess', N, i, got, want))
    print('validation done', len(out['failures']), 'failures', round(time.time() - t0, 1), 's', flush=True)
    cases = [((3, 1), range(4, 9)), ((3, 2), range(5, 10)), ((4, 1), range(5, 10)), ((3, 1, 1), range(5, 10)),
             ((3, 3), range(7, 12))]
    for c, Ns in cases:
        for N in Ns:
            t1 = time.time(); dims = tor_dims(N, c, 3); sec = round(time.time() - t1, 2)
            for i in (1, 2, 3):
                got = dims[i]; claim = N >= 2 * sum(c) - i
                rec = {'c': list(c), 'N': N, 'i': i, 'tor': got, 'claimed_zero': claim, 'seconds_all_i': sec}
                out['tests'].append(rec); print(json.dumps(rec), flush=True)
                if claim and got: out['failures'].append(('T', c, N, i, got))
    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
    print('failures', out['failures'], 'seconds', out['seconds'])

if __name__ == '__main__':
    main()
