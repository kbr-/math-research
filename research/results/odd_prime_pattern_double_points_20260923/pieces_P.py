"""Row Horace pieces on the pattern algebra P (lex degenerate functional top algebra, faces of size <= 3 by
thm:initial-complex-patterns): board R = n+1 rows, L = n-1 labels, faces = matchings avoiding {(r,0),(s,1)} (r<s) and,
on rows a<b<c, the label patterns (0,2,3),(1,0,2),(1,2,0),(1,2,3); faces multiply to their union.
Split off the last row R-1.  For forms l = l' + l_last (l' zero on the last row), with ranks by the compiled prefix kernel:
  full     : rank of (u_j) -> sum l_j^2 u_j, (+)P_1 -> P_3             expected min(g3, M(g1-1))
  trace    : same on P' (faces avoiding the last row), forms l'          expected min(g3', M(g1'-1))
  residual : (v_j) -> sum l_j'^2 v_j, v_j in the last row's cells          expected min(g3 - g3', M*L)
  coupling = full - trace - residual (coupling-dual lemma, part 1)
Families for the last-row part: uniform, and single cell y_{last, j mod L}.  Forms nonconstant on every row asserted.
Usage: python3 pieces_P.py --n 6 --Mmax 57 --seed S --out OUT.json   (or --R R --L L, --Mmax 0 = ceil(capacity)+1)"""
import argparse, itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_alignment_mechanism_20260922')); sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923'))
import gf3
from gf3_prefix import prefix_ranks
PAT3 = {(0, 2, 3), (1, 0, 2), (1, 2, 0), (1, 2, 3)}
def faces(R, L, t):
    out = []
    for rows in itertools.combinations(range(R), t):
        for labs in itertools.permutations(range(L), t):
            if any(labs[i] == 0 and labs[j] == 1 for i in range(t) for j in range(i + 1, t)): continue
            if t == 3 and labs in PAT3: continue
            out.append(tuple(r * L + c for r, c in zip(rows, labs)))
    return out
def series(blocks, cols):
    P_, W = gf3.pack(np.vstack(blocks))[:2]
    return [int(x) for x in prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W, cols, np.cumsum([b.shape[0] for b in blocks]).tolist())]
def dp_blocks(forms, F2, F3, vars_):
    i2 = {f: k for k, f in enumerate(F2)}; i3 = {f: k for k, f in enumerate(F3)}; out = []
    for f in forms:
        sq = np.array([(2 * f[a] * f[b]) % 3 for a, b in F2], dtype=np.int64)
        B = np.zeros((len(vars_), len(F3)), dtype=np.uint8); vi = {v: k for k, v in enumerate(vars_)}
        for k, S in enumerate(F3):
            for drop in range(3):
                v = S[drop]; rest = S[:drop] + S[drop + 1:]
                if v in vi and rest in i2: B[vi[v], k] = (int(B[vi[v], k]) + sq[i2[rest]]) % 3
        out.append(B)
    return out
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--R', type=int, default=0); ap.add_argument('--L', type=int, default=0); ap.add_argument('--Mmax', type=int, default=57)
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out', required=True); a = ap.parse_args(); t0 = time.time()
n = a.n; R, L = (a.R or n + 1), (a.L or n - 1); last = R - 1; v = R * L
F2, F3 = faces(R, L, 2), faces(R, L, 3); F3p = [S for S in F3 if all(x // L != last for x in S)]; F3r = [S for S in F3 if any(x // L == last for x in S)]
g1, g3, g1p, g3p = v, len(F3), (R - 1) * L, len(F3p)
rng = np.random.default_rng(300 + a.seed); base = []
if a.Mmax <= 0: a.Mmax = int(np.ceil(len(F3) / (v - 1))) + 1
while len(base) < a.Mmax:
    f = rng.integers(0, 3, size=v); f[last * L:] = 0
    if all(f[r * L:(r + 1) * L].any() for r in range(R - 1)): base.append(f)
lastvars = list(range(last * L, R * L)); allvars = list(range(v)); pvars = list(range(last * L))
trace = series(dp_blocks(base, F2, F3p, pvars), g3p)
resid = series(dp_blocks(base, F2, F3r, lastvars), len(F3r))
out = dict(n=n, R=R, L=L, g1=g1, g3=g3, g1p=g1p, g3p=g3p, residual_dim=len(F3r), capacity=g3 / (g1 - 1), families={})
for fam in ('uniform', 'single'):
    forms = []
    for k, f in enumerate(base):
        g = f.copy()
        if fam == 'uniform': g[last * L:] = rng.integers(1, 3, size=L)
        else: g[last * L + (k % L)] = 1
        forms.append(g)
    full = series(dp_blocks(forms, F2, F3, allvars), g3); rows = []
    for M in range(1, a.Mmax + 1):
        fe, te, re_ = min(g3, M * (g1 - 1)), min(g3p, M * (g1p - 1)), min(len(F3r), M * L)
        rows.append(dict(M=M, full=full[M - 1], full_exp=fe, trace=trace[M - 1], trace_exp=te, resid=resid[M - 1], resid_exp=re_,
                         coupling=full[M - 1] - trace[M - 1] - resid[M - 1], coupling_exp=fe - te - re_))
    dev = {k: [r['M'] for r in rows if r[k] != r[k + '_exp']] for k in ('full', 'trace', 'resid', 'coupling')}
    out['families'][fam] = dict(rows=rows, deviations=dev)
    print(f'R={R} L={L} {fam}: capacity {g3/(g1-1):.1f}; deviations', {k: (x[:5], len(x)) for k, x in dev.items()}, f'({time.time()-t0:.0f}s)', flush=True)
json.dump(out, open(a.out, 'w'), indent=1)
