-- Construct the embedded n4,d2 free cyclic hull from its four-generator boundary
-- ideal, not by a full double dual. Also test the proposed differential-jet
-- generation of that ideal from the top boundary equation. Reuse exact stored G.
-- Stages: top-coordinate ideal equality and derivative comparison; unimodular
-- elimination plus Hilbert-Burch transpose; polynomial embedded frame; covariance,
-- grading, distinguished vector and all divided iterates through order13.
needsPackage "Elimination";
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}]; BT=B[T];
cubePlain=M->map(B^(numrows M),B^(numcols M),M);
cubeLines=separate("\n",get "research/results/cube-four-reflexive-hull-test-20260927/boundary-perfection.txt");
cubeKey="BOUNDARY_VECTOR=";
cubeHits=select(cubeLines,l->substring(0,#cubeKey,l)==cubeKey);
assert(#cubeHits==2);
cubeG=cubePlain matrix apply(value substring(#cubeKey,cubeHits#1),row->apply(row,f->sub(f,B)));
assert(numrows cubeG==13);
cubeIdeal=ideal cubeG;
cubeHrow=cubePlain transpose submatrix(cubeG,toList(9..12),);
assert(ideal cubeHrow==cubeIdeal);
cubeDeltaValues={2*e_2-e_1^2,3*e_3-e_1*e_2,4*e_4-e_1*e_3,-e_1*e_4};
cubeDelta=f->sum(toList(0..3),j->diff(B_j,f)*cubeDeltaValues#j);
cubeDeltaMatrix=M->cubePlain matrix apply(entries M,row->apply(row,cubeDelta));
cubeF=cubeG_(12,0);
assert(12*cubeG_(11,0)==-cubeDelta(cubeF)+18*e_1*cubeF);
cubeDerivs={cubeF};
for j from 1 to 3 do cubeDerivs=append(cubeDerivs,cubeDelta last cubeDerivs);
cubeJetIdeal=ideal cubeDerivs;
<< "DERIVATIVE_IDEAL_EQUALS_BOUNDARY=" << (cubeJetIdeal==cubeIdeal) << endl;
<< "DERIVATIVE_MEMBERSHIP=" << apply(cubeDerivs,f->f % cubeIdeal==0) << endl;
<< "SECOND_DERIVATIVE_REMAINDER=" << toString(cubeDerivs#2 % cubeIdeal) << endl << flush;
cubeLift=(transpose submatrix(cubeG,toList(0..8),))//cubeHrow;
assert(cubeHrow*cubeLift==transpose submatrix(cubeG,toList(0..8),));
cubeTmut=mutableMatrix id_(B^13);
for j from 0 to 8 do for i from 0 to 3 do cubeTmut_(j,9+i)=-cubeLift_(i,j);
cubeTransform=matrix cubeTmut;
cubeInverse=2*id_(B^13)-cubeTransform;
assert(cubeTransform*cubeInverse==id_(B^13));
assert(cubeTransform*cubeG==(map(B^9,B^1,0)||transpose cubeHrow));
cubeHgraded=map(B^1,,cubeHrow);
cubeS=mingens kernel cubeHgraded;
assert(numcols cubeS==3 and cubeHgraded*cubeS==0 and minors(3,cubeS)==cubeIdeal);
cubeExtraWeights=apply(flatten degrees source cubeS,b->27-b);
cubeW=cubePlain transpose cubeS;
cubeZ=matrix table(4,4,(i,j)->if j<3 then (if i==j+1 then 1_B else 0_B) else (-1)^(5-i)*B_(3-i));
cubeBzero=-cubeZ*diagonalMatrix{0_B,1_B,2_B,3_B};
cubeCoeff=(M,j)->matrix apply(entries M,row->apply(row,f->sub(coefficient(T^j,f),B)));
cubeHs=new MutableHashTable; cubeWeights=new MutableHashTable; cubeMs=new MutableHashTable;
for s from 0 to 2 do (
    inds:=subsets(4,s); rs:=#inds;
    cs:=exteriorPower(s,id_(BT^4)+T*sub(cubeZ,BT));
    ds:=exteriorPower(s,id_(BT^4)+T*sub(cubeBzero,BT));
    hs:={id_(B^rs)};
    for j from 1 to 13 do hs=append(hs,(cubeCoeff(cs,j)-sum(toList(1..j-1),i->hs#i*hs#(j-i)))/2);
    cubeHs#s=hs; cubeWeights#s=apply(inds,I->sum I-s*(s-1)//2);
    cubeMs#s=cubeCoeff(ds,1)+(s-1/2)*cubeCoeff(cs,1);
);
cubeRows=flatten apply(toList(0..1),q->flatten apply(toList(0..2-2*q),s->
    apply(toList(0..binomial(4,s)-1),j->(q,s,j,(cubeWeights#s)#j))));
cubeAll=cubePlain matrix apply(cubeRows,rw->apply(toList(0..13),c->if c<rw#0 then 0_B else ((cubeHs#(rw#1))#(c-rw#0))_(rw#2,0)));
cubePhi=submatrix(cubeAll,,toList(0..12));
assert(cubePhi*cubeG==0);
cubeChanged=cubePhi*cubeInverse;
<< "SOLVE_POLYNOMIAL_FRAME 12x3 from4 boundary columns" << endl << flush;
cubeEta=cubePlain transpose((transpose submatrix(cubeChanged,,toList(9..12)))//(transpose cubeW));
assert(cubeEta*cubeW==submatrix(cubeChanged,,toList(9..12)));
cubeHull=submatrix(cubeChanged,,toList(0..8))|cubeEta;
cubeHullWeights=toList(0..8)|cubeExtraWeights;
cubeRowWeights=apply(cubeRows,rw->rw#0+rw#3);
for i from 0 to 11 do for j from 0 to 11 do if cubeHull_(i,j)!=0 then
    assert(first degree cubeHull_(i,j)==cubeHullWeights#j-cubeRowWeights#i);
cubeBZ=B[z]; cubeP=z^4-e_1*z^3+e_2*z^2-e_3*z+e_4;
cubeDisc=sub(discriminant(cubeP,z),B);
cubeExpected=e_4^5*cubeDisc;
cubeDet=det cubeHull; cubeRatio=cubeDet//cubeExpected;
assert(cubeRatio!=0 and first degree cubeRatio==0 and cubeDet==cubeRatio*cubeExpected);
<< "FRAME_WEIGHTS=" << cubeHullWeights << endl;
<< "FRAME_DETERMINANT_FACTOR=" << toString cubeRatio << endl;
<< "FRAME=" << toString entries cubeHull << endl << flush;
cubeConnection=cubePlain matrix table(12,12,(i,j)->(
    ri:=cubeRows#i;rj:=cubeRows#j;
    if ri#1!=rj#1 then 0_B else if ri#0==rj#0 then (cubeMs#(ri#1))_(ri#2,rj#2)
    else if ri#0==rj#0+1 and ri#2==rj#2 then 1_B else 0_B));
assert(trace cubeConnection==-7*e_1);
<< "SOLVE_HULL_CONNECTION" << endl << flush;
cubeHullDerivative=cubeDeltaMatrix(cubeHull)+cubeConnection*cubeHull;
cubeHullConnection=cubeHullDerivative//cubeHull;
assert(cubeHull*cubeHullConnection==cubeHullDerivative);
for i from 0 to 11 do for j from 0 to 11 do if cubeHullConnection_(i,j)!=0 then
    assert(first degree cubeHullConnection_(i,j)==1+cubeHullWeights#j-cubeHullWeights#i);
cubeVector=cubePlain matrix table(12,1,(i,j)->if i==0 then 1_B else 0_B);
assert(cubeHull*cubeVector==submatrix(cubeAll,,{0}));
cubeIterate=cubeVector;
for j from 0 to 13 do (
    assert(cubeHull*(cubeIterate/(j!))==submatrix(cubeAll,,{j}));
    cubeIterate=cubeDeltaMatrix(cubeIterate)+cubeHullConnection*cubeIterate;
);
assert(cubeDeltaMatrix(cubeHull)!=0);
<< "UNIMODULAR_TRANSFORM=" << toString entries cubeTransform << endl;
<< "HILBERT_BURCH=" << toString entries cubeS << endl;
<< "HULL_CONNECTION=" << toString entries cubeHullConnection << endl;
<< "PASS polynomial frame, determinant, covariance, degrees, distinguished vector, all168 divided-iterate identities and Abel subleading identity" << endl;
exit 0;
