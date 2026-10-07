# Fixed exact controls: dimension2 over F2 and F3.
# All nonzero combinations of two homogenized diagonal forms have rank2.
# On u=1 the tensor f^T(u I+lambda N)z has bias q^-2, despite
# relative partition rank1 modulo the leading constraint u.
for p in [2,3] do
 F:=GF(p);one:=One(F);zero:=Zero(F);elts:=Elements(F);
 vecs:=Tuples(elts,2);combos:=0;
 for av in vecs do
  if av<>[zero,zero] then
   mat:=[[zero,zero,-av[1]],[zero,zero,-av[2]],[av[1],av[2],zero]];
   if RankMat(mat)<>2 then Error("diagonal combination rank");fi;
   combos:=combos+1;
  fi;
 od;
 id:=IdentityMat(2,F);nilp:=[[zero,one],[zero,zero]];
 counts:=List([1..p],i->0);points:=0;
 for lam in elts do
  pencil:=id+lam*nilp;
  if RankMat(pencil)<>2 then Error("legal affine pencil lost rank");fi;
  for f in vecs do
   for z in vecs do
    value:=IntFFE(f*pencil*z);
    counts[value+1]:=counts[value+1]+1;points:=points+1;
   od;
  od;
 od;
 if not ForAll(counts{[2..p]},x->x=counts[2]) then Error("nonzero counts");fi;
 bias:=(counts[1]-counts[2])/points;
 if bias<>1/p^2 then Error("affine-slice bias");fi;
 Print("field=",p," diagonal_combinations=",combos," rank=2",
       " slice_points=",points," value_counts=",counts," bias=",bias,"\n");
od;
Print("PASS fixed exact controls; all-parameter conclusions use symbolic proofs\n");
QUIT;
