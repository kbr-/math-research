# Independent GAP verification of torsion divisors, full RR frames and every local period.
f:=GF(25);; one:=One(f);; zero:=Zero(f);; a:=Z(25)^8;;
decode:=c->(c mod 5)*one+QuoInt(c,5)*a;;
x:=Indeterminate(f,"x");;inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(one),v,inum);;
cut:=function(p,n)local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return poly(c);end;;
coeff:=function(p,j)local c;if j<0 then return zero;fi;c:=CoefficientsOfUnivariatePolynomial(p);if j<Length(c) then return c[j+1];fi;return zero;end;;
bit:=function(mask,i)return QuoInt(mask,2^i) mod 2;end;;
weight:=mask->Sum([0..3],i->bit(mask,i));;
basis:=function(M)local bs,s,j;bs:=[];for s in [0..15] do for j in [0..QuoInt(M-weight(s),2)] do Add(bs,[s,j]);od;od;return bs;end;;
lucas:=function(n,j)local v,r,t;v:=1;while n>0 or j>0 do r:=n mod 5;t:=j mod 5;if t>r then return 0;fi;v:=(v*Binomial(r,t)) mod 5;n:=QuoInt(n,5);j:=QuoInt(j,5);od;return v;end;;
for curve in [0,1,2,3] do
 if curve=0 then Read("research/results/bmd-nine-quinary-period-20261008/raw-certificate.g");elif curve=1 then Read("research/results/bmd-nine-quinary-period-20261008/raw-certificate-second.g");elif curve=2 then Read("research/results/bmd-nine-quinary-period-20261008/raw-certificate-third.g");else Read("research/results/bmd-nine-quinary-period-20261008/raw-certificate-fourth.g");fi;
 if curve=0 then slCodes:=[1,2,3,4];fi;
 slopes:=List(slCodes,decode);; roots:=List(slopes,s->poly(List([0..1280],j->lucas(1563,j)*s^j)));;
 for i in [1..4] do if cut(roots[i]^2-one-slopes[i]*x,1281)<>zero*x^0 then Error("root square identity");fi;od;
 subs:=List([0..15],s->cut(Product(Filtered([1..4],i->bit(s,i-1)=1),i->roots[i])*one*x^0,1281));;
 phiPoly:=Sum([1..16],i->subs[i]*poly(List(phiCodes[i],decode)));;
 kbound:= [32,96,96,160][curve+1];;zeroOrder:=8*kbound;;
 if cut(phiPoly,zeroOrder)<>zero*x^0 or coeff(phiPoly,zeroOrder)=zero then Error("exact torsion divisor");fi;
 for mask in [0..15] do for j in [0..QuoInt(kbound,2)] do if decode(phiCodes[mask+1][j+1])<>zero and 2*j+weight(mask)>kbound then Error("torsion pole bound");fi;od;od;
 if curve=3 then
  bs32:=basis(32);;J32:=List([0..255],i->List(bs32,m->coeff(subs[m[1]+1],i-m[2])));;ConvertToMatrixRep(J32,25);
  if RankMat(J32)<>252 then Error("nontrivial five-primary torsion part");fi;
  Print("GAP_FIVE_PRIMARY empty32H_minus256P=true\n");
 fi;
 if curve>0 then
 if curve=3 then frames:=[frame1,frame2,frame3,frame4,frame5];else frames:=[frame1,frame2,frame3];fi;
 for z in [1..Length(frames)] do
  M:=32*(z+2)-72;;N:=256*(z+2)-768;;bs:=basis(M);;K:=List(frames[z],r->List(r,decode));;
  if Length(K)<>Length(bs) or not ForAll(K,r->Length(r)=188) then Error("complete RR frame shape");fi;
  ConvertToMatrixRep(K,25);if RankMat(K)<>188 then Error("independent RR frame");fi;
  if N>0 then
   J:=List([0..N-1],i->List(bs,m->coeff(subs[m[1]+1],i-m[2])));;
   ConvertToMatrixRep(J,25);if not IsZero(J*K) then Error("full marked RR kernel");fi;
  fi;
  Print("GAP_RR curve=",curve," degree=",z+2," columns188=true all_marked_jets=true\n");
 od;
 fi;
 Print("GAP_TORSION curve=",curve," zero_order=",zeroOrder," pole_bound=",kbound,"\n");
od;
Read("research/results/bmd-nine-quinary-period-20261008/local-certificates.g");
for curve in [1..4] do
 recd:=LOCAL_CERTIFICATES[curve];;period:=recd[6];;deg:=recd[1];;fq:=GF(5^deg);;oneq:=One(fq);;zeroq:=Zero(fq);;xq:=Indeterminate(fq,"xq");;
 b:=RootsOfPolynomial(fq,Sum([0..deg],j->recd[2][j+1]*xq^j))[1];;
 decodeq:=c->Sum([0..deg-1],j->(QuoInt(c,5^j) mod 5)*b^j);;
 y:=Indeterminate(fq,"y");;iy:=IndeterminateNumberOfUnivariateRationalFunction(y);;
 polq:=v->UnivariatePolynomialByCoefficients(FamilyObj(oneq),v,iy);;
 off:=0;;for L in [15,15,15,15,4] do for point in [1..8] do
  v:=List(recd[4]{[off+1..off+L]},decodeq);;h:=polq(v);;
  if PowerMod(h,period,y^L)<>oneq*y^0 then Error("complete geometric local period");fi;
  off:=off+L;
 od;od;
 if off<>512 then Error("all geometric charts");fi;
 Print("GAP_PERIOD curve=",curve-1," local_period=",period," all512=true\n");
od;
Print("GAP_QUINARY_CERTIFICATES_COMPLETED four_torsion_divisors eleven_RR_frames all_local_periods\n");
QUIT;
