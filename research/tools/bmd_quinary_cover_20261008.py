#!/usr/bin/env python3
"""Compose only complete certified paired periods; never call failures original exceptions."""
import csv,json
from pathlib import Path
P=Path('research/results/bmd-nine-quinary-period-20261008')
def read(name):
    rows=list(csv.DictReader((P/name).open()))
    data={int(r['degree_residue']):r for r in rows}
    assert len(data)==len(rows)
    return data
first=read('full.csv');second=read('second-full.csv')
assert set(first)==set(range(150))
needed={d for d in range(23400) if int(first[d%150]['rank'])<188}
assert len(needed)==8112 and set(second)==needed
rows=[];fail=[]
for d in range(23400):
    record=first[d%150] if int(first[d%150]['rank'])==188 else second[d]
    row=dict(degree_residue=d,representative=d,rank=int(record['rank']),order_index=int(record['order_index']))
    rows.append(row)
    if row['rank']<188:fail.append(d)
assert len(fail)==48 and set(fail)=={d for d in range(23400) if d%975 in (125,856)}
with (P/'before-third.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'two-curve-coverage.json').write_text(json.dumps(dict(period=23400,covered=23352,remaining=fail,residual_modulus=975,residual_residues=[125,856]),indent=2)+'\n')
print('COMPLETE two-curve cover: 23352/23400, exactly two residual classes modulo975.')
