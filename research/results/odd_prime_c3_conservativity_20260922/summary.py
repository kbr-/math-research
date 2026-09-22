"""Join the C3 conservativity results with the saturation counts; write c3_summary.txt.
A test is nonvacuous only when the base closure is unsaturated (gap > 0)."""
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sat = {(r['name'], r['D']): r for r in json.load(open(os.path.join(HERE, 'c3_saturation.json')))}
res = {}
for f in ('c3_small.json', 'c3_twobase.json', 'c3_rerun.json', 'c3_lag.json', 'c3_threebase7.json', 'c3_d8.json', 'c3_r3d6.json', 'c3_r3d7.json'):
    path = os.path.join(HERE, f)
    if os.path.exists(path):
        for r in json.load(open(path)): res[(r['name'], r['D'])] = r
fams = collections.defaultdict(list)
for key, r in sorted(res.items()):
    if r['name'].startswith('small-fake'): continue          # unsound control, reported separately
    s = sat.get(key)
    gap = None if s is None else s['semantic'] - s['dim_base']
    if s is not None: assert s['dim_base'] == r['dim_base'], key
    fams[(r['name'].rsplit('-s', 1)[0], r['D'])].append((r['name'], gap, r['dim_existing_after'] - r['dim_base']))
lines = ['family D | instances | saturation known | unsaturated | with rise | gap total | rise total',
         '---']
for (fam, D), xs in sorted(fams.items()):
    known = [x for x in xs if x[1] is not None]
    lines.append(f'{fam} D={D} | {len(xs)} | {len(known)} | {sum(x[1] > 0 for x in known)} | '
                 f'{sum(x[2] > 0 for x in xs)} | {sum(x[1] for x in known)} | {sum(x[2] for x in xs)}')
lines += ['', 'unsaturated or rising instances (name, D, gap, rise):']
for (fam, D), xs in sorted(fams.items()):
    for n, g, r in xs:
        if (g or 0) > 0 or r > 0: lines.append(f'  {n} D={D} gap={g} rise={r}')
open(os.path.join(HERE, 'c3_summary.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
