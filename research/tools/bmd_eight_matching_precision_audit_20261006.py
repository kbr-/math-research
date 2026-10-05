#!/usr/bin/env python3
"""Certify the order417 determinant coefficient from entry precision192.
SciPy solves exact small integer assignment problems; PARI checks the polynomial
determinant and direct series cofactors. No floating-point rank or Python algebra kernel.
"""
import argparse
import itertools
import json
import re
import subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment

ap=argparse.ArgumentParser()
ap.add_argument("--input",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
args=ap.parse_args()
lines=args.input.read_text().splitlines()
def one(prefix):
    hits=[s[len(prefix):] for s in lines if s.startswith(prefix)]
    assert len(hits)==1,(prefix,len(hits))
    return hits[0]
prec=int(re.match(r"(\d+)",one("precision="))[1])
leading=int(re.match(r"(\d+)",one("leading_order="))[1])
matrix=one("matrix=")
def parse_matrix(raw):
    return [[int(x.strip()) for x in row.split(",")] for row in raw.strip().strip("[]").split(";")]
weights=np.array(parse_matrix(one("entry_valuations=")),dtype=np.int64)
n=len(weights)
assert n==22 and prec==192 and leading==417
assert np.all((weights>=0)&(weights<=prec))
costs=np.zeros((n,n),dtype=np.int64)
for i,j in itertools.product(range(n),repeat=2):
    small=np.delete(np.delete(weights,i,axis=0),j,axis=1)
    rr,cc=linear_sum_assignment(small)
    costs[i,j]=int(small[rr,cc].sum())
# At least two errors: a minimum matching of size n-2 for the unchanged factors.
k=2
aug=np.zeros((n+k,n+k),dtype=np.int64)
aug[:n,:n]=weights
aug[n:,n:]=1000000
rr,cc=linear_sum_assignment(aug)
assert np.count_nonzero((rr<n)&(cc<n))==n-k
two_error=2*prec+int(aug[rr,cc].sum())
three_error=3*prec
print(f"assignment one-error={prec+int(costs.min())}; two-error={two_error}; >=3 errors={three_error}",flush=True)
gp=f"""default(parisizemax,3000000000);
default(nbthreads,1);
u;
F={matrix};
FP=matrix({n},{n},i,j,lift(F[i,j]));
FS=matrix({n},{n},i,j,FP[i,j]+O(u^{prec}));
DS=matdet(FS);
print("SERIES order=",valuation(DS,u)," coefficient=",polcoef(DS,valuation(DS,u),u));
EX=matdet(FP);
if(valuation(EX,u)!={leading} || polcoef(EX,{leading},u)!=Mod(1,3),error("exact determinant mismatch"));
print("EXACT polynomial determinant order={leading}, coefficient=1");
AD=matrix({n},{n},i,j,(-1)^(i+j)*matdet(matrix({n-1},{n-1},r,c,FS[r+(r>=j),c+(c>=i)])));
CHK=FS*AD-DS*matid({n});
for(i=1,{n},for(j=1,{n},if(valuation(CHK[i,j],u)<min(serprec(DS,u),vecmin(vector({n},k,min(serprec(FS[i,k],u)+valuation(AD[k,j],u),valuation(FS[i,k],u)+serprec(AD[k,j],u))))),error("adjugate identity"))));
print("AD_IDENTITY all known coefficients vanish; minimum precision=",vecmin(vector({n*n},k,serprec(CHK[(k-1)\\{n}+1,(k-1)%{n}+1],u))));
AV=matrix({n},{n},i,j,valuation(AD[i,j],u));
AP=matrix({n},{n},i,j,serprec(AD[i,j],u));
print("AD_ORDERS=",AV);
print("AD_PRECISIONS=",AP);
{{
my(best=100000,ii=0,jj=0);
for(i=1,{n},for(j=1,{n},if(AV[i,j]<best,best=AV[i,j];ii=i;jj=j)));
my(CF=(-1)^(ii+jj)*matdet(matrix({n-1},{n-1},r,c,FP[r+(r>=jj),c+(c>=ii)])));
if(valuation(CF,u)!=best || valuation(CF-AD[ii,jj],u)<AP[ii,jj],error("independent exact cofactor mismatch"));
print("DIRECT minimum-cofactor check position=",ii,",",jj," order=",best," precision=",serprec(CF,u));
}}
print("PASS_AD");
quit;
"""
args.out.parent.mkdir(parents=True,exist_ok=True)
proc=subprocess.run(["gp","-q","-f"],input=gp,text=True,capture_output=True,timeout=160)
args.out.with_suffix(".gp-output.txt").write_text(proc.stdout+"\nSTDERR\n"+proc.stderr)
assert proc.returncode==0 and "PASS_AD" in proc.stdout and "at top-level" not in proc.stderr,proc.stdout+proc.stderr
def gp_line(prefix):
    vals=[s[len(prefix):] for s in proc.stdout.splitlines() if s.startswith(prefix)]
    assert len(vals)==1
    return vals[0]
orders=np.array(parse_matrix(gp_line("AD_ORDERS=")),dtype=np.int64)
precisions=np.array(parse_matrix(gp_line("AD_PRECISIONS=")),dtype=np.int64)
assert orders.shape==(n,n) and precisions.shape==(n,n)
single=prec+int(np.minimum(orders,precisions).min())
bound=min(single,two_error,three_error)
assert leading<bound,(leading,bound)
result={"passed":True,"dimension":n,"entry_precision":prec,"leading_order":leading,
"leading_coefficient":1,"one_error_assignment_bound":prec+int(costs.min()),
"one_error_cofactor_bound":single,"two_error_assignment_bound":two_error,
"at_least_three_error_bound":three_error,"error_order_at_least":bound,
"assignment_minor_costs":costs.tolist(),"cofactor_orders":orders.tolist(),"cofactor_precisions":precisions.tolist()}
args.out.write_text(json.dumps(result,indent=2)+"\n")
print(f"PASS: order {leading} coefficient1; omitted-entry errors start at least at {bound}",flush=True)
