#!/usr/bin/env python3
"""Certify upper-outlier window determinants with verified polynomial right inverses.
PARI proposes a truncated inverse, but acceptance uses only exact polynomial
multiplication: F*B = u^h I mod u^(h+1). This bounds every inverse pole by h.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path
ap=argparse.ArgumentParser()
ap.add_argument("--input",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
args=ap.parse_args()
cases=[]
current=None
for line in args.input.read_text().splitlines():
    if line.startswith("CASE "):
        current={k:int(v) for k,v in re.findall(r"(exponent_class|precision|reduced_dimension)=(\d+)",line)}
    elif line.startswith("matrix="):
        current["matrix"]=line.split("=",1)[1]
    elif line.startswith("leading_order="):
        current["leading_order"]=int(re.search(r"leading_order=(\d+)",line)[1])
        current["leading_coefficient"]=int(re.search(r"Mod\((\d+), 3\)",line)[1])
        cases.append(current)
        current=None
cases=[case for case in cases if case["exponent_class"] in (11,26)]
assert [case["exponent_class"] for case in cases]==[11,26]
reports=[]
args.out.parent.mkdir(parents=True,exist_ok=True)
for case in cases:
    n=case["reduced_dimension"]
    p=case["precision"]
    val=case["leading_order"]
    coef=case["leading_coefficient"]
    print(f"Audit class {case['exponent_class']}, dimension {n}",flush=True)
    gp=f"""default(parisizemax,3000000000);
default(nbthreads,1);
u;
F={case['matrix']};
FP=matrix({n},{n},i,j,lift(F[i,j]));
D=matdet(FP);
if(valuation(D,u)!={val} || polcoef(D,{val},u)!=Mod({coef},3),error("exact determinant mismatch"));
R=matrix({n},{n},i,j,FP[i,j]+O(u^{4*p}))^-1;
h=max(0,-vecmin(vector({n*n},k,valuation(R[(k-1)\\{n}+1,(k-1)%{n}+1],u))));
if(h>={p},error("inverse pole exceeds entry precision"));
for(i=1,{n},for(j=1,{n},if(serprec(R[i,j],u)<=0,error("inverse proposal lacks required coefficients"))));
B=matrix({n},{n},i,j,Polrev(vector(h+1,k,polcoef(R[i,j],k-1-h,u)),u));
C=FP*B-u^h*matid({n});
orders=matrix({n},{n},i,j,valuation(C[i,j],u));
if(vecmin(vector({n*n},k,orders[(k-1)\\{n}+1,(k-1)%{n}+1]))<=h,error("exact polynomial right-inverse certificate failed"));
print("POLE=",h);
print("RIGHT_INVERSE_POLYNOMIAL=",B);
print("RESIDUAL_ORDERS=",orders);
print("PASS exact determinant order={val} coefficient={coef}; exact polynomial product congruence");
quit;
"""
    proc=subprocess.run(["gp","-q","-f"],input=gp,text=True,capture_output=True,timeout=150)
    path=args.out.with_name(args.out.stem+f"-class{case['exponent_class']}.txt")
    path.write_text(proc.stdout+"\nSTDERR\n"+proc.stderr)
    assert proc.returncode==0 and "PASS exact determinant" in proc.stdout and "at top-level" not in proc.stderr,proc.stdout+proc.stderr
    pole=int(re.search(r"^POLE=(\d+)$",proc.stdout,re.M)[1])
    bound=val+p-pole
    assert pole<p and bound>val
    reports.append({k:v for k,v in case.items() if k!="matrix"}|{"inverse_pole_bound":pole,"determinant_error_order_at_least":bound,"certificate":str(path)})
    print(f"PASS class {case['exponent_class']}: order {val}, error >= {bound}, inverse poles <= {pole}",flush=True)
args.out.write_text(json.dumps({"passed":True,"method":"verified polynomial right-inverse congruence","cases":reports},indent=2)+"\n")
