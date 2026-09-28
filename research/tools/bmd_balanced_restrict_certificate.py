#!/usr/bin/env python3
"""Restrict the saved generic 3+3 certificate to equal/opposite slope families.

This is a symbolic restriction over F3(b), not another dimension or numerical
sample. Eight saved constant transforms must remain defined and invertible;
the normalized final endpoint plane must remain rank two. Then saturation
commutes with these specified restrictions. Python only extracts bounded text.
"""
from pathlib import Path
import subprocess
import tempfile

src=Path("research/results/cube-balanced-smoothing-review-20260928/generic-mixed.txt")
rows=[]
for line in src.read_text().splitlines():
    if line.startswith("PIVOT_ROWS = "):
        left,right=line.split("; KERNEL_ROWS = ",1)
        rows.append((left.split(" = ",1)[1],right))
assert len(rows)==8
basis=[line.split(" = ",1)[1] for line in src.read_text().splitlines() if line.startswith("GENERIC_LIMIT_BASIS = ")]
assert len(basis)==1
program=[
"default(parisizemax,256000000);",
"default(parisize,64000000);",
"y='y;b='b;c='c;d='d;",
"B="+basis[0]+";",
"pivs=["+",".join(x for x,_ in rows)+"];",
"kers=["+",".join(y for _,y in rows)+"];",
r"""
{
my(one=Mod(1,3),nr=9,db=one*b*(b-1));
for(signcase=1,2,
 my(sgn=if(signcase==1,one,-one),nc=sgn,nd=sgn*b);
 print("SLOPE_RESTRICTION c=",nc," d=",nd);
 for(k=1,#pivs,
  my(ix=pivs[k],rk=#ix,K=kers[k]);
  my(P=matrix(nr,nr,i,j,if(i<=rk,if(j==ix[i],one,0*one),K[i-rk,j])));
  my(Q=subst(subst(P,c,nc),d,nd),dd=matdet(Q));
  if(dd==0,error("restricted transform singular"));
  print("TRANSFORM ",k," DEFINED_INVERTIBLE = 1");
 );
 my(sb=b+1,sc=nc+nd,dc=nc*nd*(nc-nd));
 my(Q=[-dc^2*sb,0*one,0*one,db^2*sc;0*one,one*sc^4,one*sb^4,0*one]);
 if(matrank(Q)!=2,error("restricted endpoint plane loses rank"));
 my(Bspec=subst(subst(B,c,nc),d,nd),frame=matrix(9,25,i,j,polcoef(Bspec[i],j-1,y)));
 if(matrank(frame)!=9,error("full restricted residue basis loses rank"));
 my(ends=[7,8,16,17],actual=matrix(2,4,i,j,polcoef(Bspec[7+i],ends[j],y)));
 my(both=matrix(4,4,i,j,if(i<=2,actual[i,j],Q[i-2,j])));
 if(matrank(actual)!=2||matrank(both)!=2,error("restricted normal form mismatch"));
 print("FULL_RESTRICTED_RESIDUE_RANK = 9");
 print("RESTRICTED_NORMAL_FORM_EQUAL = 1");
 my(coupling=db^2*sb^3+dc^2*sc^3);
 print("ENDPOINT_PLANE_RANK = 2");
 print("COUPLING = ",coupling);
 if(signcase==1 && coupling==0,error("equal-slope coupling zero"));
 if(signcase==2 && coupling!=0,error("mirror coupling nonzero"));
 print("RESTRICTION_VERIFIED = 1");
);
print("GENERIC_CERTIFICATE_RESTRICTIONS_COMPLETED");
}
quit;
"""
]
with tempfile.TemporaryDirectory(prefix="bmd-restrict-") as tmp:
    driver=Path(tmp)/"restrict.gp"
    driver.write_text("\n".join(program))
    result=subprocess.run(["gp","-fq",str(driver)],capture_output=True,text=True,check=True)
    print(result.stdout,end="")
    print(result.stderr,end="")
    if "GENERIC_CERTIFICATE_RESTRICTIONS_COMPLETED" not in result.stdout:
        raise SystemExit("PARI did not complete certificate restrictions")
