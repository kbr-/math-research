#!/usr/bin/env python3
"""Compose complete cut periods and export exact local certificates; failures remain undecided."""
import argparse,csv,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--fourth-log',type=Path,required=True);args=p.parse_args()
P=Path('research/results/bmd-nine-quinary-period-20261008')
def read(name):
    rows=list(csv.DictReader((P/name).open()));data={int(r['degree_residue']):r for r in rows}
    assert len(rows)==len(data)
    assert all(0<=int(r['rank'])<=188 and 0<=int(r['order_index'])<24 for r in rows)
    return data
first,second,fourth=read('full.csv'),read('second-full.csv'),read('fourth-full.csv')
assert set(first)==set(range(150))
text=args.fourth_log.read_text();match=re.search(r'LOCAL_PERIOD (\d+) DEGREE_PERIOD (\d+)',text);assert match
r4,p4=map(int,match.groups());assert p4==5*r4
assert 'all_selected_ranks_FLINT_verified=true' in text and 'full=1' in text
common=math.lcm(23400,p4)
def prior(d):
    return first[d%150] if int(first[d%150]['rank'])==188 else second[d%23400]
needed={d%p4 for d in range(common) if int(prior(d)['rank'])<188}
assert set(fourth)==needed
uncovered=[d for d in range(common) if int(prior(d)['rank'])<188 and int(fourth[d%p4]['rank'])<188]
local=[]
for suffix,step,period in [('',1,150),('-second',3,7800),('-third',3,7800),('-fourth',5,r4)]:
    v=list(map(int,(P/f'local-data{suffix}.txt').read_text().split()));f=v[0]
    assert f in [2,4]
    start=f+3+24*188
    local.append([f,v[1:f+2],v[f+2],v[start:start+512],step,period])
(P/'local-certificates.g').write_text('LOCAL_CERTIFICATES := '+json.dumps(local)+';\n')
result=dict(periods=[150,23400,p4],common_period=common,first_covered=98,
            second_required=8112,second_covered=8064,fourth_unique_required=len(needed),
            fourth_covered=sum(int(r['rank'])==188 for r in fourth.values()),
            uncovered_residues=uncovered,complete_bulk_cover=not uncovered,
            scope='Sufficient original n9,p5 bulk normality; low degrees2..6 separately certified.')
(P/'coverage.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
