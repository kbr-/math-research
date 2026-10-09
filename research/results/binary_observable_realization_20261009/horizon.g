# Exhaustive linear-basis control of finite-horizon observation quotients.
# n=4, D=4, lambda is the normalized F2 sum over nonzero Boolean points.
# All products are Boolean-reduced; field equations therefore vanish exactly.
hzN:=4;; hzAll:=Concatenation(List([0..hzN],k->Combinations([1..hzN],k)));;
hzOne:=One(GF(2));; hzZero:=Zero(GF(2));;
hzMoment:=function(S)
 if Length(S)=0 or Length(S)=hzN then return hzOne; fi;
 return hzZero;
end;;
hzBases:=List([0..hzN],b->Filtered(hzAll,S->Length(S)<=b));;
hzMatrices:=List([0..hzN],b->List(hzBases[b+1],S->
 List(hzBases[hzN-b+1],T->hzMoment(Union(S,T)))));;
hzKernels:=List(hzMatrices,NullspaceMat);;
hzChecks:=0;;
for hzB in [0..hzN] do
 hzRank:=RankMat(hzMatrices[hzB+1]);;
 if hzB=0 or hzB=hzN then hzExpected:=1;
 else hzExpected:=Binomial(hzN,hzB)+1; fi;
 if hzRank<>hzExpected then Error("rank formula"); fi;
 Print("horizon=",hzB," prefix_dimension=",Length(hzBases[hzB+1]),
       " rank=",hzRank," kernel_dimension=",Length(hzKernels[hzB+1]),"\n");
 if hzB<hzN then
  for hzVector in hzKernels[hzB+1] do
   hzEmbedded:=Concatenation(hzVector,List([1..Length(hzBases[hzB+2])-Length(hzVector)],i->hzZero));;
   if not IsZero(hzEmbedded*hzMatrices[hzB+2]) then Error("inclusion"); fi;
   hzChecks:=hzChecks+1;
   for hzX in [1..hzN] do
    hzImage:=List(hzBases[hzB+2],S->hzZero);;
    for hzI in [1..Length(hzVector)] do
     hzJ:=Position(hzBases[hzB+2],Union(hzBases[hzB+1][hzI],[hzX]));;
     hzImage[hzJ]:=hzImage[hzJ]+hzVector[hzI];
    od;
    if not IsZero(hzImage*hzMatrices[hzB+2]) then Error("multiplication"); fi;
    hzChecks:=hzChecks+1;
   od;
  od;
 fi;
od;
hzFull:=List(hzAll,S->List(hzAll,T->hzMoment(Union(S,T))));;
if RankMat(hzFull)<>2^hzN-1 then Error("full Hankel rank"); fi;
# x1 vanishes under all contexts of degree <=2 but not the degree-3 complement.
if not ForAll(hzBases[3],T->IsZero(hzMoment(Union([1],T)))) then Error("death premise"); fi;
if hzMoment([1,2,3,4])<>hzOne then Error("reuse control"); fi;
Print("PASS full_rank=",RankMat(hzFull)," kernel_transition_checks=",hzChecks,
      " normalized_unit=true lost_x1_detected=true\n");
QUIT;
