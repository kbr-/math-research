-- Test the new-jet obstruction on the actual n4,d2 monic order19 operator.
-- Question: can its left multiples reach the d4 boundary order28, or does
-- its added-layer response already require the full16 extra orders?
-- Stages: exact QQ polynomial solve for H19 (not a full kernel recomputation);
-- reduce coefficients mod32003; construct the independently known next-row
-- square-root blocks; form the sixteen new-jet response coordinates; iterate
-- their fixed connection16 times and evaluate at collision-free rational roots.
-- A nonzero modular16x16 determinant certifies generic char0 rank16 after
-- checking every rational denominator survives. Retain H19 and full minor.
n=4; oldDegree=2; operatorCutoff=19;
B=QQ[e_1..e_n,Degrees=>toList(1..n)]; BT=B[T];
cubeZ=matrix table(n,n,(i,j) -> if j<n-1 then (if i==j+1 then 1_B else 0_B) else (-1)^(n-i+1)*B_(n-i-1));
cubeCoeff=(M,j) -> matrix apply(entries M,row -> apply(row,f -> sub(coefficient(T^j,f),B)));
cubeHs=new MutableHashTable; cubeWeights=new MutableHashTable;
for s from 0 to 2 do (
    inds:=subsets(n,s); rs:=#inds;
    cs:=exteriorPower(s,id_(BT^n)+T*sub(cubeZ,BT)); hs:={id_(B^rs)};
    for j from 1 to operatorCutoff do hs=append(hs,(cubeCoeff(cs,j)-sum(toList(1..j-1),i->hs#i*hs#(j-i)))/2);
    cubeHs#s=hs; cubeWeights#s=apply(inds,I->sum I-s*(s-1)//2);
);
cubeRows=flatten apply(toList(0..oldDegree//2),q->flatten apply(toList(0..min(n,oldDegree-2*q)),s->
    apply(toList(0..binomial(n,s)-1),j->(q,s,j,(cubeWeights#s)#j))));
cubeAll=matrix apply(cubeRows,rw->apply(toList(0..operatorCutoff),c->if c<rw#0 then 0_B else ((cubeHs#(rw#1))#(c-rw#0))_(rw#2,0)));
cubeMap=map(B^(apply(cubeRows,rw->operatorCutoff-rw#0-rw#3)),B^(toList reverse(1..operatorCutoff)),submatrix(cubeAll,,toList(0..operatorCutoff-1)));
cubeRhs=map(target cubeMap,B^1,-submatrix(cubeAll,,{operatorCutoff}));
<< "START exact monic order19 lift" << endl << flush;
cubeLift=cubeRhs//cubeMap;
assert(cubeMap*cubeLift==cubeRhs);
cubeW=(entries cubeLift)/first|{1_B};
assert(cubeAll*transpose matrix{cubeW}==0);
for c from 0 to operatorCutoff do if cubeW#c!=0 then assert(first degree cubeW#c==operatorCutoff-c);
<< "MONIC_W_TOP1=" << toString cubeW << endl << flush;
<< "PASS exact QQ monic lift; P=sum Wc*D^c/c!, multiply by19! for leading coefficient1" << endl << flush;
cubePrime=32003; FF=ZZ/cubePrime;
BF=FF[f_1..f_n,Degrees=>toList(1..n)]; BFT=BF[t];
for f in cubeW do scan(flatten entries last coefficients f,c->assert((denominator lift(c,QQ))%cubePrime!=0));
cubeReduce=map(BF,B,toList gens BF);
cubeWF=apply(cubeW,f->cubeReduce f);
cubeDeltaValues=apply(toList(0..n-1),j->(if j<n-1 then (j+2)*BF_(j+1) else 0_BF)-BF_0*BF_j);
cubeDelta=f->sum(toList(0..n-1),j->diff(BF_j,f)*cubeDeltaValues#j);
cubeZF=matrix table(n,n,(i,j)->if j<n-1 then (if i==j+1 then 1_BF else 0_BF) else (-1)^(n-i+1)*BF_(n-i-1));
cubeBzero=-cubeZF*diagonalMatrix apply(toList(0..n-1),j->j*1_BF);
cubeCoeffF=(M,j)->matrix apply(entries M,row->apply(row,f->sub(coefficient(t^j,f),BF)));
cubeConnectionBlocks={}; cubeResponseBlocks={};
for s from 0 to n do (
    rs:=binomial(n,s); ks:=if s>oldDegree then 0 else (oldDegree-s)//2+1;
    cs:=exteriorPower(s,id_(BFT^n)+t*sub(cubeZF,BFT));
    ds:=exteriorPower(s,id_(BFT^n)+t*sub(cubeBzero,BFT));
    ms:=cubeCoeffF(ds,1)+(s-1/2)*cubeCoeffF(cs,1);
    hs:={id_(BF^rs)};
    for j from 1 to operatorCutoff-ks do hs=append(hs,(cubeCoeffF(cs,j)-sum(toList(1..j-1),i->hs#i*hs#(j-i)))/2);
    vec:=matrix table(rs,1,(i,j)->if i==0 then 1_BF else 0_BF);
    response:=sum(toList(ks..operatorCutoff),c->cubeWF#c*hs#(c-ks)*vec)/(ks!);
    cubeConnectionBlocks=append(cubeConnectionBlocks,ms);
    cubeResponseBlocks=append(cubeResponseBlocks,response);
    << "NEW_LAYER s=" << s << " rank=" << rs << " old_jet_length=" << ks << endl << flush;
);
cubeConnection=directSum cubeConnectionBlocks;
cubeResponse=fold((a,b)->a||b,cubeResponseBlocks);
assert(numrows cubeResponse==16);
cubeRoots={1,2,3,5};
cubeParameterValues=apply(toList(1..n),j->sum(subsets(n,j),S->product(S,i->cubeRoots#i)));
cubeEvaluate=map(FF,BF,cubeParameterValues);
cubeColumns={};
for j from 0 to 15 do (
    cubeColumns=append(cubeColumns,cubeEvaluate cubeResponse);
    if j<15 then cubeResponse=matrix apply(entries cubeResponse,row->apply(row,cubeDelta))+cubeConnection*cubeResponse;
    << "RESPONSE_COLUMN " << j << endl << flush;
);
cubeMinor=fold((a,b)->a|b,cubeColumns);
cubeDeterminant=det cubeMinor;
<< "RESPONSE_ROOTS=" << cubeRoots << " e=" << cubeParameterValues << " prime=" << cubePrime << endl;
<< "RESPONSE_MINOR=" << toString entries cubeMinor << endl;
<< "RESPONSE_DETERMINANT=" << cubeDeterminant << " rank=" << rank cubeMinor << endl;
assert(cubeDeterminant!=0);
<< "PASS generic characteristic-zero obstruction cyclic rank16; no left multiple of H19 of order<35 reaches J4" << endl;
exit 0;
