"""Falsification test of the glued degree-3 theorem on the functional board.

Tested statement: for selectors 1-(L_j - v_j)^2 whose linear parts l_j (as elements of G_1 of the functional board,
R = n+1 rows, N = n labels) have (a) squares independent in G_2 and (b) double-point map w -> (D_{l_j}^2 w)_j on K_3 of
rank M(gamma_1 - 1) (injective side, M <= gamma_3/(gamma_1 - 1)), functional PHP^{n+1}_n plus the selectors has no PC
refutation of degree 3.  One uniform random selector sequence; for every prefix M: the two hypotheses at those forms
(prefix ranks in the compiled kernel), and whether the degree-3 PC closure of the functional base plus the prefix
contains 1 (incremental closure in the compiled kernel).  Prediction: the first refuted M exceeds every prefix at which
(a) and (b) hold.
Usage: python3 glued_check.py --n 6 --Mmax 60 --seed S --out OUT.json"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(RES, 'odd_prime_horace_pieces_20260923')); sys.path.insert(0, os.path.join(RES, 'odd_prime_local_falls_20260923')); sys.path.insert(0, os.path.join(RES, 'odd_prime_short_generation_20260923'))
from horace_pieces import Board, series
from local_falls import Closure, QSpace, base_rows, random_eq, sel
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=6); ap.add_argument('--Mmax', type=int, default=60)
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--threads', type=int, default=12); ap.add_argument('--out', required=True)
a = ap.parse_args(); t0 = time.time(); n = a.n; R, N = n + 1, n
sp = QSpace(n, 3); v = sp.v; rng = np.random.default_rng(500 + a.seed)
forms = []
while len(forms) < a.Mmax:
    L = random_eq(rng, v); arr = np.zeros((R, N), dtype=np.int64)
    for m, c in L.items():
        if m: arr[m[0] // n, m[0] % n] = c
    if all(len(set(arr[x])) > 1 for x in range(R)): forms.append((L, arr))       # nonconstant on every row
b = Board(R, N); g3 = b.Kb.shape[1]; g1 = R * (N - 1)
full3 = series([b.D2K(arr, np.arange(g3)) for _, arr in forms], g3)
# degree 2: squares in G_2 <-> functionals w -> D_l^2 w on K_2 (a row of length dim K_2 per form)
import itertools
from second_degree_lift import marg_basis
inj2, B2 = marg_basis(N, 2); pairs = list(itertools.combinations(range(R), 2))
def sq_row(arr):
    out = []
    for (x, y) in pairs:
        coef = np.array([2 * arr[x, c] * arr[y, d] for (c, d) in inj2]) % 3
        out.append((coef @ B2) % 3)
    return np.concatenate(out).astype(np.uint8)[None, :]
g2 = len(pairs) * B2.shape[1]
full2 = series([sq_row(arr) for _, arr in forms], g2)
print(f'n={n}: gamma3={g3} gamma2={g2} gamma1={g1} capacity={g3/(g1-1):.1f}; ranks done ({time.time()-t0:.0f}s)', flush=True)
fun = [{(i * n + j, i * n + k): 1} for i in range(R) for j in range(N) for k in range(j + 1, N)]    # row collisions
C = Closure(sp, a.threads); C.add(base_rows(n) + fun); base = C.split(); rows = []
for M in range(1, a.Mmax + 1):
    C.add([sel(forms[M - 1][0])]); s = C.split()
    ha = full2[M - 1] == min(M, g2); hb = full3[M - 1] == M * (g1 - 1)
    rows.append(dict(M=M, squares_independent=bool(ha), double_point_injective=bool(hb), **s))
    if s['refuted']: break
hyp = [r['M'] for r in rows if r['squares_independent'] and r['double_point_injective']]
first = next((r['M'] for r in rows if r['refuted']), None)
res = dict(n=n, seed=a.seed, base=base, gamma3=g3, gamma2=g2, gamma1=g1, capacity=g3 / (g1 - 1), rows=rows,
           last_M_with_hypotheses=max(hyp) if hyp else None, first_refuted_M=first,
           prediction_holds=(first is None) or (not hyp) or first > max(hyp))
json.dump(res, open(a.out, 'w'), indent=1)
print(f'base {base}; hypotheses hold up to M={res["last_M_with_hypotheses"]}; first refuted M={first}; prediction holds: {res["prediction_holds"]} ({time.time()-t0:.0f}s)', flush=True)
