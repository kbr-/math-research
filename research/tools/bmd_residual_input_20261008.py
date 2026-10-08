"""Adapt retained GAP syntax for exact residual-reference comparisons; no numerical work."""
import argparse, ast, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--modules',nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args()
rows=[]
for name in a.modules:
 s=Path(name).read_text();prefix='LOW_MULTIPLIER_PRECISION := 28;\nLOW_MULTIPLIER_MODULES := '
 assert s.startswith(prefix) and s.rstrip().endswith(';')
 r=ast.literal_eval(s[len(prefix):].strip()[:-1]);assert len(r)==1 and r[0][0]==3 and r[0][1] in (5,13)
 rows.extend(r)
s=Path('research/results/bmd-exception-low-multipliers-20261008/return-vectors.g').read_text()
v=ast.literal_eval(s.split(':=',1)[1].strip()[:-1]);v=[x for x in v if x[0]==3 and x[2]==27];assert len(v)==3
Path(a.out).write_text('{\nRM_MODULES='+json.dumps(rows)+';\nRM_VECTORS='+json.dumps(v)+';\n}\n')
print('RESIDUAL_INPUT_COMPLETE modules',len(rows),'return_vectors',len(v))
