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
PP:=matrix(LIFT_PP);; Hnum:=matrix(LIFT_HNUM);; Coef:=matrix(LIFT_COEFF);;
if RankMat(PP)<>2 or Residue*PP<>NullMat(140,2,f) then Error("complete principal-part space"); fi;
for j in [1..2] do
 R:=polyvec(List([1..Q],i->PP[i][j]));; total:=zz*x^0;;
 for S in [0..511] do
  P:=cut(R*invS[S+1],Q);;
  bound:=Q+QuoInt(3-weights[S+1]-((3-weights[S+1]) mod 2),2);;
  if Length(CoefficientsOfUnivariatePolynomial(P))-1>bound or cut(P*prodS[S+1],Q)<>R then Error("global completion conditions"); fi;
  total:=cut(total+P*prodS[S+1],N);;
 od;
 actual:=coeffs(total/(512*o),N);;
 if actual<>List([1..N],i->Hnum[i][j]) then Error("complete global lift mismatch"); fi;
od;
F0:=matrix(LIFT_F0);; G0:=matrix(LIFT_G0);;
if FC*K<>F0 or GC*K<>G0 or PP*Coef<>F0{[1..Q]} then Error("kernel series/correction coefficients"); fi;
A:=TransposedMat(Reversed(G0))*Hnum*Coef;;
C2:=TransposedMat(Reversed(G0))*F0;;
if A+TransposedMat(A)<>C2 then Error("global residue identity"); fi;
forms:=List(LIFT_O2,matrix);;
if forms[1]<>-A+C2 or forms[2]<>-A or forms[1]<>-TransposedMat(forms[2]) then Error("second map/sign duality"); fi;
if List(forms,RankMat)<>[0,0] or LIFT_RANKS<>[0,0] then Error("second ranks"); fi;
Third:=TransposedMat(Reversed(G0{[Q+1..N]}))*F0{[Q+1..N]};;
if Third<>matrix(LIFT_THIRD) or RankMat(Third)<>LIFT_THIRD_RANK then Error("third restricted matrix"); fi;
if DeterminantMat(Third)<>decode(LIFT_THIRD_DET) then Error("restricted determinant mismatch"); fi;
Read("research/results/bmd-exception-torsion-deflation-20261007/cup-data.g");
if CUP_FIELD_POLY<>LIFT_FIELD or TransposedMat(K)*matrix(CUP_CODES)*K<>Third then Error("independent next Cartier cup restriction"); fi;
Print("GAP_THIRD_RESTRICTED_CUP rank=",RankMat(Third)," target61 previous_Phi5_restriction_matched\n");
Print("GAP_SECOND_LIFT_COMPLETED jet_rank79 first_rank79 kernel61 liftable_principal_parts2 global_completions1024 second_ranks0,0 survivors61 sign_duality=true\n");
QUIT;
