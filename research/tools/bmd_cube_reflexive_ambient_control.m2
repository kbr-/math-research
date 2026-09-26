-- Construct the actual n3,d2 reflexive hull as a polynomial ambient connection.
-- The retained cyclic relation is reduced by a graded unimodular map to
-- (0,...,0,h²,f), f=e1³-4e1e2+8e3, h=e1²-4e2.  This identifies the whole
-- residual ideal, not just its support. Construct the embedded hull frame,
-- connection, vector, cyclic coordinates and all divided iterates through9.
B=QQ[e_1,e_2,e_3,Degrees=>{1,2,3}]; BT=B[T];
-- Use common ungraded ambient modules for entrywise matrix algebra; the
-- intended source/target weights are checked explicitly below.
cubePlain=M->map(B^(numrows M),B^(numcols M),M);
cubeLines=separate("\n",get "research/results/cube-operator-global-degree-review-20260927/bounded-control-n3-qq.txt");
cubeKey="KERNEL_GROEBNER_MATRIX=";
cubeHits=select(cubeLines,l->substring(0,#cubeKey,l)==cubeKey);
assert(#cubeHits==1);
cubeG=cubePlain matrix apply(value substring(#cubeKey,cubeHits#0),row->apply(row,f->sub(f,B)));
cubeH=e_1^2-4*e_2; cubeF=e_1*cubeH+8*e_3;
assert(cubeG_(8,0)==4096*cubeF);
assert(cubeG_(7,0)==256*cubeH^2+6656*e_1*cubeF);
cubeTwo=cubePlain matrix{{cubeF,cubeH^2}};
cubeGrow=cubePlain transpose cubeG;
cubeLift=cubeGrow//cubeTwo;
assert(cubeTwo*cubeLift==cubeGrow);
cubeTmut=mutableMatrix id_(B^9);
cubeTmut_(8,8)=1/4096; cubeTmut_(7,7)=1/256; cubeTmut_(7,8)=-13*e_1/2048;
for j from 0 to 6 do (
    cubeTmut_(j,7)=-cubeLift_(1,j)/256;
    cubeTmut_(j,8)=-cubeLift_(0,j)/4096+13*e_1*cubeLift_(1,j)/2048;
);
cubeTransform=matrix cubeTmut;
assert(entries(cubeTransform*cubeG)==entries(transpose matrix{toList(7:0_B)|{cubeH^2,cubeF}}));
assert(first degree det cubeTransform==0 and det cubeTransform!=0);
cubeInverse=id_(B^9)//cubeTransform;
assert(cubeTransform*cubeInverse==id_(B^9));
cubeZ=matrix{{0_B,0_B,e_3},{1_B,0_B,-e_2},{0_B,1_B,e_1}};
cubeBzero=-cubeZ*diagonalMatrix{0_B,1_B,2_B};
cubeCoeff=(M,j)->matrix apply(entries M,row->apply(row,f->sub(coefficient(T^j,f),B)));
cubeHs=new MutableHashTable;cubeWeights=new MutableHashTable;cubeMs=new MutableHashTable;
for s from 0 to 2 do (
    inds:=subsets(3,s); rs:=#inds;
    cs:=exteriorPower(s,id_(BT^3)+T*sub(cubeZ,BT));
    ds:=exteriorPower(s,id_(BT^3)+T*sub(cubeBzero,BT));
    hs:={id_(B^rs)};
    for j from 1 to 9 do hs=append(hs,(cubeCoeff(cs,j)-sum(toList(1..j-1),i->hs#i*hs#(j-i)))/2);
    cubeHs#s=hs; cubeWeights#s=apply(inds,I->sum I-s*(s-1)//2);
    cubeMs#s=cubeCoeff(ds,1)+(s-1/2)*cubeCoeff(cs,1);
);
cubeRows=flatten apply(toList(0..1),q->flatten apply(toList(0..min(3,2-2*q)),s->
    apply(toList(0..binomial(3,s)-1),j->(q,s,j,(cubeWeights#s)#j))));
cubeAll=cubePlain matrix apply(cubeRows,rw->apply(toList(0..9),c->if c<rw#0 then 0_B else ((cubeHs#(rw#1))#(c-rw#0))_(rw#2,0)));
cubePhi=submatrix(cubeAll,,toList(0..8));
assert(cubePhi*cubeG==0);
cubeChanged=cubePhi*cubeInverse;
cubeLast=cubePlain matrix apply(entries submatrix(cubeChanged,,{7}),row->apply(row,f->f//cubeF));
assert(cubeLast*cubeF==submatrix(cubeChanged,,{7}));
assert(-cubeLast*cubeH^2==submatrix(cubeChanged,,{8}));
cubeHull=submatrix(cubeChanged,,toList(0..6))|cubeLast;
cubeDiscriminant=e_1^2*e_2^2-4*e_2^3-4*e_1^3*e_3-27*e_3^2+18*e_1*e_2*e_3;
cubeExpectedDet=e_3^4*cubeDiscriminant;
cubeDetRatio=(det cubeHull)//cubeExpectedDet;
assert(cubeDetRatio!=0 and first degree cubeDetRatio==0 and det cubeHull==cubeDetRatio*cubeExpectedDet);
cubeCoordinates=cubePhi//cubeHull;
assert(cubeHull*cubeCoordinates==cubePhi);
assert(ideal submatrix(cubeCoordinates,{7},)==ideal(cubeF,cubeH^2));
cubeHullWeights={0,1,2,3,4,5,6,4};
cubeRowWeights=apply(cubeRows,rw->rw#0+rw#3);
for i from 0 to 7 do for j from 0 to 7 do if cubeHull_(i,j)!=0 then
    assert(first degree cubeHull_(i,j)==cubeHullWeights#j-cubeRowWeights#i);
cubeDeltaValues={2*e_2-e_1^2,3*e_3-e_1*e_2,-e_1*e_3};
cubeDelta=f->sum(toList(0..2),j->diff(B_j,f)*cubeDeltaValues#j);
cubeDeltaMatrix=M->cubePlain matrix apply(entries M,row->apply(row,cubeDelta));
cubeConnection=cubePlain matrix table(8,8,(i,j)->(
    ri:=cubeRows#i;rj:=cubeRows#j;
    if ri#1!=rj#1 then 0_B
    else if ri#0==rj#0 then (cubeMs#(ri#1))_(ri#2,rj#2)
    else if ri#0==rj#0+1 and ri#2==rj#2 then 1_B else 0_B));
cubeHullDerivative=cubeDeltaMatrix(cubeHull)+cubeConnection*cubeHull;
cubeHullConnection=cubeHullDerivative//cubeHull;
assert(cubeHull*cubeHullConnection==cubeHullDerivative);
for i from 0 to 7 do for j from 0 to 7 do if cubeHullConnection_(i,j)!=0 then
    assert(first degree cubeHullConnection_(i,j)==1+cubeHullWeights#j-cubeHullWeights#i);
cubeVector=cubePlain matrix table(8,1,(i,j)->if i==0 then 1_B else 0_B);
assert(cubeHull*cubeVector==submatrix(cubeAll,,{0}));
cubeIterate=cubeVector;
for j from 0 to 9 do (
    assert(cubeHull*(cubeIterate/(j!))==submatrix(cubeAll,,{j}));
    cubeIterate=cubeDeltaMatrix(cubeIterate)+cubeHullConnection*cubeIterate;
);
assert(cubeDelta(cubeF)==-(5/2)*e_1*cubeF-cubeH^2/2);
assert(cubeDelta(cubeH^2)==-e_1*cubeH^2-3*cubeH*cubeF);
assert(cubeDeltaMatrix(cubeHull)!=0);
<< "RESIDUAL_IDEAL=" << toString entries cubeTwo << endl;
<< "UNIMODULAR_TRANSFORM=" << toString entries cubeTransform << endl;
<< "HULL_WEIGHTS=" << cubeHullWeights << endl;
<< "HULL_FRAME=" << toString entries cubeHull << endl;
<< "HULL_DETERMINANT_FACTOR=" << cubeDetRatio << endl;
<< "HULL_CONNECTION=" << toString entries cubeHullConnection << endl;
<< "CYCLIC_COORDINATES=" << toString entries cubeCoordinates << endl;
<< "PASS exact residual ideal, polynomial free hull, covariance, distinguished vector, all80 divided-iterate identities, weight checks and differential-ideal identities" << endl;
exit 0;
