# Exhaustive binary stable-core calibration on all unital affine subspaces
# of the three-bit Boolean algebra. Native GAP spaces/membership/rank.
# 16 spaces, 256 ordered pairs, 1632 initial (U,V,b) steps; no scaling sweep.
# Stages: construct exact algebra; every initial step; terminating chains;
# common eigenvectors; two actual source tuples per pair; bad-step controls.
scRequire:=function(ok,msg)
  if not ok then Print("FAIL: ",msg,"\n"); QUIT_GAP(1); fi;
end;
scF:=GF(2);;
scTable:=EmptySCTable(8,Zero(scF));;
for scI in [1..8] do SetEntrySCTable(scTable,scI,scI,[One(scF),scI]); od;
scAlg:=AlgebraByStructureConstants(scF,scTable);;
scBasis:=CanonicalBasis(scAlg);;
scPoints:=BasisVectors(scBasis);;
scOne:=Sum(scPoints);;
scZero:=Zero(scAlg);;
scBits:=List([0..7],m->Filtered([1..3],i->QuoInt(m,2^(i-1)) mod 2=1));;
scVars:=List([1..3],i->Sum(Filtered([1..8],j->i in scBits[j]),j->scPoints[j]));;
scSpan:=xs->VectorSpace(scF,xs);;
scBasisOf:=v->BasisVectors(Basis(v));;
scContains:=function(v,w) return ForAll(scBasisOf(w),x->x in v); end;
scProd:=function(u,v)
  return scSpan(List(Cartesian(scBasisOf(u),scBasisOf(v)),p->p[1]*p[2]));
end;
scDegree:=function(x)
  local vals,s,t,c,d;
  vals:=Coefficients(scBasis,x); d:=0;
  for s in [1..8] do
    c:=Zero(scF);
    for t in [1..8] do
      if IsSubset(scBits[s],scBits[t]) then c:=c+vals[t]; fi;
    od;
    if c<>Zero(scF) then d:=Maximum(d,Length(scBits[s])); fi;
  od;
  return d;
end;
scSpaces:=[];;
scInputs:=[];;
scIterator:=Iterator(Subspaces(scF^3));;
while not IsDoneIterator(scIterator) do
  scW:=NextIterator(scIterator);
  scGs:=List(BasisVectors(Basis(scW)),c->Sum([1..3],i->c[i]*scVars[i]));
  Add(scInputs,scGs);
  Add(scSpaces,scSpan(Concatenation([scOne],scGs)));
od;
scRequire(Length(scSpaces)=16,"sixteen unital affine spaces");
scStep:=function(u,v,b,y)
  local un,vn;
  un:=scSpan(Filtered(Elements(u),a->a*b in v));
  vn:=scSpan(Concatenation(scBasisOf(v),List(scBasisOf(u),a->b*a)));
  scRequire(scOne in un and scOne in vn,"units retained");
  scRequire(Dimension(un)+Dimension(vn)=Dimension(u)+Dimension(v),"dimension balance");
  scRequire(scContains(u,un) and scContains(vn,v),"nested spaces");
  scRequire(scContains(y,scProd(un,vn)),"product containment");
  return [un,vn];
end;
scNormalize:=function(gs,u,f,q)
  local vg,core,rs,cur,g,j,r,beta,p,prod,rr;
  if Length(gs)=0 then gs:=[scZero]; fi;
  vg:=scSpan(gs); core:=Intersection(vg,u);
  rs:=Filtered(scBasisOf(core),g->f*g=f);
  beta:=List(gs,g->scZero);
  if Length(rs)>0 then
    # gs is an independent list in the tested nonzero cases.
    beta:=List(Coefficients(Basis(vg,gs),rs[1]),c->c*scOne);
  else
    scRequire(ForAll(scBasisOf(core),g->f*g=scZero),"zero core character");
    cur:=core; rs:=[];
    for j in [1..Length(gs)] do
      if not gs[j] in cur then
        Add(rs,j); cur:=scSpan(Concatenation(scBasisOf(cur),[gs[j]]));
      fi;
    od;
    scRequire(Length(rs)<=q,"residual rank");
    prod:=scOne;
    for j in rs do
      beta[j]:=prod; prod:=prod*(scOne+gs[j]);
    od;
  fi;
  p:=scOne+Sum([1..Length(gs)],j->beta[j]*gs[j]);
  for g in gs do scRequire(f*g*p=scZero,"weighted complete companion"); od;
  for g in beta do
    scRequire(g*g=g,"fresh Booleanity");
    scRequire(scDegree(g)<=Maximum(1,q-1),"coefficient degree");
  od;
  return Length(gs);
end;
Print("SIZE spaces=16 pairs=256 initial_steps=1632 points=8\n");
scSteps:=0;; scCases:=0;; scChains:=0;; scMaps:=0;; scCompanions:=0;;
for scUi in [1..16] do
  for scVi in [1..16] do
    scU0:=scSpaces[scUi]; scV0:=scSpaces[scVi]; scY:=scProd(scU0,scV0);
    for scB in Elements(scV0) do
      scPair:=scStep(scU0,scV0,scB,scY); scSteps:=scSteps+1;
    od;
    scU:=scU0; scV:=scV0; scLen:=0;
    while not scContains(scV,scProd(scU,scV)) do
      scB:=First(scBasisOf(scV),b->not ForAll(scBasisOf(scU),a->a*b in scV));
      scPair:=scStep(scU,scV,scB,scY);
      scRequire(Dimension(scPair[1])<Dimension(scU),"strict descent");
      scU:=scPair[1]; scV:=scPair[2]; scLen:=scLen+1;
      scRequire(scLen<=Dimension(scU0)-1,"termination bound");
    od;
    scQ:=Minimum(Dimension(scU0)-1,Dimension(scY)-Dimension(scV0));
    scRequire(Dimension(scU0)-Dimension(scU)<=scQ,"core codimension");
    scFvec:=First(Elements(scV),f->f<>scZero and
      ForAll(scBasisOf(scU),a->a*f=scZero or a*f=f));
    scRequire(scFvec<>fail and scDegree(scFvec)<=2,"paid common eigenvector");
    scGs:=scInputs[scUi];
    scCompanions:=scCompanions+scNormalize(scGs,scU,scFvec,scQ);
    scCompanions:=scCompanions+scNormalize(List(scGs,g->scOne+g),scU,scFvec,scQ);
    scMaps:=scMaps+2; scCases:=scCases+1; scChains:=scChains+scLen;
    Print("CASE ",scCases," U=",Dimension(scU0)," V=",Dimension(scV0),
      " Y=",Dimension(scY)," q=",scQ," core=",Dimension(scU),
      " stable=",Dimension(scV)," steps=",scLen," weight_degree=",scDegree(scFvec),"\n");
  od;
od;
scU:=scSpan([scOne,scVars[1],scVars[3]]);;
scV:=scSpan([scOne,scVars[2]]);;
scY:=scProd(scU,scV);;
scBadV:=scSpan(Concatenation(scBasisOf(scV),List(scBasisOf(scU),a->a*scVars[2])));;
scRequire(not scContains(scY,scProd(scU,scBadV)),"omitting colon step must fail");
scRequire(scVars[1]<>scZero,"all-zero coefficients fail unweighted nonzero input");
scRequire(scCases=256 and scSteps=1632 and scMaps=512,"completion counts");
Print("PASS pairs=",scCases," initial_steps=",scSteps," chain_steps=",scChains,
      " source_maps=",scMaps," companions=",scCompanions," negative_controls=2\n");
QUIT_GAP(0);
