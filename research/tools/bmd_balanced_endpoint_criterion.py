#!/usr/bin/env python3
"""Analyze the saved generic mixed basis, not a new dimension or parameter test.

The only Python work is bounded text extraction and orchestration (seconds).
PARI performs exact symbolic ranks and determinants over F3(b,c,d).
The question is whether generic normality reduces to the two rational endpoint
constraints on x^-9,x^-7,x^9,x^11, with the seven middle odd powers retained.
"""
from pathlib import Path
import subprocess
import tempfile

source = Path("research/results/cube-balanced-smoothing-review-20260928/generic-mixed.txt")
matches = [line.split(" = ", 1)[1] for line in source.read_text().splitlines()
           if line.startswith("GENERIC_LIMIT_BASIS = ")]
assert len(matches) == 1
program = r"""
default(parisizemax,512000000);
default(parisize,128000000);
y='y;b='b;c='c;d='d;
B=__BASIS__;
{
my(one=Mod(1,3),ends=[7,8,16,17],Q=matrix(2,4,i,j,polcoef(B[7+i],ends[j],y)));
for(i=1,9,if(poldegree(B[i],y)>17,error("upper pole bound")));
for(i=1,9,for(j=0,6,if(polcoef(B[i],j,y)!=0,error("lower pole bound"))));
for(i=1,7,for(j=1,4,if(polcoef(B[i],ends[j],y)!=0,error("middle rows have endpoints"))));
my(mid=matrix(7,7,i,j,polcoef(B[i],j+8,y)));
if(matrank(mid)!=7,error("middle span incomplete"));
my(R=matrix(4,4,i,j,if(i<=2,Q[i,j],if(i==3,if(j==1||j==3,one,0*one),if(j==2||j==4,one,0*one)))));
print("GENERIC_MIDDLE_ODD_RANK = ",matrank(mid));
print("ENDPOINT_EXPONENTS = [-9,-7,9,11]");
print("GENERIC_ENDPOINT_ROWS = ",Q);
print("GENERIC_ENDPOINT_TEST_MATRIX = ",R);
my(dd=matdet(R));
print("GENERIC_ENDPOINT_TEST_DETERMINANT = ",dd);
print("GENERIC_ENDPOINT_TEST_NONZERO = ",dd!=0);
my(db=one*b*(b-1),dc=one*c*d*(c-d));
my(coupling=db^2*(b+1)^3+dc^2*(c+d)^3);
my(pred=dc*db^2*(b+1)*coupling);
if(dd!=pred,error("endpoint factorization failed"));
print("ENDPOINT_FACTORIZATION_VERIFIED = 1");
print("FACTORIZATION = DeltaC * DeltaB^2 * (b+1) * (DeltaB^2*(b+1)^3 + DeltaC^2*(c+d)^3)");
print("DeltaB=b*(b-1); DeltaC=c*d*(c-d)");
my(sb=b+1,sc=c+d);
my(NQ=[-dc^2*sb,0*one,0*one,db^2*sc;0*one,one*sc^4,one*sb^4,0*one]);
my(both=matrix(4,4,i,j,if(i<=2,Q[i,j],NQ[i-2,j])));
if(matrank(NQ)!=2||matrank(both)!=2,error("normalized endpoint rowspace mismatch"));
my(NR=matrix(4,4,i,j,if(i<=2,NQ[i,j],R[i,j])));
if(matdet(NR)!=-one*sb*sc*coupling,error("normalized endpoint determinant mismatch"));
print("NORMALIZED_ENDPOINT_ROWS = ",NQ);
print("NORMALIZED_ROWSPACE_EQUAL = 1");
print("NORMALIZED_DETERMINANT = -(b+1)*(c+d)*(DeltaB^2*(b+1)^3+DeltaC^2*(c+d)^3)");
if(dd==0,error("generic endpoint criterion failed"));
print("GENERIC_ENDPOINT_CRITERION_COMPLETED");
}
quit;
""".replace("__BASIS__", matches[0])
with tempfile.TemporaryDirectory(prefix="bmd-endpoint-") as tmp:
    driver = Path(tmp) / "criterion.gp"
    driver.write_text(program)
    result = subprocess.run(["gp", "-fq", str(driver)], check=True, capture_output=True, text=True)
    print(result.stdout, end="")
    print(result.stderr, end="")
    if "GENERIC_ENDPOINT_CRITERION_COMPLETED" not in result.stdout:
        raise SystemExit("PARI did not finish the endpoint checks")
