# Independent GAP verification of torsion divisors, full RR frames and every local period.
f:=GF(49);; one:=One(f);; zero:=Zero(f);; a:=RootsOfPolynomial(f,UnivariatePolynomial(GF(7),[6,1,1]))[1];;
decode:=c->(c mod 7)*one+QuoInt(c,7)*a;;
x:=Indeterminate(f,"x");;inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(one),v,inum);;
cut:=function(p,n)local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return poly(c);end;;
coeff:=function(p,j)local c;if j<0 then return zero;fi;c:=CoefficientsOfUnivariatePolynomial(p);if j<Length(c) then return c[j+1];fi;return zero;end;;
bit:=function(mask,i)return QuoInt(mask,2^i) mod 2;end;;
weight:=mask->Sum([0..3],i->bit(mask,i));;
basis:=function(M)local bs,s,j;bs:=[];for s in [0..15] do for j in [0..QuoInt(M-weight(s),2)] do Add(bs,[s,j]);od;od;return bs;end;;
lucas:=function(n,j)local v,r,t;v:=1;while n>0 or j>0 do r:=n mod 7;t:=j mod 7;if t>r then return 0;fi;v:=(v*Binomial(r,t)) mod 7;n:=QuoInt(n,7);j:=QuoInt(j,7);od;return v;end;;
for curve in [1,3] do
 if curve=1 then Read("research/results/bmd-nine-septenary-period-20261008/raw-certificate.g");else Read("research/results/bmd-nine-septenary-period-20261008/raw-certificate-third.g");fi;
 slopes:=List(slCodes,decode);; roots:=List(slopes,s->poly(List([0..768],j->lucas(1201,j)*s^j)));;
 for i in [1..4] do if cut(roots[i]^2-one-slopes[i]*x,769)<>zero*x^0 then Error("root square identity");fi;od;
 subs:=List([0..15],s->cut(Product(Filtered([1..4],i->bit(s,i-1)=1),i->roots[i])*one*x^0,769));;
 phiPoly:=Sum([1..16],i->subs[i]*poly(List(phiCodes[i],decode)));;
 kbound:=96;;zeroOrder:=8*kbound;;
 if cut(phiPoly,zeroOrder)<>zero*x^0 or coeff(phiPoly,zeroOrder)=zero then Error("exact torsion divisor");fi;
 for mask in [0..15] do for j in [0..QuoInt(kbound,2)] do if decode(phiCodes[mask+1][j+1])<>zero and 2*j+weight(mask)>kbound then Error("torsion pole bound");fi;od;od;
 frames:=[frame1,frame2,frame3];
 for z in [1..Length(frames)] do
  M:=32*(z+2)-72;;N:=256*(z+2)-768;;bs:=basis(M);;K:=List(frames[z],r->List(r,decode));;
  if Length(K)<>Length(bs) or not ForAll(K,r->Length(r)=188) then Error("complete RR frame shape");fi;
  ConvertToMatrixRep(K,49);if RankMat(K)<>188 then Error("independent RR frame");fi;
  if N>0 then
   J:=List([0..N-1],i->List(bs,m->coeff(subs[m[1]+1],i-m[2])));;
   ConvertToMatrixRep(J,49);if not IsZero(J*K) then Error("full marked RR kernel");fi;
  fi;
  Print("GAP_RR curve=",curve," degree=",z+2," columns188=true all_marked_jets=true\n");
 od;
 Print("GAP_TORSION curve=",curve," zero_order=",zeroOrder," pole_bound=",kbound,"\n");
od;
Print("GAP_SEPTENARY_CERTIFICATES_COMPLETED two_divisors_and_six_RR_frames\n");
QUIT;
