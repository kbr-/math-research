#!/usr/bin/env python3
"""Exact integer extraction from saved six-root QQ rank certificates.

No new rank or unproved continuation: certify degreewise full-ring injectivity
only when an observed t^e quotient is injective, using induction and division
by t^e in the free source/target. Small integer Hilbert convolution (<5000
additions) interprets those exact ranks and the graded PID increments.
"""
import argparse, ast, json, re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--completed');args=p.parse_args()
paths=[Path('research/results/bmd-six-torsion-thickenings-20261007/first-two.txt'),Path('research/results/bmd-six-torsion-thickenings-20261007/through-three.txt')]
if args.completed:paths.append(Path(args.completed))
records={};observed={}
for path in paths:
    for line in path.read_text().splitlines():
        if line.startswith('THICKENING_DATA='):
            e,data=ast.literal_eval(line.split('=',1)[1].replace('{','[').replace('}',']'))
            if e in records:assert records[e]==dict(data)
            records[e]=dict(data)
        m=re.fullmatch(r'THICKENING e=(\d+) weight=(\d+) rows=(\d+) cols=(\d+) gammaRank=(\d+) hidden=(\d+) quotient=(\d+) cpu=.*',line)
        if m:
            e,d,r,c,k,h,q=map(int,m.groups());observed[e,d]=(r,c,k,h,q)
assert sorted(records)==list(range(1,max(records)+1)) and max(records)>=3
lengths={e:sum(data.values()) for e,data in records.items()}
births={}
for e in records:
    prev=records.get(e-1,{})
    birth={d-2*(e-1):records[e].get(d,0)-prev.get(d,0) for d in range(0,34+2*(e-1))}
    assert all(v>=0 for v in birth.values())
    births[e]={d:v for d,v in birth.items() if v}
    if e>1:assert all(v<=births[e-1].get(d,0) for d,v in births[e].items())
known_torsion={e:{d:births[e].get(d,0)-births[e+1].get(d,0) for d in sorted(set(births[e])|set(births[e+1])) if births[e].get(d,0)!=births[e+1].get(d,0)} for e in range(1,max(records))}
cap=35;mon=[0]*(cap+1);mon[0]=1
for w in (2,3,4,5,6):
    for d in range(w,cap+1):mon[d]+=mon[d-w]
def coeff(d):return mon[d] if d>=0 else 0
def upper(d):
    m=(d-4)//2
    return max(d-8,0)+((m+1)*(m+2)//2 if d>=4 else 0)
def image(d):return sum(d>=w and (d-w)%2==0 for w in (12,13,13,14,14,15))+(d==14)
full=[];independent=set(range(11));proof=[]
for d in range(11,cap+1):
    good=[e for (e,dd),(r,c,k,h,q) in observed.items() if dd==d and c==k and d-2*e in independent]
    assert good,('no full-ring injectivity certificate',d)
    e=min(good);independent.add(d);proof.append({'degree':d,'quotient_exponent':e,'lower_degree':d-2*e})
    free=sum(coeff(d-w) for w in (4,5,6,6,7,8))
    cyclic=sum(coeff(d-w) for w in range(11,d+1))
    h=free-cyclic-upper(d)-image(d)
    assert h>=0
    full.append([d,h])
result={'lengths':lengths,'surviving_births':births,'exact_torsion_births':known_torsion,'full_ring_injectivity':proof,'full_kernel_hilbert_through35':full,'scope':'Only saved exact ranks and proved degreewise injectivity lifting; no torsion cutoff beyond the displayed implications.'}
if args.completed:
    final=max(records);free=births[final];assert sum(free.values())==48
    relations={};torsion_length=0;count=0
    for e,group in known_torsion.items():
        for d,m in group.items():
            relations[d+2*e]=relations.get(d+2*e,0)+m
            count+=m;torsion_length+=e*m
    assert count==136 and count+sum(free.values())==sum(births[1].values())
    result.update(free_births=free,torsion_summands=count,torsion_length=torsion_length,
                  parameter_relation_weights=dict(sorted(relations.items())),
                  max_parameter_relation_weight=max(relations),max_torsion_exponent=max(e for e,g in known_torsion.items() if g))
    result['scope']='Complete graded A-module Smith data from the certified rank squeeze; four full S-actions remain separate.'
out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
