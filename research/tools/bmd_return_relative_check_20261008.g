# Independently reconstruct source series, residue constraints, both global principal-part lifts,
# and the induced second matrices over GAP's finite-field arithmetic.
Read("research/results/bmd-exception-second-lift-20261008/data.g");
f:=GF(27);; o:=One(f);; zz:=Zero(f);; x:=Indeterminate(f,"x");;
inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
a:=RootsOfPolynomial(f,Sum([0..3],i->LIFT_FIELD[i+1]*x^i))[1];;
decode:=function(c) return (c mod 3)*o+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2; end;;
matrix:=m->List(m,row->List(row,decode));;
Q:=LIFT_Q;; N:=2*Q;;
cut:=function(p,n)
 local c;
 c:=CoefficientsOfUnivariatePolynomial(p);
 if Length(c)>n then c:=c{[1..n]}; fi;
 return UnivariatePolynomialByCoefficients(FamilyObj(o),c,inum);
end;;
coeffs:=function(p,n)
 local c;
 c:=CoefficientsOfUnivariatePolynomial(p);
 return List([1..n],i->(function()
  if i<=Length(c) then return c[i]; else return zz; fi;
 end)());
end;;
polyvec:=v->UnivariatePolynomialByCoefficients(FamilyObj(o),v,inum);;
labels:=List([0..8],i->a^i);;
roots:=List(labels,b->cut((o+b*x)^122,N));;
inverseRoots:=List(labels,b->cut((o+b*x)^121,N));;
prodS:=[o*x^0];; invS:=[o*x^0];; weights:=[0];;
for S in [1..511] do
 bit:=First([0..8],i->QuoInt(S,2^i) mod 2=1);;
 parent:=S-2^bit;;
 prodS[S+1]:=cut(prodS[parent+1]*roots[bit+1],N);;
 invS[S+1]:=cut(invS[parent+1]*inverseRoots[bit+1],N);;
 weights[S+1]:=weights[parent+1]+1;;
od;
I:=[];;
for S in [0..511] do
 if weights[S+1]<=3 then
  for j in [0..QuoInt(3-weights[S+1],2)] do Add(I,[S,j]); od;
 fi;
od;
if Length(I)<>140 then Error("complete source"); fi;
FC:=TransposedMat(List(I,v->coeffs(cut(x^v[2]*prodS[v[1]+1],N),N)));;
J:=matrix(LIFT_J);; C:=matrix(LIFT_C);; K:=matrix(LIFT_K);;
if FC{[1..Q]}<>J or RankMat(J)<>79 or RankMat(C)<>79 or RankMat(K)<>61 then Error("source/rank mismatch"); fi;
nu:=coeffs(invS[512],N);;
Toep:=List([1..N],i->List([1..N],j->(function()
 if i>=j then return nu[i-j+1]; else return zz; fi;
end)()));;
GC:=Toep*FC;;
Residue:=TransposedMat(Reversed(GC{[1..Q]}));;
if Residue*J<>C or C<>TransposedMat(C) or J*K<>NullMat(Q,61,f) then Error("first cup identity"); fi;

Read("research/results/bmd-exception-return-multipliers-20261008/relative-data.g");
Read("research/results/bmd-exception-return-multipliers-20261008/relative-vector.g");
Cnu:=matrix(REL_CNU);; C2:=TransposedMat(Reversed(GC))*FC;;
F0:=matrix(REL_F0);; F1:=matrix(REL_F1);;
if C2<>matrix(REL_C2) then Error("second cup mismatch"); fi;
if C*F1<>-C2*F0 or C*F0<>NullMat(140,1,f) or J*F0<>NullMat(81,1,f) then Error("correction equation"); fi;
if F0=NullMat(140,1,f) then Error("zero radical vector"); fi;
A:=TransposedMat(K)*Cnu*K;;
if RankMat(A)<>60 or TransposedMat(K)*Cnu*F0<>NullMat(61,1,f) then Error("radical mismatch"); fi;
value:=(TransposedMat(F0)*Cnu*F1)[1][1];;
if value=zz or value<>decode(REL_DERIVATIVE) then Error("derivative mismatch"); fi;
if (TransposedMat(F0)*Cnu*(F1+F0))[1][1]<>value then Error("gauge mismatch"); fi;
# Reconstruct the complete tangent independently by eight Cartier steps.
polys:=[o*x^0];; offsets:=[];; lam:=[];;
for S in [1..511] do
 bit:=First([0..8],i->QuoInt(S,2^i) mod 2=1);;
 polys[S+1]:=polys[S-2^bit+1]*(o+labels[bit+1]*x);;
od;
for S in [0..511] do
 offsets[S+1]:=Length(lam);;
 g:=Maximum(0,QuoInt(weights[S+1]-1,2));;
 if g>0 then
  cf:=coeffs(polys[S+1],3*g+1);;
  B:=List([1..g],i->List([1..g],j->(function()
   if 3*i-j>=0 then return cf[3*i-j+1]; else return zz; fi;
  end)()));;
  row:=Concatenation([o],List([2..g],i->zz));;
  for step in [1..8] do row:=List(row,c->c^3)*B; od;
  Append(lam,row);
 fi;
od;
if Length(lam)<>769 then Error("differential count"); fi;
lam:=lam+List(REL_VECTOR,decode);;
for i in [1..140] do
 for j in [1..140] do
  common:=Sum([0..8],b->2^b*(QuoInt(I[i][1],2^b) mod 2)*(QuoInt(I[j][1],2^b) mod 2));;
  U:=511-(I[i][1]+I[j][1]-2*common);;
  shift:=I[i][2]+I[j][2];;
  cf:=CoefficientsOfUnivariatePolynomial(polys[common+1]);;
  expected:=Sum([1..Length(cf)],l->cf[l]*lam[offsets[U+1]+shift+l]);;
  if Cnu[i][j]<>expected then Error("full tangent reconstruction mismatch"); fi;
 od;
od;
Print("RELATIVE_GAP_CHECK_COMPLETED full_tangent=140x140 mixed_rank=60 derivative_nonzero=true code=",REL_DERIVATIVE,"\n");
QUIT;
