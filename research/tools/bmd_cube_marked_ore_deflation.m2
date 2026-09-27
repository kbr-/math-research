-- Audit exact polynomial marked deflation for the existing five-root blocks.
-- Two retained original controls: bounded total19/order17/topc2 and monic
-- total19/order19/top1. Predicted core operators: total10, orders8 and10.
-- Stages: read saved polynomial matrices, weighted monic Ore-module reduction,
-- verify both operator identities and the independent rank3 core action,
-- then detect omission of the feedback term in the original pair target.
S=QQ[c_2..c_5,Degrees=>{2,3,4,5}];
cubeClock=cpuTime();cubeWidth=18;
cubeCurved=separate("\n",get "research/results/cube-centered-curvature-recurrence-20260927/centered-block-certificate.txt");
cubeCoupled=separate("\n",get "research/results/cube-coupled-epd-elimination-20260927/minimum-normal-form-certificate.txt");
cubeRead=(data,label)->(
    hit:=select(data,l->substring(0,#label,l)==label);assert(#hit==1);
    sub(matrix value substring(#label,first hit),S)
);
cubeBoundary=cubeRead(cubeCurved,"BLOCK_BOUNDARY_COORDINATES=");
cubeT=cubeRead(cubeCurved,"DIVIDED_POWER_SOURCE_CHANGE=");
cubeW0=cubeRead(cubeCoupled,"ORIGINAL_CENTERED_RELATION=");
cubeW0=cubeW0||matrix{{0_S}};
cubeW1=cubeRead(cubeCurved,"MONIC_PAIR_ORDER17_LOWER_COEFFICIENTS=");
cubeW1=cubeW1||matrix{{1_S}};
cubeFactorials=apply(toList(0..17),j->(j!)_S);
cubeNormalChange=diagonalMatrix apply(cubeFactorials,f->1/f)*cubeT;
cubeControls={15!*cubeNormalChange*cubeW0,17!*cubeNormalChange*cubeW1};
cubeKappa=2*c_2/5;
cubeDeltaValues={3*c_3,4*c_4-3*cubeKappa*c_2,5*c_5-2*cubeKappa*c_3,-cubeKappa*c_4};
cubeDelta=f->sum(toList(0..3),j->cubeDeltaValues#j*diff(S_j,f));
cubeDer=M->matrix apply(entries M,row->apply(row,f->cubeDelta f));
cubeLeftD=M->cubeDer(M)+matrix table(cubeWidth,numcols M,(i,j)->if i==0 then 0_S else M_(i-1,j));
cubeOp=xs->matrix table(cubeWidth,1,(i,j)->if i<#xs then xs#i else 0_S);
cubeZeroOp=cubeOp({});
cubeUnitOp=j->cubeOp(apply(toList(0..j),i->if i==j then 1_S else 0_S));
cubeOrder=Q->if Q==0 then -1 else max select(toList(0..cubeWidth-1),i->Q_(i,0)!=0);
cubeL1=cubeUnitOp(7)-cubeOp(apply(toList(0..6),j->cubeBoundary_(j,0)));
cubeB2=cubeOp(apply(toList(0..2),j->cubeBoundary_(7+j,0)));
cubeC1=cubeOp(apply(toList(0..6),j->cubeBoundary_(j,1)));
cubeH3=cubeUnitOp(3)-cubeOp(apply(toList(0..2),j->cubeBoundary_(7+j,1)));
assert(cubeOrder(cubeB2)==2 and cubeOrder(cubeC1)==3);
cubeRels={cubeL1|(-cubeB2),(-cubeC1)|cubeH3};
cubeLengths={7,3};cubeHeadWeights={2,4};
cubeShifted=apply(toList(0..1),r->(
    ans:={cubeRels#r};
    for j from 1 to cubeWidth-cubeLengths#r-1 do ans=append(ans,cubeLeftD last ans);
    ans
));
cubeMultiply=(A,B)->(
    result:=cubeZeroOp; current:=B;
    for j from 0 to cubeOrder(A) do (
        result=result+A_(j,0)*current;
        current=cubeLeftD current;
    );result
);
cubeCoreConnection=matrix{{0_S,0_S,-(21/8)*c_3},{1_S,0_S,-(23/20)*c_2},{0_S,1_S,0_S}};
cubeCoreMark=submatrix(cubeB2,toList(0..2),);
cubeCoreIters={cubeCoreMark};
for j from 1 to 10 do cubeCoreIters=append(cubeCoreIters,cubeDer(last cubeCoreIters)+cubeCoreConnection*last cubeCoreIters);
cubeCorePowers=fold((A,B)->A|B,cubeCoreIters);
cubeActualWedge=cubeRead(cubeCurved,"CENTERED_WEDGE_CONNECTION=");
cubeActualHeads=cubeRead(cubeCurved,"BLOCK_HEADS=");
cubeActualIters={submatrix(cubeActualHeads,,{0})};
for j from 1 to 17 do cubeActualIters=append(cubeActualIters,cubeDer(last cubeActualIters)+cubeActualWedge*last cubeActualIters);
cubeActualPowers=fold((A,B)->A|B,cubeActualIters);
for control from 0 to 1 do (
    P:=cubeControls#control; work:=P|cubeZeroOp;
    multipliers:={cubeZeroOp,cubeZeroOp};steps:=0;
    while work!=0 do (
        choices:=flatten apply(toList(0..1),r->apply(select(toList(cubeLengths#r..17),j->work_(j,r)!=0),j->{cubeHeadWeights#r+j,r,j}));
        assert(#choices>0);
        pick:=last sort choices;r:=pick#1;j:=pick#2;
        f:=work_(j,r);shift:=j-cubeLengths#r;
        work=work-f*(cubeShifted#r)#shift;
        multipliers=apply(toList(0..1),s->if s==r then multipliers#s+f*cubeUnitOp(shift) else multipliers#s);
        steps=steps+1;assert(steps<100);
    );
    U:=multipliers#0;V:=multipliers#1;
    assert(cubeMultiply(U,cubeB2)==cubeMultiply(V,cubeH3));
    cubeRebuilt:=cubeMultiply(U,cubeL1)-cubeMultiply(V,cubeC1);
    << "RECONSTRUCTION_NONZERO_ROWS=" << select(toList(0..17),j->P_(j,0)!=cubeRebuilt_(j,0)) << endl;
    assert(entries P==entries cubeRebuilt);
    expectedOrder:=if control==0 then 8 else 10;
    assert(cubeOrder(U)==expectedOrder);
    assert(U_(expectedOrder,0)==(if control==0 then c_2 else 1_S));
    assert(all(toList(0..17),j->U_(j,0)==0 or first degree U_(j,0)==10-j));
    assert(all(toList(0..17),j->V_(j,0)==0 or first degree V_(j,0)==12-j));
    assert(all(toList(0..17),j->P_(j,0)==0 or first degree P_(j,0)==17-j));
    assert(cubeCorePowers*submatrix(U,toList(0..10),)==0);
    assert(cubeMultiply(V,cubeC1)!=0);
    assert(cubeActualPowers*P==0);
    assert(cubeActualPowers*cubeMultiply(V,cubeC1)!=0);
    << "CONTROL=" << control << " reduction_steps=" << steps << endl;
    << "CORE_OPERATOR_U=" << toString entries U << endl;
    << "FEEDBACK_MULTIPLIER_V=" << toString entries V << endl;
    << "ORIGINAL_PAIR_OPERATOR_P=" << toString entries P << endl;
    << "PASS UB2=VH3 and P=UL1-VC1; core total10/order" << expectedOrder
       << "; original total19/order" << expectedOrder+9 << endl << flush;
);
<< "FIRST_BLOCK_OPERATOR_L1=" << toString entries cubeL1 << endl;
<< "FEEDBACK_OPERATOR_C1=" << toString entries cubeC1 << endl;
<< "CORE_OPERATOR_H3=" << toString entries cubeH3 << endl;
<< "CORE_MARK_OPERATOR_B2=" << toString entries cubeB2 << endl;
<< "PASS both core actions vanish; feedback omission is nonzero in the original pair target" << endl;
<< "MARKED_DEFLATION_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;
