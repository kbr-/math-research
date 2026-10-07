# Fixed control for the general trade-cube proof, not a PC-degree computation.
# q=3, r=h=2: 8 cube points, 3 distinct supports, 6 companions per point.
# Expected: all normalized companions vanish; ranks 4 and 7; zero map fails.
F:=GF(2);; pts:=Tuples(Elements(F),3);;
sets:=[[1,2],[1,3],[2,3]];;
mat:=[];; bad:=0;; checked:=0;;
for z in pts do
 row:=Concatenation([One(F)],z);;
 for S in sets do
  inputs:=List(S,i->One(F)-z[i]);;
  product:=Product(List(inputs,g->One(F)-g));;
  expected:=Product(List(S,i->z[i]));;
  Assert(0,product=expected);
  for g in inputs do
   Assert(0,g*product=Zero(F)); checked:=checked+1;
   if g<>Zero(F) then bad:=bad+1; fi;
  od;
  Add(row,product);
 od;
 Add(mat,row);
od;
Assert(0,RankMat(List(mat,row->row{[1..4]}))=4);
Assert(0,RankMat(mat)=7);
Assert(0,bad>0);
Print("points=",Length(pts)," distinct supports=",Length(sets),"\n");
Print("normalized companions checked=",checked,"; failures=0\n");
Print("affine rank=4; affine plus selector rank=7\n");
Print("all-zero coefficient negative control: nonzero companions=",bad,"\n");
QUIT;
