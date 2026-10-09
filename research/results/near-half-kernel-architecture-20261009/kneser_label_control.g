# Check the fixed one-vertex Kneser label queries and the hemisphere chain ladder.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
LabelData:=function(x,k)
 local a,b,sgn,chosen;
 a:=Filtered([1..Length(x)],i->x[i]=1);b:=Filtered([1..Length(x)],i->x[i]=-1);
 if Length(a)>Length(b) or (Length(a)=Length(b) and a>b) then sgn:=1;chosen:=a;else sgn:=-1;chosen:=b;fi;
 if Length(a)+Length(b)<=2*k-2 then return rec(sgn:=sgn,low:=Length(a)+Length(b),chosen:=[]);fi;
 Check(Length(chosen)>=k,"large side contains k-set");return rec(sgn:=sgn,low:=0,chosen:=chosen{[1..k]});
end;
vertices:=0;pairs:=0;oppositequeries:=0;
Print("SIZING n=5,7 signed-subset label checks; at most78125 nested pairs; hemisphere flags through dimension3\n");
for k in [1,2] do
 n:=2*k+3;points:=Difference(Tuples([-1,0,1],n),[List([1..n],i->0)]);
 for x in points do
  lx:=LabelData(x,k);la:=LabelData(-x,k);
  Check(la.sgn=-lx.sgn and la.low=lx.low and la.chosen=lx.chosen,"antipodal fixed query");vertices:=vertices+1;
  support:=Filtered([1..n],i->x[i]<>0);
  for sub in Combinations(support) do
   if Length(sub)>0 and Length(sub)<Length(support) then
    y:=List([1..n],i->0);for i in sub do y[i]:=x[i];od;ly:=LabelData(y,k);pairs:=pairs+1;
    if ly.low>0 and lx.low>0 then Check(ly.low<lx.low,"low labels differ on strict chain");fi;
    if ly.low=0 and lx.low=0 and ly.sgn<>lx.sgn then
     Check(Intersection(ly.chosen,lx.chosen)=[],"opposite high queries are a Kneser edge");oppositequeries:=oppositequeries+1;
    fi;
   fi;
  od;
 od;
od;
VertexMask:=function(x)
 return Sum(Filtered([1..Length(x)],i->x[i]=1),i->2^(i-1))+2^4*Sum(Filtered([1..Length(x)],i->x[i]=-1),i->2^(i-1));
end;
Antipode:=function(a)return (a mod 2^4)*2^4+QuoInt(a,2^4);end;
chains:=[];
for d in [0..3] do
 chain:=[];
 for signs in Tuples([-1,1],d) do
  signs:=Concatenation(signs,[1]);
  for perm in PermutationsList([1..d+1]) do
   x:=[0,0,0,0];face:=[];
   for i in perm do x[i]:=signs[i];Add(face,VertexMask(x));od;AddSet(chain,Set(face));
  od;
 od;
 Check(Length(chain)=2^d*Factorial(d+1),"hemisphere flag count");Add(chains,chain);
 if d>0 then
  bd:=[];
  for face in chain do for i in [1..Length(face)] do
   sub:=face{Difference([1..Length(face)],[i])};
   if sub in bd then RemoveSet(bd,sub);else AddSet(bd,sub);fi;
  od;od;
  expected:=Union(chains[d],List(chains[d],f->Set(List(f,Antipode))));
  Check(bd=expected,"hemisphere boundary equals antipodal norm");
 fi;
od;
Check(Length(chains[1])=1,"marked augmentation one");
Print("LABEL_VERTICES=",vertices," STRICT_COMPARABLE_PAIRS=",pairs," OPPOSITE_HIGH_QUERIES=",oppositequeries," HEMISPHERE_COUNTS=",List(chains,Length),"\n");
Print("ALL KNESER LABEL CONTROLS PASSED\n");
QUIT;
