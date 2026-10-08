#!/usr/bin/env python3
"""Orchestrate bounded PARI low-degree fields, sharing every field's root prefixes."""
import argparse,concurrent.futures,json,os,re,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--workers',type=int,default=3);a=p.parse_args()
assert 1<=a.workers<=3
jobs=json.loads(a.spec.read_text());a.out.mkdir(parents=True,exist_ok=True)
assert isinstance(jobs,list) and len(jobs)<=12
for j in jobs:
    assert j['prime'] in [3,5,7,11,13,17] and 1<=j['extension']<=6
    assert j['degrees'] and len(set(j['degrees']))==len(j['degrees']) and all(isinstance(d,int) and 2<=d<=7 for d in j['degrees'])
    assert isinstance(j['seed'],int)
def run(j):
    tag=f"p{j['prime']}-f{j['extension']}";path=a.out/(tag+'.txt')
    assert not path.exists(),'preserve earlier output'
    env=os.environ.copy();env.update(BMD_PRIME=str(j['prime']),BMD_EXTENSION=str(j['extension']),BMD_DEGREES=json.dumps(j['degrees']),BMD_SEED=str(j['seed']))
    start=time.monotonic();print('FIELD_STARTED',tag,'degrees',j['degrees'],flush=True)
    with path.open('w') as f:
        try:r=subprocess.run(['gp','-q','research/tools/bmd_ten_low_worker_20261009.gp'],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240);status=r.returncode
        except subprocess.TimeoutExpired:status=124
    text=path.read_text();m=re.search(r'LOW_FIELD_FINISHED prime=(\d+) certified=(\d+) remaining=(\[[^\n]*\])',text)
    result=dict(j,output=str(path),seconds=time.monotonic()-start,returncode=status,finished=bool(m))
    if m:
        result.update(certified=int(m[2]),remaining=json.loads(m[3]));assert int(m[1])==j['prime']
    print('FIELD_FINISHED',tag,json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:results=list(pool.map(run,jobs))
(a.out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['returncode']==0 and r['finished'] for r in results),'a field job failed; inspect complete logs'
print('LOW_SERIES_FINISHED',sum(r['certified'] for r in results),'certificates; unresolved',sum(len(r['remaining']) for r in results),flush=True)
