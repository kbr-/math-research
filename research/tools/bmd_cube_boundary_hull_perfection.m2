-- Decide the free-cyclic-hull hypothesis through the boundary-coordinate ideal.
-- For n4, all d>=2 in characteristic zero, the proved boundary gcd and collision
-- Smith theorems identify the boundary-column hull with the full cyclic hull.
-- For a primitive boundary column G, the hull is free iff B/ideal(G) has
-- projective dimension two (or ideal(G)=B). A minimal third syzygy refutes it.
-- Reuse the complete stored kernels; test n3,d2 as the known free control and
-- n4,d2 as the first unresolved case. No new threshold row is computed.
-- Stages: extract the unique boundary vector, minimize its scalar ideal,
-- compute its resolution, assert homogeneity/minimality and zero compositions,
-- and retain the full boundary vector and every resolution differential.
for cubeN in {3,4} do (
    cubeR:=if cubeN==3 then 8 else 12;
    cubeU:=if cubeN==3 then 9 else 19;
    B:=QQ[e_1..e_cubeN,Degrees=>toList(1..cubeN)];
    fileName:=if cubeN==3 then "bounded-control-n3-qq.txt" else "bounded-row-n4-qq.txt";
    lines:=separate("\n",get("research/results/cube-operator-global-degree-review-20260927/"|fileName));
    key:="KERNEL_GROEBNER_MATRIX=";
    hits:=select(lines,l->substring(0,#key,l)==key);
    assert(#hits==1);
    allG:=matrix apply(value substring(#key,hits#0),row->apply(row,f->sub(f,B)));
    wanted:=select(toList(0..numcols allG-1),j->all(toList(cubeR+1..cubeU-1),i->allG_(i,j)==0));
    assert(#wanted==1);
    G:=submatrix(allG,toList(0..cubeR),wanted);
    gcdG:=fold((a,b)->gcd(a,b),flatten entries G);
    assert(first degree gcdG==0);
    I:=ideal G;
    << "BOUNDARY n=" << cubeN << " coordinates=" << numrows G << " topdegree=" << degree G_(cubeR,0) << endl << flush;
    << "BOUNDARY_VECTOR=" << toString entries G << endl << flush;
    clock:=cpuTime();
    minI:=mingens I;
    << "MINIMAL_IDEAL n=" << cubeN << " generators=" << numcols minI << " degrees=" << degrees source minI << " cpu=" << cpuTime()-clock << endl << flush;
    << "MINIMAL_IDEAL_MATRIX=" << toString entries minI << endl << flush;
    C:=res coker minI;
    << "RESOLUTION n=" << cubeN << " length=" << length C << " cpu=" << cpuTime()-clock << endl << flush;
    << "BETTI=" << betti C << endl << flush;
    for j from 1 to length C do (
        mat:=C.dd_j;
        assert isHomogeneous mat;
        assert all(flatten entries mat,f->f==0 or first degree f>0);
        if j>1 then assert(C.dd_(j-1)*mat==0);
        << "DIFFERENTIAL n=" << cubeN << " index=" << j << " source_degrees=" << degrees source mat << " target_degrees=" << degrees target mat << endl;
        << "MATRIX=" << toString entries mat << endl << flush;
    );
    assert(length C>=2);
    if length C==2 then (
        syzMat:=C.dd_2;
        assert(numrows syzMat==numcols syzMat+1);
        assert(minors(numcols syzMat,syzMat)==I);
        assert(ideal minI==I);
        totalDegree:=cubeR+first degree G_(cubeR,0);
        removed:=apply(flatten degrees source C.dd_1,a->totalDegree-a);
        added:=apply(flatten degrees source C.dd_2,b->totalDegree-b);
        assert(#unique removed==#removed and all(removed,c->0<=c and c<=cubeR));
        hullWeights:=sort(join(select(toList(0..cubeR),c->not member(c,removed)),added));
        assert(#hullWeights==cubeR);
        << "HULL_WEIGHTS=" << hullWeights << endl;
        << "PASS independent Hilbert-Burch maximal-minor equality and weighted Hilbert numerator" << endl;
    );
    if cubeN==3 then (
        assert(I==ideal(e_1^3-4*e_1*e_2+8*e_3,(e_1^2-4*e_2)^2));
        assert(length C==2);
        << "PASS known doubled ideal with free hull" << endl;
    );
    << "HULL_FREE n=" << cubeN << " result=" << (length C==2) << endl << flush;
);
exit 0;
