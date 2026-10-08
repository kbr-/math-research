# Exact controls for occurrence copying, clause splitting, and parallel-edge stars.
# Exhaust all 256 subformulas of the 8 nonempty proper clauses on two variables.
# Only minimal unsatisfiable formulas are transformed; even the full inventory
# has 12 literal occurrences, so copying needs at most 4096 Boolean assignments.
OccBit := function(a,i) return RemInt(QuoInt(a,2^(i-1)),2); end;
OccSatisfies := function(cls,a)
 return ForAll(cls,c->ForAny(c,l->(l>0 and OccBit(a,AbsInt(l))=1) or (l<0 and OccBit(a,AbsInt(l))=0)));
end;
OccSat := function(cls,n) return ForAny([0..2^n-1],a->OccSatisfies(cls,a)); end;
OccIndicator := function(n,scope,ones)
 local c,b,s;
 c:=List([1..2^n],i->0);
 for b in [0..2^n-1] do
  s:=Filtered([1..n],i->OccBit(b,i)=1);
  if IsSubset(scope,s) and IsSubset(s,ones) then c[b+1]:=(-1)^(Length(s)-Length(ones)); fi;
 od;
 return c;
end;
OccMain := function()
 local inventory,mask,f,minimal,formulaCount,copyCount,splitCount,copyAssignments,
 q,copied,groups,origMap,c,cc,l,i,j,r,idx,occ,split,used,splitOcc,
 splitIdentities,n,a,ones,p,p0,p1,ra,rb,aa,bb,parallelUnsat,cycleCases,bits;
 inventory:=[[1],[-1],[2],[-2],[1,2],[1,-2],[-1,2],[-1,-2]];
 formulaCount:=0;copyCount:=0;splitCount:=0;copyAssignments:=0;
 for mask in [0..255] do
  f:=Filtered([1..8],i->OccBit(mask,i)=1);f:=List(f,i->inventory[i]);
  formulaCount:=formulaCount+1;
  if not OccSat(f,2) then
   minimal:=ForAll([1..Length(f)],i->OccSat(Concatenation(f{[1..i-1]},f{[i+1..Length(f)]}),2));
   if minimal then
    q:=0;copied:=[];groups:=[[],[]];origMap:=[];
    for c in f do
     cc:=[];
     for l in c do
      q:=q+1;Add(cc,SignInt(l)*q);Add(groups[AbsInt(l)],q);Add(origMap,AbsInt(l));
     od;
     if List(cc,l->SignInt(l)*origMap[AbsInt(l)])<>c then Error("copy substitution failed");fi;
     Add(copied,cc);
    od;
    if q>12 then Error("unsized copied instance");fi;
    for i in [1..2] do
     r:=Length(groups[i]);
     if r=1 then Error("minimal CNF has a private variable");fi;
     if r>=2 then
      for j in [1..r] do
       idx:=RemInt(j,r)+1;
       if origMap[groups[i][j]]<>origMap[groups[i][idx]] then Error("cycle substitution not Booleanity");fi;
       Add(copied,[-groups[i][j],groups[i][idx]]);
      od;
     fi;
    od;
    occ:=List([1..q],i->Sum(copied,c->Number(c,l->AbsInt(l)=i)));
    if not ForAll(occ,o->o=3) then Error("copy occurrence count");fi;
    if OccSat(copied,q) then Error("copy changed unsatisfiability");fi;
    copyAssignments:=copyAssignments+2^q;copyCount:=copyCount+1;
    split:=[];
    for i in [1..Length(f)] do
     Add(split,Concatenation(f[i],[2+i]));Add(split,Concatenation(f[i],[-2-i]));
    od;
    if OccSat(split,2+Length(f)) then Error("split satisfiable");fi;
    if not ForAll([1..Length(split)],i->OccSat(Concatenation(split{[1..i-1]},split{[i+1..Length(split)]}),2+Length(f))) then Error("split lost minimality");fi;
    used:=Set(List(Concatenation(f),AbsInt));
    splitOcc:=List(used,i->Sum(split,c->Number(c,l->AbsInt(l)=i)));
    if not ForAll(splitOcc,o->o>=4) then Error("old split variable not branching");fi;
    for i in [1..Length(f)] do
     if Sum(split,c->Number(c,l->AbsInt(l)=2+i))<>2 then Error("new split variable count");fi;
    od;
    splitCount:=splitCount+1;
   fi;
  fi;
 od;
 splitIdentities:=0;
 for n in [0..3] do
  for a in [0..2^n-1] do
   ones:=Filtered([1..n],i->OccBit(a,i)=1);
   p:=OccIndicator(n+1,[1..n],ones);
   p0:=OccIndicator(n+1,[1..n+1],ones);
   p1:=OccIndicator(n+1,[1..n+1],Union(ones,[n+1]));
   if p0+p1<>p then Error("integer split identity failed");fi;
   splitIdentities:=splitIdentities+1;
  od;
 od;
 cycleCases:=0;
 for r in [2..6] do
  for a in [0..2^r-1] do
   bits:=List([1..r],i->OccBit(a,i));
   if ForAll([1..r],j->bits[j]<=bits[RemInt(j,r)+1])<>(Length(Set(bits))=1) then Error("cycle equality failed");fi;
   cycleCases:=cycleCases+1;
  od;
 od;
 parallelUnsat:=0;
 for ra in [0..15] do
  for rb in [0..15] do
   aa:=Filtered([0..3],a->OccBit(ra,a+1)=1);bb:=Filtered([0..3],a->OccBit(rb,a+1)=1);
   if Intersection(aa,bb)=[] then
    p:=List([1..4],i->0);
    for a in [0..3] do
     if a in aa and a in bb then Error("parallel-star missing violated input");fi;
     p:=p+OccIndicator(2,[1,2],Filtered([1,2],i->OccBit(a,i)=1));
    od;
    if p<>[1,0,0,0] then Error("parallel-star refutation identity");fi;
    parallelUnsat:=parallelUnsat+1;
   fi;
  od;
 od;
 Print("formula_inventory=",formulaCount," copied_minimal_controls=",copyCount," copied_assignments=",copyAssignments," split_minimal_controls=",splitCount,"\n");
 Print("integer_split_identities=",splitIdentities," cycle_assignments=",cycleCases," parallel_star_pairs=256 parallel_unsat_identities=",parallelUnsat,"\n");
 Print("PASS: exact encoding/occurrence/minimality controls; no asymptotic lower bound computed\n");
end;
OccMain();
QUIT;
