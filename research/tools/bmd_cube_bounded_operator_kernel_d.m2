-- Parametrized copy (5 October 2026, cycles bmd-20261005-r and -x): CUBE_D sets d for CUBE_N=4 with U=20d-21;
-- CUBE_PS is a list of characteristics (0 for QQ) computed in one run, e.g. CUBE_PS="0 3 5"; CUBE_P (single prime)
-- is kept for compatibility.  In characteristic p > 0 the order-zero cutoff U is the characteristic-zero one, so only
-- thresholds at orders m < U are reported as computed; the value at m = U is the characteristic-zero bound.
-- Bounded commutative kernel for the polynomial operator ideal.
-- CUBE_N=3 uses the retained monic order9 control; CUBE_N=4 uses the
-- characteristic-zero order-zero upper bound U=19.  Compute ALL kernel
-- generators below U, not independent truncated kernels at each order.
-- Position-first module order retains the marked largest coefficient index.
n=value getenv "CUBE_N";
assert(n==3 or n==4);
d=if getenv "CUBE_D"=="" then 2 else value getenv "CUBE_D"; assert(n==4 or d==2); boundU=if n==3 then 9 else 20*d-21; m=boundU-1;
charList=if getenv "CUBE_PS"!="" then apply(select(separate(" ",getenv "CUBE_PS"),s->s!=""),value) else if getenv "CUBE_P"!="" then {value getenv "CUBE_P"} else {0};
runKernel=charP->(
B:=(if charP==0 then QQ else ZZ/charP)[e_1..e_n,Degrees=>toList(1..n),MonomialOrder=>{Position=>Up,GRevLex}];
T:=symbol T; BT:=B[T]; T=BT_0;
Z:=matrix table(n,n,(i,j) -> if j<n-1 then (if i==j+1 then 1_B else 0_B) else (-1)^(n-i+1)*B_(n-i-1));
coeffMatrix:=(M,j) -> matrix apply(entries M,row -> apply(row,v -> sub(coefficient(T^j,v),B)));
cubeBlocks:=new MutableHashTable; cubeWeights:=new MutableHashTable;
for s from 0 to min(n,d) do (
    inds:=subsets(n,s); rs:=#inds;
    Cs:=exteriorPower(s,id_(BT^n)+T*sub(Z,BT));
    hs:={id_(B^rs)};
    for j from 1 to m do hs=append(hs,(coeffMatrix(Cs,j)-sum(toList(1..j-1),i -> hs#i*hs#(j-i)))/2);
    cubeBlocks#s=hs; cubeWeights#s=apply(inds,I -> sum I-s*(s-1)//2);
);
rowData:=flatten apply(toList(0..d//2),q -> flatten apply(toList(0..min(n,d-2*q)),s ->
    apply(toList(0..binomial(n,s)-1),j -> (q,s,j,(cubeWeights#s)#j))));
cubeMatrix:=matrix apply(rowData,rw -> apply(toList(0..m),c -> if c<rw#0 then 0_B else ((cubeBlocks#(rw#1))#(c-rw#0))_(rw#2,0)));
phi:=map(B^(apply(rowData,rw -> m-rw#0-rw#3)),B^(apply(toList(0..m),c -> m-c)),cubeMatrix);
assert isHomogeneous phi;
<< "BOUNDED_KERNEL char=" << char B << " n=" << n << " d=" << d << " U=" << boundU << " matrix=" << numrows phi << "x" << numcols phi << endl << flush;
cubeClock:=cpuTime();
cubeKernel:=kernel phi;
<< "COMPLETE_KERNEL cpu=" << cpuTime()-cubeClock << endl << flush;
cubeGB:=gens gb gens cubeKernel;
assert(phi*cubeGB==0 and isHomogeneous cubeGB);
<< "KERNEL_GROEBNER_MATRIX=" << toString entries cubeGB << endl << flush;
cubePairs:=apply(toList(0..numcols cubeGB-1),j -> (
    rr:=last select(toList(0..m),c -> cubeGB_(c,j)!=0);
    leadRows:=select(toList(0..m),c -> (leadTerm cubeGB)_(c,j)!=0);
    assert(leadRows=={rr});
    ee:=first degree cubeGB_(rr,j);
    << "GENERATOR order=" << rr << " excess=" << ee << endl << flush;
    {rr,ee}));
for mm from 0 to boundU do (
    eligible:=select(cubePairs,p -> p#0<=mm);
    valueAtM:=if mm==boundU then 0 else if #eligible==0 then infinity else min apply(eligible,p->p#1);
    << "THRESHOLD char=" << char B << " m=" << mm << " excess=" << valueAtM << (if mm==boundU and charP!=0 then " (characteristic-zero cutoff, not computed)" else "") << endl;
    if n==3 and charP==0 then assert(valueAtM==(if mm<8 then infinity else if mm==8 then 3 else 0));
);
<< "PASS char=" << char B << " complete bounded kernel; zero residual; homogeneity; position order; cpu=" << cpuTime()-cubeClock << endl;
);
scan(charList,runKernel);
exit 0;
