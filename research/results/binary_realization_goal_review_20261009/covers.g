# Every two-arrow diagram F2^2 -> F2^2 -> F2^2: 16^2=256 cases.
# Construct the cover by retaining every newly needed generator to the end.
# Verify surjectivity, inclusion compatibility and the sharp dimension ledger.
cvF:=GF(2);; cvI:=IdentityMat(2,cvF);;
cvMatrices:=List(Tuples(Elements(cvF),4),v->[v{[1,2]},v{[3,4]}]);;
cvComplement:=function(A)
 local rows, result, e, oldrank;
 rows:=ShallowCopy(A); result:=[]; oldrank:=RankMat(rows);
 for e in cvI do
  if RankMat(Concatenation(rows,[e]))>oldrank then
   Add(rows,e); Add(result,e); oldrank:=oldrank+1;
  fi;
 od;
 return result;
end;;
cvCounts:=List([1..6],i->0);; cvCases:=0;; cvChecks:=0;;
for cvA in cvMatrices do
 for cvB in cvMatrices do
  cvP0:=cvI;;
  cvC1:=cvComplement(cvA);; cvP1:=Concatenation(cvA,cvC1);;
  cvC2:=cvComplement(cvB);; cvP2:=Concatenation(cvP1*cvB,cvC2);;
  if RankMat(cvP1)<>2 or RankMat(cvP2)<>2 then Error("not onto"); fi;
  if cvP1{[1..2]}<>cvP0*cvA then Error("first square"); fi;
  if cvP2{[1..Length(cvP1)]}<>cvP1*cvB then Error("second square"); fi;
  cvCost:=6-RankMat(cvA)-RankMat(cvB);;
  if Length(cvP2)<>cvCost then Error("birth cost"); fi;
  cvCounts[cvCost]:=cvCounts[cvCost]+1;
  cvCases:=cvCases+1; cvChecks:=cvChecks+5;
 od;
od;
if cvCases<>256 then Error("enumeration guard"); fi;
Print("PASS cover_cases=",cvCases," checks=",cvChecks,"\n");
for cvR in [2..6] do Print("terminal_dimension=",cvR," cases=",cvCounts[cvR],"\n"); od;
# Full binary gate truth tables used by the F2 algebraic-to-CNF source screen.
cvGateChecks:=0;;
for cvBits in Tuples([0,1],3) do
 cvU:=cvBits[1]; cvV:=cvBits[2]; cvW:=cvBits[3];
 cvAndClauses:=(cvU=0 or cvV=0 or cvW=1) and
               (cvU=1 or cvW=0) and (cvV=1 or cvW=0);
 if cvAndClauses<>(cvW=cvU*cvV) then Error("AND gate"); fi;
 cvXorClauses:=true;
 for cvBad in Tuples([0,1],3) do
  if cvBad[3]<>(cvBad[1]+cvBad[2]) mod 2 then
   cvXorClauses:=cvXorClauses and cvBits<>cvBad;
  fi;
 od;
 if cvXorClauses<>(cvW=(cvU+cvV) mod 2) then Error("XOR gate"); fi;
 cvGateChecks:=cvGateChecks+2;
od;
Print("PASS binary_gate_checks=",cvGateChecks,"\n");
QUIT;
