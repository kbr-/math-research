#!/usr/bin/env python3
"""Two original low-degree complements, with shared compiled PARI polynomial kernels."""
import argparse,concurrent.futures,json,os,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
def run(n):
 degrees=list(range(2,7 if n==9 else 8));env=os.environ.copy();env.update(BMD_DIMENSION=str(n),BMD_PRIME='31',BMD_EXTENSION='2',BMD_DEGREES=json.dumps(degrees),BMD_SEED=str(20261009+n))
 path=a.out/f'n{n}.txt';assert not path.exists()
 with path.open('w') as f:r=subprocess.run(['gp','-q','research/tools/bmd_nineteen_low_worker_20261009.gp'],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 t=path.read_text();assert r.returncode==0 and 'LOW_FIELD_FINISHED prime=31' in t and 'remaining=[]' in t
 m=re.search(r'FIELD_CODES (\d+) (\d+) (\[[^\n]*\])',t);assert m
 groups=[]
 for line in t.splitlines():
  mpoint=re.fullmatch(r'POINT_CODES trial=(\d+) labels=(\[.*\])',line)
  if mpoint:
   labels=json.loads(mpoint[2]);assert len(labels)==n and len(set(labels))==n and 0 not in labels;groups.append([labels,[]])
  cert=re.fullmatch(r'CERTIFIED d=(\d+) N=(\d+) determinant_code=(\d+)',line)
  if cert:groups[-1][1].append(list(map(int,cert.groups())))
 groups=[g for g in groups if g[1]];assert sorted(c[0] for g in groups for c in g[1])==degrees
 inp=a.out/f'n{n}-input.txt';lines=[' '.join(map(str,[n,31,2,*json.loads(m[3])])),str(len(groups))]
 for labels,cases in groups:lines+=[' '.join(map(str,labels)),str(len(cases)),*[' '.join(map(str,c)) for c in cases]]
 inp.write_text('\n'.join(lines)+'\n');print('ORIGINAL_COMPLEMENT',n,len(degrees),'nonzero',flush=True);return str(inp)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:inputs=list(pool.map(run,[9,10]))
(a.out/'manifest.txt').write_text('\n'.join(inputs)+'\n')
print('COMPLETE 11 original determinants; exact independent inputs saved')
