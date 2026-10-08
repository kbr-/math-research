# Exact encoding/replay controls, not a finite extrapolation of the degree theorem.
# 81 four-group systems, four one-pair-overlap systems, 8192 local reverse-map
# inputs, every graph on four vertices, and 891 ordinary restriction identities.
Bit:=b->Position([false,true],b)-1;;
OldOK:=function(scopes,bs,x)
  return ForAll([1..Length(scopes)],a->Sum(scopes[a],i->x[2*i-1]+x[2*i]) mod 5=bs[a]);
end;;
NewOK:=function(scopes,bs,z)
  local h,a,b,i;
  h:=List([1..Length(scopes)],a->(Sum(scopes[a],i->z[i])+bs[a]) mod 2);
  for a in [1..Length(scopes)] do
    if Sum(scopes[a],i->z[i])>1 then return false;fi;
  od;
  for i in [1..Length(z)] do
    if z[i]=0 then
      if Length(Set(List(Filtered([1..Length(scopes)],a->i in scopes[a]),a->h[a])))>1 then return false;fi;
    fi;
  od;
  return true;
end;;
Lift:=function(scopes,bs,z)
  local x,i,a,h;
  x:=[];
  for i in [1..Length(z)] do
    a:=First([1..Length(scopes)],a->i in scopes[a]);
    if a=fail then h:=0;else h:=(Sum(scopes[a],j->z[j])+bs[a]) mod 2;fi;
    Append(x,[(1-z[i])*h,((1-z[i])*h+z[i]) mod 2]);
  od;
  return x;
end;;
cases:=0;;originalInputs:=0;;targetInputs:=0;;
CheckCase:=function(n,scopes,bs)
  local old,image,target,x,z;
  old:=Filtered(Tuples([0,1],2*n),x->OldOK(scopes,bs,x));
  image:=Set(List(old,x->List([1..n],i->(x[2*i-1]+x[2*i]) mod 2)));
  target:=Filtered(Tuples([0,1],n),z->NewOK(scopes,bs,z));
  if image<>target then Error("parity image");fi;
  for z in target do
    x:=Lift(scopes,bs,z);
    if not OldOK(scopes,bs,x) or List([1..n],i->(x[2*i-1]+x[2*i]) mod 2)<>z then Error("reconstruction");fi;
  od;
  cases:=cases+1;originalInputs:=originalInputs+2^(2*n);targetInputs:=targetInputs+2^n;
  Print("case=",cases," n=",n," scopes=",scopes," rhs=",bs,
        " old solutions=",Length(old)," parity solutions=",target,"\n");
end;;
scopes4:=Combinations([1..4],3);;
for state in Tuples([-1,0,1],4) do
  chosen:=Filtered([1..4],i->state[i]<>-1);;
  CheckCase(4,scopes4{chosen},state{chosen});
od;
for bs in Tuples([0,1],2) do CheckCase(5,[[1,2,3],[3,4,5]],bs);od;
Print("equivalence cases=",cases," original inputs=",originalInputs,
      " target inputs=",targetInputs," PASS\n");
# Largest support needed by the width-six reverse substitution: one original
# row plus one chosen incident row for each of its three groups, nine groups.
reverseInputs:=0;;validLocal:=0;;badWithoutGuard:=fail;;
for rhs in Tuples([0,1],4) do
  for z in Tuples([0,1],9) do
    reverseInputs:=reverseInputs+1;
    h:=(Sum(z{[1..3]})+rhs[1]) mod 2;;
    chosenH:=[(z[1]+z[4]+z[5]+rhs[2]) mod 2,
              (z[2]+z[6]+z[7]+rhs[3]) mod 2,
              (z[3]+z[8]+z[9]+rhs[4]) mod 2];;
    x:=Concatenation(List([1..3],i->[(1-z[i])*chosenH[i],((1-z[i])*chosenH[i]+z[i]) mod 2]));;
    edgesOK:=Sum(z{[1..3]})<=1;;
    guardsOK:=ForAll([1..3],i->z[i]=1 or chosenH[i]=h);;
    if edgesOK and guardsOK then
      validLocal:=validLocal+1;
      if Sum(x) mod 5<>rhs[1] then Error("reverse axiom implication");fi;
    elif edgesOK and Sum(x) mod 5<>rhs[1] and badWithoutGuard=fail then
      badWithoutGuard:=[rhs,z,x];
    fi;
  od;
