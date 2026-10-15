# Paid-reference row-law control over the full Boolean field ideal, not a charged hard instance.
# Fixed fixture: X,U1..U6,Z1..Z6; g_i=X*U_i+(1+X)*m_i, degree3.
# Parent A=(g1,g2,g3,g4), parent B=(g1+g5,g2+g6); w=X,K5,h3,D21.
# Full seed has6 binary coordinates; canonical projections read first4 and first2.
# Expected: initial joint rank equals H, weighted high dimension4 exceeds h3,
# and the exact shared-row mean is below the paid degree1 bound and H.
# Refuted by: A mean above the predicted bound, failed original/reference comparison or mass count.
# Possible because: Incorrect coupled projections, unweighted comparisons or degree-block closure change these quantities.
# One fixed exact identity/rank control; no fitting, size series or proof-hardness inference.
prField := GF(2);;
SizeScreen([2000,50]);
prOne := One(prField);;
prEff := 4;; prSeedDim := 6;; prQ := 6;; prK := 5;; prRows := 3;;
prV := 1+2*prQ;; prDelta := 3;; prD := 21;;
prAssertions := 0;;
prCheck := function(ok, label)
  if not ok then Print("FAILED ",label,"\n"); QUIT_GAP(1); fi;
  prAssertions := prAssertions+1;
end;;
prPacked := function(bits)
  local vec;
  vec := List(bits,b->b*prOne);
  ConvertToVectorRep(vec,prField);
  return vec;
end;;
prN := function(v,k)
  if k<0 then return 0; fi;
  return Sum([0..Minimum(v,k)],i->Binomial(v,i));
end;;
prRank := function(rows)
  if IsEmpty(rows) then return 0; fi;
  return RankMat(rows);
end;;
prCheck(prD>=1+prK+(prRows+1)*prDelta,"actual old product reserve");
prCheck(prD>=1+prK+prRows*(prDelta+1)+prDelta,"original raw replay reserve");
prCheck(prEff>prRows,"weighted input dimension beyond code rows");
prCheck(prQ>prK,"initial common zero selector is above multiplier degree");
prSpace := prField^prEff;;
prIter := Iterator(Subspaces(prSpace));;
prStates := [];;
while not IsDoneIterator(prIter) do Add(prStates,NextIterator(prIter)); od;
prCount := Length(prStates);;
prCheck(prCount<=100,"refuse oversized code-state fixture");
prExpectedStates := Size(Subspaces(prSpace));;
prCheck(prCount=prExpectedStates,"subspace inventory versus independent size formula");
prBases := List(prStates,s->BasisVectors(Basis(s)));;
prDims := List(prStates,Dimension);;
prZeroId := Position(prDims,0);;
prToInt := function(vec)
  return Sum([1..Length(vec)],i->IntFFE(vec[i])*2^(i-1));
end;;
prDot := function(vec,u)
  return Sum([1..prEff],i->IntFFE(vec[i])*u[i]) mod 2;
end;;
prPoints := Tuples([0,1],prQ);;
prMonomialSupports := List([0..prK],d->Concatenation(List([0..d],j->Combinations([1..prQ],j))));;
prEvaluation := List(prMonomialSupports,sups->List(prPoints,u->prPacked(List(sups,t->Product(u{t})))));;
prProfile := function(ids)
  return List([0..prK],d->prRank(prEvaluation[d+1]{ids}));
end;;
prWeighted := function(profile)
  return Sum([0..prK],j->Binomial(prQ,j)*profile[prK-j+1]);
end;;
prSupport := function(basis,which)
  local ids,ii,u,ca,cb,ea,eb,l1,l2;
  ids := [];
  for ii in [1..Length(prPoints)] do
    u := prPoints[ii];
    ca := ForAll(basis,v->prDot(v,u)=0);
    l1 := (u[1]+u[5]) mod 2; l2 := (u[2]+u[6]) mod 2;
    cb := ForAll(basis,v->(IntFFE(v[1])*l1+IntFFE(v[2])*l2) mod 2=0);
    ea := ca and ForAny(u{[1..prEff]},x->x=1);
    eb := cb and (l1=1 or l2=1);
    if (which=1 and ea) or (which=2 and eb) or (which=0 and (ea or eb)) then Add(ids,ii); fi;
  od;
  return ids;
