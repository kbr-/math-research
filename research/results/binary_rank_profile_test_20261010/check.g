# Fixed orientation check for the support-profile identity and its MRD control.
# All67 binary subspaces of a2x2 tensor space; only54 have minimal output2.
# Three flags per retained space; native GAP intersections and ranks.
rpOut:="research/results/binary_rank_profile_test_20261010/check.txt";;
rpF:=GF(2);; rpZ:=Zero(rpF);; rpO:=One(rpF);;
rpAmbient:=rpF^4;; rpSpaces:=List(Subspaces(rpAmbient));;
rpDirections:=Filtered(Elements(rpF^2),v->not IsZero(v));;
Assert(0,Length(rpSpaces)=67 and Length(rpDirections)=3);
PrintTo(rpOut,"All67 subspaces in F2^2 tensor F2^2; full-output support required.\n");
rpCases:=0;; rpUsed:=0;; rpDual:=0;;
for rpW in rpSpaces do
  rpB:=BasisVectors(Basis(rpW)); rpM:=Length(rpB);
  if rpM>0 then
    rpSupport:=Concatenation(List(rpB,b->[b{[1,2]},b{[3,4]}]));
    if RankMat(rpSupport)=2 then
      rpUsed:=rpUsed+1;
      for rpH in rpDirections do
        rpK:=First(rpDirections,k->RankMat([rpH,k])=2);
        rpGinv:=Inverse([rpH,rpK]);
        rpBN:=List(rpB,b->Concatenation(b{[1,2]}*rpGinv,b{[3,4]}*rpGinv));
        rpM1:=TransposedMat(List(rpBN,b->[b[1],b[3]]));
        rpM2:=TransposedMat(List(rpBN,b->[b[2],b[4]]));
        rpCode:=List([rpM1,rpM2],m->Concatenation(m));
        Assert(0,RankMat(rpCode)=2);
        rpFlagTensor:=Subspace(rpAmbient,[[rpH[1],rpH[2],rpZ,rpZ],
          [rpZ,rpZ,rpH[1],rpH[2]]]);
        rpR1:=Dimension(Intersection(rpW,rpFlagTensor));
        rpR2:=rpM-rpR1;
        rpS1:=RankMat(rpM2); rpS2:=RankMat(Concatenation(rpM1,rpM2));
        Assert(0,rpS1=rpR2 and rpS2-rpS1=rpR1 and rpS2=rpM);
        rpPsi:=[];
        for rpI in [1..2] do
          for rpJ in [1..rpM] do
            Add(rpPsi,rpBN[rpJ]{[2*rpI-1,2*rpI]});
          od;
        od;
        rpD1:=Subspace(rpF^(2*rpM),NullspaceMat(TransposedMat(rpCode)));
        rpD2:=Subspace(rpF^(2*rpM),NullspaceMat(rpPsi));
        Assert(0,rpD1=rpD2 and Dimension(rpD1)=2*rpM-2);
        rpCases:=rpCases+1; rpDual:=rpDual+1;
        AppendTo(rpOut,"basis=",rpB," flag=",rpH," fibres=",[rpR1,rpR2],
          " reverse_support_increments=",[rpS1,rpS2-rpS1],"\n");
      od;
    fi;
  fi;
od;
Assert(0,rpUsed=54 and rpCases=162 and rpDual=162);
# Multiplication by1 and omega in F4, omega²=omega+1, in binary coordinates.
rpMRD:=Subspace(rpAmbient,[[rpO,rpZ,rpZ,rpO],[rpZ,rpO,rpO,rpO]]);;
for rpA in Filtered(Elements(rpMRD),v->not IsZero(v)) do
  Assert(0,RankMat([rpA{[1,2]},rpA{[3,4]}])=2);
od;
rpMRDCases:=0;;
for rpH in rpDirections do
  rpFlagTensor:=Subspace(rpAmbient,[[rpH[1],rpH[2],rpZ,rpZ],
    [rpZ,rpZ,rpH[1],rpH[2]]]);
  Assert(0,Dimension(Intersection(rpMRD,rpFlagTensor))=0);
  for rpRow in rpDirections do
    rpContraction:=List(BasisVectors(Basis(rpMRD)),b->
      rpRow[1]*b{[1,2]}+rpRow[2]*b{[3,4]});
    Assert(0,RankMat(rpContraction)=2);
    rpMRDCases:=rpMRDCases+1;
  od;
od;
Assert(0,rpMRDCases=9);
AppendTo(rpOut,"PASS:54 full-support spaces;162 flag identities;162 trace-dual ",
 "identities; MRD3 nonzero matrices rank2 and9 flag/row controls with ",
 "actual intersection0 versus flag bound1.\n");
QUIT;
