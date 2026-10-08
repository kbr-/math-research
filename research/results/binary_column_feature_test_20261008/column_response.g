# All one-column Boolean monomials for m=4,r=2,n=2, GF(2),GF(3).
# Check Razborov pullback, proper column normal form, common-response
# scalar maps and both complete companion images at accuracies one and two.
ccVars:=[];; ccOne:=1;; ccZero:=0;; ccCols:=2;; ccPigeons:=6;;
CCSum:=function(xs) local s,x; s:=ccZero; for x in xs do s:=s+x; od; return s; end;;
CCProd:=function(xs) local s,x; s:=ccOne; for x in xs do s:=s*x; od; return s; end;;
CCY:=function(i,j) return ccVars[(i-1)*ccCols+j]; end;;
CCNorm:=function(f) local ex,out,i,j,seen,idx,col,label,term,dead;
 ex:=ExtRepPolynomialRatFun(f); out:=ccZero;
 for i in [1,3..Length(ex)-1] do
  seen:=List([1..ccCols],j->0); term:=ccOne; dead:=false;
  for j in [1,3..Length(ex[i])-1] do
   idx:=ex[i][j];
   if idx<1 or idx>Length(ccVars) then Error("Unexpected variable index"); fi;
   col:=(idx-1) mod ccCols+1; label:=QuoInt(idx-1,ccCols)+1;
   if seen[col]<>0 and seen[col]<>label then dead:=true; break; fi;
   seen[col]:=label; term:=term*ccVars[idx];
  od;
  if not dead then out:=out+ex[i+1]*term; fi;
 od;
 return out;
end;;
ccMonChecks:=0;; ccBlocks:=0;; ccCompanions:=0;; ccFieldChecks:=0;; ccNonzeroImages:=0;;
ccSubsets:=Combinations([1..4],2);; ccAllSubsets:=Combinations([1..4]);;
ccAlpha:=[];; ccQ:=[];;
for ccPrime in [2,3] do
 ccField:=GF(ccPrime);;
 ccRing:=PolynomialRing(ccField,12);;
 ccVars:=IndeterminatesOfPolynomialRing(ccRing);; ccOne:=One(ccRing);; ccZero:=Zero(ccRing);;
 ccAlpha:=List([1..4],i->List([1..2],j->CCSum(List(Filtered([1..6],a->i in ccSubsets[a]),a->CCY(a,j)))));;
 for ccJ in [1..2] do
  for ccS in ccAllSubsets do
   ccOld:=CCProd(List(ccS,i->ccAlpha[i][ccJ]));;
   if Length(ccS)=0 then ccExpected:=ccOne;
   else ccExpected:=CCSum(List(Filtered([1..6],a->IsSubset(ccSubsets[a],ccS)),a->CCY(a,ccJ))); fi;
   if CCNorm(ccOld)<>ccExpected then Error("Column pullback identity"); fi;
   ccMonChecks:=ccMonChecks+1;
  od;
 od;
 ccTotal:=CCSum(ccVars);;
 ccRowSum:=CCSum(List([1..6],a->CCSum(List([1..2],j->CCY(a,j)))-ccOne));;
 if ccRowSum<>ccTotal-6*ccOne then Error("Total row identity"); fi;
 ccQ:=List([1..4],k->CCSum(List([1..2],j->CCSum(List(Combinations([1..4],k),S->CCProd(List(S,i->ccAlpha[i][j])))))));;
 for ccK in [1..4] do for ccOffset in [0..ccPrime-1] do for ccShift in [0,1] do
  ccG:=[ccQ[ccK]+ccOffset*ccOne,ccQ[1]+ccShift*ccOne];;
  ccLambda:=[Binomial(2,ccK)*One(ccField),2*One(ccField)];;
  ccC:=[(ccOffset+6*Binomial(2,ccK))*One(ccField),(ccShift+12)*One(ccField)];;
  for ccI in [1..2] do
   if CCNorm(ccG[ccI]-ccC[ccI]*ccOne-ccLambda[ccI]*ccRowSum)<>ccZero then Error("Response certificate"); fi;
  od;
  ccChosen:=PositionProperty(ccC,c->c<>Zero(ccField));;
  for ccH in [1,2] do
   ccCoeffs:=List([1..ccH],u->List([1..2],i->Zero(ccField)));;
   if ccChosen<>fail then ccCoeffs[1][ccChosen]:=Inverse(ccC[ccChosen]); fi;
   ccP:=CCProd(List(ccCoeffs,row->ccOne-CCSum(List([1..2],i->row[i]*ccG[i]))));;
   for ccI in [1..2] do
    ccImage:=ccG[ccI]*ccP;;
    if ccChosen=fail then ccRowPart:=ccLambda[ccI]*ccRowSum; ccCost:=[ccK,1][ccI];
    else
     ccRowPart:=-ccG[ccI]*Inverse(ccC[ccChosen])*ccLambda[ccChosen]*ccRowSum;
     ccCost:=[ccK,1][ccI]+[ccK,1][ccChosen];
    fi;
    if CCNorm(ccImage-ccRowPart)<>ccZero then Error("Complete companion image"); fi;
    if ccCost>ccH*(ccK+1)+[ccK,1][ccI] then Error("Original companion budget"); fi;
    ccCompanions:=ccCompanions+1;
    if ccImage<>ccZero then ccNonzeroImages:=ccNonzeroImages+1; fi;
   od;
   for ccRow in ccCoeffs do for ccBeta in ccRow do
    if ccBeta^ccPrime-ccBeta<>Zero(ccField) then Error("Coefficient domain"); fi;
    ccFieldChecks:=ccFieldChecks+1;
   od; od;
   ccBlocks:=ccBlocks+1;
  od;
 od; od; od;
 # Cross-column products survive the proper column normal form.
 ccCross:=ccAlpha[1][1]*ccAlpha[1][2];;
 if CCNorm(ccCross)<>ccCross or Length(ExtRepPolynomialRatFun(ccCross))/2<>9 then Error("Expansion control"); fi;
od;
if ccMonChecks<>64 or ccBlocks<>80 or ccCompanions<>160 or ccNonzeroImages=0 then Error("Coverage count"); fi;
Print("column_monomials=",ccMonChecks," complete_blocks=",ccBlocks,
 " companion_images=",ccCompanions," nonzero_images=",ccNonzeroImages,
 " coefficient_domains=",ccFieldChecks,"\n");
Print("PASS: common column responses; original degree charges; cross-column nine-term control.\n");
QUIT;
