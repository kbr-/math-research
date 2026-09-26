-- Test every homogeneous monic order19 old annihilator, not just one choice.
-- The complete retained position-first kernel has one degree19 generator G17
-- and no lower total degree, so the family is H19+alpha G17.
-- Construct both added-jet responses and symbolic connection iterates BEFORE
-- root evaluation. Two degree10 binary minors with nonzero resultant certify
-- that no family member has cyclic rank<=9, hence none reaches order28 by
-- left multiplication. All denominators must survive the prime32003.
B=QQ[e_1..e_4,Degrees=>{1,2,3,4}];
cubeLines=separate("\n",get "research/results/cube-jet-layer-relations-20260927/monic-obstruction.txt");
cubeKey="MONIC_W_TOP1=";
cubeHit=select(cubeLines,l->substring(0,#cubeKey,l)==cubeKey);
assert(#cubeHit==1); cubeH=apply(value substring(#cubeKey,cubeHit#0),f->sub(f,B));
cubeLines=separate("\n",get "research/results/cube-operator-global-degree-review-20260927/bounded-row-n4-qq.txt");
cubeKey="KERNEL_GROEBNER_MATRIX=";
cubeHit=select(cubeLines,l->substring(0,#cubeKey,l)==cubeKey);
assert(#cubeHit==1); cubeStored=value substring(#cubeKey,cubeHit#0);
cubeDegrees=apply(toList(0..#(cubeStored#0)-1),j->(
    rr:=last select(toList(0..18),i->cubeStored#i#j!=0);
    rr+first degree cubeStored#rr#j));
assert(min cubeDegrees==19);
cubeIndices=select(toList(0..#cubeDegrees-1),j->cubeDegrees#j==19);
assert(#cubeIndices==1);
cubeG=apply(cubeStored,row->sub(row#(cubeIndices#0),B))|{0_B};
assert(cubeG#18==0 and cubeG#17!=0 and first degree cubeG#17==2);
<< "FAMILY totaldegree19 kernel_dimension1; Gorder17; Htop1" << endl << flush;
<< "FAMILY_G=" << toString cubeG << endl << flush;
cubePrime=32003; FF=ZZ/cubePrime;
BF=FF[f_1..f_4,Degrees=>{1,2,3,4}]; BFT=BF[t];
for f in cubeH|cubeG do scan(flatten entries last coefficients f,c->assert((denominator lift(c,QQ))%cubePrime!=0));
cubeReduction=map(BF,B,toList gens BF);
cubeWF=matrix{apply(cubeH,f->cubeReduction f),apply(cubeG,f->cubeReduction f)};
cubeDeltaValues=apply(toList(0..3),j->(if j<3 then (j+2)*BF_(j+1) else 0_BF)-BF_0*BF_j);
cubeDelta=f->sum(toList(0..3),j->diff(BF_j,f)*cubeDeltaValues#j);
cubeZ=matrix table(4,4,(i,j)->if j<3 then (if i==j+1 then 1_BF else 0_BF) else (-1)^(5-i)*BF_(3-i));
cubeBzero=-cubeZ*diagonalMatrix apply(toList(0..3),j->j*1_BF);
cubeCoeff=(M,j)->matrix apply(entries M,row->apply(row,f->sub(coefficient(t^j,f),BF)));
cubeConBlocks={}; cubeRespBlocks={};
for s from 0 to 4 do (
    rs:=binomial(4,s); ks:=if s>2 then 0 else (2-s)//2+1;
    cs:=exteriorPower(s,id_(BFT^4)+t*sub(cubeZ,BFT));
    ds:=exteriorPower(s,id_(BFT^4)+t*sub(cubeBzero,BFT));
    ms:=cubeCoeff(ds,1)+(s-1/2)*cubeCoeff(cs,1);
    hs:={id_(BF^rs)};
    for j from 1 to 19-ks do hs=append(hs,(cubeCoeff(cs,j)-sum(toList(1..j-1),i->hs#i*hs#(j-i)))/2);
    vv:=matrix table(rs,1,(i,j)->if i==0 then 1_BF else 0_BF);
    response:=fold((a,b)->a|b,apply({0,1},col->sum(toList(ks..19),c->cubeWF_(col,c)*hs#(c-ks)*vv)/(ks!)));
    cubeConBlocks=append(cubeConBlocks,ms); cubeRespBlocks=append(cubeRespBlocks,response);
);
cubeConnection=directSum cubeConBlocks;
cubeResponse=fold((a,b)->a||b,cubeRespBlocks);
cubeRootValues={1,2,3,5};
cubeEs=apply(toList(1..4),j->sum(subsets(4,j),S->product(S,i->cubeRootValues#i)));
cubeEvaluate=map(FF,BF,cubeEs);
cubeColsH={}; cubeColsG={};
for j from 0 to 15 do (
    ev:=cubeEvaluate cubeResponse;
    cubeColsH=append(cubeColsH,submatrix(ev,,{0}));
    cubeColsG=append(cubeColsG,submatrix(ev,,{1}));
    if j<15 then cubeResponse=matrix apply(entries cubeResponse,row->apply(row,cubeDelta))+cubeConnection*cubeResponse;
);
cubeKrylovH=fold((a,b)->a|b,cubeColsH);cubeKrylovG=fold((a,b)->a|b,cubeColsG);
assert(det cubeKrylovH==10034_FF);
<< "FAMILY_KRYLOV_H=" << toString entries cubeKrylovH << endl;
<< "FAMILY_KRYLOV_G=" << toString entries cubeKrylovG << endl;
P=FF[z];
cubePencil=sub(cubeKrylovH,P)+z*sub(cubeKrylovG,P);
cubeMinorA=det submatrix(cubePencil,toList(0..9),toList(0..9));
cubeMinorB=det submatrix(cubePencil,toList(1..10),toList(0..9));
<< "FAMILY_MINOR_A=" << toString cubeMinorA << endl;
<< "FAMILY_MINOR_B=" << toString cubeMinorB << endl;
assert(first degree cubeMinorA==10 and first degree cubeMinorB==10);
cubeResultant=resultant(cubeMinorA,cubeMinorB,z);
<< "FAMILY_RESULTANT=" << cubeResultant << "; gcd=" << gcd(cubeMinorA,cubeMinorB) << endl;
assert(cubeResultant!=0);
<< "PASS no projective member has response rank<=9; no homogeneous monic order19 choice reaches order28 by a left multiple" << endl;
exit 0;
