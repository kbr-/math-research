# New general anchor-cycle composition identities, smallest new odd lengths5,7.
# Reuses the already-verified pair projection; no repeat of its expensive expansion.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0;fi;e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;return d;
end;;
ids:=0;deletions:=0;
for F in [GF(2),GF(4)] do
 for rim in [5,7] do
  R:=PolynomialRing(F,2*rim);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
  u:=List([1..rim],i->x[2*i-1]);v:=List([1..rim],i->x[2*i]);
  du:=u[1]+u[2];dv:=v[1]+v[2];
  ts:=List([1..rim],i->du*(v[i]+v[1])+dv*(u[i]+u[1]));
  Check(IsZero(ts[1]) and IsZero(ts[2]),"zero triples");
  for i in [3..rim] do
   tau:=u[1]*v[2]+u[2]*v[1]+u[1]*v[i]+u[i]*v[1]+u[2]*v[i]+u[i]*v[2];
   Check(IsZero(ts[i]-tau),"triple expansion");ids:=ids+1;
  od;
  su:=Zero(R);sv:=Zero(R);
  for i in [1..rim] do
   j:=(i mod rim)+1;uu:=u[i]+u[j];vv:=v[i]+v[j];q:=(o+uu)*(o+vv);
   leftu:=du*q+(o+uu)*(ts[i]+ts[j])+dv*(u[i]^2+u[i]+u[j]^2+u[j]);
   leftv:=dv*q+(o+vv)*(ts[i]+ts[j])+du*(v[i]^2+v[i]+v[j]^2+v[j]);
   Check(IsZero(leftu-du*(o+uu)) and IsZero(leftv-dv*(o+vv)),"weighted rim identities");
   Check(Maximum(Deg(du*q),Deg((o+uu)*(ts[i]+ts[j])),Deg(dv*(u[i]^2+u[i]+u[j]^2+u[j])))<=3,"new degree3 ceiling");
   su:=su+leftu;sv:=sv+leftv;ids:=ids+2;
  od;
  Check(IsZero(su-du) and IsZero(sv-dv),"odd cycle sum");
  Check(IsZero((o+du)*(o+dv)+du+dv+du*dv-o),"unit combination");ids:=ids+3;
  Print("field=",F," odd rim=",rim," new products degree<=3, earlier triple derivations<=6 PASS\n");
 od;
od;
# Complete edge-deletion witnesses. These are Boolean colour assignments, field-independent.
for rim in [5,7] do
 c:=rim+1;d:=rim+2;
 cycle:=List([1..rim],i->[i,(i mod rim)+1]);
 edges:=Concatenation(cycle,[[c,d]],List([1..rim],i->[c,i]),List([1..rim],i->[d,i]));
 Check(Length(edges)=3*rim+1,"edge inventory");
 for removed in edges do
  colour:=List([1..rim+2],i->0);colour[d]:=1;
  if removed=[c,d] then
   colour[c]:=0;colour[d]:=0;
   for i in [1..rim-1] do colour[i]:=1+((i-1) mod 2);od;colour[rim]:=3;
  elif removed in cycle then
   start:=removed[2];
   for j in [0..rim-1] do colour[((start-1+j) mod rim)+1]:=2+(j mod 2);od;
  else
   anchor:=removed[1];vertex:=removed[2];other:=First([c,d],i->i<>anchor);
   colour[anchor]:=0;colour[other]:=1;colour[vertex]:=0;
   for j in [1..rim-1] do colour[((vertex-1+j) mod rim)+1]:=2+((j-1) mod 2);od;
  fi;
  Check(ForAll(Difference(edges,[removed]),e->colour[e[1]]<>colour[e[2]]),"edge-deletion colouring");
  deletions:=deletions+1;
  Print("rim=",rim," removed=",removed," colouring=",colour," PASS\n");
 od;
 Check(ForAll([1..rim+2],i->Number(edges,e->i in e)>=4),"every bit in >=4 edge blocks");
od;
Print("TOTAL literal identities=",ids," edge-deletion witnesses=",deletions,"\nALL ANCHOR CONTROLS PASSED\n");
QUIT;
