#!/usr/bin/env python3
"""Exact finite remainder for the all-odd n9/n10 theorem, with explicit reuse.

Four single-thread PARI references share polynomial prefixes per point; their
stack caps total approximately8 GB. The separate four-worker FLINT/FFPACK stage
uses one modular BLAS factorization per point. Accepted pilot work is reused.
"""
import argparse
import concurrent.futures
from functools import lru_cache
import json
from math import comb,ceil
import os
from pathlib import Path
import re
import subprocess
import time

parser=argparse.ArgumentParser()
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--checker',type=Path,required=True)
parser.add_argument('--plan-only',action='store_true')
args=parser.parse_args()
plan=json.loads((args.out/'plan.json').read_text())
assert len(plan)==284 and plan[0][0]==101 and plan[-1][0]==2039
assert [p for p,_ in plan]==sorted({p for p,_ in plan})
@lru_cache(None)
def dimension(n,d):
    assert n in (9,10) and 2<=d<=n-3
    return sum(comb(n,s)*(1+(d-s)//2) for s in range(min(n,d)+1))
jobs=[]
for prime,parts in plan:
    assert len(parts)==2
    for n,degrees in zip((9,10),parts):
        assert degrees==sorted(set(degrees))
        if degrees:
            assert 2<=degrees[0] and degrees[-1]<=n-3
            jobs.append((n,prime,degrees))
assert len(jobs)==410 and sum(len(ds) for _,_,ds in jobs)==731

def reference_estimate(job):
    n,_,degrees=job
    sizes=[dimension(n,d) for d in degrees]
    # Calibrated by the identical n10 p101 degree6/7 point:4.68s total,
    # matrix times0.867s and1.697s, including a repeated-root control.
    return 1.25*(max(sizes)/1793)*(2**n/1024)+1.8*sum((x/1793)**2 for x in sizes)+1.8*(min(sizes)/1793)**2

def independent_estimate(job):
    n,_,degrees=job
    # Complete largest two-degree FLINT/FFPACK check, including control:0.67s.
    return .85*(max(dimension(n,d) for d in degrees)/1793)**2

estimate=dict(jobs=len(jobs),matrices=731,workers=4,pilot_reused=[10,101,[6,7]],
              reference_worker_seconds=sum(map(reference_estimate,jobs)),
              independent_worker_seconds=sum(map(independent_estimate,jobs)),
              measured_reference_seconds=4.68,measured_independent_seconds=.67,
              measured_reference_peak_kib=834104,measured_independent_peak_kib=78952)
estimate['wall_seconds_with_margin']=ceil(1.4*(estimate['reference_worker_seconds']+estimate['independent_worker_seconds'])/4+15)
(args.out/'sizing.json').write_text(json.dumps(estimate,indent=2)+'\n')
print('SIZED_PLAN',json.dumps(estimate,sort_keys=True),flush=True)
if args.plan_only:raise SystemExit(0)
assert args.checker.is_file()
references=args.out/'references';inputs=args.out/'inputs'
references.mkdir();inputs.mkdir()


def parse_reference(path,n,prime,degrees):
    text=path.read_text()
    assert f'LOW_FIELD_FINISHED prime={prime} certified={len(degrees)} remaining=[]' in text,path
    field=re.search(r'FIELD_CODES (\d+) (\d+) (\[[^\n]*\])',text)
    assert field and (int(field[1]),int(field[2]),json.loads(field[3]))==(prime,1,[0,1]),path
    groups=[]
    for line in text.splitlines():
        point=re.fullmatch(r'POINT_CODES trial=(\d+) labels=(\[.*\])',line)
        if point:
            labels=json.loads(point[2]);assert len(labels)==n and len(set(labels))==n and all(0<x<prime for x in labels)
            groups.append([labels,[]])
        value=re.fullmatch(r'CERTIFIED d=(\d+) N=(\d+) determinant_code=(\d+)',line)
        if value:
            d,N,det=map(int,value.groups());assert d in degrees and N==dimension(n,d) and 0<det<prime and groups
            groups[-1][1].append([d,N,det])
    groups=[g for g in groups if g[1]]
    assert sorted(c[0] for _,cs in groups for c in cs)==degrees
    assert 'repeated_root_zero=true' in text
    payload=[f'{n} {prime} 1 0 1',str(len(groups))]
    for labels,cases in groups:payload+=[' '.join(map(str,labels)),str(len(cases)),*[' '.join(map(str,c)) for c in cases]]
    output=inputs/f'n{n}-p{prime}.txt';output.write_text('\n'.join(payload)+'\n')
    return output,len(groups)


def reference(job):
    n,prime,degrees=job;begin=time.monotonic()
    reused=(n,prime)==(10,101)
    if reused:
        assert degrees==[6,7]
        path=args.out/'pilot/reference.txt'
    else:
        path=references/f'n{n}-p{prime}.txt'
        env=dict(os.environ,BMD_DIMENSION=str(n),BMD_PRIME=str(prime),BMD_EXTENSION='1',
                 BMD_DEGREES=json.dumps(degrees),BMD_SEED=str(20261009+n))
        with path.open('x') as output:
            result=subprocess.run(['gp','-q','research/tools/bmd_nineteen_low_worker_20261009.gp'],
                                  env=env,stdout=output,stderr=subprocess.STDOUT,timeout=60)
        assert result.returncode==0,f'Failed n={n} p={prime}; inspect {path}'
    input_path,points=parse_reference(path,n,prime,degrees)
    return dict(n=n,p=prime,degrees=degrees,input=str(input_path),reference=str(path),
                points=points,reused_pilot=reused,seconds=time.monotonic()-begin)

completed=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    futures=[pool.submit(reference,job) for job in sorted(jobs,key=reference_estimate,reverse=True)]
    try:
        for future in concurrent.futures.as_completed(futures):
            row=future.result();completed.append(row)
            print(f'REFERENCE_COMPLETE jobs={len(completed)}/410 n={row["n"]} p={row["p"]} determinants={len(row["degrees"])} reused={row["reused_pilot"]}',flush=True)
    except BaseException:
        for future in futures:future.cancel()
        raise
completed.sort(key=lambda r:(r['n'],r['p']))
assert len(completed)==410 and sum(len(row['degrees']) for row in completed)==731
pilot=next(row for row in completed if row['reused_pilot'])
assert Path(pilot['input']).read_text()==(args.out/'pilot/n10-p101-input.txt').read_text()
pilot_check=(args.out/'pilot/independent/n10-p101.txt').read_text()
assert 'COMPLETE count=2 one_prime_LU_per_point=true' in pilot_check
manifest=args.out/'new-independent-manifest.txt'
manifest.write_text('\n'.join(row['input'] for row in completed if not row['reused_pilot'])+'\n')
print('INDEPENDENT_START fields=409 new_determinants=729 reused_pilot_determinants=2 workers=4',flush=True)
check_log=args.out/'independent.txt'
with check_log.open('x') as output:
    result=subprocess.run([str(args.checker),str(manifest),str(args.out/'independent'),'4'],
                          stdout=output,stderr=subprocess.STDOUT,timeout=180)
text=check_log.read_text()
assert result.returncode==0 and 'COMPLETE independent_prime_determinants=729 fields=409 exact_modular_BLAS=true' in text,text[-3000:]
summary=dict(original_matrices=731,distinct_primes=284,field_dimension_jobs=410,
             reused_reference_determinants=2,reused_independent_determinants=2,
             new_independent_matches=729,independent_matches=731,
             complete_prime_divisor_scope=True,jobs=completed,sizing=estimate)
(args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('COMPLETE original_determinants=731 independent_matches=731 primes=284 fields=410 no_unresolved_cases=true',flush=True)
