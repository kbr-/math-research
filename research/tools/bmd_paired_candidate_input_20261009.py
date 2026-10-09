#!/usr/bin/env python3
"""Choose a bounded exact marked-order candidate from a completed prime-field search."""
import argparse,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--selection',type=Path,required=True);p.add_argument('--prime',type=int,required=True);p.add_argument('--bound',type=int,required=True);p.add_argument('--modulus',type=int,nargs=3,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
assert 17<=a.prime<=97 and all(a.prime%d for d in range(2,math.isqrt(a.prime)+1))
assert a.bound%32==0 and 32<=a.bound<=672
m0,m1,m2=a.modulus;assert m2==1 and 0<=m0<a.prime and 0<=m1<a.prime
assert pow((m1*m1-4*m0)%a.prime,(a.prime-1)//2,a.prime)==a.prime-1
text=a.selection.read_text();assert 'COMPLETE selected=' in text and f'BMD_PRIME={a.prime}' in text
candidates=[]
for line in text.splitlines():
 m=re.fullmatch(r'INPUT (\[.*?\]) marked_orders=(\[.*?\]) bound=(\d+)',line)
 if m and int(m[3])==a.bound:
  labels,orders=json.loads(m[1]),json.loads(m[2]);assert len(set(labels))==4 and labels[0]==1 and all(0<v<a.prime for v in labels)
  assert len(orders)==5 and all(r>0 for r in orders)
  assert math.lcm(32,8*math.lcm(*(r//math.gcd(r,8) for r in orders)))==a.bound
  candidates.append((labels,orders))
assert candidates;labels,orders=candidates[0];step=a.bound//32;degrees=list(range(3,4+step//2))
assert not a.out.exists() and not a.out.with_suffix('.json').exists()
a.out.write_text(f'{a.prime} {a.bound} {len(degrees)}\n'+' '.join(map(str,degrees))+'\n'+' '.join(map(str,labels))+'\n'+' '.join(map(str,a.modulus))+'\n')
report=dict(source=str(a.selection),prime=a.prime,slopes=labels,marked_orders=orders,torsion_pole=a.bound,step=step,references=degrees,modulus=a.modulus,candidates_at_bound=len(candidates))
a.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
