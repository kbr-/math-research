# Exact coefficient-kernel distribution via subspace-lattice Mobius inversion.
# Fixed complete test: all 67 W<=F2^2 tensor F2^2, all 0/1/2-row matrices,
# all kernel dimensions; same matrices test the full-row-rank version.
# Also compare the two existing 2-bit labelled-prefix controls.
# GAP native Subspaces/Basis/RankMat perform finite linear algebra.
# Full output destination is explicit; no parameter sweep or larger case.
countPath := "research/results/binary_legal_design_rows_20261009/count-checks.jsonl";;
countOut := OutputTextFile(countPath,false);;
SetPrintFormattingStatus(countOut,false);;
countField := GF(2);;
countZero := Zero(countField);;
countOne := One(countField);;
countMatrices := h -> List(Tuples([countZero,countOne],2*h),
    row -> List([1..h],j -> row{[2*j-1,2*j]}));;
countRank := function(rows)
    if Length(rows)=0 then return 0; fi;
    return RankMat(rows);
end;;
countBasis := space -> List(BasisVectors(Basis(space)),ShallowCopy);;
countSupport := function(rows,k,d)
    local columns,z,j;
    columns:=[];
    for z in rows do
        for j in [1..d] do
            Add(columns,List([1..k],i->z[(i-1)*d+j]));
        od;
    od;
    return countRank(columns);
end;;
countGaussian := function(n,j)
    local ans,i;
    if j<0 or j>n then return 0; fi;
    ans:=1;
    for i in [1..j] do ans:=ans*(2^(n-i+1)-1)/(2^i-1); od;
    return ans;
end;;
countAnnihilators := function(k,h,r,full)
    local ans,i;
    if not full then return 2^(h*(k-r)); fi;
    ans:=1;
    for i in [0..h-1] do ans:=ans*(2^(k-r)-2^i); od;
    return ans;
end;;
countPrediction := function(dim,k,h,children,full,wrong)
    local hist,Z,d,j,mu,number;
    hist:=List([0..dim],j->0);
    for Z in children do
        d:=Z.dim; number:=countAnnihilators(k,h,Z.support,full);
        for j in [0..d] do
            mu:=(-1)^(d-j);
            if not wrong then mu:=mu*2^Binomial(d-j,2); fi;
            hist[j+1]:=hist[j+1]+countGaussian(d,j)*mu*number;
        od;
    od;
    return hist;
end;;
countActual := function(rows,k,d,h)
    local hist,full,C,images,z,c,j;
    hist:=List([0..Length(rows)],j->0); full:=ShallowCopy(hist);
    for C in countMatrices(h) do
        images:=[];
        for z in rows do
            Add(images,Concatenation(List(C,c->
                List([1..d],j->Sum([1..k],i->c[i]*z[(i-1)*d+j])))));
        od;
        if h=0 then j:=Length(rows); else j:=Length(rows)-countRank(images); fi;
        hist[j+1]:=hist[j+1]+1;
        if countRank(C)=h then full[j+1]:=full[j+1]+1; fi;
    od;
    return [hist,full];
end;;
countAmbient := FullRowSpace(countField,4);;
countSpaces := List(Subspaces(countAmbient));;
Assert(0,Length(countSpaces)=67);
countData := List(countSpaces,space->rec(space:=space,rows:=countBasis(space),
    dim:=Dimension(space),support:=countSupport(countBasis(space),2,2)));;
countCells:=0;; countDraws:=0;; countContainments:=0;; countW:=fail;;
PrintTo(countOut,"{\"test\":\"all_binary_2_by_2_subspaces\",\"spaces\":67,\"matrix_draws_planned\":1407}\n");
for countIndex in [1..Length(countData)] do
    countW:=countData[countIndex];
    countChildren:=Filtered(countData,Z->ForAll(Z.rows,z->z in countW.space));
    countContainments:=countContainments+Length(countChildren);
    for countH in [0..2] do
        countAll:=countPrediction(countW.dim,2,countH,countChildren,false,false);
        countFull:=countPrediction(countW.dim,2,countH,countChildren,true,false);
        countSeen:=countActual(countW.rows,2,2,countH);
        Assert(0,countSeen=[countAll,countFull]);
        Assert(0,Sum(countAll)=2^(2*countH));
        Assert(0,ForAll(countAll,n->IsInt(n) and n>=0));
        Assert(0,ForAll(countFull,n->IsInt(n) and n>=0));
        countCells:=countCells+2*(countW.dim+1);
        countDraws:=countDraws+2^(2*countH);
        AppendTo(countOut,"{\"w\":",countIndex,",\"basis\":",
          List(countW.rows,row->List(row,IntFFE)),",\"h\":",countH,
          ",\"all\":",countAll,",\"full_rank\":",countFull,"}\n");
    od;
od;
# Complete W control: omitting the q-binomial Mobius factor gives a wrong count.
countAllChildren:=countData;;
countRight:=countPrediction(4,2,2,countAllChildren,false,false);;
countWrong:=countPrediction(4,2,2,countAllChildren,false,true);;
Assert(0,countRight[1]=6 and countWrong[1]<>6);
AppendTo(countOut,"{\"control\":\"omit_mobius_power\",\"right\":",countRight,
    ",\"wrong\":",countWrong,"}\n");
# Existing block-prefix gap at k=2: evaluate all functions on the four points.
countPoints:=[[countZero,countZero],[countOne,countZero],
              [countZero,countOne],[countOne,countOne]];;
for countKind in ["linear","nonlinear"] do
    countRows:=[];
    for countJ in [2..4] do
        countPoint:=countPoints[countJ];
        if countKind="linear" then countValue:=countPoint;
        else countValue:=[countOne,countPoint[2]]; fi;
        countVec:=List([1..8],i->countZero);
        countVec[countJ]:=countValue[1]; countVec[4+countJ]:=countValue[2];
        Add(countRows,countVec);
    od;
    countV:=Subspace(FullRowSpace(countField,8),countRows);
    countSubs:=List(Subspaces(countV));
    countChildren:=List(countSubs,space->rec(dim:=Dimension(space),
        support:=countSupport(countBasis(space),2,4)));
    countSeen:=countActual(countRows,2,4,1);
    countAll:=countPrediction(3,2,1,countChildren,false,false);
    countFull:=countPrediction(3,2,1,countChildren,true,false);
    Assert(0,countSeen=[countAll,countFull]);
    if countKind="linear" then Assert(0,countAll=[0,3,0,1]);
    else Assert(0,countAll=[1,1,1,1]); fi;
    countCells:=countCells+8; countDraws:=countDraws+4;
    AppendTo(countOut,"{\"control\":\"",countKind,"\",\"all\":",countAll,
        ",\"full_rank\":",countFull,"}\n");
od;
Assert(0,countDraws=1415 and countCells=1222);
AppendTo(countOut,"{\"status\":\"PASS\",\"matrix_draws\":",countDraws,
    ",\"histogram_cells\":",countCells,",\"subspace_containments\":",
    countContainments,",\"negative_controls\":1}\n");
Print("PASS: ",countDraws," matrix draws, ",countCells," exact histogram cells; ",
      "full result in ",countPath,"\n");
CloseStream(countOut);
QUIT_GAP(0);
