# Load a LOCAL_CERTIFICATE data file first. Independently check every geometric fibre.
r:=LOCAL_CERTIFICATE;;deg:=r[1];;fq:=GF(13^deg);;o:=One(fq);;z:=Zero(fq);;x:=Indeterminate(fq,"x");;
b:=RootsOfPolynomial(fq,Sum([0..deg],j->r[2][j+1]*x^j))[1];;
decode:=c->Sum([0..deg-1],j->(QuoInt(c,13^j) mod 13)*b^j);;
y:=Indeterminate(fq,"y");;iy:=IndeterminateNumberOfUnivariateRationalFunction(y);;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(o),v,iy);;
off:=0;;scales:=[];;
for L in [15,15,15,15,4] do
 scale:=fail;;
 for point in [1..8] do
  h:=poly(List(r[4]{[off+1..off+L]},decode));;v:=PowerMod(h,r[5],y^L);;
  c:=CoefficientsOfUnivariatePolynomial(v);;
  if Length(c)<>1 or c[1]=z then Error("scalar germ through full local length");fi;
  if scale=fail then scale:=c[1];elif scale<>c[1] then Error("same scalar at all eight sign points");fi;
  off:=off+L;
 od;
 Add(scales,scale);
od;
if off<>512 then Error("complete local algebra");fi;
Print("GAP_FIBRE_SCALAR_PERIOD ",r[5]," all512=true scales=",scales,"\n");
if Length(Set(scales))<>1 then Error("one global scalar required for normalization");fi;
gammaInt:=First([1..12],c->(c*o)^r[5]*scales[1]=o);;
if gammaInt=fail then Error("prime-field normalization missing");fi;
gamma:=gammaInt*o;;off:=0;;
for L in [15,15,15,15,4] do for point in [1..8] do
 h:=poly(List(r[4]{[off+1..off+L]},decode));;
 if PowerMod(gamma*h,r[5],y^L)<>o*y^0 then Error("normalized entrywise period");fi;
 off:=off+L;
od;od;
Print("GAP_NORMALIZED_PERIOD ",r[5]," gamma=",gammaInt," all512=true\n");
Print("GAP_SCALAR_LOCAL_CERTIFICATE_COMPLETED\n");
QUIT;
