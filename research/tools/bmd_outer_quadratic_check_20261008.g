# Independent full coefficient rows, kernels and restrictions on the reduced outer period.
Read("research/results/bmd-exception-outer-cups-20261008/pilot.g");
outer:=ShallowCopy(OUTER_QUADRATIC_DATA);;
Read("research/results/bmd-exception-outer-cups-20261008/remainder.g");
Append(outer,OUTER_QUADRATIC_DATA);;
RADICAL_EXPONENTS:=List(outer,r->r[1]);;count:=Length(outer);;
f:=GF(27);; o:=One(f);; z:=Zero(f);; x:=Indeterminate(f,"x");;
a:=RootsOfPolynomial(f,x^3-x-o)[1];;
decode:=c->(c mod 3)*o+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
mat:=A->List(A,r->List(r,decode));;
frob:=function(A,e) return List(A,r->List(r,c->c^e)); end;;
poly:=[o*x^0];; weights:=[0];; offsets:=[];; vectors:=List([1..count],i->[[],[]]);;
for S in [1..511] do
 bit:=First([0..8],b->QuoInt(S,2^b) mod 2=1);;
 poly[S+1]:=poly[S-2^bit+1]*(o+a^bit*x);;
 weights[S+1]:=weights[S-2^bit+1]+1;;
od;
total:=0;;
for S in [0..511] do
 offsets[S+1]:=total;; g:=Maximum(0,QuoInt(weights[S+1]-1,2));;
 if g>0 then
  coeff:=CoefficientsOfUnivariatePolynomial(poly[S+1]);;
  get:=function(i) if i>=0 and i<Length(coeff) then return coeff[i+1]; else return z; fi; end;;
  B:=List([1..g],i->List([1..g],j->get(3*i-j)));;
  D:=frob(B,9)*frob(B,3)*B;;
  for moment in [1..2] do
   initial:=List([1..g],j->z);;
   if moment=1 then initial[1]:=o;
   else initial[1]:=get(1); if g>1 then initial[2]:=o; fi; fi;
   for low in [1..3] do
    small:=initial*D^QuoInt(low,3);;large:=initial*D^QuoInt(low+4680,3);;
    for step in [1..low mod 3] do small:=List(small,c->c^3)*B;large:=List(large,c->c^3)*B;od;
    if small<>large then Error("both rows short period");fi;
   od;
   for ii in [1..count] do
    s:=RADICAL_EXPONENTS[ii];;
    row:=initial*D^QuoInt(s,3);;
    for step in [1..s mod 3] do row:=List(row,c->c^3)*B;od;
    Append(vectors[ii][moment],row);
   od;
  od;
  total:=total+g;
 fi;
od;
if total<>769 then Error("complete holomorphic basis"); fi;
I:=[];;
for S in [0..511] do
 if weights[S+1]<=3 then
  for j in [0..QuoInt(3-weights[S+1],2)] do Add(I,[S,j]); od;
 fi;
od;
for ii in [1..count] do
 cups:=[];;
 for moment in [1..2] do
  A:=NullMat(140,140,f);;
  for i in [1..140] do
   for j in [1..140] do
    common:=Sum([0..8],b->2^b*(QuoInt(I[i][1],2^b) mod 2)*(QuoInt(I[j][1],2^b) mod 2));;
    U:=511-(I[i][1]+I[j][1]-2*common);; shift:=I[i][2]+I[j][2];;
    coeff:=CoefficientsOfUnivariatePolynomial(poly[common+1]);;
    A[i][j]:=Sum([1..Length(coeff)],l->coeff[l]*vectors[ii][moment][offsets[U+1]+shift+l]);;
   od;
  od;
  if vectors[ii][moment]<>List(outer[ii][3][moment],decode) then Error("full coefficient vector disagreement");fi;
  Add(cups,A);
 od;
 K:=mat(outer[ii][4]);;h:=140-outer[ii][2];;
 if RankMat(cups[1])<>140-h or RankMat(K)<>h or cups[1]*K<>NullMat(140,h,f) then Error("actual complete radical");fi;
 restricted:=TransposedMat(K)*cups[2]*K;;
 if restricted<>mat(outer[ii][5]) then Error("full second restriction disagreement");fi;
 Print("GAP_OUTER_QUADRATIC exponent=",outer[ii][1]," rank=",outer[ii][2]," full_vectors_kernels_restriction=true\n");
od;
Print("GAP_OUTER_QUADRATIC_COMPLETED cases=",count," stable_both_rows=true\n");
QUIT;
