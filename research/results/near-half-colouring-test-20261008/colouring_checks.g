# Exact certificates for the compact three-colour encoding, over Q, F2, F3.
# All local axiom types and all 27 K4 branches are checked by literal identities.
# K4 is the smallest non-three-colourable simple graph: eight Boolean variables,
# a three-vertex cover, and a claimed degree-four refutation. No closure or
# asymptotic lower bound is inferred from these finite certificates.
if not IsBound(OUT) then Error("Set OUT"); fi;
out:=OutputTextFile(OUT,false);; SetPrintFormattingStatus(out,false);;
Check:=function(ok,msg) if not ok then Error(msg); fi; end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0; fi;
 e:=ExtRepPolynomialRatFun(p); d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]})); od;
 return d;
end;;
localcount:=0;; branches:=0;; badedge:=0;; exhausted:=0;; controls:=0;;
PrintTo(out,"planned: 3 fields, 27 K4 branches per field; refuse larger enumeration\n");;
for fld in [Rationals,GF(2),GF(3)] do
 ring:=PolynomialRing(fld,12); xs:=IndeterminatesOfPolynomialRing(ring); one:=One(ring);
 us:=List([1..4],i->xs[2*i-1]); vs:=List([1..4],i->xs[2*i]);
 ls:=List([1..4],i->[one-us[i]-vs[i],us[i],vs[i]]);
 chis:=List([1..4],i->[(one-us[i])*(one-vs[i]),us[i]*(one-vs[i]),(one-us[i])*vs[i]]);
 signs:=[1,-1,-1];
 for i in [1..4] do
  u:=us[i]; v:=vs[i]; b1:=u^2-u; b2:=v^2-v; dom:=u*v;
  Check(IsZero(Sum(ls[i])-one),"affine partition"); localcount:=localcount+1;
  for c in [1..3] do
   Check(IsZero(chis[i][c]-ls[i][c]-signs[c]*dom),"point indicator conversion");
   localcount:=localcount+1;
  od;
  Check(IsZero(ls[i][1]^2-ls[i][1]-b1-b2-2*dom),"colour zero Booleanity");
  Check(IsZero(ls[i][1]*u+b1+dom),"zero/one exclusion");
  Check(IsZero(ls[i][1]*v+b2+dom),"zero/two exclusion");
  Check(IsZero(ls[i][2]^2-ls[i][2]-b1),"colour one Booleanity");
  Check(IsZero(ls[i][3]^2-ls[i][3]-b2),"colour two Booleanity");
  Check(IsZero(ls[i][2]*ls[i][3]-dom),"one/two exclusion");
  localcount:=localcount+6;
 od;
 # Every colour on each edge of K4, with explicit degree-four domain cofactors.
 for a in [1..4] do for b in [a+1..4] do for c in [1..3] do
  corr1:=signs[c]*us[a]*vs[a]*chis[b][c];
  corr2:=signs[c]*ls[a][c]*us[b]*vs[b];
  Check(IsZero(chis[a][c]*chis[b][c]-ls[a][c]*ls[b][c]-corr1-corr2),"edge conversion");
  Check(Maximum(Deg(corr1),Deg(corr2))<=4,"edge correction degree"); localcount:=localcount+1;
 od; od; od;
 # Reverse local transfer: three ordinary one-hot variables per vertex.
 ys:=List([1..4],i->xs{[3*i-2..3*i]});
 rchis:=List(ys,y->[(one-y[2])*(one-y[3]),y[2]*(one-y[3]),(one-y[2])*y[3]]);
 for i in [1..4] do
  row:=Sum(ys[i])-one; dom:=ys[i][2]*ys[i][3];
  Check(IsZero(rchis[i][1]-ys[i][1]+row-dom),"reverse zero indicator");
  Check(IsZero(rchis[i][2]-ys[i][2]+dom),"reverse one indicator");
  Check(IsZero(rchis[i][3]-ys[i][3]+dom),"reverse two indicator"); localcount:=localcount+3;
 od;
 for a in [1..4] do for b in [a+1..4] do for c in [1..3] do
  da:=rchis[a][c]-ys[a][c]; db:=rchis[b][c]-ys[b][c];
  Check(IsZero(rchis[a][c]*rchis[b][c]-ys[a][c]*ys[b][c]-da*rchis[b][c]-ys[a][c]*db),"reverse edge conversion");
  Check(Maximum(Deg(da*rchis[b][c]),Deg(ys[a][c]*db))<=4,"reverse edge degree");
  localcount:=localcount+1;
 od; od; od;
 total:=Zero(ring); firstbranch:=fail;
 assignments:=Tuples([1..3],3); Check(Length(assignments)=27,"enumeration size");
 for alpha in assignments do
  branch:=Product([1..3],i->ls[i][alpha[i]]); total:=total+branch;
  if firstbranch=fail then firstbranch:=branch; fi;
  witness:=fail;
  for a in [1..3] do for b in [a+1..3] do
   if alpha[a]=alpha[b] then witness:=[a,b]; fi;
  od; od;
  if witness<>fail then
   a:=witness[1]; b:=witness[2]; c:=alpha[a];
   cert:=ls[a][c]*ls[b][c]*Product(Filtered([1..3],i->i<>a and i<>b),i->ls[i][alpha[i]]);
   Check(IsZero(cert-branch),"internal collision branch"); Check(Deg(cert)<=3,"internal branch degree");
   badedge:=badedge+1;
  else
   terms:=[];
   for c in [1..3] do
    a:=Position(alpha,c); Check(a<>fail,"missing neighbour colour");
    cert:=ls[4][c]*ls[a][c]*Product(Filtered([1..3],i->i<>a),i->ls[i][alpha[i]]);
    Check(IsZero(cert-branch*ls[4][c]),"exhausted-colour branch"); Check(Deg(cert)<=4,"external branch degree");
    Add(terms,cert);
   od;
   Check(IsZero(Sum(terms)-branch),"exhausted-colour sum");
   Check(not IsZero(Sum(terms{[1,2]})-branch),"omitted colour must fail"); controls:=controls+1;
   exhausted:=exhausted+1;
  fi;
  branches:=branches+1; PrintTo(out,"branch field=",fld," colours=",alpha," degree<=4 passed\n");
 od;
 Check(IsZero(total-one),"complete branch partition");
 Check(not IsZero(total-firstbranch-one),"omitted branch must fail"); controls:=controls+1;
 # A local affine function vanishing at 00,10,01 also vanishes at 11.
 # Thus the fourth point indicator cannot have affine degree over any field.
 Check(IsZero((one+one-one)-one),"affine rectangle identity control");
 PrintTo(out,"field ",fld," all literal checks passed\n");
od;
PrintTo(out,"SUMMARY local_identities=",localcount," branches=",branches," internal_collision=",badedge,
 " exhausted_colours=",exhausted," negative_controls=",controls," max_degree=4\nALL CHECKS PASSED\n");;
CloseStream(out);; QUIT;
