#!/usr/bin/env python3
"""Compose complete cut periods and export exact local certificates; failures remain undecided."""
import argparse,csv,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--second-log',type=Path,required=True);p.add_argument('--first-normalization-log',type=Path,required=True);p.add_argument('--second-normalization-log',type=Path,required=True);args=p.parse_args()
P=Path('research/results/bmd-nine-thirteen-period-20261008')
def read(name):
    rows=list(csv.DictReader((P/name).open()));data={int(r['degree_residue']):r for r in rows}
    assert len(rows)==len(data)
    assert all(0<=int(r['rank'])<=188 and 0<=int(r['order_index'])<24 for r in rows)
    return data
first,second=read('full.csv'),read('second-full.csv')
assert set(first)==set(range(3549))
text=args.second_log.read_text();match=re.search(r'LOCAL_SCALAR_PERIOD (\d+) DEGREE_PERIOD (\d+)',text);assert match
r3,p3=map(int,match.groups());assert p3==3*r3
assert 'all_selected_ranks_FLINT_verified=true' in text and 'full=1' in text
common=math.lcm(3549,p3)
needed={d%p3 for d in range(common) if int(first[d%3549]['rank'])<188}
assert set(second)==needed
uncovered=[d for d in range(common) if int(first[d%3549]['rank'])<188 and int(second[d%p3]['rank'])<188]
local=[];normalizations=[]
for log in [args.first_normalization_log,args.second_normalization_log]:
    match=re.search(r'GAP_NORMALIZED_PERIOD (\d+) gamma=(\d+) all512=true',log.read_text());assert match
    normalizations.append(tuple(map(int,match.groups())))
for index,(suffix,step,period) in enumerate ([('',1,3549),('-second',3,r3)]):
    v=list(map(int,(P/f'local-data{suffix}.txt').read_text().split()));f=v[0]
    assert f in [2,4]
    start=f+3+24*188
    assert normalizations[index][0]==period
    gamma=normalizations[index][1];assert 0<gamma<13
    normalized=[sum((gamma*(c//13**j%13)%13)*13**j for j in range(f)) for c in v[start:start+512]]
    local.append([f,v[1:f+2],v[f+2],normalized,step,period])
(P/'local-certificates.g').write_text('LOCAL_CERTIFICATES := '+json.dumps(local)+';\n')
result=dict(normalization_multipliers=[g for _,g in normalizations],local_periods=[r for r,_ in normalizations],periods=[3549,p3],common_period=common,
            first_covered=sum(int(r['rank'])==188 for r in first.values()),
            second_unique_required=len(needed),
            second_covered=sum(int(r['rank'])==188 for r in second.values()),
            uncovered_residues=uncovered,complete_bulk_cover=not uncovered,
            scope='Sufficient original n9,p13 bulk normality; low degrees2..6 separately certified.')
(P/'coverage.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
