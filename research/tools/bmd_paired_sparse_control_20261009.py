#!/usr/bin/env python3
"""Compare sparse direct and reflected control ranks with the retained exhaustive table."""
import csv,json
from pathlib import Path
old=Path('research/results/bmd-thirty-seven-paired-20261009');new=Path('research/results/bmd-thirty-seven-moving-mark-20261009')
def table(p):
 rows=list(csv.DictReader(p.open()));d={int(r['degree_residue']):int(r['rank']) for r in rows};assert len(d)==len(rows);return d
full=table(old/'full.csv');direct=table(new/'control-direct.csv');prior=table(old/'combined.csv');Q=len(full);needed={r%Q for r,v in prior.items() if v<188}
for r,v in direct.items():assert v==full[r]==full[(6-r)%Q]
assert needed==set(direct)|{(6-r)%Q for r in direct}
report=dict(exhaustive_control_period=Q,required_states=len(needed),direct_states=len(direct),all_direct_and_reflected_ranks_match=True)
(new/'sparse-control.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
