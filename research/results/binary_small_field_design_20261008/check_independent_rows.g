# Verify the independent-row expected dimension bound on actual multiplication
# images, and exact line incidence for all full-row-rank matrices in fixed small
# controls. GAP native finite-field ranks; no parameter fitting or larger runs.
# F2: k=3, h=1,2,3; F3: k=3, h=1,2. Six domains per matrix:
# A=1 or x1, with U degree 0,p-1,3(p-1). Full domains also verify saturation.
mul := function(a,b) return List([1..Length(a)],i->a[i]*b[i]); end;;
points:=[];; elements:=[];; inputs:=[];; coeffs:=[];; domains:=[];; amps:=[];;
zero:=0;; one:=1;; mat:=[];; rows:=[];; totals:=[];; incidence:=[];;
aa:=[];; uu:=[];; qq:=[];; rr:=[];; wmat:=[];; rankw:=[];;
checks:=0;; matrices:=0;; negative:=0;;
Print("Fixed enumeration: 867 full-rank matrices, six multiplication domains each\n");
for prime in [2,3] do
 field:=GF(prime); zero:=Zero(field);one:=One(field);
 elements:=List([0..prime-1],i->i*one);
 points:=Tuples(elements,3);
 inputs:=List([1..3],i->List(points,x->x[i]));
 degrees:=[0,prime-1,3*(prime-1)];
 domains:=[];
 for deg in degrees do
  exps:=Filtered(Tuples([0..prime-1],3),e->Sum(e)<=deg);
  Add(domains,List(exps,e->List(points,x->Product([1..3],i->x[i]^e[i]))));
 od;
 amps:=[List(points,x->one),inputs[1]];
 rankw:=[];
 for aa in amps do
  for uu in domains do
   wmat:=List(uu,f->Concatenation(List(inputs,g->mul(mul(aa,g),f))));
   Add(rankw,RankMat(wmat));
  od;
 od;
 if prime=2 then hs:=[1,2,3];else hs:=[1,2];fi;
 for h in hs do
  beta:=(prime^(3-h)-1)/(prime^3-1);
  totals:=List([1..6],i->0);incidence:=List(points,x->0); count:=0;
  for coeffs in Tuples(elements,3*h) do
   mat:=List([1..h],j->coeffs{[3*j-2..3*j]});
   if RankMat(mat)=h then
    count:=count+1;matrices:=matrices+1;
    rows:=List(mat,c->List([1..Length(points)],j->Sum([1..3],i->c[i]*inputs[i][j])));
    for j in [1..Length(points)] do
     if ForAll(rows,q->q[j]=zero) then incidence[j]:=incidence[j]+1;fi;
    od;
    idx:=0; nullities:=[];
    for aa in amps do
     for uu in domains do
      idx:=idx+1;
      rr:=List(uu,f->Concatenation(List(rows,q->mul(mul(aa,q),f))));
      nullity:=rankw[idx]-RankMat(rr);
      if nullity<0 then Error("map did not factor");fi;
      totals[idx]:=totals[idx]+nullity;Add(nullities,nullity);checks:=checks+1;
     od;
    od;
    if nullities[3]<>prime^(3-h)-1 then Error("full-domain saturation");fi;
    Print("p=",prime," h=",h," C=",List(coeffs,IntFFE)," intersections=",nullities,"\n");
   fi;
  od;
  expected:=Product([0..h-1],j->prime^3-prime^j);
  if count<>expected then Error("enumeration count");fi;
  for j in [2..Length(points)] do
   if incidence[j]<>count*beta then Error("line-incidence rate");fi;
  od;
  means:=List(totals,x->x/count);
  for j in [1..6] do
   if means[j]>beta*rankw[j] then Error("expected dimension bound");fi;
  od;
  if means[3]<>beta*rankw[3] or means[6]<>beta*rankw[6] then Error("full-function mean");fi;
  if 3-h>3*beta then negative:=negative+1;fi;
  Print("PASS p=",prime," h=",h," count=",count," beta=",beta," ranks=",rankw," means=",means,"\n");
 od;
od;
if matrices<>867 or checks<>5202 or negative<>4 then Error("scope totals");fi;
Print("ALL CHECKS PASSED: matrices=",matrices," actual-domain checks=",checks," abstract-space failures=",negative,"\n");
QUIT;
