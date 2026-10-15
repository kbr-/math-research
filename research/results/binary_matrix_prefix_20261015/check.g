# Test the paired excluded-middle prefix and bounded-word matrix mechanism.
# Stages: all sixteen matrices; all unital subalgebras by native algebra closure;
# short-word span checks; all two-variable source points; pair-only control.
# Native GAP exact matrix/algebra arithmetic; no custom elimination kernel.
# Expected: paired prefix is zero or identity; every irreducible algebra has
# an order-three element in its length-three word span; triangular source P^2=0.
# Refuted by: A noncentral paired prefix, missing short-word span element,
# irreducible order-three-free algebra, or nonzero triangular source mask.
# Possible because: One copy has noncentral unipotent prefixes, and pairwise
# commutator detectors can miss an irreducible tuple of three matrices.
mpF:=GF(2);; mpZ:=Zero(mpF);; mpO:=One(mpF);;
mpI:=IdentityMat(2,mpF);; mp0:=NullMat(2,2,mpF);;
mpOut:="research/results/binary_matrix_prefix_20261015/algebra-grid.txt";;
PrintTo(mpOut,"Exact GAP GF(2) matrices; Z(2)^0=one, 0*Z(2)=zero.\n");
mpAssert:=function(ok,msg) if not ok then Print("FAILED ",msg,"\n"); QUIT_GAP(1); fi; end;;
mpMats:=Set(List(Tuples([mpZ,mpO],4),v->[[v[1],v[2]],[v[3],v[4]]]));;
mpLines:=[[mpO,mpZ],[mpZ,mpO],[mpO,mpO]];;
mpCommon:=function(xs)
  return Filtered(mpLines,v->ForAll(xs,m->v*m=0*v or v*m=v));
end;;
mpElements:=function(a)
  local bs,cs;
  bs:=BasisVectors(Basis(a));
  return Set(List(Tuples([mpZ,mpO],Length(bs)),cs->
    Sum(List([1..Length(bs)],i->cs[i]*bs[i]))));
end;;
mpCentral:=0;; mpOneCopy:=0;; mpKilled:=0;;
for mpX in mpMats do
  mpB:=mpX^2+mpX;; mpS:=(mpI+mpB)^5;;
  mpAssert(mpB^2=mp0 or mpB^2=mpI,"Boolean defect square");
  mpAssert(mpS^2=mpI+mpB^2,"paired full five-line prefixes");
  mpAssert(mpS^2=mp0 or mpS^2=mpI,"paired central flag");
  mpCentral:=mpCentral+1;;
  if mpS<>mp0 and mpS<>mpI then mpOneCopy:=mpOneCopy+1; fi;
  if mpS^2=mp0 then mpKilled:=mpKilled+1; fi;
  AppendTo(mpOut,"matrix=",mpX," defect=",mpB," one-prefix=",mpS,
    " paired-prefix=",mpS^2,"\n");
od;
mpAssert(mpOneCopy>0 and mpKilled>0,"nonvacuous one-copy and order-three controls");

mpSets:=[mpElements(AlgebraWithOne(mpF,[mpI]))];; mpGens:=[[]];;
mpIndex:=1;;
while mpIndex<=Length(mpSets) do
  for mpX in mpMats do
    if not mpX in mpSets[mpIndex] then
      mpGs:=Concatenation(mpGens[mpIndex],[mpX]);;
      mpEs:=mpElements(AlgebraWithOne(mpF,Concatenation([mpI],mpGs)));;
      if not mpEs in mpSets then Add(mpSets,mpEs); Add(mpGens,mpGs); fi;
    fi;
  od;
  mpIndex:=mpIndex+1;;
od;
mpIrred:=0;; mpSpans:=0;; mpSpan:=fail;;
for mpIndex in [1..Length(mpSets)] do
  mpEs:=mpSets[mpIndex];; mpGs:=mpGens[mpIndex];;
  mpOrder:=Filtered(mpEs,x->x^2+x=mpI);;
  mpCls:=mpCommon(mpEs);;
  mpAssert((Length(mpCls)=0)=(Length(mpOrder)>0),"irreducibility/order-three comparison");
  mpWs:=[mpI];; mpLayer:=[mpI];;
  for mpLen in [1..3] do
    mpLayer:=Set(Concatenation(List(mpLayer,w->List(mpGs,x->w*x))));;
    mpWs:=Union(mpWs,mpLayer);;
  od;
  mpSpan:=VectorSpace(mpF,List(mpWs,Concatenation));;
  mpAssert(ForAll(mpEs,x->Concatenation(x) in mpSpan),"length-three word span");
  mpAssert(Dimension(mpSpan)<=4,"four-word basis suffices");
  mpSpans:=mpSpans+1;;
  if Length(mpCls)=0 then mpIrred:=mpIrred+1; fi;
  AppendTo(mpOut,"algebra-generators=",mpGs," elements=",mpEs,
    " invariant-row-lines=",mpCls," order-three-witnesses=",mpOrder,
    " short-word-span-dimension=",Dimension(mpSpan),"\n");
od;

mpPoints:=0;; mpTri:=0;; mpUnit:=0;; mpOr:=0;;
for mpX in mpMats do for mpY in mpMats do
  mpEs:=mpElements(AlgebraWithOne(mpF,[mpI,mpX,mpY]));;
  mpFlag:=mpI;;
  if ForAny(mpEs,t->t^2+t=mpI) then mpFlag:=mp0; fi;
  mpPunit:=(mpI+mpX)*(mpI+mpI+mpX);;
  mpPOr:=(mpI+(mpI+mpX)*(mpI+mpY))*(mpI+mpX)*(mpI+mpY);;
  if Length(mpCommon([mpX,mpY]))>0 then
    mpAssert(mpPunit^2=mp0 and mpPOr^2=mp0,"triangular unsatisfiable source prefix");
    mpTri:=mpTri+1;;
  fi;
  mpAssert(mpFlag*mpPunit^2=mp0 and mpFlag*mpPOr^2=mp0,"complete seed/input mask");
  mpPoints:=mpPoints+1;; mpUnit:=mpUnit+1;; mpOr:=mpOr+1;;
  AppendTo(mpOut,"pair=",[mpX,mpY]," bounded-span-seed-flag=",mpFlag,
    " units-P2=",mpPunit^2," or-source-P2=",mpPOr^2,"\n");
od; od;
# This grid uses the native generated algebra and proved short-word span,
# not explicit enumeration of the polynomially many four-word syntax tuples.
mpTriple:=fail;;
for mpCs in Combinations(mpMats,3) do
  if mpTriple=fail and Length(mpCommon(mpCs))=0
     and ForAll(mpCs,x->(x^2+x)^2=mp0)
     and ForAll(Combinations(mpCs,2),p->(p[1]*p[2]+p[2]*p[1])^2=mp0) then
    mpTriple:=mpCs;;
  fi;
od;
mpAssert(mpTriple<>fail,"pair-only detector counterexample exists");
AppendTo(mpOut,"pair-only counterexample=",mpTriple,"\n");
Print("Matrices checked: ",mpCentral,"; noncentral one-copy controls: ",mpOneCopy,
  "; killed order-three points: ",mpKilled,"\n");
Print("Unital subalgebras: ",Length(mpSets),"; irreducible: ",mpIrred,
  "; short-word spans: ",mpSpans,"\n");
Print("Old matrix pairs: ",mpPoints,"; triangularizable: ",mpTri,
  "; source masks checked: ",mpUnit+mpOr,"; pair-only triple controls: ",1,"\n");
Print("PASS paired matrix prefix controls\n");
QUIT_GAP(0);
