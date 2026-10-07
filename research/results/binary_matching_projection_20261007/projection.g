# Verify Fourier phase/fiber projection on the 3-edge charge-c slice over F4,
# retaining coordinate 1. This checks the local algebra, not expander hypotheses.
# 3 charges * sum_T 3^|T| =192 conjunctions, evaluated at 3 labels:576 checks.
F:=GF(4);; om:=Z(4);; zero:=Zero(F);; one:=One(F);;
supports:=Combinations([1..3]);; total:=0;; zeroCases:=0;; constCases:=0;; flatCases:=0;;
for charge in [0..2] do
 for T in supports do
  for labels in Tuples([0,1,2],Length(T)) do
   full:=List([1..3],i->0);;
   for j in [1..Length(T)] do full[T[j]]:=labels[j]; od;
   projected:=List([0,1,2],y->zero);;
   for values in Tuples([0,1,2],Length(T)) do
    beta:=List([1..3],i->0);;
    for j in [1..Length(T)] do beta[T[j]]:=values[j]; od;
    for alpha1 in [0,1,2] do
     # alpha-beta is a multiple a*(1,1,1).
     delta:=List([alpha1-beta[1],-beta[2],-beta[3]],x->x mod 3);;
     if delta[1]=delta[2] and delta[2]=delta[3] then
      phase:=(-Sum([1..3],i->full[i]*beta[i])-charge*delta[1]) mod 3;;
      for y in [0,1,2] do
       projected[y+1]:=projected[y+1]+om^((phase+alpha1*y) mod 3);
      od;
     fi;
    od;
   od;
   expected:=[];
   for y in [0,1,2] do
    count:=Number(Tuples([0,1,2],2),bc->
      (y+bc[1]+bc[2]) mod 3=charge and
      ForAll(T,i->[y,bc[1],bc[2]][i]=full[i]));
    Add(expected,(count mod 2)*one);
   od;
   if projected<>expected then Error("Projection phase mismatch"); fi;
   wt:=Number(projected,x->x<>zero);;
   if wt=0 then zeroCases:=zeroCases+1;
   elif wt=3 then constCases:=constCases+1;
   elif wt=1 then flatCases:=flatCases+1;
   else Error("Not zero or affine flat"); fi;
   total:=total+3;
  od;
 od;
od;
if total<>576 then Error("Sizing"); fi;
Print("evaluations=",total," zero=",zeroCases," constant=",constCases,
 " codimension_one_flat=",flatCases,"\n");
Print("PASS: all 192 projected conjunctions match phase-correct fiber counts.\n");
QUIT;
