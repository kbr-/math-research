# The first unsaturated induced-support obstruction needs a vertex of degree4.
# Verify the explicit determinant on every 4-leaf colour assignment and centre.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
for F in [GF(2),GF(4)] do
 R:=PolynomialRing(F,8);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
 rows:=List([1..4],i->[o,x[2*i-1],x[2*i],x[2*i-1]*x[2*i]]);
 p:=DeterminantMat(rows);rep:=ExtRepPolynomialRatFun(p);
 deg:=Maximum(List([1,3..Length(rep)-1],i->Sum(rep[i]{[2,4..Length(rep[i])]})));
 Check(deg=4,"determinant degree");
 colours:=Tuples([Zero(F),One(F)],2);allowed:=0;nonzero:=0;
 for leaves in Tuples(colours,4) do
  value:=DeterminantMat(List(leaves,c->[One(F),c[1],c[2],c[1]*c[2]]));
  distinct:=Length(Set(leaves))=4;
  Check((not IsZero(value))=distinct,"four-state determinant support");
  if distinct then Check(value=One(F),"injective value one");nonzero:=nonzero+1;fi;
  for centre in colours do
   if ForAll(leaves,c->c<>centre) then
    Check(IsZero(value),"vanishes on every allowed star colouring");allowed:=allowed+1;
   fi;
  od;
 od;
 Check(nonzero=24 and allowed=324,"complete table counts");
 Print("field=",F," degree=",deg," leaf assignments=256, injective=",nonzero," allowed star assignments=",allowed," PASS\n");
od;
Print("ALL STAR CONTROLS PASSED\n");
QUIT;
