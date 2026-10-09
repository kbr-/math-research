# Exact controls for ternary leader charts with at most two S entries per column.
# Tests the gain inequality and the three-vertex path improvement, not PC minima.
Check := function(ok,msg) if not ok then Error(msg); fi; end;
Weight := x -> Number(x,a -> a<>0);
Residue := function(x,p) return List(x,a->a mod p); end;
Print("SIZING path=128; charts=361+3249; wide-control=243 received words\n");
pathcount:=0;
for cf in Tuples([1,2],4) do
 cols:=[[cf[1],cf[2],0],[0,cf[3],cf[4]]];
 for a in Tuples([1,2],3) do
  gains:=List(Tuples([0,1,2],2),l->Number([1..3],i->(l[1]*cols[1][i]+l[2]*cols[2][i]-a[i]) mod 3=0)-Weight(l));
  Check(Maximum(gains)>=1,"three-vertex gain");pathcount:=pathcount+1;
 od;
od;
smallcols:=Filtered(Tuples([0,1,2],3),c->Weight(c)<=2);
Check(Length(smallcols)=19,"column count");
chartcounts:=[0,0];leadercounts:=[0,0];connectedleaders:=[0,0];
for extra in [0,1] do
 for pair in Tuples(smallcols,2) do
  for tail in Tuples([0,1,2],2*extra) do
   cols:=List([1,2],j->Concatenation(pair[j],List([1..extra],i->tail[j])));
   target:=Concatenation([1,1,1],List([1..extra],i->0));
   reps:=List(Tuples([0,1,2],2),l->Weight(l)+Weight(Residue(target-l[1]*cols[1]-l[2]*cols[2],3)));
   chartcounts[extra+1]:=chartcounts[extra+1]+1;
   if Minimum(reps)=3 then
    leadercounts[extra+1]:=leadercounts[extra+1]+1;
    edges:=Set(List(Filtered(pair,c->Weight(c)=2),c->Filtered([1..3],i->c[i]<>0)));
    if Length(edges)=2 then
     connectedleaders[extra+1]:=connectedleaders[extra+1]+1;
     Check(extra>=1,"connected triple cannot have zero slack");
    fi;
    for l in Tuples([0,1,2],2) do
     value:=Residue(l[1]*cols[1]+l[2]*cols[2],3);
     matches:=Number([1..3],i->value[i]=1);
     zeros:=Number([4..3+extra],i->value[i]<>0);
     Check(matches<=Weight(l)+zeros,"full gain budget");
    od;
   fi;
  od;
 od;
od;
# F5 negative control: a connected three-vertex incidence path can have zero slack.
cols:=[[1,4,0],[0,1,4]];target:=[1,1,1];
reps:=List(Tuples([0..4],2),l->Weight(l)+Weight(Residue(target-l[1]*cols[1]-l[2]*cols[2],5)));
Check(Minimum(reps)=3,"F5 negative control");
# Nonzero slack does not imply the extra graphical-chart hypothesis.
h:=[1,1,2,1];target:=[1,1,1,0];
Check(Minimum(List([0,1,2],l->Weight([l])+Weight(Residue(target-l*h,3))))=3,"wide ternary leader");
gen:=Concatenation(Residue(-h,3),[1]);
radius:=Maximum(List(Tuples([0,1,2],5),z->Minimum(List([0,1,2],l->Weight(Residue(z-l*gen,3))))));
Check(radius=3 and Weight(h{[1..3]})=3,"wide ternary maximum leader and nongraphical chart");
Print("PATH_CASES=",pathcount," CHARTS=",chartcounts," LEADERS=",leadercounts," CONNECTED_LEADERS=",connectedleaders,"\n");
Print("F5 connected zero-slack control: radius=3 by leader and redundancy\n");
Print("F3 wide-column control: v=5 rank=1 radius=",radius," slack=1 S_support=3\n");
Print("ALL TERNARY GRAPH CONTROLS PASSED\n");
QUIT;
