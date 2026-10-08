#!/usr/bin/env python3
"""Compose the complete normalized n9,p17 cut periods; no degree extrapolation."""
import argparse,csv,json,math,re
from pathlib import Path
p=argparse.ArgumentParser()
for name in ('first-log','second-log','first-local-log','second-local-log'):p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args();root=Path('research/results/bmd-nine-seventeen-period-20261008')
def table(name):
    rows=list(csv.DictReader((root/name).open()));data={int(r['degree_residue']):r for r in rows}
    assert len(data)==len(rows) and all(0<=int(r['rank'])<=188 and 0<=int(r['order_index'])<24 for r in rows)
    return data
def period(log,local,step):
    s=log.read_text();m=re.search(r'LOCAL_PERIOD (\d+) DEGREE_PERIOD (\d+) NORMALIZATION_CODE (\d+)',s);assert m
    r,d,g=map(int,m.groups());assert d==step*r and 'full=1' in s and 'all_selected_ranks_FLINT_verified=true' in s
    n=re.search(r'GAP_NORMALIZED_PERIOD (\d+) gamma_code=(\d+) all512=true',local.read_text());assert n and tuple(map(int,n.groups()))==(r,g)
    return r,d,g
pa=period(a.first_log,a.first_local_log,3);pb=period(a.second_log,a.second_local_log,5)
first=table('full.csv');second=table('second-pilot.csv')
assert set(first)==set(range(pa[1]))
common=math.lcm(pa[1],pb[1]);residual=[d for d in range(common) if int(first[d%pa[1]]['rank'])<188];needed={d%pb[1] for d in residual};assert set(second)==needed
uncovered=[d for d in residual if int(second[d%pb[1]]['rank'])<188]
result=dict(local_periods=[pa[0],pb[0]],degree_steps=[3,5],degree_periods=[pa[1],pb[1]],normalization_codes=[pa[2],pb[2]],common_period=common,first_covered=sum(int(r['rank'])==188 for r in first.values()),first_failed_residues=sorted(d for d,r in first.items() if int(r['rank'])<188),remaining_common_period_classes=len(residual),second_unique_required=len(needed),second_covered=sum(int(r['rank'])==188 for r in second.values()),uncovered_residues=uncovered,complete_bulk_cover=not uncovered,scope='Original generic n9,p17 bulk normality via exact normalized cut periods; original degrees2..6 separately certified. The fallback pilot already exhausts its domain.')
(root/'coverage.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
