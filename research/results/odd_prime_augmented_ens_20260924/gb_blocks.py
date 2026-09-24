"""Reduced degree-order Groebner bases of one augmented ENS block over F_3.

Tested statements (finite checks, h = 1..HMAX):
  (B) every top-degree form of the reduced dp Groebner basis of
      (q_i P : i) + (y_i^3 - y_i, r_i^3 - r_i), q_i = 1 - y_i^2, P = 1 - sum_k r_k q_k,
      is bihomogeneous in (y-degree, r-degree);
  (Y) the tops of r-degree 0, other than the field equations y_i^3, are exactly the
      C(h,2) monomials y_1...y_h * y_j y_k (j < k).
  (V) vdim equals |Z| = 6^h + sum_{S nonempty} 2^(h-|S|) 3^(h-1), the number of points
      (y, r) in F_3^h x F_3^h with P = 0 whenever some q_i = 1.
The Groebner basis is computed by Singular (compiled); Python only parses.
"""
import itertools, json, re, subprocess, sys, time, os
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = open(os.path.join(HERE, 'gb_block.sing')).read()
HMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 5
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'gb_blocks.json')
TMP = os.path.join(HERE, '..', '..', 'tmp', 'augmented_ens'); os.makedirs(TMP, exist_ok=True)

def npoints(h):
    return 6 ** h + sum(comb(h, s) * 2 ** (h - s) * 3 ** (h - 1) for s in range(1, h + 1))

def monomial_exps(mono, h):
    e = [0] * h
    for f in mono.split('*'):
        m = re.fullmatch(r'y\((\d+)\)(?:\^(\d+))?', f)
        assert m, f
        e[int(m.group(1)) - 1] += int(m.group(2) or 1)
    return tuple(e)

results = []
for h in range(1, HMAX + 1):
    path = f'{TMP}/gb_{h}.sing'
    open(path, 'w').write(TEMPLATE.replace('HH', str(h)))
    t0 = time.time()
    run = subprocess.run(['Singular', '-q', path], capture_output=True, text=True, check=True)
    el = time.time() - t0
    gens = []; vdim = None
    for l in run.stdout.splitlines():
        if l.startswith('GEN'):
            d = int(re.search(r'deg=(\d+)', l).group(1))
            top = re.search(r'top=(.*) bideg=', l).group(1)
            bd = [tuple(map(int, x)) for x in re.findall(r'\((\d+),(\d+)\)', l.split('bideg=')[1])]
            gens.append((d, top, bd))
        elif l.startswith('VDIM'):
            vdim = int(l.split()[1])
    inhom = [g for g in gens if len(set(g[2])) > 1]
    pure = sorted(monomial_exps(g[1], h) for g in gens if g[2][0][1] == 0 and g[0] > 3 or (g[2][0][1] == 0 and g[0] == 3 and '+' in g[1]))
    field_y = [g for g in gens if g[2][0] == (3, 0) and g[0] == 3 and '+' not in g[1] and '-' not in g[1]]
    expected = sorted(tuple(1 + (i in (j, k)) for i in range(h)) for j, k in itertools.combinations(range(h), 2))
    bydeg = {}
    for d, top, bd in gens:
        key = f'{d}:{bd[0][0]},{bd[0][1]}'
        bydeg[key] = bydeg.get(key, 0) + 1
    rec = dict(h=h, generators=len(gens), vdim=vdim, points=npoints(h), vdim_ok=vdim == npoints(h),
               bihomogeneous=not inhom, pure_tops=[list(p) for p in pure], pure_expected=pure == expected,
               field_y_tops=len(field_y), by_degree_bidegree=bydeg, seconds=round(el, 2))
    print(json.dumps({k: rec[k] for k in ('h', 'generators', 'vdim_ok', 'bihomogeneous', 'pure_expected', 'seconds')}), flush=True)
    results.append(rec)
json.dump(results, open(OUT, 'w'), indent=1)
