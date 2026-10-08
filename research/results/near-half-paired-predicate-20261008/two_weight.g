# Exact finite controls for the two-weight affine map, carry gluing,
# branch classification and modular chain cores. This is not a PC search.
# Stages: 672 local Boolean inputs; 5376 two-row inputs; 81 four-group
# systems; a two-component conflict; 6804 ternary words in two chain sizes.
FF:=GF(2);;
for q in [3,5,7] do
  N:=q+1;; cube:=Tuples([0,1],N);; pairs:=Combinations([1..N],2);;
  for bit in [0,1] do
    allowed:=Filtered(cube,x->Sum(x) mod q=bit);;
    image:=List(cube,x->List(x,t->(Sum(x)+t+bit) mod 2));;
    if not ForAll([1..Length(cube)],i->((cube[i] in allowed)=(Sum(image[i])<=1))) then Error("affine map"); fi;
    for i in [1..Length(cube)] do
      if List(image[i],t->(Sum(image[i])+t+bit) mod 2)<>cube[i] then Error("involution"); fi;
    od;
    aff:=List(allowed,x->Concatenation([One(FF)],List(x,t->t*One(FF))));;
    quad:=List(pairs,ij->List(image,u->(u[ij[1]]*u[ij[2]])*One(FF)));;
    if RankMat(aff)<>N+1 or RankMat(quad)<>Binomial(N,2) then Error("complete local spaces"); fi;
    Print("q=",q," bit=",bit," allowed=",Length(allowed)," affine rank=",RankMat(aff),
          " quadratic basis rank=",RankMat(quad)," PASS\n");
  od;
od;
checked:=0;; negative:=fail;;
for overlap in [2,4,6] do
  scopeA:=[1..6];;scopeB:=Concatenation([1..overlap],[7..12-overlap]);;
  for rhs in Tuples([0,1],2) do
    admissible:=6-overlap<5-AbsInt(rhs[1]-rhs[2]);;
    good:=0;; different:=0;;
    for x in Tuples([0,1],12-overlap) do
      checked:=checked+1;
      sums:=[Sum(scopeA,j->x[j]),Sum(scopeB,j->x[j])];;
      if ForAll([1..2],j->sums[j] mod 5=rhs[j]) then
        good:=good+1;;flags:=List([1..2],j->(sums[j]-rhs[j])/5);;
        if flags[1]<>flags[2] then different:=different+1;negative:=[overlap,rhs,x,flags];fi;
      fi;
    od;
    if admissible and different<>0 then Error("carry gluing");fi;
    Print("overlap=",overlap," rhs=",rhs," eligible=",admissible,
          " joint=",good," unequal carries=",different,"\n");
  od;
od;
if negative=fail then Error("missing forbidden-edge control");fi;
Print("two-row inputs=",checked," forbidden-edge witness=",negative," PASS\n");
scopes4:=Combinations([1..4],3);;systems:=0;;unsat:=0;;branchChecks:=0;;
for states in Tuples([-1,0,1],4) do
  chosen:=Filtered([1..4],i->states[i]<>-1);;
  if IsEmpty(chosen) then continue;fi;
  scopes:=scopes4{chosen};;bs:=states{chosen};;
  if Union(scopes)<>[1..4] then continue;fi;
  systems:=systems+1;
  sols:=Filtered(Tuples([0,1,2],4),t->ForAll([1..Length(scopes)],i->Sum(scopes[i],j->t[j]) mod 5=bs[i]));;
  if IsEmpty(sols) then unsat:=unsat+1;fi;
  # Any two distinct 3-subsets of four groups overlap in two groups: one carry component.
  for eps in [0,1] do
    for a in Tuples([0,1],4) do
      if not ForAll([1..Length(scopes)],i->Sum(scopes[i],j->a[j]) mod 2=(bs[i]+eps) mod 2) then continue;fi;
      branchChecks:=branchChecks+1;
      collision:=ForAny(scopes,S->Sum(S,j->a[j])>=2);;
      if not collision then
        t:=List(a,z->eps*2*(1-z)+z);;
        if not t in sols then Error("branch satisfying lift");fi;
      elif not IsEmpty(sols) then
        # A blocked branch is allowed even when another branch satisfies the system.
      fi;
    od;
  od;
od;
Print("four-group configurations=81 covering=",systems," unsatisfiable=",unsat,
      " compatible parity branches=",branchChecks," PASS\n");
# Opposite carries on two rows sharing only the third group, with all group parities zero.
badLift:=Filtered(Tuples([0,1,2],5),t->ForAll(t,z->z mod 2=0)
  and Sum(t{[1,2,3]})=0 and Sum(t{[3,4,5]})=6);;
if not IsEmpty(badLift) then Error("component conflict");fi;
Print("two-component zero-parity conflict has no lift PASS\n");
total:=0;;
for a in [1,2] do
  n:=3*a+2;; inds:=Filtered([1..n],i->i mod 3<>0);;m:=Length(inds);;
  scopes:=List(inds,i->List([0..2],d->1+((i+d-1) mod n)));;
  bs:=List(inds,i->Position([false,true],i=n)-1);;
  H:=List(scopes,S->List([1..n],j->(Position([false,true],j in S)-1)));;
  rk5:=RankMat(List(H,row->List(row,t->t*One(GF(5)))));;
  rk2:=RankMat(List(H,row->List(row,t->t*One(FF))));;
  if rk5<>m or rk2<>m then Error("chain rank");fi;
  full:=0;; deleted:=List([1..m],i->0);;witnesses:=List([1..m],i->fail);;
  for t in Tuples([0,1,2],n) do
    total:=total+1;
    badRows:=Filtered([1..m],i->Sum(scopes[i],j->t[j]) mod 5<>bs[i]);;
    if IsEmpty(badRows) then full:=full+1;fi;
    if Length(badRows)=1 then
      i:=badRows[1];deleted[i]:=deleted[i]+1;
      if witnesses[i]=fail then witnesses[i]:=t;fi;
    fi;
  od;
  occ:=List([1..n],j->Number(scopes,S->j in S));;
  if full<>0 or not ForAll(deleted,t->t>0) or Number(occ,t->t=3)<>2 or Minimum(occ)<>2 then Error("chain minimality");fi;
  Print("a=",a," n=",n," rows=",m," ranks=",[rk2,rk5]," full=",full,
       " deleted-only counts=",deleted," witnesses=",witnesses," occurrences=",occ,"\n");
od;
Print("chain ternary inputs=",total," PASS\n");
Print("ALL TWO-WEIGHT CONTROLS PASSED\n");
QUIT;
