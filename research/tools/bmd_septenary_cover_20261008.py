#!/usr/bin/env python3
"""Compose complete cut periods and export exact local certificates; failures remain undecided."""
import argparse,csv,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--third-log',type=Path,required=True);args=p.parse_args()
P=Path('research/results/bmd-nine-septenary-period-20261008')
def read(name):
    rows=list(csv.DictReader((P/name).open()));data={int(r['degree_residue']):r for r in rows}
    assert len(rows)==len(data)
    assert all(0<=int(r['rank'])<=188 and 0<=int(r['order_index'])<24 for r in rows)
    return data
first,third=read('full.csv'),read('third-full.csv')
assert set(first)==set(range(882))
text=args.third_log.read_text();match=re.search(r'LOCAL_PERIOD (\d+) DEGREE_PERIOD (\d+)',text);assert match
r3,p3=map(int,match.groups());assert p3==3*r3
assert 'all_selected_ranks_FLINT_verified=true' in text and 'full=1' in text
common=math.lcm(882,p3)
needed={d%p3 for d in range(common) if int(first[d%882]['rank'])<188}
assert set(third)==needed
uncovered=[d for d in range(common) if int(first[d%882]['rank'])<188 and int(third[d%p3]['rank'])<188]
local=[]
for suffix,period in [('',294),('-third',r3)]:
    v=list(map(int,(P/f'local-data{suffix}.txt').read_text().split()));f=v[0]
    assert f in [2,4]
    start=f+3+24*188
    local.append([f,v[1:f+2],v[f+2],v[start:start+512],3,period])
(P/'local-certificates.g').write_text('LOCAL_CERTIFICATES := '+json.dumps(local)+';\n')
result=dict(periods=[882,p3],common_period=common,
            first_covered=sum(int(r['rank'])==188 for r in first.values()),
            third_unique_required=len(needed),
            third_covered=sum(int(r['rank'])==188 for r in third.values()),
            uncovered_residues=uncovered,complete_bulk_cover=not uncovered,
            scope='Sufficient original n9,p7 bulk normality; low degrees2..6 separately certified.')
(P/'coverage.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
