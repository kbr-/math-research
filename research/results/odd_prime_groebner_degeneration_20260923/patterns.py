"""Pattern check for the lex initial complex Delta' of the functional top algebra, degrees 2 and 3.
Tested statement: the minimal non-faces of Delta' of size 2 are exactly {(r,0),(s,1)} for r<s, and those of size 3 are
exactly, for every row triple r<s<u, the four patterns (0,2,3), (1,0,2), (1,2,0), (1,2,3) (labels on rows r, s, u).
Recomputes in(I) in degrees 2 and 3 (same construction as degeneration.py) and compares the full generator sets.
Usage: python3 patterns.py --ns 5,6,7,8 --out OUT.json"""
import argparse, itertools, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--ns', default='5,6,7,8'); ap.add_argument('--out', required=True); a = ap.parse_args(); res = []
PAT3 = [(0, 2, 3), (1, 0, 2), (1, 2, 0), (1, 2, 3)]
for n in map(int, a.ns.split(',')):
    tmp = os.path.join(HERE, f'_pat_{n}.json')
    subprocess.check_call([sys.executable, os.path.join(HERE, 'degeneration.py'), '--n', str(n), '--T', '3', '--out', tmp, '--all-generators'], stdout=subprocess.DEVNULL)
    d = json.load(open(tmp)); os.remove(tmp); R = n + 1
    g2 = {tuple(map(tuple, m)) for m in d['generators']['2']}; g3 = {tuple(map(tuple, m)) for m in d['generators']['3']}
    p2 = {((r, 0), (s, 1)) for r, s in itertools.combinations(range(R), 2)}
    p3 = {tuple(sorted([(r, x), (s, y), (u, z)])) for r, s, u in itertools.combinations(range(R), 3) for x, y, z in PAT3}
    res.append(dict(n=n, deg2_equal=g2 == p2, deg3_equal=g3 == p3, n_deg2=len(g2), n_deg3=len(g3))); print(res[-1], flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
