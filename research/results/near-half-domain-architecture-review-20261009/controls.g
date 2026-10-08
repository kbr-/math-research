# One bounded exact review suite: all 256 relations on three bits, all 256
# Horn clause sets on two bits, each over Q/F2/F3; all 16 four-colour polarities.
# Tests the actual Horn re-encoding/forward proof identities and fixed bridge
# controls, not asymptotic hardness. No scaling series is requested.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0;fi;e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;return d;
end;;
Meet:=function(a,b) return List([1..Length(a)],i->Minimum(a[i],b[i]));end;;
ClosedMeet:=function(R) return ForAll(R,a->ForAll(R,b->Meet(a,b) in R));end;;
Violates:=function(c,a) return ForAll(c.prem,i->a[i]=1) and (c.head=0 or a[c.head]=0);end;;
PointInd:=function(xs,o,a) return Product([1..Length(a)],function(i) if a[i]=1 then return xs[i];else return o-xs[i];fi;end);end;;
Mon:=function(indices,xs,o) local z,i;z:=o;for i in indices do z:=z*xs[i];od;return z;end;;
HornPoly:=function(c,xs,o) local z;z:=Mon(c.prem,xs,o);if c.head<>0 then z:=z*(o-xs[c.head]);fi;return z;end;;
cube3:=Tuples([0,1],3);relations:=Combinations(cube3);
Check(Length(relations)=256,"relation sizing");closed:=Filtered(relations,ClosedMeet);
identityCount:=0;forwardCount:=0;unsatCount:=0;
Print("SIZING relations=256 fields=3 polarities=8; Horn formula sets=256 fields=3\n");
for fld in [Rationals,GF(2),GF(3)] do
 ring:=PolynomialRing(fld,3);xs:=IndeterminatesOfPolynomialRing(ring);o:=One(ring);
 for rel in closed do
  hc:=[];
  for a in Difference(cube3,rel) do
   prem:=Filtered([1..3],i->a[i]=1);extensions:=Filtered(rel,b->ForAll(prem,i->b[i]=1));
   if IsEmpty(extensions) then hd:=0;
   else hd:=First(Difference([1..3],prem),j->ForAll(extensions,b->b[j]=1));Check(hd<>fail,"Horn separator exists");fi;
   Add(hc,rec(prem:=prem,head:=hd));
  od;
  Check(Filtered(cube3,a->ForAll(hc,c->not Violates(c,a)))=rel,"Horn semantic equality");
  for flip in cube3 do
   ys:=List([1..3],function(i) if flip[i]=0 then return xs[i];else return o-xs[i];fi;end);
   for c in hc do
    lhs:=HornPoly(c,ys,o);rhs:=Zero(ring);
    for a in cube3 do
     af:=List([1..3],i->(a[i]+flip[i]) mod 2);
     if Violates(c,af) then rhs:=rhs+PointInd(xs,o,a);fi;
    od;
    Check(lhs=rhs and Deg(lhs)<=3,"paid polarity interpolation identity");identityCount:=identityCount+1;
   od;
  od;
 od;
 # Enumerate all Horn clause sets on two variables, including empty clauses.
 cs:=[];
 for prem in Combinations([1,2]) do
  Add(cs,rec(prem:=prem,head:=0));
  for hd in Difference([1,2],prem) do Add(cs,rec(prem:=prem,head:=hd));od;
 od;
 Check(Length(cs)=8,"Horn clause sizing");
 for formula in Combinations(cs) do
  forced:=[];contradiction:=false;changed:=true;
  while changed and not contradiction do
   changed:=false;
   for c in formula do
    if not ForAll(c.prem,i->i in forced) then continue;fi;
    if c.head<>0 and c.head in forced then continue;fi;
    current:=HornPoly(c,xs,o);remaining:=ShallowCopy(c.prem);
    for i in c.prem do
     RemoveSet(remaining,i);cofactor:=Mon(remaining,xs,o);
     if c.head<>0 then cofactor:=cofactor*(o-xs[c.head]);fi;
     term:=(xs[i]-o)*cofactor;
     Check(Deg(term)<=Length(c.prem)+Minimum(c.head,1),"forward multiplication degree");
     current:=current-term;Check(current=cofactor,"forward cancellation");forwardCount:=forwardCount+1;
    od;
    if c.head=0 then Check(current=o,"empty-clause result");contradiction:=true;break;
    else Check(current=o-xs[c.head],"derived fact");AddSet(forced,c.head);changed:=true;fi;
   od;
  od;
  sat:=ForAny(Tuples([0,1],2),a->ForAll(formula,c->not Violates(c,a)));
  Check(contradiction=(not sat),"Horn propagation completeness");
  if contradiction then unsatCount:=unsatCount+1;fi;
 od;
 # Degree-three sharpness for quadratic Boolean binomial inputs.
 xx:=xs[1];yy:=xs[2];zz:=xs[3];g1:=xx*yy-o;g2:=yy*zz-o;g3:=xx*zz;
 aa:=xx*g1-yy*(xx^2-xx)-g1;bb:=zz*g2-yy*(zz^2-zz)-g2;
 Check(aa=o-xx and bb=o-zz and g3+zz*aa+bb=o,"binomial degree-three refutation");
 Check(Maximum(List([xx*g1,yy*(xx^2-xx),zz*g2,yy*(zz^2-zz),zz*aa],Deg))=3,"sharp witness degree");
 Print("field=",fld," Horn and sharpness identities PASS\n");
od;
# Four-colour inequality remains non-Horn after every bit polarity.
cube4:=Tuples([0,1],4);rel4:=Filtered(cube4,a->a{[1,2]}<>a{[3,4]});polarityCount:=0;
for flip in cube4 do
 transformed:=Set(List(rel4,a->List([1..4],i->(a[i]+flip[i]) mod 2)));
 pair:=First(Tuples(transformed,2),ab->not Meet(ab[1],ab[2]) in transformed);
 Check(pair<>fail,"four-colour non-Horn polarity control");polarityCount:=polarityCount+1;
 Print("polarity=",flip," meet witnesses=",pair,"\n");
od;
# Fixed exact topology, periodic cellular-automaton, and colour-orbit controls.
fld:=GF(2);u:=One(fld);z:=Zero(fld);
boundary:=[[u,z,u],[u,u,z],[z,u,u]];
Check(boundary*[u,u,u]=[z,z,z],"triangle cycle");
Check(boundary*[u,z,u]=[z,u,u],"support projection is not a chain map");
ca:=[[z,u,u],[u,z,u],[u,u,z]];
Check(ca*[u,u,u]=[z,z,z] and RankMat(ca)=2,"periodic rule90 unit loss");
Check(3*u=u and 6*u=z,"pinned Potts counts");
Check(Sum([u,z,u,z])=z and Sum([z,z,u,z])=u,"orbit quotient multiplier failure");
Print("TOTAL closed relations=",Length(closed)," local identities=",identityCount,
 " forward identities=",forwardCount," UNSAT Horn formula-field pairs=",unsatCount,
 " four-colour polarities=",polarityCount,"\n");
Print("ALL DOMAIN REVIEW CONTROLS PASSED\n");
QUIT;
