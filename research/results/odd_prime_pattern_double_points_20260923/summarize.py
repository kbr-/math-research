"""Reads the saved piece-rank and tropical JSONs and prints the tables quoted in the notebook entry."""
import glob, json, os, re
D = os.path.dirname(os.path.abspath(__file__)); rows = {}
for p in sorted(glob.glob(os.path.join(D, 'grid', 'pieces_R*_L*.json'))):
    m = re.search(r'pieces_R(\d+)_L(\d+)(?:_s(\d+))?\.json', p); R, L, s = int(m[1]), int(m[2]), int(m[3] or 1)
    r = json.load(open(p)); dev = r['families']['uniform']['deviations']
    rows.setdefault((R, L), []).append((s, len(r['families']['uniform']['rows']), len(dev['full']), dev['full'][:3], r['capacity']))
for (R, L), v in sorted(rows.items()):
    print(f'R={R} L={L} cap={v[0][4]:.1f} ' + '; '.join(f'seed {s}: {nm} values of M, full deviates at {k} (first {f})' for s, nm, k, f, _ in sorted(v)))
for n in (6, 7):
    r = json.load(open(os.path.join(D, f'pieces_P_n{n}.json')))
    print(f'n={n}:', {fam: (len(x['rows']), {k: len(d) for k, d in x['deviations'].items()}) for fam, x in r['families'].items()})
for p in sorted(glob.glob(os.path.join(D, 'tropical_R*_L*.json'))):
    r = json.load(open(p))
    for x in r['runs']: print(f"tropical R={r['R']} L={r['L']} M={x['M']} {x['family']}: {x['best']}/{x['target']} = {x['fraction']:.3f}")
