-- Shared exact polynomial source for the sixfold kernel test and its N5 control.
-- No closure, rank, or endpoint is assumed. Every used recurrence and the
-- polynomial feedback after constant-pivot elimination is checked entrywise.
bmdBuildKernelSource=(srcN,srcCap)->(
    assert(member(srcN,{5,6}) and srcCap>=2*srcN-2 and srcCap<=60);
    srcS:=QQ[c_2..c_srcN,Degrees=>toList(2..srcN)];
    srcC:=gens srcS;
    srcPairs:=subsets(toList(0..srcN-1),2);
    srcPW:=apply(srcPairs,p->sum p+1);
    srcR:=#srcPairs;
    srcPowers:=apply(toList(0..srcN-1),j->submatrix(id_(srcS^srcN),,{j}));
    for j from srcN to srcCap+1 do srcPowers=append(srcPowers,
        sum(toList(2..srcN),i->(-1)^(i+1)*srcC#(i-2)*srcPowers#(j-i)));
    srcGamma:={1_QQ};
    for j from 1 to srcCap do srcGamma=append(srcGamma,last(srcGamma)*(-3/2-j+1)/j);
    srcCols:=apply(toList(0..srcCap),j->matrix table(srcR,1,(r,col)->(
        ab:=srcPairs#r;
        sum(toList(0..j),i->srcGamma#i*srcGamma#(j-i)*
            ((srcPowers#i)_(ab#0,0)*(srcPowers#(j-i+1))_(ab#1,0)
             -(srcPowers#i)_(ab#1,0)*(srcPowers#(j-i+1))_(ab#0,0)))
    )));
    srcKap:=2*srcC#0/srcN;
    srcDrift:=apply(toList(2..srcN),j->
        (if j<srcN then (j+1)*srcC#(j-1) else 0_srcS)
        -srcKap*(srcN-j+1)*(if j>2 then srcC#(j-3) else 0_srcS));
    srcDelta:=f->sum(toList(0..srcN-2),j->srcDrift#j*diff(srcC#j,f));
    srcDer:=mat->matrix apply(entries mat,row->apply(row,f->srcDelta f));
    srcRoot:=fold((a,b)->a|b,apply(toList(0..srcN-1),j->
        -(j+1/2)*srcPowers#(j+1)
        -(if j>0 then j*srcKap*srcPowers#(j-1) else map(srcS^srcN,srcS^1,0))));
    srcConn:=matrix table(srcR,srcR,(r,col)->(
        ab:=srcPairs#r;uv:=srcPairs#col;
        (if ab#1==uv#1 then srcRoot_(ab#0,uv#0) else 0_srcS)
        -(if ab#0==uv#1 then srcRoot_(ab#1,uv#0) else 0_srcS)
        +(if ab#0==uv#0 then srcRoot_(ab#1,uv#1) else 0_srcS)
        -(if ab#1==uv#0 then srcRoot_(ab#0,uv#1) else 0_srcS)
    ));
    for j from 0 to srcCap-1 do (
        rhs:=(j+1)*srcCols#(j+1);
        if j>0 then rhs=rhs+srcKap*(j+2)*srcCols#(j-1);
        lhs:=srcDer(srcCols#j)+srcConn*srcCols#j;
        if entries lhs!=entries rhs then (
            << "RECURRENCE_FAILURE N=" << srcN << " order=" << j
               << " difference=" << toString entries(lhs-rhs) << endl << flush;
        );
        assert(entries lhs==entries rhs);
    );
    srcPivPairs:=apply(toList(1..srcN-1),j->{0,j})|
        apply(toList(1..srcN-2),j->{j,srcN-1});
    srcPiv:=apply(srcPivPairs,p->position(srcPairs,q->p==q));
    srcRest:=select(toList(0..srcR-1),i->not member(i,srcPiv));
    srcSplit:=2*srcN-3;srcQ:=#srcRest;
    srcAll:=fold((a,b)->a|b,srcCols);
    srcOld:=submatrix(srcAll,,toList(0..srcSplit-1));
    srcPivot:=submatrix(srcOld,srcPiv,);
    srcDet:=det srcPivot;
    assert(srcDet!=0 and degree srcDet=={0});
    srcInv:=inverse srcPivot;
    assert(srcPivot*srcInv==id_(target srcPivot));
    srcProj:=submatrix(id_(srcS^srcR),srcRest,)
        -submatrix(srcOld,srcRest,)*srcInv*submatrix(id_(srcS^srcR),srcPiv,);
    assert(srcProj*srcOld==0);
    srcCW:=apply(srcRest,i->srcPW#i);
    assert(srcCW==(if srcN==5 then {4,5,6} else {4,5,6,6,7,8}));
    srcF:=srcS^(-srcCW);

    srcEmb:=submatrix(id_(srcS^srcR),,srcRest);
    srcCoreConnection:=srcProj*srcConn*srcEmb;
    for i from 0 to srcQ-1 do for j from 0 to srcQ-1 do
        assert(srcCoreConnection_(i,j)==0 or
            first degree srcCoreConnection_(i,j)==srcCW#j+1-srcCW#i);
    srcCoreCols:=apply(srcCols,g->srcProj*g);
    srcOldDerivative:=srcProj*(srcDer(srcOld)+srcConn*srcOld);
    assert(submatrix(srcOldDerivative,,toList(0..srcSplit-2))==0);
    assert(entries(submatrix(srcOldDerivative,,{srcSplit-1}))==
        entries(srcSplit*srcCoreCols#srcSplit));
    for j from srcSplit to srcCap-1 do (
        coords:=srcInv*submatrix(srcCols#j,srcPiv,);
        rhs:=(j+1)*srcCoreCols#(j+1)+srcKap*(j+2)*srcCoreCols#(j-1)
            -srcSplit*coords_(srcSplit-1,0)*srcCoreCols#srcSplit;
        assert(entries(srcDer(srcCoreCols#j)+srcCoreConnection*srcCoreCols#j)==entries rhs);
    );
    new HashTable from {
        "ring"=>srcS,"coefficients"=>srcC,"pairWeights"=>srcPW,"pairs"=>srcPairs,
        "pairColumns"=>srcCols,"pairConnection"=>srcConn,"delta"=>srcDelta,
        "projection"=>srcProj,"weights"=>srcCW,"module"=>srcF,
        "columns"=>srcCoreCols,"connection"=>srcCoreConnection,"split"=>srcSplit
    }
);
