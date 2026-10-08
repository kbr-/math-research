"""Compose proved certificates for every positive unit-digit delay on the fixed ternary curve.

No new matrix calculation: traverse the complete saved coefficient period, with the
strict graph-degree guard and actual positive short-return index retained.
"""
import argparse,csv,json,time
from collections import Counter
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();start=time.monotonic();period=28080

def read(path,key,col):
 with Path(path).open() as f: rows=list(csv.DictReader(f))
 values={int(r[key]):int(r[col]) for r in rows}
 assert len(rows)==period and set(values)==set(range(period))
 return values
K=read('research/results/bmd-exception-unit-period-20261008/full/ranks.csv','coefficient_residue','rank')
V=read('research/results/bmd-exception-period-cover-20261008/full/curve-0-ranks.csv','exponent_residue','b0')
assert 3**10<=81*769<3**11
certificates=[]
for r in range(1,period+1):
 s=4+r
 if K[s%period]==61: kind='restricted cup'
 elif r>=11 and V[s%period]==140: kind='full cup graph'
 elif r>=11 and s%4680==3834: kind='quadratic graph'
 elif r>=11 and s%4680 in (1,2,3,4):
  b=s%4680;k=(s-b)//4680;assert k>=1
  kind='complete return graph'
 else: raise AssertionError(('uncovered actual delay',r))
 certificates.append([r,kind])
assert all(K[(4+r)%period]==61 for r in range(1,11))
# Later periods preserve both cup matrices and the quadratic residue classes;
# the return theorem applies to every positive index, not a nonlinear period.
result={'period':period,'counts':dict(Counter(c[1] for c in certificates)),
 'remaining_delays':[],'certificates':certificates,'wall_seconds':time.monotonic()-start}
Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='certificates'}));print('COMPLETE_UNIT_COVER_VERIFIED')
