# Independent complete-source and sufficient-precision GAP verification of the two residual references.
Read("research/results/bmd-exception-residual-multipliers-20261008/module5.g");
original:=ShallowCopy(LOW_MULTIPLIER_MODULES);;
Read("research/results/bmd-exception-residual-multipliers-20261008/module13.g");
Append(original,LOW_MULTIPLIER_MODULES);;
f:=GF(27);;o:=One(f);;zero:=Zero(f);;x:=Indeterminate(f,"x");;
a:=RootsOfPolynomial(f,x^3-x-o)[1];;inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
decode:=c->(c mod 3)*o+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
mat:=A->List(A,r->List(r,decode));;
sub:=function(A,rr,cc) return List(rr,i->A[i]{cc});end;;
cut:=function(p,n) local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return UnivariatePolynomialByCoefficients(FamilyObj(o),c,inum);end;;
coeffs:=function(p,n) local c;c:=CoefficientsOfUnivariatePolynomial(p);return List([1..n],i->(function()if i<=Length(c) then return c[i];else return zero;fi;end)());end;;
polyvec:=v->UnivariatePolynomialByCoefficients(FamilyObj(o),v,inum);;
pivotcols:=function(A) local heads;heads:=SemiEchelonMat(A).heads;return Filtered([1..Length(heads)],i->heads[i]<>0);end;;
smith:=function(A,wantJet)
 local H,E0,E1,depth,pivots,nr,nc,rr,cc,rank,prec,rs,cs,U,B,C,D,inv,X,k,j,tmp,new0,new1;
 H:=Length(A[1][1]);E0:=IdentityMat(H,f);E1:=NullMat(H,H,f);depth:=0;pivots:=[];
 while Length(A)>0 do
  nr:=Length(A[1]);nc:=Length(A[1][1]);prec:=Length(A);
  rr:=pivotcols(TransposedMat(A[1]));rank:=Length(rr);
  if rank>0 then
   cc:=pivotcols(A[1]{rr});rs:=Difference([1..nr],rr);cs:=Difference([1..nc],cc);
   U:=List(A,M->sub(M,rr,cc));B:=List(A,M->sub(M,rr,cs));inv:=U[1]^-1;X:=[];
   for k in [1..prec] do
    tmp:=B[k];for j in [2..k] do tmp:=tmp-U[j]*X[k-j+1];od;X[k]:=inv*tmp;
   od;
   if Length(cs)>0 then
    new0:=sub(E0,[1..H],cs)-sub(E0,[1..H],cc)*X[1];
    if prec>=2 then new1:=sub(E1,[1..H],cs)-sub(E1,[1..H],cc)*X[1]-sub(E0,[1..H],cc)*X[2];
    else if wantJet then Error("first jet precision not retained");fi;new1:=NullMat(H,Length(cs),f);fi;
   else new0:=[];new1:=[];fi;
   E0:=new0;E1:=new1;Add(pivots,[depth,rank]);
   if rank=nr then return [pivots,E0,E1,0];fi;
   C:=List(A,M->sub(M,rs,cc));D:=List(A,M->sub(M,rs,cs));A:=[];
   for k in [1..prec] do tmp:=D[k];for j in [1..k] do tmp:=tmp-C[j]*X[k-j+1];od;A[k]:=tmp;od;
   if A[1]<>NullMat(Length(rs),Length(cs),f) then Error("Schur constant");fi;
  fi;
  if Length(A)=1 then if wantJet then Error("insufficient precision");fi;return [pivots,E0,E1,Length(A[1])];fi;
  A:=A{[2..Length(A)]};depth:=depth+1;
 od;
 Error("unexpected exhausted matrix");
end;;
L:=675;;labels:=List([0..8],i->a^i);;
roots:=List(labels,b->cut((o+b*x)^365,L));;iroots:=List(labels,b->cut((o+b*x)^364,L));;
prod:=[o*x^0];;iprod:=[o*x^0];;weights:=[0];;rpoly:=[o*x^0];;savedAll:=[];;
for S in [1..511] do
 bit:=First([0..8],b->QuoInt(S,2^b) mod 2=1);;
 rpoly[S+1]:=rpoly[S-2^bit+1]*(o+labels[bit+1]*x);;
 prod[S+1]:=cut(prod[S-2^bit+1]*roots[bit+1],L);;
 iprod[S+1]:=cut(iprod[S-2^bit+1]*iroots[bit+1],L);;
 weights[S+1]:=weights[S-2^bit+1]+1;;
