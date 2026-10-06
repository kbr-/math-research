#!/usr/bin/env python3
"""Exact polynomial certificates for the remaining fixed conic window matrices.
Two single-thread PARI processes share retained inputs. A series inverse proposes
C only; exact polynomial multiplication must verify A*C = u^h I mod u^(h+1).
Unresolved or singular truncated matrices are not nonnormality claims.
"""
import argparse
import concurrent.futures
import json
import re
import subprocess
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('--input',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args()
cases=[]
current=None
for line in args.input.read_text().splitlines():
    if line.startswith('CASE '):
        current={k:int(v) for k,v in re.findall(r'(exponent_class|precision|reduced_dimension)=(\d+)',line)}
    elif line.startswith('matrix='):
        current['matrix']=line.split('=',1)[1]
        cases.append(current)
assert cases and len({c['exponent_class'] for c in cases})==len(cases)
args.out.parent.mkdir(parents=True,exist_ok=True)

def audit(case):
    n=case['reduced_dimension']; p=case['precision']; ec=case['exponent_class']
    print(f'Audit class {ec}, dimension {n}',flush=True)
    gp=f'''default(parisizemax,3000000000);
default(nbthreads,1);
u;
F={case['matrix']};
audit()={{
my(A=matrix({n},{n},i,j,lift(F[i,j])),D=matdet(A));
if(D==0,print("UNRESOLVED exact polynomial matrix singular");return());
my(v=valuation(D,u),coef=lift(polcoef(D,v,u)));
print("ORDER=",v," COEFFICIENT=",coef);
my(R=matrix({n},{n},i,j,A[i,j]+O(u^{4*p}))^-1);
my(h=max(0,-vecmin(vector({n*n},k,valuation(R[(k-1)\\{n}+1,(k-1)%{n}+1],u)))));
print("POLE=",h);
if(h>={p},print("UNRESOLVED inverse poles reach entry precision");return());
for(i=1,{n},for(j=1,{n},if(serprec(R[i,j],u)<=0,error("inverse proposal lacks coefficients"))));
my(C=matrix({n},{n},i,j,Polrev(vector(h+1,k,polcoef(R[i,j],k-1-h,u)),u)));
my(E=A*C-u^h*matid({n}),orders=matrix({n},{n},i,j,valuation(E[i,j],u)));
if(vecmin(vector({n*n},k,orders[(k-1)\\{n}+1,(k-1)%{n}+1]))<=h,error("exact certificate failed"));
print("RIGHT_INVERSE_POLYNOMIAL=",C);
print("RESIDUAL_ORDERS=",orders);
print("PASS exact polynomial determinant and right inverse");
}};
audit();
quit;
'''
    path=args.out.with_name(args.out.stem+f'-class{ec}.txt')
    proc=subprocess.run(['gp','-q','-f'],input=gp,text=True,capture_output=True,timeout=150)
    path.write_text(proc.stdout+'\nSTDERR\n'+proc.stderr)
    assert proc.returncode==0 and 'at top-level' not in proc.stderr, f'class {ec}: {proc.stderr}'
    report={k:v for k,v in case.items() if k!='matrix'}|{'certificate':str(path)}
    order=re.search(r'ORDER=(\d+) COEFFICIENT=(\d+)',proc.stdout)
    pole=re.search(r'POLE=(\d+)',proc.stdout)
    if order:
        report|={'leading_order':int(order[1]),'leading_coefficient':int(order[2])}
    if pole:
        report['inverse_pole_bound']=int(pole[1])
    if 'PASS exact polynomial determinant' in proc.stdout:
        report['certified']=True
        report['determinant_error_order_at_least']=int(order[1])+p-int(pole[1])
    else:
        assert 'UNRESOLVED' in proc.stdout,proc.stdout
        report['certified']=False
    print(json.dumps(report),flush=True)
    return report

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    reports=list(pool.map(audit,cases))
args.out.write_text(json.dumps({'method':'verified exact polynomial right-inverse congruence','cases':reports},indent=2)+'\n')
