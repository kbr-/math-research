"""Degree-4 Taylor generation for width-1 W clauses on the functional board (R = n+1 rows, N = n labels, GF(3)).

Tested statement (prop:width-one-degree-four-glue): a normalized width-1 W clause chi_v(L_i)(L_j - u) has top
-l_i^2 l_j.  If (a3) the tops are linearly independent in G_3 and (b4) the kernel of mu_4: (+)_C G_1 -> G_4,
(g_C) -> sum g_C l_i^2 l_j, is spanned by the Frobenius syzygies l_i e_C (then (F) alone gives Taylor generation
through degree 4; shared outside forms or crossed pairs would add non-Frobenius kernel vectors), then functional PHP plus the clauses has no PC refutation of degree 4
(thm:based-taylor-glue over the functional base, which is stable through 4 for R >= 4, N >= 7).
(b4) with Frobenius only: rank mu_4 = M (gamma_1 - 1), computed as the rank of the dual map K_4 -> (+)_C K_1,
w -> (D_{l_j} D_{l_i}^2 w)_C, for every prefix M of one random sequence (forms nonconstant on every row, outside
linear parts pairwise non-proportional, asserted).  The semi-regular prediction is that (a3) and (b4) hold for every
M up to the capacity floor(gamma_4 / (gamma_1 - 1)); a failure below capacity means width-1 tops have syzygies beyond
Taylor's.  Ranks by the compiled prefix-rank kernel, one incremental pass.
Usage: python3 width1_check.py --n 7 --Mmax 360 --seed S --out OUT.json"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..')
D4 = os.path.join(RES, 'odd_prime_glue_degree_four_20260923')
for p in (D4, os.path.join(RES, 'odd_prime_permutation_forms_20260923'), os.path.join(RES, 'odd_prime_short_generation_20260923'),
          os.path.join(RES, 'odd_prime_local_falls_20260923'), os.path.join(RES, 'odd_prime_alignment_mechanism_20260922')):
    sys.path.insert(0, p)
src = open(os.path.join(D4, 'deg4_check.py')).read(); src = src[:src.index('ap = argparse.ArgumentParser()')]
ns = {'__file__': os.path.join(D4, 'deg4_check.py')}; exec(compile(src, 'deg4_check_prefix', 'exec'), ns)   # Board, series
Board, series, random_eq = ns['Board'], ns['series'], ns['random_eq']
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=7); ap.add_argument('--Mmax', type=int, default=360)
ap.add_argument('--seed', type=int, default=1); ap.add_argument('--out', required=True); a = ap.parse_args(); t0 = time.time()
n = a.n; R, N = n + 1, n; b = Board(R, N); g3, g4 = b.Kb[3].shape[1], b.Kb[4].shape[1]; g1 = R * (N - 1)
rng = np.random.default_rng(1700 + a.seed); v = n * (n + 1)
def form():
    while True:
        L = random_eq(rng, v); arr = np.zeros((R, N), dtype=np.int64)
        for m, c in L.items():
            if m: arr[m[0] // n, m[0] % n] = c
        if all(len(set(arr[x])) > 1 for x in range(R)): return arr
def key(arr):                                   # linear part up to sign
    f = arr.ravel() % 3; g = (2 * f) % 3; return min(tuple(f), tuple(g))
clauses, seen = [], set()
while len(clauses) < a.Mmax:
    fi, fj = form(), form()
    if key(fi) in seen or key(fi) == key(fj): continue
    seen.add(key(fi)); clauses.append((fi, fj))
assert len({key(fi) for fi, _ in clauses}) == len(clauses)
distinct_forms = len({key(f) for c in clauses for f in c})
outs = {key(fi): idx for idx, (fi, _) in enumerate(clauses)}
crossed = sum(1 for idx, (fi, fj) in enumerate(clauses) if key(fj) in outs and key(clauses[outs[key(fj)]][1]) == key(fi))
def ddd(fi, fj, t):                             # D_{l_j} D_{l_i} D_{l_i} on the K_t basis, into full (t-3)-coordinates
    X = b.D(fi, t) @ b.Kb[t]; X = b.D(fi, t - 1) @ X; X = b.D(fj, t - 2) @ X
    return (X.toarray() % 3).astype(np.uint8)
r3 = series([ddd(fi, fj, 3) for fi, fj in clauses], g3)
print(f'n={n}: gamma1={g1}, gamma3={g3}, gamma4={g4}; (a3) ranks done ({time.time()-t0:.0f}s)', flush=True)
r4 = series([ddd(fi, fj, 4) for fi, fj in clauses], g4)
cap = g4 // (g1 - 1)
rows = [dict(M=M, a3=bool(r3[M - 1] == M), rank4=int(r4[M - 1]), predicted=int(min(M * (g1 - 1), g4)),
             b4=bool(r4[M - 1] == M * (g1 - 1))) for M in range(1, a.Mmax + 1)]
hyp = [r['M'] for r in rows if r['a3'] and r['b4']]
first_fail = next((r['M'] for r in rows if not (r['a3'] and r['b4'])), None)
res = dict(n=n, seed=a.seed, gamma1=g1, gamma3=g3, gamma4=g4, capacity=cap, distinct_linear_parts=distinct_forms,
           crossed_pairs=crossed, rows=rows,
           last_M_with_hypotheses=max(hyp) if hyp else None, first_failure_M=first_fail,
           rank_equals_min_prediction=all(r['rank4'] == r['predicted'] for r in rows), seconds=round(time.time() - t0, 1))
json.dump(res, open(a.out, 'w'), indent=1)
print(f'capacity {cap}; hypotheses hold up to M = {res["last_M_with_hypotheses"]}; first failure {first_fail}; '
      f'rank4 = min(M(g1-1), g4) at every prefix: {res["rank_equals_min_prediction"]} ({time.time()-t0:.0f}s)', flush=True)
