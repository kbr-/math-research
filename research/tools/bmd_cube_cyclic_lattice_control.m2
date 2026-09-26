-- Test height-one reconstruction on the ACTUAL n3,d2 full cyclic image.
-- A retained monic order9 relation makes the first9 columns generate it.
-- Reuse the complete rank-one kernel; verify the full cofactor ideal and its
-- height-two defect, not just a determinant or a generic rank.
B=QQ[e_1,e_2,e_3,Degrees=>{1,2,3}]; BT=B[T];
cubeLines=separate("\n",get "research/results/cube-operator-global-degree-review-20260927/bounded-control-n3-qq.txt");
cubeKey="KERNEL_GROEBNER_MATRIX=";
cubeHits=select(cubeLines,l->substring(0,#cubeKey,l)==cubeKey);
assert(#cubeHits==1);
cubeG=matrix apply(value substring(#cubeKey,cubeHits#0),row->apply(row,f->sub(f,B)));
cubeZ=matrix{{0_B,0_B,e_3},{1_B,0_B,-e_2},{0_B,1_B,e_1}};
cubeCoeff=(M,j)->matrix apply(entries M,row->apply(row,f->sub(coefficient(T^j,f),B)));
cubeHs=new MutableHashTable; cubeWeights=new MutableHashTable;
for s from 0 to 2 do (
    inds:=subsets(3,s); rs:=#inds;
    cs:=exteriorPower(s,id_(BT^3)+T*sub(cubeZ,BT)); hs:={id_(B^rs)};
    for j from 1 to 8 do hs=append(hs,(cubeCoeff(cs,j)-sum(toList(1..j-1),i->hs#i*hs#(j-i)))/2);
    cubeHs#s=hs; cubeWeights#s=apply(inds,I->sum I-s*(s-1)//2);
);
cubeRows=flatten apply(toList(0..1),q->flatten apply(toList(0..min(3,2-2*q)),s->
    apply(toList(0..binomial(3,s)-1),j->(q,s,j,(cubeWeights#s)#j))));
cubeMatrix=matrix apply(cubeRows,rw->apply(toList(0..8),c->if c<rw#0 then 0_B else ((cubeHs#(rw#1))#(c-rw#0))_(rw#2,0)));
assert(numrows cubeMatrix==8 and numcols cubeMatrix==9 and cubeMatrix*cubeG==0);
cubeDiscriminant=e_1^2*e_2^2-4*e_2^3-4*e_1^3*e_3-27*e_3^2+18*e_1*e_2*e_3;
Root=QQ[a_1,a_2,a_3];
cubeRootMap=map(Root,B,apply(toList(1..3),j->sum(subsets(3,j),I->product(I,i->Root_i))));
assert(cubeRootMap cubeDiscriminant==product(subsets(3,2),I->(Root_(I#0)-Root_(I#1))^2));
cubeDivisor=e_3^4*cubeDiscriminant;
cubeCofactors=apply(toList(0..8),j->(-1)^j*det submatrix(cubeMatrix,,select(toList(0..8),i->i!=j)));
cubeRatio=(cubeCofactors#8)//(cubeDivisor*cubeG_(8,0));
assert(cubeRatio!=0 and first degree cubeRatio==0);
for j from 0 to 8 do assert(cubeCofactors#j==cubeRatio*cubeDivisor*cubeG_(j,0));
cubePrimitive=fold(gcd,flatten entries cubeG);
assert(cubePrimitive!=0 and first degree cubePrimitive==0);
Param=QQ[t];
cubeAtDoublePair=map(Param,B,{2*t,t^2,0_Param});
assert(cubeAtDoublePair cubeG==0);
cubePrime=ideal(e_3,e_1^2-4*e_2);
assert(dim(B/cubePrime)==1);
assert(all(flatten entries cubeG,f->f%cubePrime==0));
<< "FITTING_DIVISOR=" << toString cubeDivisor << "; weighted_degree=" << degree cubeDivisor << endl;
<< "SIGNED_COFACTOR_RATIO=" << cubeRatio << endl;
<< "KERNEL_COORDINATE_GCD=" << cubePrimitive << endl;
<< "SIGNED_MAXIMAL_MINORS=" << toString cubeCofactors << endl;
<< "HEIGHT_TWO_PRIME=" << toString entries gens cubePrime << endl;
<< "PASS all9 cofactor identities, primitive kernel, exact vanishing on (e1,e2,e3)=(2t,t²,0); local presentation is minimal of projective dimension1" << endl;
exit 0;
