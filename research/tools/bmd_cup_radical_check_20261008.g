# Independent GAP reconstruction of the six full first/second coefficient cups.
Read("research/results/bmd-exception-cup-radical-20261008/data.g");
f:=GF(27);; o:=One(f);; z:=Zero(f);; x:=Indeterminate(f,"x");;
a:=RootsOfPolynomial(f,x^3-x-o)[1];;
decode:=c->(c mod 3)*o+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
mat:=A->List(A,r->List(r,decode));;
frob:=function(A,e) return List(A,r->List(r,c->c^e)); end;;
poly:=[o*x^0];; weights:=[0];; offsets:=[];; vectors:=List([1..6],i->[[],[]]);;
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
   for ii in [1..6] do
    s:=RADICAL_EXPONENTS[ii];;
    if s mod 3<>0 then Error("unexpected exponent"); fi;
    row:=initial*D^QuoInt(s,3);;
    if row*D^9360<>row then Error("second moment stable period"); fi;
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
for ii in [1..6] do
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
  if A<>mat(RADICAL_DATA[ii][1][moment]) then Error("complete matrix disagreement"); fi;
  Add(cups,A);
 od;
 v:=List(RADICAL_DATA[ii][2],decode);;
 if RankMat(cups[1])<>139 or cups[1]*v<>List([1..140],i->z) or v=List([1..140],i->z) then Error("complete kernel check"); fi;
 scalar:=v*cups[2]*v;;
 if scalar=z or scalar<>decode(RADICAL_DATA[ii][3]) then Error("quadratic scalar mismatch"); fi;
 Print("GAP_CUP_RADICAL exponent=",RADICAL_EXPONENTS[ii]," rank139=true full_matrices_match=true nonzero=true code=",RADICAL_DATA[ii][3],"\n");
od;
Print("GAP_CUP_RADICAL_COMPLETED stable_second_moments=true\n");
QUIT;
