# Robust subset-sum groups force affine fullness in every target fibre in
# mismatched characteristic. Native GAP ranks; finite tests do not certify
# the random-source probability estimates.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
Sums:=function(a,q)
 return Set(List(Tuples([0,1],Length(a)),x->Sum([1..Length(a)],i->a[i]*x[i]) mod q));
end;
Robust:=function(a,q,d)
 return ForAll(Filtered(Combinations([1..Length(a)]),s->Length(s)<=d),s->Length(Sums(a{Difference([1..Length(a)],s)},q))=q);
end;
affine:=0;equalchar:=0;conditional:=0;quad:=0;
Print("SIZING q3 two three-coordinate groups:64 coefficient patterns,3 targets,3 proof fields; q5 all-ones ten-bit control; q3 ten-bit robust-three group with603 conditional fibres\n");
for a in Tuples([1,2],6) do
 Check(Robust(a{[1..3]},3,1) and Robust(a{[4..6]},3,1),"two robust groups");
 for b in [0..2] do
  allowed:=Filtered(Tuples([0,1],6),x->Sum([1..6],i->a[i]*x[i]) mod 3=b);
  mat:=List(allowed,x->Concatenation([1],x));
  for fld in [GF(2),GF(5),Rationals] do Check(RankMat(mat*One(fld))=7,"mismatched affine fullness");affine:=affine+1;od;
  Check(RankMat(mat*One(GF(3)))<7,"matching characteristic negative control");equalchar:=equalchar+1;
 od;
od;
a:=List([1..10],i->1);Check(Robust(a{[1..5]},5,1),"quintic robust group");
for b in [0..4] do
 allowed:=Filtered(Tuples([0,1],10),x->Sum(x) mod 5=b);mat:=List(allowed,x->Concatenation([1],x));
 for fld in [GF(2),GF(3),Rationals] do Check(RankMat(mat*One(fld))=11,"quintic affine fullness");affine:=affine+1;od;
od;
# Both groups cover F3, but not after deleting a coordinate. Weight-two fibre
# on four bits has a binary parity consequence.
Check(Length(Sums([1,1],3))=3 and not Robust([1,1],3,1),"robustness scope");
allowed:=Filtered(Tuples([0,1],4),x->Sum(x) mod 3=2);
Check(RankMat(List(allowed,x->Concatenation([1],x))*One(GF(2)))=4,"mere coverage insufficient");
# Three deletions leave two nonzero coefficients, enough for F3 coverage.
Check(Robust([1,1,1,1,1],3,3),"robust-three hypothesis");pts:=Tuples([0,1],10);
for b in [0..2] do
 allowed:=Filtered(pts,x->Sum(x) mod 3=b);
 for U in Filtered(Combinations([1..10]),s->Length(s)<=2) do
  free:=Difference([1..10],U);
  for pin in Tuples([0,1],Length(U)) do
   fibre:=Filtered(allowed,x->x{U}=pin);
   Check(RankMat(List(fibre,x->Concatenation([1],x{free}))*One(GF(2)))=Length(free)+1,"conditional affine fullness");conditional:=conditional+1;
  od;
 od;
 for pair in Combinations([1..10],2) do
  Check(RankMat(List(allowed,x->Concatenation([1],x,[x[pair[1]]*x[pair[2]]]))*One(GF(2)))=12,"one quadratic moments onto");quad:=quad+1;
 od;
od;
Check(3^15<2^25,"conditional source third decay factor below one");
Print("AFFINE_RANKS=",affine," EQUAL_CHARACTERISTIC_FAILURES=",equalchar," CONDITIONAL_FIBRES=",conditional," SPARSE_QUADRATIC_RANKS=",quad," DECAY_FOURTH_POWER=",3^15/2^25,"\n");
Print("ALL ROBUST SUBSET-SUM CONTROLS PASSED\n");
QUIT;
