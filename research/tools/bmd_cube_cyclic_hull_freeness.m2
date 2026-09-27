-- Test the all-parameter free-cyclic-hull hypothesis on the first unresolved
-- dimension, n4,d2, with the exact n3,d2 hull as a control. Rebuild the already certified bounded column matrices; monic cutoffs9 and19 ensure these present the
-- entire cyclic images. Weighted double duals and MINIMAL presentations test
-- freeness, not numerical ranks at a generic parameter point.
-- Stages: rebuild each bounded column matrix, construct its graded image, dualize
-- twice, minimize, and retain all generators/relations and the Betti table.
for cubeN in {3,4} do (
    cubeU:=if cubeN==3 then 9 else 19;
    B:=QQ[e_1..e_cubeN,Degrees=>toList(1..cubeN)];
    BT:=B[T];
    Z:=matrix table(cubeN,cubeN,(i,j)->if j<cubeN-1 then (if i==j+1 then 1_B else 0_B) else (-1)^(cubeN-i+1)*B_(cubeN-i-1));
    coeffM:=(M,j)->matrix apply(entries M,row->apply(row,v->sub(coefficient(T^j,v),B)));
    blocks:=new MutableHashTable; weights:=new MutableHashTable;
    for s from 0 to 2 do (
        inds:=subsets(cubeN,s); rs:=#inds;
        Cs:=exteriorPower(s,id_(BT^cubeN)+T*sub(Z,BT));
        hs:={id_(B^rs)};
        for j from 1 to cubeU-1 do hs=append(hs,(coeffM(Cs,j)-sum(toList(1..j-1),i->hs#i*hs#(j-i)))/2);
        blocks#s=hs; weights#s=apply(inds,I->sum I-s*(s-1)//2);
    );
    rowData:=flatten apply(toList(0..1),q->flatten apply(toList(0..min(cubeN,2-2*q)),s->
        apply(toList(0..binomial(cubeN,s)-1),j->(q,s,j,(weights#s)#j))));
    rawPhi:=matrix apply(rowData,rw->apply(toList(0..cubeU-1),c->if c<rw#0 then 0_B else ((blocks#(rw#1))#(c-rw#0))_(rw#2,0)));
    phi:=map(B^(apply(rowData,rw->-rw#0-rw#3)),B^(apply(toList(0..cubeU-1),c->-c)),rawPhi);
    assert isHomogeneous phi;
    << "START n=" << cubeN << " U=" << cubeU << " matrix=" << numrows phi << "x" << numcols phi << endl << flush;
    N:=image phi;
    clock:=cpuTime();
    << "IMAGE_PRESENTATION n=" << cubeN << " dimensions=" << numrows presentation N << "x" << numcols presentation N << endl << flush;
    Ndual:=dual N;
    << "FIRST_DUAL n=" << cubeN << " cpu=" << cpuTime()-clock << " generators=" << numgens Ndual << endl << flush;
    Hull:=dual Ndual;
    H:=prune Hull;
    HP:=presentation H;
    << "HULL n=" << cubeN << " rank=" << rank H << " generators=" << numgens H << " relations=" << numcols HP << " cpu=" << cpuTime()-clock << endl << flush;
    << "HULL_GENERATOR_DEGREES=" << toString degrees H << endl;
    << "HULL_RELATION_DEGREES=" << toString degrees source HP << endl;
    << "HULL_PRESENTATION=" << toString entries HP << endl << flush;
    << "HULL_BETTI=" << betti res H << endl << flush;
    assert(rank H==(if cubeN==3 then 8 else 12));
    if cubeN==3 then (
        assert(numcols HP==0);
        assert(sort flatten degrees H=={0,1,2,3,4,4,5,6});
        << "PASS known n3 free hull with exact shifts" << endl;
    );
    << "FREENESS_RESULT n=" << cubeN << " free=" << (numcols HP==0) << endl << flush;
);
exit 0;