od;
if badWithoutGuard=fail then Error("missing reconstruction negative control");fi;
Print("reverse inputs=",reverseInputs," locally valid=",validLocal,
      " omitted-guard witness=",badWithoutGuard," PASS\n");
# The independent-set monomials give a square invertible evaluation matrix.
F:=GF(2);; allEdges:=Combinations([1..4],2);; graphCount:=0;;basisRows:=0;;
for edges in Combinations(allEdges) do
  independent:=Filtered(Combinations([1..4]),S->not ForAny(edges,e->IsSubset(S,e)));;
  M:=List(independent,S->List(independent,T->Bit(IsSubset(T,S))*One(F)));;
  if RankMat(M)<>Length(independent) then Error("independent-set function basis");fi;
  for I in independent do
    for e in edges do
      if IsSubset(I,e) then Error("independent restriction");fi;
    od;
  od;
  graphCount:=graphCount+1;basisRows:=basisRows+Length(independent);
od;
Print("graphs=",graphCount," independent basis rows=",basisRows," PASS\n");
# Literal telescoping certificates for P_sigma*m-P_sigma*m|sigma, using
# Boolean axioms. The constructed product degrees are <= |support sigma|+deg m.
xx:=List([1..4],i->Indeterminate(F,i));;monSupports:=Filtered(Combinations([1..4]),S->Length(S)<=2);;
identities:=0;;nonzero:=0;;
for state in Tuples([-1,0,1],4) do
  C:=Filtered([1..4],i->state[i]<>-1);;
  factors:=List(C,i->xx[i]+(1-state[i])*One(F));;
  P:=Product(factors,One(xx[1]));;
  for S in monSupports do
    m:=Product(xx{S},One(xx[1]));;
    restricted:=Product(List(S,i->(function()
      if i in C then return state[i]*One(xx[1]);else return xx[i];fi;
    end)()),One(xx[1]));;
    correction:=Zero(xx[1]);; coefficient:=One(F);;processed:=[];;
    for i in Intersection(S,C) do
      Pwithout:=Product(List(Difference(C,[i]),j->xx[j]+(1-state[j])*One(F)),One(xx[1]));;
      rest:=Product(xx{Difference(S,Concatenation(processed,[i]))},One(xx[1]));;
      correction:=correction+coefficient*Pwithout*(xx[i]^2+xx[i])*rest;
      coefficient:=coefficient*state[i];Add(processed,i);
    od;
    if not IsZero(P*m-P*restricted-correction) then Error("ordinary restriction certificate");fi;
    identities:=identities+1;
    if not IsZero(correction) then nonzero:=nonzero+1;fi;
  od;
od;
if IsZero(xx[1]^2+xx[1]) then Error("Boolean omission control");fi;
Print("ordinary restriction identities=",identities," nonzero corrections=",nonzero," PASS\n");
# New low-degree axioms have literal local certificates at the original width.
zz:=List([1..6],i->Indeterminate(F,i));;ss:=List([1..3],i->zz[2*i-1]+zz[2*i]);;
cube6:=Tuples([0,1],6);;localCertificates:=0;;
for bit in [0,1] do
  hh:=Sum(zz)+bit*One(F);;
  bad:=Filtered(cube6,a->Sum(a) mod 5<>bit);;
  low:=List(Combinations([1..3],2),ij->ss[ij[1]]*ss[ij[2]]);;
  for j in [1..3] do
    others:=Difference([1..6],[2*j-1,2*j]);;
    ml:=zz[2*j-1]*zz[2*j]+(1+ss[j])*(Sum(zz{others})+bit*One(F));;
    if not IsZero((1+ss[j])*(zz[2*j-1]+hh)-ml-(zz[2*j]^2+zz[2*j])) then Error("local Boolean correction");fi;
    Add(low,ml);
  od;
  for poly in low do
    cert:=Sum(bad,a->Value(poly,zz,List(a,t->t*One(F)))*
      Product([1..6],j->zz[j]+(1-a[j])*One(F)));;
    if not IsZero(poly-cert) then Error("forward local certificate");fi;
    localCertificates:=localCertificates+1;
  od;
od;
AA:=1+zz[1];;BB:=zz[1]+zz[2]+zz[3]+1;;gg:=AA*BB;;
if not IsZero(gg^2+gg-BB^2*(AA^2+AA)-AA*(BB^2+BB)) then Error("quadratic Boolean lift");fi;
Print("forward local polynomial certificates=",localCertificates,
      " Boolean corrections=6; reverse Boolean identity PASS\n");
Print("ALL PARITY COMPRESSION CONTROLS PASSED\n");
QUIT;
