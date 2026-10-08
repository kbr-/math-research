# Independent GAP reconstruction of full low cohomology matrices and primitive first jets.
Read("research/results/bmd-exception-low-multipliers-20261008/modules.g");
original:=LOW_MULTIPLIER_MODULES;;
Read("research/results/bmd-exception-low-multipliers-20261008/modules11.g");
if Length(LOW_MULTIPLIER_MODULES)<>1 or LOW_MULTIPLIER_MODULES[1]{[1..3]}<>[3,4,108] then Error("refined scope");fi;
original[4]:=LOW_MULTIPLIER_MODULES[1];;
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
L:=378;;labels:=List([0..8],i->a^i);;
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
GC:=TransposedMat(List(Fs,p->coeffs(cut(p*iprod[512],108),108)));;
for ci in [1..4] do
 data:=original[ci];;b:=data[1];;mult:=data[2];;N:=data[3];;extra:=data[4];;P:=Length(data[10]);;q:=3^b;;H:=140+extra;;
 K:=mat(data[7]);;E0:=mat(data[8]);;E1:=mat(data[9]);;saved:=List(data[10],mat);;h:=Length(K[1]);;
 J:=FC{[1..N]};;Residue:=TransposedMat(Reversed(GC{[1..N]}));;
 if RankMat(J)<>N-extra or RankMat(K)<>h or J*K<>NullMat(N,h,f) then Error("complete fixed kernel");fi;
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
 G0:=result[2];;G1:=result[3];;rr:=pivotcols(TransposedMat(G0));;change:=G0{rr}^-1*E0{rr};;
 if G0*change<>E0 or RankMat(change)<>h then Error("primitive specialization");fi;
 delta:=E1-G1*change;;
 if RankMat(TransposedMat(Concatenation(TransposedMat(G0),TransposedMat(delta))))<>h then Error("primitive first-jet gauge");fi;
 Print("GAP_LOW_MODULE base=",b," multiplier=",mult," full_series_match=true smith=",data[6]," primitive_first_jet=true\n");
od;
Print("GAP_LOW_MODULES_COMPLETED families4 extra_principal_parts2=true\n");
Read("research/results/bmd-exception-low-multipliers-20261008/return-vectors.g");
Read("research/results/bmd-exception-low-multipliers-20261008/comparisons.g");
Read("research/results/bmd-exception-low-multipliers-20261008/dual-frame.g");
Read("research/results/bmd-exception-low-multipliers-20261008/derivatives.g");
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
Dual:=mat(LOW_DUAL_FRAME);;IR:=List([1..142],i->List([1..140],j->(function()if i=j then return o;else return zero;fi;end)()));;
Residue:=TransposedMat(Reversed(GC{[1..108]}));;
if Dual{[1..108]}<>TransposedMat(Residue) or Dual{[109..142]}*mat(original[4][7])<>IdentityMat(34,f) or RankMat(Dual)<>140 then Error("intrinsic dual frame");fi;
baseM:=List(savedAll[4]{[1..10]},A->Concatenation(A,NullMat(34,142,f)));;
if TransposedMat(Dual)*baseM[1]<>NullMat(140,142,f) or TransposedMat(Dual)*baseM[2]*IR<>4*phis[3] then Error("calibrated central cup");fi;
for item in LOW_COMPARISONS do
 b:=item[1];;mult:=item[2];;k:=item[3];;degree:=item[4];;u:=item[5];;kind:=item[6];;
 ci:=Position(List(original,c->c{[1,2]}),[b,mult]);;K:=mat(original[ci][7]);;E0:=mat(original[ci][8]);;W:=E0{[1..140]};;
 if k=0 then Cnu:=u*phis[5];
 else idx:=Position(List(LOW_RETURN_VECTORS,v->v{[1,2]}),[b,k]);d:=LogInt(degree,3);Cnu:=mult*mu[idx]+u*phis[b+d];fi;
 retained:=mat(item[9]);;
 if kind=0 then
  if retained<>TransposedMat(K)*Cnu*W or RankMat(retained)<>item[8] then Error("independent strict pairing");fi;
 else
  if TransposedMat(Dual)*retained*IR<>Cnu then Error("equal-order tangent identification");fi;
  test:=ShallowCopy(baseM);;test[10]:=test[10]+retained;;res:=smith(test,false);;
  before:=Sum(Filtered(res[1],v->v[1]<9),v->v[2]);;
  if 142-before<>item[7] or Last(res[1])<>[9,item[8]] then Error("independent equal-order pivots");fi;
 fi;
od;
Print("GAP_LOW_COMPARISONS_COMPLETED cases=",Length(LOW_COMPARISONS)," independent_complete_matrices=true\n");
for item in LOW_DERIVATIVES do
 b:=item[1];;k:=item[2];;degree:=item[3];;tail:=item[4];;C:=mat(item[5]);;f0:=mat(item[6]);;f1:=mat(item[7]);;
 ci:=Position(List(original,c->c{[1,2]}),[b,4]);;K:=mat(original[ci][7]);;E0:=mat(original[ci][8]);;E1:=mat(original[ci][9]);;W:=E0{[1..140]};;h:=Length(K[1]);;
 idx:=Position(List(LOW_RETURN_VECTORS,v->v{[1,2]}),[b,k]);;
 if C<>4*mu[idx]+tail*phis[b+LogInt(degree,3)] then Error("derivative full tangent");fi;
 rr:=pivotcols(TransposedMat(W));;coords:=W{rr}^-1*f0{rr};;g1:=E1*coords;;
 if W*coords<>f0 or g1{[1..140]}<>f1 then Error("actual primitive derivative");fi;
 if Length(g1)>140 and g1{[141..Length(g1)]}<>NullMat(Length(g1)-140,1,f) then Error("first correction regularity");fi;
 if RankMat(TransposedMat(K)*C*W)<>h-1 or TransposedMat(f0)*C*K<>NullMat(1,h,f) then Error("actual left radical");fi;
 value:=(TransposedMat(f0)*C*f1)[1][1];;
 if value=zero or value<>decode(item[8]) then Error("nonzero derivative");fi;
 Print("GAP_LOW_DERIVATIVE base=",b," k=",k," code=",item[8]," nonzero=true\n");
od;
Print("GAP_LOW_FULL_CHECK_COMPLETED modules4 comparisons52 derivatives2=true\n");
QUIT;
