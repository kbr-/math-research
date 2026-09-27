-- Finite homological test of minimal polynomial Ore generators, five roots.
-- Stages: reuse the certified rank-three core and monic order-ten operator;
-- compute its 3x10 marked presentation and minimal kernel; lift the connection
-- to that kernel; reduce modulo the parameter ideal and measure Jordan starts.
-- This tests the general Tor generator mechanism, not a larger dimension or
-- a new threshold row. Betti dimensions predict at least six Ore generators,
-- refuting generation by the two retained degree-ten controls.
S=QQ[c_2..c_5,Degrees=>{2,3,4,5}];
cubeClock=cpuTime();
cubeData=separate("\n",get "research/results/cube-block-ore-syzygies-20260927/marked-deflation-certificate.txt");
cubeReadAll=label->apply(select(cubeData,l->substring(0,#label,l)==label),
    l->sub(matrix value substring(#label,l),S));
cubeUs=cubeReadAll("CORE_OPERATOR_U=");assert(#cubeUs==2);
cubeH=last cubeUs;assert(cubeH_(10,0)==1);
cubeB=first cubeReadAll("CORE_MARK_OPERATOR_B2=");
cubeConnection=matrix{{0_S,0_S,-(21/8)*c_3},{1_S,0_S,-(23/20)*c_2},{0_S,1_S,0_S}};
cubeDeltaValues={3*c_3,4*c_4-6*c_2^2/5,5*c_5-4*c_2*c_3/5,-2*c_2*c_4/5};
cubeDelta=f->sum(toList(0..3),j->cubeDeltaValues#j*diff(S_j,f));
cubeDer=M->matrix apply(entries M,row->apply(row,f->cubeDelta f));
cubeColumns={submatrix(cubeB,{0,1,2},)};
for j from 1 to 10 do cubeColumns=append(cubeColumns,cubeDer(last cubeColumns)+cubeConnection*last cubeColumns);
cubePhi=map(S^{-4,-5,-6},S^(-toList(9..18)),entries fold((a,b)->a|b,take(cubeColumns,10)));
assert isHomogeneous cubePhi;
assert(fold((a,b)->a|b,cubeColumns)*submatrix(cubeH,toList(0..10),)==0);
cubeGamma=matrix table(10,10,(i,j)->if j==9 then -cubeH_(i,0) else if i==j+1 then 1_S else 0_S);
assert(entries(cubeDer(cubePhi)+cubeConnection*cubePhi)==entries(cubePhi*cubeGamma));
<< "MARKED_PRESENTATION=" << toString entries cubePhi << endl;
<< "SOURCE_CONNECTION=" << toString entries cubeGamma << endl;
cubeK=mingens kernel cubePhi;
cubeDegrees=apply(degrees source cubeK,first);
assert(cubeDegrees=={19,20,20,21,21,21,21,21,22,22,22,22,22,23,23,23,23});
assert(cubePhi*cubeK==0 and isHomogeneous cubeK);
<< "KERNEL_GENERATOR_DEGREES=" << cubeDegrees << endl;
<< "KERNEL_GENERATORS=" << toString entries cubeK << endl << flush;
cubeDK=map(target cubeK,S^(-apply(cubeDegrees,d->d+1)),entries(cubeDer(cubeK)+cubeGamma*cubeK));
assert isHomogeneous cubeDK;
-- Only complementary weights 0..5 occur. Expand those finite homogeneous
-- spaces over QQ instead of recomputing an unrestricted module Groebner basis.
cubeMonomials=d->if d<0 then {} else flatten entries basis(d,S);
cubeLiftColumns=apply(toList(0..16),j->matrix table(17,1,(i,k)->0_S));
for d from 20 to 24 do (
    wanted:=select(toList(0..16),j->cubeDegrees#j+1==d);
    candidates:=flatten apply(toList(0..16),i->apply(cubeMonomials(d-cubeDegrees#i),mon->{i,mon}));
    coords:=flatten apply(toList(0..9),i->apply(cubeMonomials(d-9-i),mon->{i,mon}));
    encode:=V->matrix table(#coords,numcols V,(i,j)->lift(coefficient((coords#i)#1,V_((coords#i)#0,j)),QQ));
    multipliers:=matrix table(17,#candidates,(i,j)->if i==(candidates#j)#0 then (candidates#j)#1 else 0_S);
    rationalA:=encode(cubeK*multipliers);
    rationalB:=encode(submatrix(cubeDK,,wanted));
    answer:=rationalB//rationalA;
    assert(rationalA*answer==rationalB);
    solved:=multipliers*sub(answer,S);
    cubeLiftColumns=apply(toList(0..16),j->if member(j,wanted) then submatrix(solved,,{position(wanted,i->i==j)}) else cubeLiftColumns#j);
    << "HOMOGENEOUS_SOLVE weight=" << d << " rows=" << #coords << " unknowns=" << #candidates << " rhs=" << #wanted << endl << flush;
);
cubeLift=fold((a,b)->a|b,cubeLiftColumns);
assert(entries(cubeK*cubeLift)==entries cubeDK);
assert(all(toList(0..16),i->all(toList(0..16),j->cubeLift_(i,j)==0 or
    first degree cubeLift_(i,j)==1+cubeDegrees#j-cubeDegrees#i)));
cubeAug=map(QQ,S,{0_QQ,0_QQ,0_QQ,0_QQ});
cubeTor=cubeAug cubeLift;
assert(cubeTor^5==0);
assert(all(toList(0..16),i->all(toList(0..16),j->cubeTor_(i,j)==0 or cubeDegrees#i==cubeDegrees#j+1)));
<< "SYZYGY_CONNECTION_LIFT=" << toString entries cubeLift << endl;
<< "TOR_DEGREE_ONE_ACTION=" << toString entries cubeTor << endl;
cubeStarts={};
for d from 19 to 23 do (
    rows:=select(toList(0..16),i->cubeDegrees#i==d);
    cols:=select(toList(0..16),i->cubeDegrees#i==d-1);
    rr:=if #cols==0 then 0 else rank submatrix(cubeTor,rows,cols);
    cubeStarts=append(cubeStarts,{d-9,#rows,rr,#rows-rr});
);
<< "CORE_STARTS_degree_dimension_incomingrank_generators=" << cubeStarts << endl;
<< "ADDITIONAL_MONIC_GENERATOR_degree=10" << endl;
<< "TOR_POWER_RANKS=" << apply(toList(0..5),j->rank(cubeTor^j)) << endl;
cubeSelected={};
for d from 19 to 23 do (
    rows:=select(toList(0..16),i->cubeDegrees#i==d);
    prev:=select(toList(0..16),i->cubeDegrees#i==d-1);
    incoming:=submatrix(cubeTor,rows,prev);
    for j in rows do (
        trial:=incoming|submatrix(id_(QQ^17),rows,{j});
        if rank trial>rank incoming then (
            incoming=trial;cubeSelected=append(cubeSelected,j);
        );
    );
    assert(rank incoming==#rows);
);
assert(#cubeSelected==5);
cubeSeeds=submatrix(id_(QQ^17),,cubeSelected);
cubeTorOrbit=fold((a,b)->a|b,apply(toList(0..4),j->cubeTor^j*cubeSeeds));
assert(rank cubeTorOrbit==17);
cubeMinimal=(submatrix(cubeK,,cubeSelected)||matrix table(1,5,(i,j)->0_S))|submatrix(cubeH,toList(0..10),);
assert(fold((a,b)->a|b,cubeColumns)*cubeMinimal==0);
cubeMinimalDegrees=apply(cubeSelected,j->cubeDegrees#j-9)|{10};
assert(sort cubeMinimalDegrees=={10,10,11,12,12,12});
assert(all(toList(0..5),j->all(toList(0..10),i->cubeMinimal_(i,j)==0 or first degree cubeMinimal_(i,j)==cubeMinimalDegrees#j-i)));
<< "SELECTED_SYZYGY_COLUMNS=" << cubeSelected << endl;
<< "MINIMAL_ORE_GENERATORS=" << toString entries cubeMinimal << endl;
<< "MINIMAL_ORE_GENERATOR_DEGREES=" << cubeMinimalDegrees << endl;
<< "MINIMAL_ORE_GENERATOR_ORDERS=" << apply(toList(0..5),j->max select(toList(0..10),i->cubeMinimal_(i,j)!=0)) << endl;
<< "PASS six generators vanish; five finite classes and their D-orbits span all17 Tor dimensions" << endl;
<< "PASS minimal kernel, exact lifted connection, homogeneous Tor action, nilpotence" << endl;
<< "CORE_TOR_ACTION_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;
