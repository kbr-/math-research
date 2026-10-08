# Exhaustive control of the claimed row threshold on one three-input group:
# 64 two-row matrices versus 512 three-row matrices, each at all eight inputs.
# Also check the common-weight repair for the full three-prefix registry.
F:=GF(2);; points:=Tuples([Zero(F),One(F)],3);;
out:=OutputTextFile("research/results/binary_exact_implication_20261008/matrices.txt",false);;
SetPrintFormattingStatus(out,false);;
counts:=[];;
for rows in [2,3] do
 passed:=0;tested:=0;
 for flat in Tuples([Zero(F),One(F)],3*rows) do
  mat:=List([1..rows],i->flat{[3*i-2..3*i]});
  values:=List(points,x->Product(mat,r->One(F)-r*x));
  target:=List(points,x->Product(x,y->One(F)-y));
  good:=values=target;
  if good then passed:=passed+1; fi;
  if good<>(RankMat(mat)=3) then Error("rank versus product control"); fi;
  tested:=tested+1;
  AppendTo(out,rows,";",List(flat,Int),";",List(values,Int),";",good,"\n");
 od;
 Add(counts,[rows,tested,passed]);
od;
CloseStream(out);
if counts<>[[2,64,0],[3,512,168]] then Error("threshold count"); fi;
checks:=0;;
for x in points do
 weight:=x[1];prefix:=One(F)-x[1];
 for i in [2..3] do
  defect:=prefix-(One(F)-x[i])*prefix;
  if weight*defect<>Zero(F) then Error("weighted MP defect"); fi;
  checks:=checks+1;
  for j in [1..i] do
   if weight*x[j]*prefix<>Zero(F) then Error("weighted companion"); fi;
   checks:=checks+1;
  od;
 od;
od;
Print("rows,tested,exact-products: ",counts,"\nweighted identities=",checks,
 "\nAll controls passed; degree and profile certificates are analytic.\n");
QUIT;
