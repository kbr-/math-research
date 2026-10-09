# Stronger scope control: every fully pinned shared fibre admits arbitrary
# constant, linear and any one private-quadratic moment, but no degree-neutral
# retraction exists because product of s>=3 shared bits equals a quadratic.
# One smallest instance s=3, three disjoint private pairs; 512 assignments.
Iv:=function(b) if b then return 1; else return 0; fi; end;
Main:=function()
 local one,sp,pp,pairs,q,a,fiber,sz,rel,ranks,checks,ij,mat,rr;
 one:=One(GF(2));sp:=Combinations([1..3]);pp:=Combinations([4..9]);
 pairs:=[[4,5],[6,7],[8,9]];
 q:=b->Sum(pairs,z->Iv(IsSubset(b,z))) mod 2;
 sz:=[];ranks:=[];rel:=[];checks:=0;
 Print("SIZING 512 assignments, eight fibres, fifteen private pairs; matrices<=36x8\n");
 for a in sp do
  fiber:=Filtered(pp,b->q(b)=Iv(Length(a)=3));
  Add(sz,Length(fiber));
  rr:=RankMat(List(fiber,b->Concatenation([one],List([4..9],i->Iv(i in b)*one))));
  if rr<>7 then Error("affine rank"); fi;
  for ij in Combinations([4..9],2) do
   mat:=List(fiber,b->Concatenation([one],List([4..9],i->Iv(i in b)*one),[Iv(IsSubset(b,ij))*one]));
   rr:=RankMat(mat); if rr<>8 then Error("one quadratic not free"); fi;
   checks:=checks+1;
  od;
  Add(ranks,rr);Append(rel,List(fiber,b->Union(a,b)));
 od;
 if RankMat(List(rel,p->Concatenation([one],List([1..9],i->Iv(i in p)*one))))<>10 then Error("full affine rank"); fi;
 if not ForAll(rel,p->Iv(IsSubset(p,[1..3]))=q(p)) then Error("monic drop"); fi;
 Print("ROW_SIZE=",Length(rel)," FIBER_SIZES=",sz," ONE_QUADRATIC_CHECKS=",checks," ALL_RANKS=8 FULL_AFFINE_RANK=10 MONIC_DROP=3_TO_2\n");
 Print("ALL CONDITIONAL QUADRATIC CONTROLS PASSED\n");
end;
Main();
QUIT;
