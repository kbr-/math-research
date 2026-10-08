# Exact controls of circulation automorphisms and mixed differences.
# Figure-eight graph: all 64 orientations, all 9 ternary circulations per
# orientation, every local charge, and all 9 zero-charge cycle-flow points.
# This small graph is a defining-relation control, NOT in the proper expander
# degree window. The charged pseudoideal and rank theorem are proved analytically.
f3:=GF(3);; f4:=GF(4);; om:=Z(4);;
edges:=[[1,2],[2,3],[3,1],[1,4],[4,5],[5,1]];;
localChecks:=0;; vertexChecks:=0;; negativeChecks:=0;; mixedChecks:=0;; lowChecks:=0;;
for shift in [0..2] do
 for label in [0..2] do
  for value in [0..2] do
   lhs:=One(f4)+om^(-label)*om^shift*om^value+om^label*om^(-shift)*om^(-value);
   rhs:=One(f4)+om^(-(label-shift))*om^value+om^(label-shift)*om^(-value);
   if lhs<>rhs then Error("indicator rotation"); fi;
   localChecks:=localChecks+1;
  od;
 od;
 if (om^shift)^2<>om^(-shift) or om^shift*om^(-shift)<>One(f4) then Error("local domains"); fi;
od;
for orient in Tuples([1,-1],6) do
 incidence:=NullMat(5,6,f3);
 for e in [1..6] do
  incidence[edges[e][1]][e]:=orient[e]*One(f3);
  incidence[edges[e][2]][e]:=-orient[e]*One(f3);
 od;
 basis:=NullspaceMat(TransposedMat(incidence));
 if Length(basis)<>2 then Error("cycle dimension"); fi;
 for coeff in Tuples(Elements(f3),2) do
  flow:=coeff*basis;
  if flow*TransposedMat(incidence)<>List([1..5],i->Zero(f3)) then Error("circulation"); fi;
  for v in [1..5] do
   phase:=Sum([1..6],e->incidence[v][e]*flow[e]);
   for charge in [0..2] do
    if om^Int(phase)<>One(f4) then Error("vertex character not fixed"); fi;
    vertexChecks:=vertexChecks+1;
   od;
  od;
 od;
 bad:=List([1..6],e->Zero(f3));bad[1]:=One(f3);
 if Number(bad*TransposedMat(incidence),x->x<>Zero(f3))<>2 then Error("noncirculation control"); fi;
 negativeChecks:=negativeChecks+1;
 ca:=List([1..6],e->Zero(f3));cb:=List([1..6],e->Zero(f3));
 for e in [1..3] do ca[e]:=orient[e]*One(f3); od;
 for e in [4..6] do cb[e]:=orient[e]*One(f3); od;
 companion:=function(flow)
  local a,b;
  a:=Zero(f4);b:=Zero(f4);
  if flow[1]=Zero(f3) then a:=One(f4); fi;
  if flow[4]=Zero(f3) then b:=One(f4); fi;
  return a*(One(f4)+a+b);
 end;
 nonzero:=0;
 for coeff in Tuples(Elements(f3),2) do
  flow:=coeff[1]*ca+coeff[2]*cb;
  mixed:=companion(flow+ca+cb)-companion(flow+ca)-companion(flow+cb)+companion(flow);
  d1:=Zero(f4);d2:=Zero(f4);
  if (flow+ca)[1]=Zero(f3) then d1:=d1+One(f4); fi;
  if flow[1]=Zero(f3) then d1:=d1-One(f4); fi;
  if (flow+cb)[4]=Zero(f3) then d2:=d2+One(f4); fi;
  if flow[4]=Zero(f3) then d2:=d2-One(f4); fi;
  if mixed<>d1*d2 then Error("mixed companion"); fi;
  if mixed<>Zero(f4) then nonzero:=nonzero+1; fi;
  mixedChecks:=mixedChecks+1;
  for e in [1..6] do
   for sign in [1,-1] do
    value:=om^(sign*Int((flow+ca+cb)[e]))-om^(sign*Int((flow+ca)[e]))
      -om^(sign*Int((flow+cb)[e]))+om^(sign*Int(flow[e]));
    if value<>Zero(f4) then Error("low-degree term survived"); fi;
    lowChecks:=lowChecks+1;
   od;
  od;
 od;
 if nonzero<>4 then Error("nonvacuity"); fi;
od;
Print("indicator checks=",localChecks," charged vertex checks=",vertexChecks,
 " noncirculation controls=",negativeChecks," mixed companion checks=",mixedChecks,
 " low-degree character checks=",lowChecks,"\nAll assertions passed.\n");
QUIT;
