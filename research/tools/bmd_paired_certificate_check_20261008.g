# Independent GAP verification of torsion divisors, full RR frames and every local period.
f:=GF(9);; one:=One(f);; zero:=Zero(f);; a:=Z(9)^2;;
decode:=c->(c mod 3)*one+QuoInt(c,3)*a;;
x:=Indeterminate(f,"x");;inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(one),v,inum);;
cut:=function(p,n)local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return poly(c);end;;
coeff:=function(p,j)local c;if j<0 then return zero;fi;c:=CoefficientsOfUnivariatePolynomial(p);if j<Length(c) then return c[j+1];fi;return zero;end;;
bit:=function(mask,i)return QuoInt(mask,2^i) mod 2;end;;
weight:=mask->Sum([0..3],i->bit(mask,i));;
basis:=function(M)local bs,s,j;bs:=[];for s in [0..15] do for j in [0..QuoInt(M-weight(s),2)] do Add(bs,[s,j]);od;od;return bs;end;;
lucas:=function(n,j)local v,r,t;v:=1;while n>0 or j>0 do r:=n mod 3;t:=j mod 3;if t>r then return 0;fi;v:=(v*Binomial(r,t)) mod 3;n:=QuoInt(n,3);j:=QuoInt(j,3);od;return v;end;;
for curve in [0,1] do
 if curve=0 then Read("research/results/bmd-exception-outside-coverage-20261008/raw-certificate.g");else Read("research/results/bmd-exception-outside-coverage-20261008/raw-certificate-second.g");fi;
 slopes:=List(slCodes,decode);; roots:=List(slopes,s->poly(List([0..768],j->lucas(1094,j)*s^j)));;
 for i in [1..4] do if cut(roots[i]^2-one-slopes[i]*x,769)<>zero*x^0 then Error("root square identity");fi;od;
 subs:=List([0..15],s->cut(Product(Filtered([1..4],i->bit(s,i-1)=1),i->roots[i])*one*x^0,769));;
 phiPoly:=Sum([1..16],i->subs[i]*poly(List(phiCodes[i],decode)));;
 if cut(phiPoly,768)<>zero*x^0 or coeff(phiPoly,768)=zero then Error("exact torsion divisor");fi;
 for mask in [0..15] do for j in [0..48] do if decode(phiCodes[mask+1][j+1])<>zero and 2*j+weight(mask)>96 then Error("torsion pole bound");fi;od;od;
 frames:=[frame1,frame2,frame3];;
 for z in [1..3] do
  M:=32*(z+2)-72;;N:=256*(z+2)-768;;bs:=basis(M);;K:=List(frames[z],r->List(r,decode));;
  if Length(K)<>Length(bs) or not ForAll(K,r->Length(r)=188) then Error("complete RR frame shape");fi;
  ConvertToMatrixRep(K,9);if RankMat(K)<>188 then Error("independent RR frame");fi;
  if N>0 then
   J:=List([0..N-1],i->List(bs,m->coeff(subs[m[1]+1],i-m[2])));;
   ConvertToMatrixRep(J,9);if not IsZero(J*K) then Error("full marked RR kernel");fi;
  fi;
  Print("GAP_RR curve=",curve," degree=",z+2," columns188=true all_marked_jets=true\n");
 od;
 Print("GAP_TORSION curve=",curve," exact_divisor=768P-96H\n");
od;
Read("research/results/bmd-exception-outside-coverage-20261008/local-certificates.g");
f81:=GF(81);;b:=Z(81)^16;;one81:=One(f81);;zero81:=Zero(f81);;y:=Indeterminate(f81,"y");;iy:=IndeterminateNumberOfUnivariateRationalFunction(y);;
decode81:=c->Sum([0..3],j->(QuoInt(c,3^j) mod 3)*b^j);;
poly81:=v->UnivariatePolynomialByCoefficients(FamilyObj(one81),v,iy);;
for curve in [1..2] do
 recd:=LOCAL_CERTIFICATES[curve];;if Sum([0..4],j->recd[1][j+1]*b^j)<>zero81 or decode81(recd[2])^2<>-one81 then Error("independent extension embedding");fi;
 period:= [135,1080][curve];;off:=0;;
 for L in [15,15,15,15,4] do for point in [1..8] do
  v:=List(recd[3]{[off+1..off+L]},decode81);;h:=poly81(v);;modulus:=y^L;;
  if PowerMod(h,period,modulus)<>one81*y^0 then Error("complete geometric local period");fi;
  off:=off+L;
 od;od;
 if off<>512 then Error("all geometric local charts");fi;
 Print("GAP_PERIOD curve=",curve-1," local_period=",period," all512=true\n");
od;
Print("GAP_PAIRED_CERTIFICATES_COMPLETED two_torsion_divisors six_RR_frames all_local_periods\n");
QUIT;
