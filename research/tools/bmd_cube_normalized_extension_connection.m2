-- Exact test of conj:cube-normalized-extension-rigidity at the first new
-- cross-map case N=6, with the proved N=5 classification as encoding control.
-- Stages: polynomial normalization/Koszul matrices; lifted connections;
-- complete degree-zero cocycles and degree-one cross maps; exact QQ kernels.
-- No parameter point is substituted for the polynomial normalization ring.
-- Full stdout is retained with tools/save-run-output.py after the protected run.

for cubeN in {5,6} do (
    cubeClock:=cpuTime();
    cubeS:=QQ[c_2..c_cubeN,Degrees=>toList(2..cubeN)];
    cubeCS:=gens cubeS;
    cubeP:=QQ[v,s,c_2..c_cubeN,
        Degrees=>join({2,1},toList(2..cubeN)),
        MonomialOrder=>{Weights=>{2,1},Lex}];
    cubeV:=cubeP_0;cubeX:=cubeP_1;
    cubeCP:=drop(gens cubeP,2);
    cubeIntoP:=map(cubeP,cubeS,cubeCP);
    cubeIntoS:=map(cubeS,cubeP,join({0_cubeS,0_cubeS},cubeCS));
    cubeC:=join({1_cubeP,0_cubeP},cubeCP);
    cubeH:={1_cubeP,2*cubeX};
    for j from 2 to cubeN do cubeH=append(cubeH,
        ((j+1)*cubeX*cubeH#(j-1)-(j+2)*cubeV*cubeH#(j-2))/j);
    cubeE:=apply(toList(0..cubeN),j->sum(toList(0..j),i->(-1)^i*cubeC#i*cubeH#(j-i)));
    cubeI:=ideal(cubeE#(cubeN-3),cubeE#(cubeN-2));
    cubeG:=gb cubeI;
    cubeBasis:=if cubeN==5 then {1_cubeP,cubeX,cubeX^2}
        else {1_cubeP,cubeX,cubeX^2,cubeV,cubeX^3,cubeX^4};
    cubeRk:=#cubeBasis;
    cubeW0:=apply(cubeBasis,m->4+first degree m);
    cubeVec:=f->(
        nf:=f % cubeG;
        cc:=coefficients(nf,Variables=>{cubeV,cubeX},Monomials=>cubeBasis);
        assert(all(flatten entries((cc#0)*(cc#1)-matrix{{nf}}),a->a==0));
        ans:=cubeIntoS(cc#1);
        assert(all(flatten entries(cubeIntoP ans-(cc#1)),a->a==0));
        ans
    );
    assert(all(toList(0..cubeRk-1),i->entries(cubeVec(cubeBasis#i))==entries submatrix(id_(cubeS^cubeRk),,{i})));
    cubeLeft:=if cubeN==5 then 4*cubeCP#2-(cubeCP#0)^2+2*cubeCP#0*cubeX^2+15*cubeX^4
        else cubeE#(cubeN-1);
    cubeRight:=if cubeN==5 then 2*cubeCP#3+(cubeCP#0)^2*cubeX+6*cubeCP#0*cubeX^3+9*cubeX^5
        else cubeE#cubeN;
    cubeML:=fold((a,b)->a|b,apply(cubeBasis,m->cubeVec(cubeLeft*m)));
    cubeMR:=fold((a,b)->a|b,apply(cubeBasis,m->cubeVec(cubeRight*m)));
    cubeW1:=join(apply(cubeW0,d->d+cubeN-1),apply(cubeW0,d->d+cubeN));
    cubeW2:=apply(cubeW0,d->d+2*cubeN-1);
    cubeD1:=map(cubeS^(-cubeW0),cubeS^(-cubeW1),entries(cubeML|cubeMR));
    cubeD2:=map(cubeS^(-cubeW1),cubeS^(-cubeW2),entries((-cubeMR)||cubeML));
    assert(isHomogeneous cubeD1 and isHomogeneous cubeD2);
    assert(all(flatten entries(cubeD1*cubeD2),a->a==0));
    cubeKap:=2*cubeCS#0/cubeN;
    cubeDeltaValues:=apply(toList(2..cubeN),j->
        (if j<cubeN then (j+1)*cubeCS#(j-1) else 0_cubeS)-
        cubeKap*(cubeN-j+1)*(if j>2 then cubeCS#(j-3) else 0_cubeS));
    cubeDelta:=f->sum(toList(0..cubeN-2),j->cubeDeltaValues#j*diff(cubeS_j,f));
    cubeDer:=M->matrix apply(entries M,row->apply(row,f->cubeDelta f));
    cubeDeltaP:=f->sum(toList(0..cubeN-2),j->cubeIntoP(cubeDeltaValues#j)*diff(cubeCP#j,f))+
        (-cubeX^2+2*cubeV-2*cubeIntoP(cubeKap))*diff(cubeX,f)-
        cubeX*(cubeV+cubeIntoP(cubeKap))*diff(cubeV,f);
    cubeConn0:=fold((a,b)->a|b,apply(cubeBasis,m->cubeVec(cubeDeltaP(m)-(7/2)*cubeX*m)));
    cubeTarget:=cubeDer(cubeD1)+cubeConn0*cubeD1;
    cubeMonS:=d->if d<0 then {} else flatten entries basis(d,cubeS);
    cubeLiftCols:=apply(cubeW1,d->map(cubeS^(2*cubeRk),cubeS^1,0));
    for cubeWeight in sort unique apply(cubeW1,d->d+1) do (
        wanted:=select(toList(0..2*cubeRk-1),j->cubeW1#j+1==cubeWeight);
        candidates:=flatten apply(toList(0..2*cubeRk-1),i->apply(cubeMonS(cubeWeight-cubeW1#i),m->{i,m}));
        coords:=flatten apply(toList(0..cubeRk-1),i->apply(cubeMonS(cubeWeight-cubeW0#i),m->{i,m}));
        encode:=M->matrix table(#coords,numcols M,(i,j)->lift(coefficient((coords#i)#1,M_((coords#i)#0,j)),QQ));
        mult:=matrix table(2*cubeRk,#candidates,(i,j)->if i==(candidates#j)#0 then (candidates#j)#1 else 0_cubeS);
        aa:=encode(cubeD1*mult);bb:=encode(submatrix(cubeTarget,,wanted));
        xx:=bb//aa;
        assert(aa*xx==bb);
        solved:=mult*sub(xx,cubeS);
        cubeLiftCols=apply(toList(0..2*cubeRk-1),j->if member(j,wanted)
            then submatrix(solved,,{position(wanted,i->i==j)}) else cubeLiftCols#j);
    );
    cubeConn1:=fold((a,b)->a|b,cubeLiftCols);
    assert(all(flatten entries(cubeD1*cubeConn1-cubeTarget),a->a==0));
    assert(all(toList(0..2*cubeRk-1),i->all(toList(0..2*cubeRk-1),j->
        cubeConn1_(i,j)==0 or first degree cubeConn1_(i,j)==cubeW1#j+1-cubeW1#i)));
    cubeR:=if cubeN==5 then QQ[z] else QQ[b,c];
    cubeB:=if cubeN==5 then -2*cubeR_0 else cubeR_0;
    cubeCroot:=if cubeN==5 then 3*cubeR_0 else cubeR_1;
    cubeRoots:={cubeB,cubeB,cubeB,cubeCroot,cubeCroot};
    if cubeN==6 then cubeRoots=append(cubeRoots,-3*cubeB-2*cubeCroot);
    cubePoly:={1_cubeR};
    for root in cubeRoots do cubePoly=apply(toList(0..#cubePoly),i->
        (if i<#cubePoly then cubePoly#i else 0_cubeR)-root*(if i>0 then cubePoly#(i-1) else 0_cubeR));
    assert(cubePoly#1==0);
    cubeCVals:=apply(toList(2..cubeN),j->(-1)^j*cubePoly#j);
    cubeToR:=map(cubeR,cubeS,cubeCVals);
    cubeDrift:=if cubeN==5 then {-(cubeR_0)^2}
        else {-cubeB^2-cubeToR(cubeKap),-cubeCroot^2-cubeToR(cubeKap)};
    cubeDeltaR:=f->sum(toList(0..numgens cubeR-1),i->cubeDrift#i*diff(cubeR_i,f));
    assert(all(toList(0..cubeN-2),j->cubeDeltaR(cubeCVals#j)==cubeToR(cubeDeltaValues#j)));
    cubeDensity:=-(7/2)*cubeB-(cubeN+3/2)*cubeCroot;
    cubeD1R:=cubeToR cubeD1;cubeD2R:=cubeToR cubeD2;cubeConn1R:=cubeToR cubeConn1;
    cubeMonR:=d->if d<0 then {} else flatten entries basis(d,cubeR);
    cubeShift:=cubeN+3;
    cubePhiCoords:=flatten apply(toList(0..2*cubeRk-1),i->apply(cubeMonR(cubeW1#i-cubeShift),m->{i,m}));
    cubeUCords:=flatten apply(toList(0..cubeRk-1),i->apply(cubeMonR(cubeW0#i+1-cubeShift),m->{i,m}));
    cubeCocycleCoords:=flatten apply(toList(0..cubeRk-1),i->apply(cubeMonR(cubeW2#i-cubeShift),m->{i,m}));
    cubeConnCoords:=flatten apply(toList(0..2*cubeRk-1),i->apply(cubeMonR(cubeW1#i+1-cubeShift),m->{i,m}));
    cubeEncode:=(M,coords)->matrix table(#coords,1,(i,j)->lift(coefficient((coords#i)#1,M_(0,(coords#i)#0)),QQ));
    cubePhiBasis:=apply(cubePhiCoords,a->matrix{apply(toList(0..2*cubeRk-1),i->if i==a#0 then a#1 else 0_cubeR)});
    cubeUBasis:=apply(cubeUCords,a->matrix{apply(toList(0..cubeRk-1),i->if i==a#0 then a#1 else 0_cubeR)});
    cubeOb:=phi->matrix apply(entries phi,row->apply(row,f->cubeDeltaR(f)))+cubeDensity*phi-phi*cubeConn1R;
    cubeCocycle:=fold((a,b)->a|b,apply(cubePhiBasis,phi->cubeEncode(phi*cubeD2R,cubeCocycleCoords)));
    cubeObstruction:=fold((a,b)->a|b,apply(cubePhiBasis,phi->cubeEncode(cubeOb phi,cubeConnCoords)));
    cubeUMap:=if #cubeUBasis==0 then map(QQ^(#cubeConnCoords),QQ^0,0)
        else fold((a,b)->a|b,apply(cubeUBasis,u->cubeEncode(-u*cubeD1R,cubeConnCoords)));
    cubeJoint:=(cubeCocycle|map(QQ^(#cubeCocycleCoords),QQ^(#cubeUBasis),0))||
        (cubeObstruction|cubeUMap);
    cubeSolutions:=gens kernel cubeJoint;
    cubeProjected:=submatrix(cubeSolutions,toList(0..#cubePhiCoords-1),);
    cubeCompatible:=rank cubeProjected;
    assert(cubeCompatible>=1);
    assert(rank cubeSolutions-cubeCompatible==#cubeUBasis-rank cubeUMap);
    for j from 0 to numcols cubeSolutions-1 do (
        phi:=sum(toList(0..#cubePhiBasis-1),i->sub(cubeSolutions_(i,j),cubeR)*cubePhiBasis#i);
        uu:=if #cubeUBasis==0 then map(cubeR^1,cubeR^cubeRk,0)
            else sum(toList(0..#cubeUBasis-1),i->sub(cubeSolutions_(#cubePhiBasis+i,j),cubeR)*cubeUBasis#i);
        assert(all(flatten entries(phi*cubeD2R),a->a==0));
        assert(all(flatten entries(cubeOb(phi)-uu*cubeD1R),a->a==0));
    );
    if cubeN==5 then (
        assert(cubeW0=={4,5,6} and #cubePhiCoords==6 and #cubeUBasis==0);
        assert(rank cubeCocycle==1 and cubeCompatible==1);
        known:=transpose matrix{{1_QQ,-3/5,-17/5,-41/25,-3/25,71/25}};
        wrong:=transpose matrix{{1_QQ,1,1,0,0,0}};
        assert(cubeJoint*known==0);
        assert(cubeCocycle*wrong==0 and cubeObstruction*wrong!=0);
        phi:=sum(toList(0..5),i->sub(known_(i,0),cubeR)*cubePhiBasis#i);
        assert(cubeOb(phi)+cubeR_0*phi!=0);
    );
    if cubeN==6 then assert(#cubePhiCoords==42 and #cubeCocycleCoords==54 and #cubeUBasis==1);
    << "N=" << cubeN << " BASIS=" << toString cubeBasis << endl;
    << "COVER_WEIGHTS=" << cubeW0 << " RELATION_WEIGHTS=" << cubeW1 << " SECOND_WEIGHTS=" << cubeW2 << endl;
    << "D1=" << toString entries cubeD1 << endl;
    << "D2=" << toString entries cubeD2 << endl;
    << "COVER_CONNECTION=" << toString entries cubeConn0 << endl;
    << "RELATION_CONNECTION=" << toString entries cubeConn1 << endl;
    << "LOWER_COEFFICIENT_MAP=" << toString cubeCVals << " DRIFT=" << toString cubeDrift << " DENSITY=" << toString cubeDensity << endl;
    << "PHI_COORDINATES=" << toString cubePhiCoords << " CROSS_COORDINATES=" << toString cubeUCords << endl;
    << "COCYCLE_MATRIX=" << toString entries cubeCocycle << endl;
    << "COMPATIBILITY_MATRIX=" << toString entries cubeObstruction << endl;
    << "CROSS_MATRIX=" << toString entries cubeUMap << endl;
    << "JOINT_KERNEL=" << toString entries cubeSolutions << endl;
    << "RESULT N=" << cubeN << " cochains=" << #cubePhiCoords << " ext0=" << #cubePhiCoords-rank cubeCocycle
        << " cross=" << #cubeUBasis << " compatible=" << cubeCompatible
        << " noCross=" << #cubePhiCoords-rank(cubeCocycle||cubeObstruction)
        << " connectionFreedom=" << #cubeUBasis-rank cubeUMap << endl;
    << "PASS exact normalization, Koszul, lifted connection, homogeneous coordinates, full polynomial residuals; cpu=" << cpuTime()-cubeClock << endl << flush;
);
exit 0;
