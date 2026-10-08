# Check the new weighted branch-comparison rule on a genuinely nonlinear
# selector pair that is nested only after weighting. z1=x1*x2,z2=x2*x3,
# w=1-(1-z1)*z2. All three chain cells survive. Two affine-plus-selector
# parent inputs, all 16 legal two-row coefficient matrices, all 8 old points.
F:=GF(2);; points:=Tuples([Zero(F),One(F)],3);;
out:=OutputTextFile("research/results/binary_overlap_learning_20261008/branch-cases.txt",false);;
SetPrintFormattingStatus(out,false);;
checks:=0;; unweightedFailures:=0;; cellSupport:=[0,0,0];;
for x in points do
 z1:=x[1]*x[2];z2:=x[2]*x[3];w:=One(F)-(One(F)-z1)*z2;
 cells:=[One(F)-z1,z1-z2,z2];
 if Sum(cells)<>One(F) or w*(z1*z2-z2)<>Zero(F) then Error("weighted chain"); fi;
 gs:=[x[1]+z1+z2,One(F)+x[3]+z2];
 for a in [0..2] do
  chi:=cells[a+1];
  if w*chi<>Zero(F) then cellSupport[a+1]:=cellSupport[a+1]+1; fi;
  states:=[Zero(F),Zero(F)];
  if a>=1 then states[1]:=One(F); fi;
  if a>=2 then states[2]:=One(F); fi;
  qs:=[x[1]+states[1]+states[2],One(F)+x[3]+states[2]];
  for j in [1..2] do
   if w*chi*(gs[j]-qs[j])<>Zero(F) then Error("branch input"); fi;
  od;
  for flat in Tuples([Zero(F),One(F)],4) do
   mat:=[flat{[1..2]},flat{[3..4]}];
   pg:=Product(mat,row->One(F)-row*gs);
   pq:=Product(mat,row->One(F)-row*qs);
   for j in [1..2] do
    diff:=chi*(gs[j]*pg-qs[j]*pq);
    if w*diff<>Zero(F) then Error("companion comparison"); fi;
    if diff<>Zero(F) then unweightedFailures:=unweightedFailures+1; fi;
    checks:=checks+1;
   od;
   AppendTo(out,List(x,Int),";",a,";",List(flat,Int),";",Int(w*chi),";",Int(pg),";",Int(pq),"\n");
  od;
 od;
od;
CloseStream(out);
if checks<>768 or not ForAll(cellSupport,n->n>0) or unweightedFailures=0 then Error("coverage"); fi;
Print("weighted companion comparisons=",checks," cell supports=",cellSupport,
 " unweighted negative controls=",unweightedFailures,"\nAll assertions passed.\n");
QUIT;
