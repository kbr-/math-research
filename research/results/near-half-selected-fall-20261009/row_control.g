# Character-row interpolation, noncentral improvement, and the central slice law.
# Exact bounded checks; no asymptotic probability experiment.
Check:=function(ok,s) if not ok then Error(s);fi;end;
EvalRank:=function(pts,k,t,fld)
 local mons,mat;
 if Length(pts)=0 then return 0;fi;
 mons:=Filtered(Combinations([1..k]),S->Length(S)<=t);
 mat:=List(pts,x->List(mons,S->Product(S,i->x[i])*One(fld)));
 return RankMat(mat);
end;
Print("SIZING nonzero rows: (q,k)=(3,4),(3,6),(5,4); two proof fields each; central maps q^k=729+625\n");
rows:=0;rankchecks:=0;centralrows:=0;noncentralrows:=0;
for pars in [[3,4],[3,6],[5,4]] do
 q:=pars[1];k:=pars[2];pts:=Tuples([0,1],k);
 if q=3 then fields:=[GF(2),GF(5)];else fields:=[GF(2),GF(3)];fi;
 for coeff in Tuples([1..q-1],k) do
  for target in [0..q-1] do
   allowed:=Filtered(pts,x->(Sum([1..k],i->coeff[i]*x[i])-target) mod q=0);
   central:=(2*target-Sum(coeff)) mod q=0;
   if central then t:=k/2;centralrows:=centralrows+1;
   else t:=k/2-1;noncentralrows:=noncentralrows+1;fi;
   for fld in fields do
    Check(EvalRank(allowed,k,t,fld)=Length(allowed),"prescribed row interpolation");rankchecks:=rankchecks+1;
   od;
   rows:=rows+1;
  od;
 od;
od;
# Sharp scope controls: centrality and characteristic cannot be dropped.
pts:=Tuples([0,1],4);
centralset:=Filtered(pts,x->Sum(x) mod 3=2);
Check(EvalRank(centralset,4,1,GF(2))<Length(centralset),"central row cannot use noncentral threshold");
noncentralset:=Filtered(pts,x->Sum(x) mod 3=0);
Check(EvalRank(noncentralset,4,1,GF(3))<Length(noncentralset),"matching characteristic negative control");
zeroexample:=Filtered(pts,x->x[1]=0);
Check(EvalRank(zeroexample,4,1,GF(2))<Length(zeroexample),"zero coefficient scope-count negative control");
# Exact central-law bijection; use the first coordinate as the complement representative.
mapcases:=0;slicepoints:=0;complementpoints:=0;fullslice:=0;
for pars in [[3,6],[5,4]] do
 q:=pars[1];k:=pars[2];half:=(q+1)/2;pts:=Tuples([0,1],k);outputs:=[];
 for coeff in Tuples([0..q-1],k) do
  target:=(half*Sum(coeff)) mod q;
  Add(outputs,Concatenation(coeff{[2..k]},[target]));
  slice:=Filtered(Tuples([0,1],k-1),x->(Sum([2..k],i->coeff[i]*x[i-1])-target) mod q=0);
  allowed:=Filtered(pts,x->(Sum([1..k],i->coeff[i]*x[i])-target) mod q=0);
  Check(Set(List(Filtered(allowed,x->x[1]=0),x->x{[2..k]}))=Set(slice),"central zero slice law");
  for x in pts do
   Check((x in allowed)=(List(x,b->1-b) in allowed),"complement invariance");complementpoints:=complementpoints+1;
  od;
  slicepoints:=slicepoints+2^(k-1);
  if Length(slice)>0 and RankMat(List(slice,x->Concatenation([1],x))*One(GF(2)))=k then
   Check(RankMat(List(allowed,x->Concatenation([1],x))*One(GF(2)))=k+1,"full-affine slice lifts to full row");fullslice:=fullslice+1;
  fi;
  mapcases:=mapcases+1;
 od;
 Check(Length(Set(outputs))=q^k,"coefficient-target map bijection");
od;
# A nonzero spectator-fall image is absorbed with a nonzero lower-degree replacement.
absorbchecks:=0;
for fld in [GF(2),GF(5),Rationals] do
 one:=One(fld);ring:=PolynomialRing(fld,["x","y","z","a","b","d","w"]);vs:=IndeterminatesOfPolynomialRing(ring);
 xx:=vs[1];yy:=vs[2];zz:=vs[3];aa:=vs[4];bb:=vs[5];dd:=vs[6];ww:=vs[7];
 g:=(one-zz)*(one-xx);h:=zz*yy;fall:=(one-xx)*yy;p:=aa*bb-aa;
 Check(yy*g+(one-xx)*h=fall,"local fall identity");
 Check(ww*fall*p+ww*aa*(yy*g)+ww*aa*((one-xx)*h)=ww*aa*bb*fall,"three-row absorption identity through degree five");
 Check(ForAll([[0,0,0],[1,1,1]],a->a[1]*a[2]-a[1]=0),"third modular-row relation");
 absorbchecks:=absorbchecks+1;
od;
Print("ROWS=",rows," CENTRAL=",centralrows," NONCENTRAL=",noncentralrows," INTERPOLATION_RANKS=",rankchecks,"\n");
Print("CENTRAL_MAPS=",mapcases," SLICE_POINT_COUNTS=",slicepoints," COMPLEMENT_POINTS=",complementpoints," FULL_SLICE_LIFTS=",fullslice," ABSORPTION_FIELDS=",absorbchecks,"\n");
Print("ALL ROW INTERPOLATION AND CENTRAL SOURCE CONTROLS PASSED\n");
QUIT;
