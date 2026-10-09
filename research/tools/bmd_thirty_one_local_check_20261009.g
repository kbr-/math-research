# Load LOCAL_CERTIFICATE first; normalize by its first nonzero geometric branch value.
r:=LOCAL_CERTIFICATE;;deg:=r[1];;fq:=GF(31^deg);;o:=One(fq);;z:=Zero(fq);;x:=Indeterminate(fq,"x");;
b:=RootsOfPolynomial(fq,Sum([0..deg],j->r[2][j+1]*x^j))[1];;
decode:=c->Sum([0..deg-1],j->(QuoInt(c,31^j) mod 31)*b^j);;
y:=Indeterminate(fq,"y");;iy:=IndeterminateNumberOfUnivariateRationalFunction(y);;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(o),v,iy);;
if decode(r[4][1])=z then Error("nonzero reference branch value");fi;
gamma:=decode(r[4][1])^-1;;
gammaCode:=First([0..31^deg-1],c->decode(c)=gamma);;
off:=0;;
for L in [15,15,15,15,4] do for point in [1..8] do
 h:=poly(List(r[4]{[off+1..off+L]},decode));;
 if PowerMod(gamma*h,r[5],y^L)<>o*y^0 then Error("complete normalized local period");fi;
 off:=off+L;
od;od;
if off<>512 then Error("complete local algebra");fi;
Print("GAP_NORMALIZED_PERIOD ",r[5]," gamma_code=",gammaCode," all512=true\n");
Print("GAP_LOCAL_CERTIFICATE_COMPLETED\n");
QUIT;