end;;
prSupports := List(prBases,b->prSupport(b,0));;
prProfiles := List(prSupports,prProfile);;
prRanks := List(prProfiles,prWeighted);;
prH := prN(prV-1,prK);;
prInitialA := prWeighted(prProfile(prSupport([],1)));;
prInitialB := prWeighted(prProfile(prSupport([],2)));;
prCheck(prRanks[prZeroId]=prH,"initial joint rank full");
prCheck(ForAll(prRanks,r->r<=prH),"same original weighted denominator");
prEta := prN(prV,prK-1)/(2*prN(prV,prK));;
prSyntaxEta := prN(prV,prK-prDelta)/(2*prN(prV,prK));;
prBound := (prInitialA+prInitialB)*(1-prEta)^prRows;;
prCoarse := 2*prH*(1-prEta)^prRows;;
prSyntaxBound := (prInitialA+prInitialB)*(1-prSyntaxEta)^prRows;;
prCheck(prBound<prH and prCoarse<prH,"paid affine prediction strict");
prCheck(prSyntaxBound>=prH,"syntactic ambient screen does not certify deficit");
# Transition counts are per distinct subspace, not per previously seen row matrix.
# The two unused full-seed coordinates give each effective row four lifts.
prMultiplicity := 2^(prSeedDim-prEff);;
prTransitions := List([1..prCount],i->List([1..prCount],j->0));;
for prI in [1..prCount] do
  prTransitions[prI][prI] := prMultiplicity*Size(prStates[prI]);
  for prJ in [1..prCount] do
    if prDims[prJ]=prDims[prI]+1 and ForAll(prBases[prI],v->v in prStates[prJ]) then
      prTransitions[prI][prJ] := prMultiplicity*(Size(prStates[prJ])-Size(prStates[prI]));
    fi;
  od;
  prCheck(Sum(prTransitions[prI])=2^prSeedDim,"all full next-row choices counted");
od;
prCounts := List([1..prCount],i->0);; prCounts[prZeroId] := 1;
prFrontiers := [ShallowCopy(prCounts)];;
for prStage in [1..prRows] do
  prNext := List([1..prCount],j->Sum([1..prCount],i->prCounts[i]*prTransitions[i][j]));
  prCounts := prNext;
  Add(prFrontiers,ShallowCopy(prCounts));
  prCheck(Sum(prCounts)=2^(prSeedDim*prStage),"complete shared-row matrix mass");
  prCheck(ForAll([1..prCount],i->prCounts[i]=0 or prDims[i]<=prStage),"reachable row rank respects stage");
od;
prMean := Sum([1..prCount],i->prCounts[i]*prRanks[i])/Sum(prCounts);;
prCheck(prMean<=prBound and prMean<prH,"actual completed mean within paid prediction");
prData := "research/results/binary_paid_reference_rows_20261015/state-data.tsv";;
prDataStream := OutputTextFile(prData,false);;
SetPrintFormattingStatus(prDataStream,false);
PrintTo(prDataStream,"state\tdimension\tbasis_codes\tU_support_indices\trank_profile_0_to_K\tweighted_joint_rank\tstage_counts\tfull_row_transition_counts\n");
for prI in [1..prCount] do
  PrintTo(prDataStream,prI,"\t",prDims[prI],"\t",List(prBases[prI],prToInt),"\t",prSupports[prI],"\t",prProfiles[prI],"\t",prRanks[prI],"\t",List(prFrontiers,c->c[prI]),"\t",prTransitions[prI],"\n");
od;
CloseStream(prDataStream);
# Independent end-to-end controls start with the actual cubic inputs on old points.
# Remove only the known duplicate multiplier columns involving X, justified by X^2=X.
prInert := [[1,2],[1,3],[1,4],[1,5],[1,6],[2,3]];;
prFreePoints := Tuples([0,1],2*prQ);;
prFullSupports := Concatenation(List([0..prK],j->Combinations([1..2*prQ],j)));;
prOldEvaluate := List(prFreePoints,p->prPacked(List(prFullSupports,t->Product(p{t}))));;
prRawValues := function(point,x)
  local u,z;
  u := point{[1..prQ]}; z := point{[prQ+1..2*prQ]};
  return List([1..prQ],i->(x*u[i]+(1+x)*Product(z{prInert[i]})) mod 2);
end;;
prRawError := function(point,x,basis)
  local gs,ca,cb,b,aRow,bRow,b1,b2;
  gs := prRawValues(point,x);
  b1 := (gs[1]+gs[5]) mod 2; b2 := (gs[2]+gs[6]) mod 2;
  ca := 1; cb := 1;
  for b in basis do
    aRow := Sum([1..prEff],i->IntFFE(b[i])*gs[i]) mod 2;
    bRow := (IntFFE(b[1])*b1+IntFFE(b[2])*b2) mod 2;
    ca := ca*(1-aRow); cb := cb*(1-bRow);
  od;
  return ForAny(gs{[1..prEff]},g->ca*g=1) or cb*b1=1 or cb*b2=1;
