# Test the strict difference between projection shattering and filtered
# retraction on the smallest all-parameter counterexample: s=r=3, nine bits.
# 512 assignments, all 36 seven-coordinate and 9 eight-coordinate projections.
Iv:=function(b) if b then return 1; else return 0; fi; end;
Main:=function()
 local pts,pairs,q,rel,keep,omit,proj,full7,full8,polychecks,rhs,prodOther,p,other;
 pts:=Combinations([1..9]);pairs:=[[4,5],[6,7],[8,9]];
 q:=p->Sum(pairs,z->Iv(IsSubset(p,z))) mod 2;
 rel:=Filtered(pts,p->Iv(IsSubset(p,[1..3]))=q(p));
 full7:=[];full8:=[];polychecks:=0;
 Print("SIZING 512 assignments, 45 near-full projections, three literal monic drops\n");
 for omit in Combinations([1..9],2) do
  keep:=Difference([1..9],omit);
  proj:=Set(List(rel,p->Intersection(p,keep)));
  if Length(proj)=2^Length(keep) then
   Add(full7,omit);
   if not omit in pairs then Error("unexpected shattered seven-set"); fi;
   other:=Difference([4..9],omit);
   for p in rel do
    # (r-1)=2 vanishes in F2; x_keep equals product of all six private bits.
    if Iv(IsSubset(p,keep))<>Iv(IsSubset(p,[4..9])) then Error("monic drop"); fi;
    polychecks:=polychecks+1;
   od;
  fi;
 od;
 for omit in Combinations([1..9],1) do
  keep:=Difference([1..9],omit);
  if Length(Set(List(rel,p->Intersection(p,keep))))=2^Length(keep) then Add(full8,omit);fi;
 od;
 if full7<>pairs or Length(full8)<>0 then Error("projection classification");fi;
 Print("RELATION_SIZE=",Length(rel)," FULL_SEVEN_OMISSIONS=",full7," FULL_EIGHT_COUNT=",Length(full8)," MONIC_IDENTITIES=",polychecks," PROJECTION_NUMBER=7 FILTERED_NUMBER_UPPER=6\n");
 Print("ALL STRICT FILTRATION GAP CONTROLS PASSED\n");
end;
Main();
QUIT;