od;
I:=[];;for S in [0..511] do if weights[S+1]<=3 then for j in [0..QuoInt(3-weights[S+1],2)] do Add(I,[S,j]);od;fi;od;
Fs:=List(I,v->cut(x^v[2]*prod[v[1]+1],L));;FC:=TransposedMat(List(Fs,p->coeffs(p,L)));;
GC:=TransposedMat(List(Fs,p->coeffs(cut(p*iprod[512],351),351)));;
for ci in [1..2] do
 data:=original[ci];;b:=data[1];;mult:=data[2];;N:=data[3];;extra:=data[4];;P:=13;;q:=3^b;;H:=140+extra;;
 K:=mat(data[7]);;E0:=mat(data[8]);;E1:=mat(data[9]);;saved:=List(data[10]{[1..P]},mat);;h:=H-N;;
 J:=FC{[1..N]};;Residue:=TransposedMat(Reversed(GC{[1..N]}));;
 if RankMat(J)<>N-extra then Error("complete jet rank");fi;
 if h>0 and (RankMat(K)<>h or J*K<>NullMat(N,h,f)) then Error("complete fixed kernel");fi;
 nums:=List(Fs,p->coeffs(cut(x^N*p,L),L));;
 if extra>0 then
  PP:=mat(data[11]);;
  if RankMat(PP)<>extra or Residue*PP<>NullMat(140,extra,f) then Error("complete principal parts");fi;
  for j in [1..extra] do
   R:=polyvec(List([1..N],i->PP[i][j]));;total:=zero*x^0;;
   for S in [0..511] do
    pol:=cut(R*iprod[S+1],N);;
    if DegreeOfUnivariateLaurentPolynomial(pol)>N+QuoInt(3-weights[S+1]-((3-weights[S+1]) mod 2),2) then Error("global pole bound");fi;
    term:=cut(pol*prod[S+1],L);;
    if cut(term-R,N)<>zero*x^0 then Error("character completion");fi;
    total:=total+term;
   od;
   total:=total/(512*o);;
   if coeffs(total,N)<>List([1..N],i->PP[i][j]) then Error("actual principal part");fi;
   Add(nums,coeffs(total,L));
  od;
 fi;
 matrices:=List([0..P-1],k->List([0..N-1],i->List([1..H],j->Binomial(k+QuoInt(i,q),QuoInt(i,q))*nums[j][q*(k+QuoInt(i,q))+(i mod q)+1])));;
 if matrices<>saved then Error("complete moving-divisor coefficient mismatch");fi;
 savedAll[ci]:=matrices;
 result:=smith(matrices,true);;
 if result[1]<>data[6] then Error("independent elementary divisors");fi;
 G0:=result[2];;G1:=result[3];;if h>0 then rr:=pivotcols(TransposedMat(G0));;change:=G0{rr}^-1*E0{rr};;
 if G0*change<>E0 or RankMat(change)<>h then Error("primitive specialization");fi;
 delta:=E1-G1*change;;
 if RankMat(TransposedMat(Concatenation(TransposedMat(G0),TransposedMat(delta))))<>h then Error("primitive first-jet gauge");fi;
 fi;
 Print("GAP_RESIDUAL_MODULE base=",b," multiplier=",mult," full_series_match=true smith=",data[6]," primitive_first_jet=true\n");
od;
Print("GAP_RESIDUAL_MODULES_COMPLETED modules2 principal_lifts213=true\n");
Read("research/results/bmd-exception-low-multipliers-20261008/return-vectors.g");
Read("research/results/bmd-exception-residual-multipliers-20261008/comparisons5.g");
offsets:=[];;vphi:=List([1..6],i->[]);;total:=0;;
for S in [0..511] do
 offsets[S+1]:=total;;g:=Maximum(0,QuoInt(weights[S+1]-1,2));;
 if g>0 then
  cf:=coeffs(rpoly[S+1],3*g+1);;
  B:=List([1..g],i->List([1..g],j->(function()if 3*i-j>=0 then return cf[3*i-j+1];else return zero;fi;end)()));;
  row:=List([1..g],i->zero);;row[1]:=o;;
  for j in [1..6] do row:=List(row,c->c^3)*B;Append(vphi[j],row);od;
  total:=total+g;
 fi;
od;
Cup:=function(v)
 local A,i,j,common,U,shift,cf;
 A:=NullMat(140,140,f);
 for i in [1..140] do for j in [1..140] do
  common:=Sum([0..8],b->2^b*(QuoInt(I[i][1],2^b) mod 2)*(QuoInt(I[j][1],2^b) mod 2));
  U:=511-(I[i][1]+I[j][1]-2*common);shift:=I[i][2]+I[j][2];
  cf:=CoefficientsOfUnivariatePolynomial(rpoly[common+1]);
  A[i][j]:=Sum([1..Length(cf)],l->cf[l]*v[offsets[U+1]+shift+l]);
 od;od;return A;
end;;
phis:=List(vphi,Cup);;mu:=List(LOW_RETURN_VECTORS,v->Cup(List(v[4],decode)));;

K:=mat(original[1][7]);;E0:=mat(original[1][8]);;W:=E0{[1..140]};;
for item in RESIDUAL_COMPARISONS do
 if item[1]<>5 or item[4]<>7 then Error("comparison scope");fi;
 idx:=Position(List(LOW_RETURN_VECTORS,v->v{[1,2]}),[3,item[2]]);;
 Cnu:=5*mu[idx]+item[3]*phis[6];;
 if Cnu<>mat(item[7]) then Error("complete tangent mismatch");fi;
 A:=TransposedMat(K)*Cnu*W;;
 if A<>mat(item[8]) or RankMat(A)<>7 or item[5]<>7 then Error("full primitive pairing");fi;
od;
Print("GAP_RESIDUAL_FULL_CHECK_COMPLETED modules2 comparisons9=true\n");
QUIT;
