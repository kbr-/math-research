# Exact finite control for the proposed graph Koszul contraction over F2[x,y,z].
# Four fresh variables; all 15 fresh monomials of total degree <=2 and all 16
# exterior masks. Native GAP polynomials verify formal identities, not only points.
# No parameter sweep: this is one 240-basis-case encoding control. The article
# proves the all-parameter result. Additional eight-point controls concern two
# actual complete ENS blocks and the non-small Boolean-companion perturbation.
pcF := GF(2);;
pcR := PolynomialRing(pcF, ["x","y","z","r1","r2","r3","r4"]);;
pcV := IndeterminatesOfPolynomialRing(pcR);;
pcIds := List(pcV, pcA -> ExtRepPolynomialRatFun(pcA)[1][1]);;
pcFresh := pcV{[4..7]};;
pcBeta := [One(pcR), One(pcR)+pcV[1]*pcV[2],
           One(pcR), One(pcR)+pcV[3]];;
pcWeights := [1,1,1,1,2,1,1];;
pcEW := [1,2,1,1];;
pcZero := function() return List([1..16], pcA -> Zero(pcR)); end;;
pcIsZero := function(pcVec) return ForAll(pcVec,IsZero); end;;
pcEq := function(pcLeft,pcRight)
  return ForAll([1..16],pcJ -> IsZero(pcLeft[pcJ]-pcRight[pcJ]));
end;;
pcRepOf := function(pcPoly)
  if IsFFE(pcPoly) then
    if IsZero(pcPoly) then return []; else return [[],pcPoly]; fi;
  fi;
  return ExtRepPolynomialRatFun(pcPoly);
end;;
pcHas := function(pcMask,pcJ)
  return QuoInt(pcMask,2^(pcJ-1)) mod 2 = 1;
end;;
pcExp := function(pcTerm)
  local pcE,pcK;
  pcE := List([1..7],pcA -> 0);
  for pcK in [1,3..Length(pcTerm)-1] do
    pcE[Position(pcIds,pcTerm[pcK])] := pcTerm[pcK+1];
  od;
  return pcE;
end;;
pcMon := function(pcE)
  return Product([1..7],pcJ -> pcV[pcJ]^pcE[pcJ]);
end;;
pcDiff := function(pcVec,pcMode)
  local pcOut,pcMask,pcJ,pcFactor;
  pcOut := pcZero();
  for pcMask in [0..15] do
    for pcJ in [1..4] do
      if pcHas(pcMask,pcJ) then
        if pcMode=0 then pcFactor:=pcFresh[pcJ];
        elif pcMode=1 then pcFactor:=pcFresh[pcJ]+pcBeta[pcJ];
        else pcFactor:=pcBeta[pcJ]; fi;
        pcOut[pcMask-2^(pcJ-1)+1] :=
          pcOut[pcMask-2^(pcJ-1)+1]+pcFactor*pcVec[pcMask+1];
      fi;
    od;
  od;
  return pcOut;
end;;
pcH := function(pcVec)
  local pcOut,pcMask,pcRep,pcK,pcE,pcJ,pcFirst;
  pcOut := pcZero();
  for pcMask in [0..15] do
    pcRep := pcRepOf(pcVec[pcMask+1]);
    for pcK in [1,3..Length(pcRep)-1] do
      pcE := pcExp(pcRep[pcK]); pcFirst := 0;
      for pcJ in [1..4] do
        if pcE[pcJ+3]>0 or pcHas(pcMask,pcJ) then
          pcFirst:=pcJ; break;
        fi;
      od;
      if pcFirst>0 and not pcHas(pcMask,pcFirst) then
        pcE[pcFirst+3]:=pcE[pcFirst+3]-1;
        pcOut[pcMask+2^(pcFirst-1)+1] :=
          pcOut[pcMask+2^(pcFirst-1)+1]+pcRep[pcK+1]*pcMon(pcE);
      fi;
    od;
  od;
  return pcOut;
end;;
pcProjection := function(pcVec,pcPerturbed)
  local pcOut,pcValues;
  pcOut:=pcZero();
  if pcPerturbed then pcValues:=pcBeta;
  else pcValues:=List([1..4],pcA -> Zero(pcR)); fi;
  pcOut[1]:=Value(pcVec[1],pcFresh,pcValues);
  return pcOut;
end;;
pcHNew := function(pcVec)
  local pcOut,pcCur,pcTerm,pcSteps;
  pcOut:=pcZero(); pcCur:=pcVec; pcSteps:=0;
  while not pcIsZero(pcCur) do
    pcSteps:=pcSteps+1;
    if pcSteps>8 then Error("fresh-degree nilpotence failed"); fi;
    pcTerm:=pcH(pcCur); pcOut:=pcOut+pcTerm;
    pcCur:=pcDiff(pcTerm,2);
  od;
  return pcOut;
end;;
pcCost := function(pcVec)
  local pcMax,pcMask,pcRep,pcK,pcE,pcExterior;
  pcMax:=-1;
  for pcMask in [0..15] do
    pcExterior:=Sum(Filtered([1..4],pcJ -> pcHas(pcMask,pcJ)),
                    pcJ -> pcEW[pcJ]);
    pcRep:=pcRepOf(pcVec[pcMask+1]);
    for pcK in [1,3..Length(pcRep)-1] do
      pcE:=pcExp(pcRep[pcK]);
      pcMax:=Maximum(pcMax,Sum([1..7],pcJ -> pcE[pcJ]*pcWeights[pcJ])+pcExterior);
    od;
  od;
  return pcMax;