end;;
prControlIds := [prZeroId];;
for prDim in [1,3] do
  Add(prControlIds,First([1..prCount],i->prDims[i]=prDim and ForAll(prBases[i],v->ForAll([prDim+1..prEff],j->v[j]=Zero(prField)))));
od;
prControlOut := "research/results/binary_paid_reference_rows_20261015/direct-controls.tsv";;
prControlStream := OutputTextFile(prControlOut,false);;
SetPrintFormattingStatus(prControlStream,false);
PrintTo(prControlStream,"state\tbasis_codes\tactual_old_supported_points\tfull_weighted_domain_columns\tdirect_rank\tdegree_block_rank\n");
for prI in prControlIds do
  prSelected := Filtered([1..Length(prFreePoints)],j->prRawError(prFreePoints[j],1,prBases[prI]));
  prDirectRank := prRank(prOldEvaluate{prSelected});
  prCheck(prDirectRank=prRanks[prI],"independent full old-domain cubic-input rank");
  PrintTo(prControlStream,prI,"\t",List(prBases[prI],prToInt),"\t",Length(prSelected),"\t",Length(prFullSupports),"\t",prDirectRank,"\t",prRanks[prI],"\n");
od;
CloseStream(prControlStream);
prBadPoint := Concatenation(List([1..prQ],i->0),List([1..prQ],i->1));;
prCheck(prRawError(prBadPoint,0,[]) and not ForAny(prBadPoint{[1..prQ]},x->x=1),"removing the weight breaks reference agreement");
prCheck(Length(prFullSupports)=prH,"all weighted-domain monomial columns retained");
prClassValues := List(prPoints,u->prRawValues(Concatenation(u,List([1..prQ],i->0)),1));;
prWeightedRankA := RankMat(List(prClassValues,g->prPacked(g{[1..prEff]})));;
prWeightedRankB := RankMat(List(prClassValues,g->prPacked([(g[1]+g[5]) mod 2,(g[2]+g[6]) mod 2])));;
prCheck(prWeightedRankA=prEff,"measured weighted high input classes");
prCheck(prWeightedRankB=2,"measured weighted mixed parent classes");
prExpectedAssertions := 10+prExpectedStates+2*prRows+1+Length(prControlIds)+4;;
if prAssertions<>prExpectedAssertions then Print("FAILED incomplete mathematical assertion count\n"); QUIT_GAP(1); fi;
prValidateTable := function(path,rows,columns)
  local stream,contents,lines;
  stream := InputTextFile(path); contents := ReadAll(stream); CloseStream(stream);
  lines := Filtered(SplitString(contents,"\n"),s->Length(s)>0);
  if Length(lines)<>rows or not ForAll(lines,s->Length(SplitString(s,"\t"))=columns) then
    Print("FAILED structured-output schema ",path,"\n"); QUIT_GAP(1);
  fi;
end;;
prValidateTable(prData,prExpectedStates+1,8);
prValidateTable(prControlOut,Length(prControlIds)+1,6);
prInputSizes := [prEff,2];;
Print("Fixture: old Boolean generators ",prV,"; companion coordinates ",Sum(prInputSizes),"; source coefficient positions ",Sum(prInputSizes)*prRows,"; seed dimension ",prSeedDim,"; effective dimension ",prEff,"\n");
Print("Code states ",prCount,"; reachable states ",Number(prCounts,c->c>0),"; complete original seed matrices ",Sum(prCounts),"\n");
Print("Original parameters: delta ",prDelta,"; K ",prK,"; h ",prRows,"; D ",prD,"; measured weighted input dimensions ",prWeightedRankA,",",prWeightedRankB,"\n");
Print("Initial H/joint rank ",prH,"/",prRanks[prZeroId],"; parent initial ranks ",prInitialA,",",prInitialB,"\n");
Print("Affine rate ",prEta,"; syntactic rate ",prSyntaxEta,"; mean ",prMean,"; paid bound ",prBound,"; coarse bound ",prCoarse,"; syntactic bound ",prSyntaxBound,"\n");
Print("Independent direct controls ",Length(prControlIds),"; full weighted-domain columns ",Length(prFullSupports),"; unweighted comparison control failed as expected\n");
Print("Structured tables validated: ",prExpectedStates+1," rows/8 columns and ",Length(prControlIds)+1," rows/6 columns\n");
Print("PASS exact shared-row mean, original-domain controls and complete mass; assertions ",prAssertions,"; expected ",prExpectedAssertions,"\n");
QUIT_GAP(0);
