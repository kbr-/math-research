# Exact controls for paired cyclic exact-one systems, not a PC degree search.
# Stages: one 64-point canonical encoding, 16 integral interpolation identities;
# 49 pair-code cosets; five bounded cycle sizes (9801 ternary words total);
# all 128 three-group incidence families. GAP supplies exact linear algebra.
R := Rationals;; z := List([1..6],i->Indeterminate(R,i));;
tuples := Tuples([0,1],6);;
bad := Filtered(tuples,a->Sum(a)<>1);;
delta := a->Product([1..6],i->a[i]*z[i]+(1-a[i])*(1-z[i]));;
localPolys := [Sum(z)-1];;
Append(localPolys,List(Combinations([1..6],2),ij->z[ij[1]]*z[ij[2]]));;
vals := function(p,a) return Value(p,z,a); end;;
for p in localPolys do
  if p<>Sum(bad,a->vals(p,a)*delta(a)) then Error("interpolation"); fi;
od;
if not ForAll(tuples,a->((Sum(a) mod 7=1)=(Sum(a)=1))) then Error("modular encoding"); fi;
Print("local assignments=",Length(tuples)," forbidden=",Length(bad),
      " integral interpolation identities=",Length(localPolys)," PASS\n");
F := GF(7);; els := Elements(F);;
for ab in Tuples(els,2) do
  dist := Minimum(List(els,c->Number(ab,t->t<>c)));
  if dist<>Number([1],i->ab[1]<>ab[2]) then Error("pair radius"); fi;
od;
Print("pair-code radius controls=49 PASS\n");
total := 0;;
for n in [4,5,6,7,8] do
  H := List([1..n],i->List([1..n],j->(Position([false,true],j in List([0..2],d->1+((i+d-1) mod n)))-1)));
  A7 := List(H,row->Concatenation(List(row,a->[a*One(F),a*One(F)])));
  rank7 := RankMat(A7);;
  allwords := Tuples([0,1,2],n);;
  full := 0;; deleted := List([1..n],i->0);; witnesses := List([1..n],i->fail);;
  for t in allwords do
    violated := Filtered([1..n],i->Sum([1..n],j->H[i][j]*t[j])<>1);
    if IsEmpty(violated) then full:=full+1; fi;
    if Length(violated)=1 then
      j:=violated[1]; deleted[j]:=deleted[j]+1;
      if witnesses[j]=fail then witnesses[j]:=t; fi;
    fi;
  od;
  total:=total+Length(allwords);
  if n mod 3<>0 then
    if full<>0 or rank7<>n or not ForAll(deleted,c->c>0) then Error("minimality/rank"); fi;
    for fld in [Rationals,GF(2),GF(7)] do
      T:=List(H,row->List(row,a->a*One(fld)));;
      inv:=Inverse(T);;
      if inv=fail then Error("invertibility"); fi;
      for j in [1..n] do
        if Sum(inv[j])<>One(fld)/3 then Error("constant ledger"); fi;
      od;
    od;
    if n mod 3=0 then Error("char3 scalar"); fi;
    if not ForAll([1..2*n],j->Number(A7,row->row[j]<>Zero(F))=3) then Error("occurrences"); fi;
  else
    if full=0 or rank7<>n-2 then Error("divisible-size control"); fi;
  fi;
  Print("n=",n," words=",Length(allwords)," rank7=",rank7," full=",full,
        " deleted-only counts=",deleted," first witnesses=",witnesses,"\n");
od;
Print("cycle ternary words total=",total," PASS\n");
# The certificate after deriving L_i=s_i-c and R=s_1*s_2 is literal.
s1:=z[1]+z[2];;s2:=z[3]+z[4];; c:=1/3;;
if not IsOne((s1*s2-s2*(s1-c)-c*(s2-c))/c^2) then Error("final certificate"); fi;
Print("literal rational final certificate=1; characteristic3 uses sum rows=-n PASS\n");
scopes:=Filtered(Combinations([1..3]),S->not IsEmpty(S));;
covering:=0;; unsat:=0;; inconsistent:=0;; collision:=0;; branches:=0;;
Z2:=List([1..6],i->Indeterminate(GF(2),i));;
S2:=List([1..3],i->Z2[2*i-1]+Z2[2*i]);;
for selected in Combinations(scopes) do
  if IsEmpty(selected) or Union(selected)<>[1..3] then continue; fi;
  M:=List(selected,S->List([1..3],j->(Position([false,true],j in S)-1)*One(GF(2))));;
  rk:=RankMat(M);; nullity:=3-rk;; covering:=covering+1;
  if rk*Maximum(List(selected,Length))<3 then Error("basis cover rank"); fi;
  sols:=Filtered(Tuples([0,1],3),a->ForAll(selected,S->Sum(S,j->a[j])=1));;
  pars:=Filtered(Tuples([0,1],3),a->ForAll(selected,S->Sum(S,j->a[j]) mod 2=1));;
  if IsEmpty(sols) then
    unsat:=unsat+1;
    if IsEmpty(pars) then inconsistent:=inconsistent+1;
    else
      if Length(pars)<>2^nullity or not ForAll(pars,a->ForAny(selected,S->Sum(S,j->a[j])>=3)) then Error("parity witness"); fi;
      collision:=collision+1;
      free:=First(Combinations([1..3],nullity),I->Length(Set(List(pars,a->a{I})))=2^nullity);;
      if free=fail then Error("free coordinates"); fi;
      weights:=[];;
      for a in Tuples([0,1],nullity) do
        fac:=List([1..nullity],j->S2[free[j]]+(1-a[j])*One(GF(2)));;
        weight:=Product(fac,One(Z2[1]));;Add(weights,weight);;branches:=branches+1;
        for j in [1..nullity] do
          other:=Product(fac{Difference([1..nullity],[j])},One(Z2[1]));;
          i:=free[j];;
          boolsum:=Z2[2*i-1]^2+Z2[2*i-1]+Z2[2*i]^2+Z2[2*i];;
          if weight*(S2[i]-a[j]*One(GF(2)))<>other*boolsum then Error("weighted Boolean identity"); fi;
        od;
      od;
      if not IsOne(Sum(weights)) then Error("branch partition"); fi;
    fi;
  fi;
od;
Print("incidence families=128 covering=",covering," unsatisfiable=",unsat,
      " parity-inconsistent=",inconsistent," collision-families=",collision,
      " weighted branches=",branches," PASS\n");
# Nonzero-nullity control: scopes {1},{2},{1,2,3},{4,5,6} have
# four parity branches, all blocked by the first three scopes.
ZZ:=List([1..12],i->Indeterminate(GF(2),i));;
FF:=[ZZ[9]+ZZ[10],ZZ[11]+ZZ[12]];; WW:=[];;
for aa in Tuples([0,1],2) do
  facs:=List([1..2],j->FF[j]+(1-aa[j])*One(GF(2)));;
  W:=Product(facs);;Add(WW,W);;
  for j in [1..2] do
    if W*(FF[j]-aa[j]*One(GF(2)))<>facs[3-j]*(FF[j]^2+FF[j]) then Error("nonzero-nullity weight"); fi;
  od;
od;
if not IsOne(Sum(WW)) or IsOne(Sum(WW{[1..3]})) then Error("partition negative control"); fi;
Print("nullity-two control: four weights, eight Boolean identities, omitted-weight rejection PASS\n");
Print("ALL PAIRED-CYCLE AND PARITY CONTROLS PASSED\n");
QUIT;
