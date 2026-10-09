#!/usr/bin/env python3
"""Run only finite complements not settled by the exact joint-leading filter.
Each dimension-ten skip requires its two lower dimension-nine degrees; a complete n9 theorem suffices but is not necessary.
PARI shares all root/subset prefixes within each dimension; Python only orchestrates.
"""
import argparse,concurrent.futures,json,os,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prime',type=int,required=True);p.add_argument('--filter',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--verify-existing',action='store_true');a=p.parse_args()
assert 17<=a.prime<=97
# Legacy filter marker records a stronger sufficient premise; actual prerequisites are
# the finite parent degrees derived below, to be certified separately in the proof.
m=re.fullmatch(r'FILTER_PRIME=(\d+);DIRECT_DEGREES=(.*);ASSUMES_N9_COMPLETE=1;\s*',a.filter.read_text());assert m and int(m[1])==a.prime
plan=json.loads(m[2]);assert isinstance(plan,list) and len(plan)==2
jobs=[]
for n,degrees in zip([9,10],plan):
 assert isinstance(degrees,list) and degrees==sorted(set(degrees)) and all(isinstance(d,int) and 2<=d<=(6 if n==9 else 7) for d in degrees)
 if degrees:jobs.append((n,degrees))
a.out.mkdir(parents=True,exist_ok=True)
parents=sorted({d-k for d in range(2,8) if d not in plan[1] for k in (0,1)})
print('FILTERED_PLAN',a.prime,json.dumps(plan),'required_n9_parent_degrees',parents,'verify_existing',a.verify_existing,flush=True)
def run(job):
 n,degrees=job;env=os.environ.copy();env.update(BMD_DIMENSION=str(n),BMD_PRIME=str(a.prime),BMD_EXTENSION='2',BMD_DEGREES=json.dumps(degrees),BMD_SEED=str(20261009+n))
 path=a.out/f'n{n}.txt'
 if not a.verify_existing:
  assert not path.exists()
  with path.open('w') as f:r=subprocess.run(['gp','-q','research/tools/bmd_nineteen_low_worker_20261009.gp'],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  assert r.returncode==0
 t=path.read_text();assert f'LOW_FIELD_FINISHED prime={a.prime}' in t and 'remaining=[]' in t
 field=re.search(r'FIELD_CODES (\d+) (\d+) (\[[^\n]*\])',t);assert field and int(field[1])==a.prime and int(field[2])==2
 groups=[]
 for line in t.splitlines():
  point=re.fullmatch(r'POINT_CODES trial=(\d+) labels=(\[.*\])',line)
  if point:
   labels=json.loads(point[2]);assert len(labels)==n and len(set(labels))==n and 0 not in labels;groups.append([labels,[]])
  cert=re.fullmatch(r'CERTIFIED d=(\d+) N=(\d+) determinant_code=(\d+)',line)
  if cert:
   case=list(map(int,cert.groups()));assert case[2]>0;groups[-1][1].append(case)
 groups=[g for g in groups if g[1]];assert sorted(c[0] for g in groups for c in g[1])==degrees
 inp=a.out/f'n{n}-input.txt';lines=[' '.join(map(str,[n,a.prime,2,*json.loads(field[3])])),str(len(groups))]
 for labels,cases in groups:lines+=[' '.join(map(str,labels)),str(len(cases)),*[' '.join(map(str,c)) for c in cases]]
 payload='\n'.join(lines)+'\n'
 if inp.exists():assert inp.read_text()==payload
 else:inp.write_text(payload)
 print('ORIGINAL_COMPLEMENT',n,len(degrees),'nonzero',flush=True);return str(inp)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:inputs=list(pool.map(run,jobs))
(a.out/'manifest.txt').write_text('\n'.join(inputs)+('\n' if inputs else ''))
(a.out/'summary.json').write_text(json.dumps(dict(prime=a.prime,direct_degrees=plan,direct_count=sum(map(len,plan)),skipped_by_joint_coefficient=11-sum(map(len,plan)),dimension_ten_required_nine_degrees=parents,legacy_complete_nine_marker_not_required=True,verified_existing_results=a.verify_existing),indent=2)+'\n')
print('COMPLETE',sum(map(len,plan)),'original determinants; exact independent inputs saved',flush=True)
