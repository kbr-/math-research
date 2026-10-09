#!/usr/bin/env python3
"""Compose exact characteristic-nineteen full-cut periods, retaining every residual."""
import argparse,csv,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--csv',type=Path,required=True);a=p.parse_args()
spec=json.loads(a.spec.read_text());covered={0:False};period=1;stages=[]
for entry in spec:
 text=Path(entry['log']).read_text();m=re.search(r'LOCAL_PERIOD (\d+) DEGREE_PERIOD (\d+) NORMALIZATION_CODE (\d+)',text);assert m
 local,newperiod,gamma=map(int,m.groups());assert newperiod==entry['step']*local
 assert 'full=1' in text and 'all_selected_ranks_FLINT_verified=true' in text
 check=Path(entry['local_check']).read_text();match=re.search(r'GAP_NORMALIZED_PERIOD (\d+) gamma_code=(\d+) all512=true',check);assert match and tuple(map(int,match.groups()))==(local,gamma)
 rows=list(csv.DictReader(Path(entry['table']).open()));table={int(r['degree_residue']):int(r['rank']) for r in rows}
 assert len(table)==len(rows) and all(0<=d<newperiod and 0<=rank<=188 for d,rank in table.items())
 common=math.lcm(period,newperiod);assert common<1000000
 needed={d%newperiod for d in range(common) if not covered[d%period]};assert set(table)==needed
 covered={d:covered[d%period] or table[d%newperiod]==188 for d in range(common)};period=common
 stages.append(dict(degree_period=newperiod,local_period=local,normalization_code=gamma,required=len(needed),passing=sum(v==188 for v in table.values()),uncovered=sum(not v for v in covered.values())))
result=dict(stages=stages,common_period=period,uncovered_residues=[d for d,v in covered.items() if not v],complete_bulk_cover=all(covered.values()))
a.out.write_text(json.dumps(result,indent=2)+'\n')
with a.csv.open('w') as f:
 w=csv.writer(f);w.writerow(['degree_residue','representative','rank','order_index'])
 for d,ok in covered.items():w.writerow([d,d,188 if ok else 0,0])
print(json.dumps(result))
