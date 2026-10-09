# Fixed minimal test exceeding two scalar rows for a quadratic relation: r=3.
# All matrices with h=0,1,2 on six bits: 4161 draws. One canonical h=3 witness.
# Precompute row zero sets once; use GAP native field products, blists and ranks.
quadPath:="research/results/binary_quadratic_critical_20261009/quadric-checks.jsonl";;
quadOut:=OutputTextFile(quadPath,false);;
SetPrintFormattingStatus(quadOut,false);;
quadField:=GF(2);; quadZero:=Zero(quadField);; quadOne:=One(quadField);;
quadR:=3;; quadN:=2*quadR;;
quadPoints:=Tuples([quadZero,quadOne],quadN);;
quadValue:=p->Sum([1..quadR],i->p[2*i-1]*p[2*i]);;
quadOmega:=Filtered(quadPoints,p->quadValue(p)=quadOne);;
Assert(0,Length(quadOmega)=28);
quadRows:=quadPoints;;
quadZeros:=List(quadRows,c->BlistList([1..Length(quadOmega)],
    Filtered([1..Length(quadOmega)],j->c*quadOmega[j]=quadZero)));;
quadMask:=function(indices)
    local mask,i;
    mask:=BlistList([1..Length(quadOmega)],[1..Length(quadOmega)]);
    for i in indices do mask:=IntersectionBlist(mask,quadZeros[i]); od;
    return mask;
end;;
Assert(0,quadMask([2])=quadZeros[2]);;
quadRank:=function(rows)
    if Length(rows)=0 then return 0; fi;
    return RankMat(rows);
end;;
quadPolar:=NullMat(quadN,quadN,quadField);;
for quadI in [1..quadR] do
    quadPolar[2*quadI-1][2*quadI]:=quadOne;
    quadPolar[2*quadI][2*quadI-1]:=quadOne;
od;
Assert(0,RankMat(quadPolar)=quadN);
quadDraws:=0;; quadPointChecks:=0;; quadMinima:=[];;
PrintTo(quadOut,"{\"r\":3,\"bits\":6,\"omega\":28,\"planned_exhaustive_draws\":4161}\n");
for quadH in [0..2] do
    quadHistogram:=List([0..28],i->0);
    for quadIndices in Tuples([1..Length(quadRows)],quadH) do
        quadC:=List(quadIndices,i->quadRows[i]);
        quadJ:=quadRank(quadC);
        quadError:=SizeBlist(quadMask(quadIndices));
        quadBias:=2^(quadN-quadJ)-2*quadError;
        Assert(0,AbsInt(quadBias)<=2^quadR);
        Assert(0,quadError>=2^(2*quadR-quadH-1)-2^(quadR-1));
        quadHistogram[quadError+1]:=quadHistogram[quadError+1]+1;
        quadDraws:=quadDraws+1;
        AppendTo(quadOut,"{\"h\":",quadH,",\"row_indices\":",quadIndices,
            ",\"rank\":",quadJ,",\"residual\":",quadError,",\"bias\":",quadBias,"}\n");
    od;
    quadMinimum:=PositionProperty(quadHistogram,n->n>0)-1;
    Assert(0,quadMinimum=2^(2*quadR-quadH-1)-2^(quadR-1));
    Add(quadMinima,quadMinimum);
    AppendTo(quadOut,"{\"h\":",quadH,",\"histogram\":",quadHistogram,
        ",\"minimum\":",quadMinimum,"}\n");
od;
quadCanonical:=[];
for quadI in [1..quadR] do
    quadVector:=List([1..quadN],i->quadZero);
    quadVector[2*quadI-1]:=quadOne;
    Add(quadCanonical,Position(quadRows,quadVector));
od;
Assert(0,SizeBlist(quadMask(quadCanonical))=0);
quadDraws:=quadDraws+1;
AppendTo(quadOut,"{\"canonical_h\":3,\"row_indices\":",quadCanonical,",\"residual\":0}\n");
quadWeightedSupport:=0;; quadRepairSupport:=0;;
for quadP in quadPoints do
    quadWeight:=quadValue(quadP);
    quadBeta:=List([1..quadN],i->quadZero);
    for quadI in [1..quadR] do quadBeta[2*quadI-1]:=quadP[2*quadI]; od;
    quadRow:=quadBeta*quadP;
    Assert(0,quadRow=quadWeight);
    if quadWeight<>quadZero then quadWeightedSupport:=quadWeightedSupport+1; fi;
    if quadWeight*quadP[1]<>quadZero then quadRepairSupport:=quadRepairSupport+1; fi;
    for quadI in [1..quadN] do
        Assert(0,quadWeight*quadP[quadI]*(quadOne+quadRow)=quadZero);
        Assert(0,quadWeight*(quadBeta[quadI]^2+quadBeta[quadI])=quadZero);
        Assert(0,quadWeight*quadP[1]*quadP[quadI]*(quadOne+quadP[1])=quadZero);
        quadPointChecks:=quadPointChecks+3;
    od;
od;
quadWitness:=List([1..quadN],i->quadZero);; quadWitness[1]:=quadOne;;
Assert(0,quadWitness[1]*(quadOne+quadValue(quadWitness))=quadOne);
Assert(0,quadDraws=4162 and quadPointChecks=1152);
Assert(0,quadWeightedSupport=28 and quadRepairSupport=16);
AppendTo(quadOut,"{\"status\":\"PASS\",\"matrix_draws\":",quadDraws,
    ",\"exhaustive_h_minima\":",quadMinima,",\"point_identities\":",quadPointChecks,
    ",\"weight_support\":",quadWeightedSupport,",\"repair_support\":",
    quadRepairSupport,",\"omitted_weight_negative_controls\":1}\n");
CloseStream(quadOut);
Print("PASS: 4162 matrix draws, 1152 point identities; ",quadPath,"\n");
QUIT_GAP(0);
