# Boundary specialization control: lengths1..3 over {0,1,x,y,1+x,1+y},
# all Boolean points. Constants/repetitions/complementary literals are included.
# 1032 clause-value checks; 2904 companion checks; positive falsity cases required.
F:=GF(2);; z:=Zero(F);; o:=One(F);;
points:=Tuples([z,o],2);;
literalValues:=List(points,p->[z,o,p[1],p[2],o+p[1],o+p[2]]);;
clauseChecks:=0;; companionChecks:=0;; falseCases:=0;;
for k in [1..3] do
 for ids in Tuples([1..6],k) do
  for vals in literalValues do
   av:=vals{ids};; gv:=List(av,a->o-a);;
   # Coefficient rows are identity: one selected input per row.
   pval:=Product(List(gv,g->o-g),o);;
   qval:=Product(av,o);;
   if pval<>qval then Error("Clause image"); fi;
   if (qval=o)<>ForAll(av,a->a=o) then Error("Falsity convention"); fi;
   clauseChecks:=clauseChecks+1;
   if qval=o then falseCases:=falseCases+1; fi;
   for i in [1..k] do
    companion:=gv[i]*pval;;
    rhs:=(av[i]-av[i]^2)*Product(av{Filtered([1..k],j->j<>i)},o);;
    if companion<>rhs or companion<>z then Error("Companion image"); fi;
    companionChecks:=companionChecks+1;
   od;
  od;
 od;
od;
if clauseChecks<>1032 or companionChecks<>2904 or falseCases<>156 then Error("Sizing"); fi;
Print("clause_checks=",clauseChecks," companion_checks=",companionChecks,
 " nonzero_falsity_cases=",falseCases,"\n");
Print("PASS: all Boolean boundary images, including constants and repeated literals.\n");
QUIT;
