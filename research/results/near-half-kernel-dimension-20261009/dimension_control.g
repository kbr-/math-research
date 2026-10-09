# Exact Boolean PC closures; tests divisor-closed standard monomials and the
# exponential quotient bound only when all unsatisfiable inputs are active.+# Native GAP BaseMat performs every row-space calculation. No degree-bounded
# Groebner surrogate. Monomial columns descend by degree then lexicographic order.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
Binom:=function(n,k) if k<0 or k>n then return 0;fi;return Binomial(n,k);end;
MakeMons:=function(n,D)
 local mons;
 mons:=Filtered(Combinations([1..n]),s->Length(s)<=D);
 Sort(mons,function(a,b)
  if Length(a)<>Length(b) then return Length(a)>Length(b);fi;
  return a>b;
 end);
 return mons;
end;
Vec:=function(mons,terms,fld)
 local row,t,j;
 row:=List(mons,s->Zero(fld));
 for t in terms do j:=Position(mons,t[1]);Check(j<>fail,"input active");row[j]:=row[j]+t[2]*One(fld);od;
 return row;
end;
InSpan:=function(base,row) return RankMat(Concatenation(base,[row]))=Length(base);end;
Counters:=rec(proper:=0,divisors:=0,layers:=0,refuted:=0);
RunFamily:=function(name,n,maxD,fld,terms)
 local D,mons,rows,base,oldbase,oldmons,row,r,i,j,pivot,new,unit,done,nonpiv,pivots,M,S,d,hd,w,sols,x,g,oldrank;
 w:=Maximum(List(terms,g->Maximum(List(g,t->Length(t[1])))));
 # Exhaustive satisfaction control is small: at most 2^12 assignments.
 sols:=Number(Tuples([0,1],n),x->ForAll(terms,g->Sum(g,t->t[2]*Product(t[1],i->x[i]))*One(fld)=Zero(fld)));
 Check(sols=0,"unsatisfiable control");oldbase:=[];oldmons:=[];
 for D in [Maximum(2,w)..maxD] do
  mons:=MakeMons(n,D);Check(Length(mons)<=300,"sizing ceiling");
  rows:=List(terms,g->Vec(mons,g,fld));
  for r in oldbase do
   row:=List(mons,s->Zero(fld));for j in [1..Length(oldmons)] do row[Position(mons,oldmons[j])]:=r[j];od;Add(rows,row);
  od;
  base:=BaseMat(rows);unit:=Vec(mons,[[[],1]],fld);done:=false;
  while not done do
   if InSpan(base,unit) then done:=true;break;fi;
   rows:=ShallowCopy(base);
   for r in base do
    pivot:=PositionNonZero(r);
    if Length(mons[pivot])<D then
     for i in [1..n] do
      row:=List(mons,s->Zero(fld));
      for j in [1..Length(mons)] do
       if not IsZero(r[j]) then
        new:=Position(mons,Union(mons[j],[i]));Check(new<>fail,"legal degree");row[new]:=row[new]+r[j];
       fi;
      od;
      Add(rows,row);
     od;
    fi;
   od;
   oldrank:=Length(base);base:=BaseMat(rows);done:=Length(base)=oldrank;
  od;
  if InSpan(base,unit) then
   Print(name," D=",D," UNIT_FOUND rank=",Length(base)," columns=",Length(mons),"\n");
   Counters.refuted:=Counters.refuted+1;break;
  fi;
  Counters.proper:=Counters.proper+1;
  pivots:=List(base,PositionNonZero);nonpiv:=Filtered([1..Length(mons)],j->not j in pivots);
  Check(Length(nonpiv)>=2^(D-1),"exponential quotient floor");
  Check(Maximum(List(nonpiv,j->Length(mons[j])))>=D-1,"nonflat degree floor");
  for j in nonpiv do
   for S in Combinations(mons[j]) do
    Check(Position(mons,S) in nonpiv,"standard divisors survive");Counters.divisors:=Counters.divisors+1;
   od;
  od;
  hd:=List([0..D],d->Number(nonpiv,j->Length(mons[j])=d));
  for d in [0..D-1] do Check(hd[d+1]>=Binom(D-1,d),"layer floor");Counters.layers:=Counters.layers+1;od;
  Print(name," D=",D," PROPER rank=",Length(base)," quotient=",Length(nonpiv)," profile=",hd,"\n");
  oldbase:=base;oldmons:=mons;
 od;
end;
Print("SIZING exact Boolean spaces <=300 columns; Q knapsack n=3,5,7; F5 n=3; F2 functional PHP4->3 n=12 through D=3\n");
for n in [3,5,7] do
 terms:=[Concatenation([[[],-n/2]],List([1..n],i->[[i],1]))];
 RunFamily(Concatenation("Q_KNAPSACK_",String(n)),n,Minimum(n+1,5),Rationals,terms);
od;
RunFamily("F5_KNAPSACK_3",3,4,GF(5),[Concatenation([[[],-4]],List([1..3],i->[[i],1]))]);
terms:=[];
for p in [1..4] do
 Add(terms,Concatenation([[[],-1]],List([1..3],h->[[3*(p-1)+h],1])));
 for pair in Combinations([1..3],2) do Add(terms,[[List(pair,h->3*(p-1)+h),1]]);od;
od;
for h in [1..3] do for pair in Combinations([1..4],2) do Add(terms,[[List(pair,p->3*(p-1)+h),1]]);od;od;
RunFamily("F2_PHP4_3",12,3,GF(2),terms);
# Satisfiable and missing-input controls: evaluation at zero has codimension
# one, is closed, but cannot contain the active contradictory input x1-1.
for fld in [Rationals,GF(2),GF(3)] do
 mons:=MakeMons(3,3);zeroeval:=List(mons,s->(Length(s)=0));
 base:=Filtered(IdentityMat(Length(mons),fld),r->IsZero(r[Position(mons,[])]));
 Check(Length(mons)-RankMat(base)=1,"satisfiable evaluation dimension");
 Check(not InSpan(base,Vec(mons,[[[1],1],[[],-1]],fld)),"active-input negative control");
od;
Print("PROPER_CUTOFFS=",Counters.proper," DIVISOR_CHECKS=",Counters.divisors," LAYER_CHECKS=",Counters.layers," UNIT_STOPS=",Counters.refuted,"\n");
Print("ALL KERNEL DIMENSION CONTROLS PASSED\n");
QUIT;
