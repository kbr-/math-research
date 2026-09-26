"""Summarize joint_union.json: vanish(S) per (field, v, k, r), min/max over seeds."""
import json
from collections import defaultdict
from pathlib import Path
rows = json.loads((Path(__file__).parent / 'joint_union.json').read_text())
g = defaultdict(list)
for c in rows:
    g[(c['v'], c['k'], c['r'], c['field'], c['S'])].append(c)
print('v k r field S full vanish(min..max) quadric_product_prediction union_points(min)')
for key in sorted(g):
    cs = g[key]; vs = [c['vanish'] for c in cs]
    print(*key[:4], key[4], cs[0]['full'], f"{min(vs)}..{max(vs)}", cs[0]['quadric_product_prediction'], min(c['union_points'] for c in cs))
f3 = [c for c in rows if c['field'] == 'F3' and c['S'] >= 2]
print('F3 S>=2: vanish == quadric product prediction in', sum(c['vanish'] == c['quadric_product_prediction'] for c in f3), 'of', len(f3))
