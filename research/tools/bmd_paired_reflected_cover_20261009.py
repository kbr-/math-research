#!/usr/bin/env python3
"""Certify all previous residual lifts with direct or proved reflected cut ranks."""
import argparse,csv,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prior',type=Path,required=True);p.add_argument('--log',type=Path,required=True);p.add_argument('--direct',type=Path,required=True);p.add_argument('--local-check',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--csv',type=Path,help='Complete coverage mask, not measured ranks');a=p.parse_args()
prior=json.loads(a.prior.read_text());P=prior['common_period'];residual=prior['uncovered_residues'];text=a.log.read_text()
m=re.search(r'LOCAL_PERIOD (\d+) DEGREE_PERIOD (\d+) NORMALIZATION_CODE (\d+)',text);assert m
local,Q,gamma=map(int,m.groups());assert 'full=1' in text and 'all_selected_ranks_FLINT_verified=true' in text
check=a.local_check.read_text();assert f'GAP_NORMALIZED_PERIOD {local} gamma_code={gamma} all512=true' in check
L=math.lcm(P,Q);g=math.gcd(P,Q);assert len(residual)*(L//P)<=1000000
lifts=[r+t*P for r in residual for t in range(L//P)];needed={d%Q for d in lifts}
crt={r+t*g for r in {d%g for d in residual} for t in range(Q//g)};assert needed==crt
rows=list(csv.DictReader(a.direct.open()));direct={int(r['degree_residue']):r for r in rows};assert len(direct)==len(rows)
expanded={};witnesses=[]
for d in sorted(needed):
 witness=d if d in direct else (6-d)%Q
 assert witness in direct
 row=direct[witness];assert int(row['representative'])%Q==witness
 expanded[d]=dict(rank=int(row['rank']),order_index=int(row['order_index']),direct_residue=witness,kind='direct' if witness==d else 'paired-cut-reflection')
assert set(direct)=={r['direct_residue'] for r in expanded.values()}
for d in sorted(lifts):witnesses.append(dict(common_residue=d,new_residue=d%Q,**expanded[d%Q]))
remaining=[w['common_residue'] for w in witnesses if w['rank']!=188]
report=dict(prior_period=P,local_period=local,degree_period=Q,normalization_code=gamma,common_period=L,crt_gcd=g,prior_residuals=residual,lift_count=len(lifts),required_states=len(needed),direct_states=len(direct),derived_states=sum(r['kind']!='direct' for r in expanded.values()),uncovered_residues=remaining,complete_bulk_cover=not remaining,witnesses=witnesses)
a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='witnesses'}))

if a.csv:
 bad=set(remaining)
 with a.csv.open('x') as f:
  w=csv.writer(f);w.writerow(['degree_residue','representative','rank','order_index'])
  for d in range(L):w.writerow([d,d,0 if d in bad else 188,0])
