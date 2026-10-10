# Exact marked-relation controls, not a hard-family degree experiment.
# Stages: all 67 binary 2x2 subspaces; then all constant/affine maps for
# the complete accuracy-one tuple (x,y,x+y), weight one, old Boolean D=3.
# Fixed sizes: 16 ambient matrices, at most 1024 relation vectors.
mrF:=GF(2);; mrZ:=Zero(mrF);; mrO:=One(mrF);;
mrV:=FullRowSpace(mrF,4);; mrSubs:=AsList(Subspaces(mrV));;
Assert(0,Length(mrSubs)=67);
mrGood:=0;;
for mrS in mrSubs do
  mrCodim:=4-Dimension(mrS);;
  mrMarked:=Filtered(AsList(mrS),v->v{[1,2]}<>[mrZ,mrZ] and RankMat([v{[1,2]},v{[3,4]}])=1);;
  if mrCodim<2 then Assert(0,Length(mrMarked)>0); mrGood:=mrGood+1; fi;
  Print("code dimension=",Dimension(mrS)," basis=",BasisVectors(Basis(mrS))," marked=",Length(mrMarked),"\n");
od;
mrA:=[[mrZ,mrO],[mrO,mrO]];;
for mrFv in AsList(FullRowSpace(mrF,2)) do
  if not IsZero(mrFv) then Assert(0,RankMat([mrFv,mrFv*mrA])=2); fi;
od;
mrPoints:=Tuples([mrZ,mrO],2);;
mrX:=List(mrPoints,p->p[1]);; mrY:=List(mrPoints,p->p[2]);;
mrOne:=List(mrPoints,p->mrO);; mrG:=[mrX,mrY,mrX+mrY];;
mrMul:=function(a,b) return List([1..Length(a)],i->a[i]*b[i]); end;;
for mrFeatures in [[mrOne],[mrOne,mrX,mrY]] do
  mrCols:=[Concatenation(mrG)];;
  for mrJ in [1..3] do
    for mrPhi in mrFeatures do
      Add(mrCols,Concatenation(List(mrG,g->mrMul(g,mrMul(mrG[mrJ],mrPhi)))));
    od;
  od;
  mrN:=3*Length(mrFeatures);; mrSuccess:=0;; mrUnmarked:=0;;
  for mrC in AsList(FullRowSpace(mrF,mrN+1)) do
    mrMaps:=[];;
    for mrJ in [1..3] do
      Add(mrMaps,Sum([1..Length(mrFeatures)],l->mrC[1+(mrJ-1)*Length(mrFeatures)+l]*mrFeatures[l]));
    od;
    mrQ:=Sum([1..3],j->mrMul(mrMaps[j],mrG[j]));;
    mrDirect:=Concatenation(List(mrG,g->mrMul(g,mrC[1]*mrOne+mrQ)));;
    Assert(0,mrDirect=mrC*mrCols);
    if IsZero(mrDirect) then
      if mrC[1]=mrO then
        mrSuccess:=mrSuccess+1;
        Assert(0,ForAll(mrMaps,a->IsZero(mrMul(a,a)+a)));
      elif not IsZero(mrC) then mrUnmarked:=mrUnmarked+1; fi;
      Print("relation features=",Length(mrFeatures)," vector=",mrC,"\n");
    fi;
  od;
  Assert(0,RankMat(mrCols)=3);
  if Length(mrFeatures)=1 then Assert(0,mrSuccess=0 and mrUnmarked=1);
  else Assert(0,mrSuccess=64 and mrUnmarked=63); fi;
  Print("features=",Length(mrFeatures)," vectors=",2^(mrN+1)," codimension=",RankMat(mrCols)," marked=",mrSuccess," unmarked=",mrUnmarked,"\n");
od;
Print("PASS: 67 codes, ",mrGood," below-threshold codes; 1040 relation identities; graph and complete fields checked.\n");
QUIT;
