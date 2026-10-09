# Exhaustive two-copy guarding control on all minimal UNSAT subformulas of
# the eight nonempty proper clauses on two variables; native exact ranks.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
Satisfies:=function(x,c) return ForAny([1..Length(c.scope)],i->x[c.scope[i]]<>c.bits[i]);end;
Sat:=function(clauses,n) return ForAny(Tuples([0,1],n),x->ForAll(clauses,c->Satisfies(x,c)));end;
baseclauses:=[];
for a in Difference(Tuples([-1,0,1],2),[[-1,-1]]) do
 scope:=Filtered([1..2],i->a[i]<>-1);Add(baseclauses,rec(scope:=scope,bits:=a{scope}));
od;
controls:=0;deletions:=0;polarities:=0;ranks:=0;identities:=0;
Print("SIZING 256 base subformulas, <=5 guarded variables, <=32 assignments or polarities per test\n");
for inds in Combinations([1..8]) do
 base:=baseclauses{inds};
 if Length(base)>0 and not Sat(base,2) and ForAll([1..Length(base)],j->Sat(base{Difference([1..Length(base)],[j])},2)) then
  vars:=Union(List(base,c->c.scope));n:=Length(vars);
  base:=List(base,c->rec(scope:=List(c.scope,i->Position(vars,i)),bits:=c.bits));
  guarded:=[];
  for side in [0,1] do for c in base do
   Add(guarded,rec(scope:=Concatenation(List(c.scope,i->i+side*n),[2*n+1]),bits:=Concatenation(c.bits,[side])));
  od;od;
  Check(not Sat(guarded,2*n+1),"guarded UNSAT");
  for j in [1..Length(guarded)] do
   Check(Sat(guarded{Difference([1..Length(guarded)],[j])},2*n+1),"guarded minimality");deletions:=deletions+1;
  od;
  occ:=List([1..n],i->Number(base,c->i in c.scope));
  newocc:=List([1..2*n+1],i->Number(guarded,c->i in c.scope));
  Check(Minimum(newocc)>=2,"occurrence retention");
  Check(Number(newocc,a->a>=3)/(2*n+1)>=Number(occ,a->a>=3)/n,"branching fraction retention");
  for pol in Tuples([0,1],2*n+1) do
   Check(not ForAll(guarded,c->Number([1..Length(c.scope)],i->(c.bits[i]+pol[c.scope[i]]) mod 2=0)<=1),"no common Horn polarity");polarities:=polarities+1;
  od;
  for c in guarded do
   allowed:=Filtered(Tuples([0,1],Length(c.scope)),x->x<>c.bits);
   Check(Set(List(allowed,x->x{[1..Length(x)-1]}))=Set(Tuples([0,1],Length(c.scope)-1)),"all non-guard coordinates shattered");
   Check(RankMat(List(allowed,x->Concatenation([1],x))*One(GF(2)))=Length(c.scope)+1,"local affine fullness");ranks:=ranks+1;
   for fld in [Rationals,GF(2),GF(3)] do
    for x in Tuples([0,1],Length(c.scope)) do
     val:=One(fld);qval:=One(fld);
     for i in [1..Length(x)] do
      if c.bits[i]=1 then factor:=x[i];else factor:=1-x[i];fi;
      val:=val*factor;if i<Length(x) then qval:=qval*factor;fi;
     od;
     if Last(c.bits)=1 then factor:=Last(x);else factor:=1-Last(x);fi;
     Check(val=qval*factor,"literal guarded indicator identity");identities:=identities+1;
    od;
   od;
  od;
  controls:=controls+1;
 fi;
od;
Check(3^29<2^47,"central projection probability decay");
Print("MINIMAL_BASES=",controls," DELETION_WITNESSES=",deletions," POLARITIES=",polarities," AFFINE_RANKS=",ranks," INDICATOR_IDENTITIES=",identities," DECAY_EIGHTH_POWER=",3^29/2^47,"\n");
Print("ALL GUARDING CONTROLS PASSED\n");
QUIT;
