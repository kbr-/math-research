-- Review controls, reusing the complete five-root core and minimal generators.
-- Test 1: graded Jordan starts versus terminal (dark-state) degrees.
-- Test 2: minimum intermediate order needed to express the existing boundary
-- relation from six minimal total-degree generators. One fixed total degree18,
-- one exact rational coefficient matrix; no new threshold or larger dimension.
S=QQ[c_2..c_5,Degrees=>{2,3,4,5}];cubeClock=cpuTime();cubeWidth=19;
cubeData=separate("\n",get "research/results/cube-core-marked-annihilator-20260927/tor-action-certificate.txt");
cubeRead=label->(
    hit:=select(cubeData,l->substring(0,#label,l)==label);assert(#hit==1);
    sub(matrix value substring(#label,first hit),S)
);
cubePhi=cubeRead("MARKED_PRESENTATION=");
cubeG=cubeRead("MINIMAL_ORE_GENERATORS=");
cubeT=sub(cubeRead("TOR_DEGREE_ONE_ACTION="),QQ);
cubeTorDegrees={10,11,11,12,12,12,12,12,13,13,13,13,13,14,14,14,14};
cubeGrading={};
for d from 10 to 14 do (
    here:=select(toList(0..16),i->cubeTorDegrees#i==d);
    before:=select(toList(0..16),i->cubeTorDegrees#i==d-1);
    after:=select(toList(0..16),i->cubeTorDegrees#i==d+1);
    incoming:=if #before==0 then 0 else rank submatrix(cubeT,here,before);
    outgoing:=if #after==0 then 0 else rank submatrix(cubeT,after,here);
    cubeGrading=append(cubeGrading,{d,#here-incoming,#here-outgoing});
);
<< "DEGREE_start_versus_terminal=" << cubeGrading << endl;
assert(cubeGrading=={{10,1,0},{11,1,0},{12,3,0},{13,0,1},{14,0,4}});
cubeBdry=matrix table(4,1,(j,k)->(-1)^j*det submatrix(cubePhi,,select(toList(0..3),i->i!=j)));
assert(submatrix(cubePhi,,toList(0..3))*cubeBdry==0);
assert(cubeBdry_(3,0)!=0 and first degree cubeBdry_(3,0)==15);
assert(all(toList(0..3),j->cubeBdry_(j,0)==0 or first degree cubeBdry_(j,0)==18-j));
assert(first degree gcd flatten entries cubeBdry==0);
cubeTarget=cubeBdry||matrix table(15,1,(i,j)->0_S);
cubeG=cubeG||matrix table(8,6,(i,j)->0_S);
cubeGDegrees={10,11,12,12,12,10};
cubeGOrders=apply(toList(0..5),j->max select(toList(0..18),i->cubeG_(i,j)!=0));
assert(cubeGOrders=={8,9,9,9,9,10});
cubeDeltaValues={3*c_3,4*c_4-6*c_2^2/5,5*c_5-4*c_2*c_3/5,-2*c_2*c_4/5};
cubeDelta=f->sum(toList(0..3),j->cubeDeltaValues#j*diff(S_j,f));
cubeLeftD=P->matrix table(19,1,(i,j)->cubeDelta(P_(i,0))+(if i==0 then 0_S else P_(i-1,0)));
cubePowers=apply(toList(0..5),g->(
    ans:={submatrix(cubeG,,{g})};
    for j from 1 to 18-cubeGDegrees#g do ans=append(ans,cubeLeftD last ans);
    ans
));
cubeMons=d->if d<0 then {} else flatten entries basis(d,S);
cubeCandidates=flatten apply(toList(0..5),g->flatten apply(toList(0..18-cubeGDegrees#g),j->
    apply(cubeMons(18-cubeGDegrees#g-j),mon->{g,j,mon,cubeGOrders#g+j})));
cubeCoords=flatten apply(toList(0..18),i->apply(cubeMons(18-i),mon->{i,mon}));
cubeEncode=P->matrix table(#cubeCoords,numcols P,(i,j)->lift(coefficient((cubeCoords#i)#1,P_((cubeCoords#i)#0,j)),QQ));
cubeProducts=fold((a,b)->a|b,apply(cubeCandidates,c->c#2*(cubePowers#(c#0))#(c#1)));
cubeA=cubeEncode cubeProducts;cubeY=cubeEncode cubeTarget;
<< "BOUNDARY_OPERATOR=" << toString entries cubeBdry << endl;
<< "HOMOGENEOUS_SYSTEM rows=" << numrows cubeA << " candidates=" << numcols cubeA << endl << flush;
cubeFound=false;cubeBudget=-1;cubeUsed={};cubeSolution=matrix{{0_QQ}};
for t from 8 to 18 do if not cubeFound then (
    cols:=select(toList(0..#cubeCandidates-1),j->(cubeCandidates#j)#3<=t);
    restricted:=submatrix(cubeA,,cols);
    rr:=rank restricted;aug:=rank(restricted|cubeY);
    << "ORDER_BUDGET=" << t << " columns=" << #cols << " rank=" << rr << " augmented_rank=" << aug << endl << flush;
    if rr==aug then (
        cubeFound=true;cubeBudget=t;cubeUsed=cols;cubeSolution=cubeY//restricted;
        assert(restricted*cubeSolution==cubeY);
    );
);
assert cubeFound;
cubeMultipliers=matrix table(9,6,(j,g)->sum(toList(0..#cubeUsed-1),i->(
    c:=cubeCandidates#(cubeUsed#i);
    if c#0==g and c#1==j then c#2*(cubeSolution_(i,0))_S else 0_S
)));
cubeRebuilt=sum(toList(0..5),g->sum(toList(0..18-cubeGDegrees#g),j->cubeMultipliers_(j,g)*(cubePowers#g)#j));
assert(entries cubeRebuilt==entries cubeTarget);
assert(all(toList(0..5),g->all(toList(0..8),j->cubeMultipliers_(j,g)==0 or
    (first degree cubeMultipliers_(j,g)==18-cubeGDegrees#g-j and j+cubeGOrders#g<=cubeBudget))));
<< "POLYNOMIAL_MULTIPLIERS=" << toString entries cubeMultipliers << endl;
<< "MINIMUM_INTERMEDIATE_ORDER=" << cubeBudget << " BOUNDARY_ORDER=3 REES_SATURATION_EXPONENT=" << cubeBudget-3 << endl;
<< "PASS exact boundary identity; all smaller intermediate orders excluded by rational rank" << endl;
<< "CORE_REVIEW_CONTROLS_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;
