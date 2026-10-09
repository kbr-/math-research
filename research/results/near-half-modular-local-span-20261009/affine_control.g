# Exact local affine interpolation and a field-consistent odd-modulus control.
Check:=function(b,s) if not b then Error(s); fi; end;
BoolInt:=function(b) if b then return 1; else return 0; fi; end;
Print("SIZING arities=0..3, all relations, affine coefficients F2/F3/{-1,0,1}; source k=8 v=16 six rows\n");
# Coefficient vectors in the squarefree monomial basis, using GAP's native fields.
identities:=0;
for k in [0..3] do
 pts:=Tuples([0,1],k); mons:=Combinations([1..k]);
 for fld in [GF(2),GF(3),Rationals] do
  one:=One(fld);zero:=Zero(fld);
  if fld=Rationals then choices:=[-1,0,1];else choices:=Elements(fld);fi;
  indicators:=[];
  for x in pts do
   Add(indicators,List(mons,S->
    (Product(Filtered([1..k],i->x[i]=1),i->BoolInt(i in S))) *
    ((-one)^Number(S,i->x[i]=0))));
  od;
  for mask in Tuples([0,1],Length(pts)) do
   for cf in Tuples(choices,k+1) do
    vals:=List(pts,x->cf[1]+Sum([1..k],i->cf[i+1]*x[i]));
    if ForAll([1..Length(pts)],i->mask[i]=0 or vals[i]=zero) then
     got:=List(mons,S->zero);
     for i in [1..Length(pts)] do if mask[i]=0 then got:=got+vals[i]*indicators[i];fi;od;
     want:=List(mons,S->zero);want[1]:=cf[1];
     for i in [1..k] do want[Position(mons,[i])]:=cf[i+1];od;
     Check(got=want,"literal affine interpolation");identities:=identities+1;
    fi;
   od;
  od;
 od;
od;
# Deterministic supports: three labelled partitions. Rank choice is existentially guaranteed.
k:=8;v:=16;q:=257;fld:=GF(q);one:=One(fld);zero:=Zero(fld);
scopes:=[[1..8],[9..16],[1,3,5,7,9,11,13,15],[2,4,6,8,10,12,14,16],[1,2,3,4,9,10,11,12],[5,6,7,8,13,14,15,16]];
pivots:=[1,9,3,2,10,5];
base:=List(scopes,S->List([1..v],i->BoolInt(i in S)));
Check(RankMat(base*one)<6,"unperturbed rank negative control");
chosen:=fail;
for flag in Tuples([0,1],6) do
 mat:=List(base,ShallowCopy);
 for j in [1..6] do mat[j][pivots[j]]:=1+2*flag[j];od;
 if RankMat(mat*one)=6 then chosen:=flag;break;fi;
od;
Check(chosen<>fail,"multilinear determinant grid");
targets:=[5,4,4,4,4,4];pinchecks:=0;hornchecks:=0;allowedcounts:=[];
for j in [1..6] do
 weights:=mat[j]{scopes[j]};target:=targets[j];pts:=Tuples([0,1],k);
 allowed:=Filtered(pts,x->Sum([1..k],i->weights[i]*x[i])=target);Add(allowedcounts,Length(allowed));
 Check(Length(allowed)>0,"nonempty row");
 Check(ForAll(allowed,x->Sum(x) mod 2=target mod 2),"binary affine consequence");
 for S in Filtered(Combinations([1..k]),S->Length(S)<=2) do
  for y in Tuples([0,1],Length(S)) do
   Check(ForAny(allowed,x->x{S}=y),"uniform pins through two");pinchecks:=pinchecks+1;
  od;
 od;
 for flip in Tuples([0,1],k) do
  pair:=First(Combinations(Filtered([1..k],i->weights[i]=1),2),S->flip[S[1]]=flip[S[2]]);
  Check(pair<>fail,"same-polarity unit pair");
  rest:=Difference(Filtered([1..k],i->weights[i]=1),pair);
  x:=List([1..k],i->0);for i in rest{[1..target-1]} do x[i]:=1;od;
  y:=ShallowCopy(x);x[pair[1]]:=1;y[pair[2]]:=1;
  Check(x in allowed and y in allowed,"allowed meet operands");
  meet:=List([1..k],i->((Minimum((x[i]+flip[i]) mod 2,(y[i]+flip[i]) mod 2)+flip[i]) mod 2));
  Check(not meet in allowed,"every polarity non-Horn");hornchecks:=hornchecks+1;
 od;
od;
Check(ForAll([1..v],i->Sum([1..4],j->base[j][i]) mod 2=0) and Sum(targets{[1..4]}) mod 2=1,"literal global affine unit");
Print("INTERPOLATION_IDENTITIES=",identities,"\n");
Print("SOURCE q=",q," rank=",RankMat(mat*one)," flags=",chosen," allowed=",allowedcounts," pin_checks=",pinchecks," polarity_checks=",hornchecks,"\n");
Print("Binary sum of first two row layers is the literal constant one; original canonical degree ceiling 8\n");
Print("ALL LOCAL AFFINE CONTROLS PASSED\n");
QUIT;
