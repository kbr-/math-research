# Exact controls for the review, not a hard-family computation.
# Six product-projection instances (m=1..3, 0 or 1 idle qubit),
# twelve external tail cutoffs; at most 16x16 matrices.
# Every nonsingular normalized one-bit moment over F4 and F16 (16 total).
qaOut := "research/results/binary_adjoint_scope_completion_20261010/check.txt";
PrintTo(qaOut,"Exact GAP review controls; maximum product matrix 16x16.\n");
qaF := GF(16);; qaZ := Z(16);; qaOne := One(qaF);; qaZero := Zero(qaF);;
qaAdj := function(a) return TransposedMat(List(a,r->List(r,x->x^4))); end;;
qaP0 := [[qaOne,qaZero],[qaZero,qaZero]];;
qaW := [[qaZ],[qaZ^2]];; qaQ0 := qaW*qaAdj(qaW);;
Assert(0, qaAdj(qaW)*qaW=[[qaOne]]);
Assert(0, qaQ0^2=qaQ0 and qaAdj(qaQ0)=qaQ0);
qaCount := 0;; qaExtreme := 0;;
for qaM in [1..3] do
  for qaIdle in [0..1] do
    qaP := [[qaOne]]; qaQ := [[qaOne]];
    for qaI in [1..qaM] do
      qaP := KroneckerProduct(qaP,qaP0);
      qaQ := KroneckerProduct(qaQ,qaQ0);
    od;
    qaP := KroneckerProduct(qaP,IdentityMat(2^qaIdle,qaF));
    qaQ := KroneckerProduct(qaQ,IdentityMat(2^qaIdle,qaF));
    Assert(0,qaP^2=qaP and qaQ^2=qaQ);
    for qaR in [1..qaM] do
      qaDiag := List([0..2^(qaM+qaIdle)-1], function(j)
        local b,s,t;
        b := QuoInt(j,2^qaIdle); s:=0;
        for t in [1..qaM] do s:=s+(b mod 2); b:=QuoInt(b,2); od;
        if s>=qaR then return qaOne; else return qaZero; fi;
      end);
      qaH := DiagonalMat(qaDiag); qaA := qaH*qaQ*qaP;
      Assert(0,RankMat(qaA)=2^qaIdle and RankMat(qaP)=2^qaIdle);
      qaCount:=qaCount+1;
      if qaR=qaM then
        Assert(0,qaA*qaAdj(qaA)=qaH);
        qaExtreme:=qaExtreme+1;
      fi;
      AppendTo(qaOut,"m=",qaM," idle=",qaIdle," tail=",qaR,
        " rankA=",RankMat(qaA)," rankP=",RankMat(qaP),"\n");
    od;
  od;
od;
qaMoments:=0;;
for qaSize in [4,16] do
  qaField:=GF(qaSize); qaO:=One(qaField); qaZ0:=Zero(qaField);
  for qaAlpha in Elements(qaField) do
    qaGram:=[[qaO,qaAlpha],[qaAlpha,qaAlpha]];
    if qaAlpha in [qaZ0,qaO] then
      Assert(0,RankMat(qaGram)=1);
    else
      Assert(0,RankMat(qaGram)=2);
      qaT:=[[qaO],[qaZ0]]; qaD:=[[qaO,qaAlpha]];
      Assert(0,qaD=TransposedMat(qaT)*qaGram);
      Assert(0,qaD*qaT=[[qaO]] and RankMat(qaT*qaD)=1);
      qaVector:=[[qaAlpha],[qaO]];
      qaX:=[[qaZ0,qaZ0],[qaO,qaO]];
      Assert(0,qaD*qaVector=[[qaZ0]]);
      Assert(0,qaD*qaX*qaVector=[[qaAlpha+qaAlpha^2]]);
      Assert(0,qaAlpha+qaAlpha^2<>qaZ0);
      qaRemainder:=IdentityMat(2,qaField)-qaT*qaD;
      Assert(0,qaRemainder^2=qaRemainder and RankMat(qaRemainder)=1);
      qaMoments:=qaMoments+1;
    fi;
  od;
od;
Assert(0,qaCount=12 and qaExtreme=6 and qaMoments=16);
AppendTo(qaOut,"PASS: 12 relative-tail ranks; 6 defect-free extreme tails; ",
 "16 nonsingular moments with reverse-kernel closure failure and idempotent remainder.\n");
QUIT;