end;;
pcExponents:=Filtered(Tuples([0..2],4),pcA -> Sum(pcA)<=2);;
if Length(pcExponents)<>15 then Error("wrong basis count"); fi;
pcCount:=0;; pcEqualities:=0;; pcBounds:=0;;
for pcE4 in pcExponents do
  for pcMask in [0..15] do
    pcVec:=pcZero(); pcVec[pcMask+1]:=pcMon(Concatenation([0,0,0],pcE4));
    if not pcEq(pcDiff(pcH(pcVec),0)+pcH(pcDiff(pcVec,0)),
       pcVec+pcProjection(pcVec,false)) then Error("initial homotopy"); fi;
    if not pcEq(pcDiff(pcHNew(pcVec),1)+pcHNew(pcDiff(pcVec,1)),
       pcVec+pcProjection(pcVec,true)) then Error("perturbed homotopy"); fi;
    if not pcIsZero(pcDiff(pcDiff(pcVec,1),1)) then Error("d squared"); fi;
    if not pcIsZero(pcHNew(pcHNew(pcVec))) then Error("h squared"); fi;
    if not pcIsZero(pcProjection(pcDiff(pcVec,1),true)) then
      Print("projection diagnostic mask=",pcMask," exponents=",pcE4,
            " d=",pcDiff(pcVec,1)," projected=",pcProjection(pcDiff(pcVec,1),true),
            " zero=",pcZero(),"\n");
      Error("projection chain map");
    fi;
    pcEqualities:=pcEqualities+5;
    if pcCost(pcHNew(pcVec))>pcCost(pcVec) then Error("homotopy degree"); fi;
    if pcCost(pcDiff(pcVec,1))>pcCost(pcVec) then Error("differential degree"); fi;
    if pcCost(pcProjection(pcVec,true))>pcCost(pcVec) then Error("projection degree"); fi;
    pcBounds:=pcBounds+3; pcCount:=pcCount+1;
    Print("graph ",pcCount," exponents=",pcE4," exterior=",pcMask,
          " weight=",pcCost(pcVec)," PASS\n");
  od;
od;
pcSourceChecks:=0;; pcBad:=0;;
for pcBits in Tuples([0,1],3) do
  pcX:=pcBits[1]; pcY:=pcBits[2]; pcZ:=pcBits[3];
  pcInputs:=[[pcX*pcY,pcZ],[pcZ,pcX]];
  pcRows:=[[1,1-pcX*pcY],[1,1-pcZ]];
  for pcA in [1..2] do
    pcProduct:=(1-Sum([1..2],pcJ -> pcRows[pcA][pcJ]*pcInputs[pcA][pcJ])) mod 2;
    for pcJ in [1..2] do
      if pcInputs[pcA][pcJ]*pcProduct mod 2 <>0 then Error("companion"); fi;
      if (pcRows[pcA][pcJ]^2-pcRows[pcA][pcJ]) mod 2 <>0 then Error("field"); fi;
      pcSourceChecks:=pcSourceChecks+2;
    od;
  od;
  pcProduct:=(1-pcX*pcY-pcZ) mod 2;
  if pcX*pcY*pcProduct mod 2 <>0 or pcZ*pcProduct mod 2<>0 then pcBad:=pcBad+1; fi;
od;
pcU:=[];; pcVBad:=[];; pcVGood:=[];;
for pcBits in Tuples([0,1],3) do
  pcX:=pcBits[1];pcY:=pcBits[2];pcRBit:=pcBits[3];
  Add(pcU,One(pcF)*(pcX*(1-pcRBit)));
  Add(pcVBad,One(pcF)*(pcY*(1-pcRBit)));
  Add(pcVGood,One(pcF)*((pcX+pcY-pcX*pcY)*(1-pcRBit)));
od;
pcId:=IdentityMat(8,pcF);; pcUM:=DiagonalMat(pcU);;
pcQM:=pcUM*(pcId-DiagonalMat(pcVBad));;
if pcQM*pcQM<>pcQM or RankMat(pcQM)<>1 or RankMat(pcId-pcQM)<>7 then
  Error("idempotent non-smallness control");
fi;
pcGoodM:=DiagonalMat(pcVGood);;
if pcUM*(pcId-pcGoodM)<>NullMat(8,8,pcF) then Error("smallness positive control"); fi;
pcEffective:=(pcId-pcUM)*pcGoodM;;
if RankMat(pcEffective)<>1 then Error("effective differential control"); fi;
if pcBad=0 then Error("negative source control vacuous"); fi;
Print("SUMMARY graph_basis=",pcCount," formal_equalities=",pcEqualities,
      " degree_checks=",pcBounds," source_checks=",pcSourceChecks,
      " negative_source_points=",pcBad,
      " non_small_q_rank=",RankMat(pcQM),
      " one_minus_q_rank=",RankMat(pcId-pcQM),
      " small_effective_rank=",RankMat(pcEffective),"\n");
Print("PASS graph contraction and actual Boolean companion controls\n");
QUIT;
