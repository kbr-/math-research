# Independently reconstruct both torsion functions and the full monomial reference frame.
f:=GF(11);;one:=One(f);;zero:=Zero(f);;decode:=c->c*one;;
x:=Indeterminate(f,"x");;inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(one),v,inum);;
cut:=function(p,n)local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return poly(c);end;;
coeff:=function(p,j)local c;if j<0 then return zero;fi;c:=CoefficientsOfUnivariatePolynomial(p);if j<Length(c) then return c[j+1];fi;return zero;end;;
bit:=function(mask,i)return QuoInt(mask,2^i) mod 2;end;;weight:=mask->Sum([0..3],i->bit(mask,i));;
lucas:=function(n,j)local v,r,t;v:=1;while n>0 or j>0 do r:=n mod 11;t:=j mod 11;if t>r then return 0;fi;v:=(v*Binomial(r,t)) mod 11;n:=QuoInt(n,11);j:=QuoInt(j,11);od;return v;end;;
for curve in [1,2] do
 if curve=1 then Read("research/results/bmd-nine-eleven-period-20261008/raw-certificate.g");slCodes:=[1,2,3,4];else Read("research/results/bmd-nine-eleven-period-20261008/raw-certificate-second.g");fi;
 slopes:=List(slCodes,decode);;if Length(Set(slopes))<>4 or zero in slopes then Error("admissible slopes");fi;
 roots:=List(slopes,s->poly(List([0..256],j->lucas(666,j)*s^j)));;
 for i in [1..4] do if cut(roots[i]^2-one-slopes[i]*x,257)<>zero*x^0 then Error("root square identity");fi;od;
 subs:=List([0..15],s->cut(Product(Filtered([1..4],i->bit(s,i-1)=1),i->roots[i])*one*x^0,257));;
 phiPoly:=Sum([1..16],i->subs[i]*poly(List(phiCodes[i],decode)));;
 if cut(phiPoly,256)<>zero*x^0 or coeff(phiPoly,256)=zero then Error("exact divisor");fi;
 for mask in [0..15] do for j in [0..16] do if decode(phiCodes[mask+1][j+1])<>zero and 2*j+weight(mask)>32 then Error("pole bound");fi;od;od;
 bs:=[];;for mask in [0..15] do for j in [0..QuoInt(24-weight(mask),2)] do Add(bs,[mask,j]);od;od;
 if Length(bs)<>188 or Length(Set(bs))<>188 then Error("complete monomial RR frame");fi;
 Print("GAP_TORSION curve=",curve," zero_order256 pole_bound32 reference_dimension188=true\n");
od;
Print("GAP_ELEVEN_DIVISORS_COMPLETED two_inputs\n");
QUIT;
