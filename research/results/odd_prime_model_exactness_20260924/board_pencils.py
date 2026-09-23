"""Model exactness on pencils: for every pencil class of column forms at n = 8 (up to AGL(2,3), span 2-dimensional modulo
constants), compare the board excess of A/(l_1, l_2)A over HS_A/(1+q+q^2)^2 (weak unary PHP top algebra, a4lib normal forms,
compiled prefix ranks) with the column-model excess of R/(l_1, l_2)R over HS_R/(1+q+q^2)^2, through degree 3.
Tested statement: the board excess equals the model excess for every class (model exactness for A on pencils at n = 8).
Classes come from pencil_exhaustive.py's enumeration, in its order; --start/--end select a batch.
Usage: python3 board_pencils.py --start 0 --end 20 --out OUT.json"""
import itertools, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..'); BA = os.path.join(RES, 'odd_prime_board_affine_20260923')
a = dict(zip(sys.argv[1::2], sys.argv[2::2])); st, en, outp = int(a['--start']), int(a['--end']), a['--out']
src = open(os.path.join(RES, 'odd_prime_pencil_freeness_20260924', 'pencil_exhaustive.py')).read()
pre = src.split("DIRS = [(1, 0)")[0].split("a = dict(zip(sys.argv[1::2], sys.argv[2::2]))")
ns_ = {'__file__': os.path.join(RES, 'odd_prime_pencil_freeness_20260924', 'pencil_exhaustive.py')}; exec(pre[0] + "T = 3\n" + pre[1].split("\n", 1)[1], ns_)            # PTS, GROUP, classes, hf, divq with T = 3
sys.argv = [sys.argv[0], '--n', '8', '--K', '3', '--rs', '', '--family', 'random']
exec(open(os.path.join(BA, 'board_affine.py')).read().split("res = []\nif opt.phis:")[0])
sys.path.insert(0, os.path.join(RES, 'odd_prime_permutation_forms_20260923')); from gf3_prefix import prefix_ranks
DIRS = [(1, 0), (0, 1), (1, 1), (1, 2)]
reps = []
for v in ns_['classes'](8):
    holes = [p for p, m in zip(ns_['PTS'], v) for _ in range(m)]
    if any(len({(u[0] * x + u[1] * y) % 3 for x, y in holes}) == 1 for u in DIRS): continue
    reps.append((v, holes))
def rows_for(F, t):
    lin = {(i * n + j,): int(F[i, j]) for i in range(P1) for j in range(n) if F[i, j] % 3}
    R_ = np.zeros((len(basis[t - 1]), g[t]), dtype=np.uint8)
    for r_, m in enumerate(basis[t - 1]): R_[r_] = L.normal_form(L.mul({m: 1}, lin) if m else lin, Q[t], g[t]) % 3
    return R_
gam = [1, g[1], g[2], g[3]]; Wb = ns_['divq'](gam, 2); HR = ns_['hf'](8, [[1] * 8]); Wm = ns_['divq'](HR, 2)
out = dict(n=8, total_classes=len(reps), HS_A=gam, board_free=Wb, model_free=Wm, results=[]); t0 = time.time()
for k in range(st, min(en, len(reps))):
    v, holes = reps[k]; phi1 = np.array([x for x, y in holes]); phi2 = np.array([y for x, y in holes])
    F = [np.tile(phi1, (P1, 1)), np.tile(phi2, (P1, 1))]; Hb = [1]
    for t in (1, 2, 3):
        P_, W_ = L.gf3.pack(np.vstack([rows_for(f, t) for f in F]))[:2]
        Hb.append(g[t] - int(prefix_ranks(np.ascontiguousarray(P_, dtype=np.uint64), W_, g[t], [2 * len(basis[t - 1])])[0]))
    Hm = ns_['hf'](8, [[1] * 8, phi1.tolist(), phi2.tolist()])
    eb = [x - y for x, y in zip(Hb, Wb)]; em = [x - y for x, y in zip(Hm, Wm)]
    cmin = min(8 - max(sum(1 for x, y in holes if (u[0] * x + u[1] * y) % 3 == z) for z in range(3)) for u in DIRS)
    out['results'].append(dict(index=k, counts=v, c_min=cmin, board_H=Hb, model_H=Hm, board_excess=eb, model_excess=em, equal=(eb == em)))
    print(k, v, 'c_min', cmin, 'board excess', eb, 'model excess', em, 'equal', eb == em, f'({time.time()-t0:.0f}s)', flush=True)
json.dump(out, open(outp, 'w'), indent=1)
