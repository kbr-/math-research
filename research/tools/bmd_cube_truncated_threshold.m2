-- Truncated, degree-limited bounded kernel for dimension four (6 October 2026; cycle bmd-20261006-a).
-- Tested statement: the thresholds l_0 at orders m <= CUBE_ORDER, restricted to excess <= CUBE_EXCESS, of the record's
-- bounded operator kernel (research/tools/bmd_cube_bounded_operator_kernel_d.m2, cutoff U = 20d-21).  A kernel element
-- of order <= CUBE_ORDER has zero entries in columns > CUBE_ORDER, so it is a syzygy of the first CUBE_ORDER+1 columns;
-- one of order c and excess l has module degree l + c - (U-1), so a Groebner basis truncated at degree
-- CUBE_EXCESS + CUBE_ORDER - (U-1) contains every kernel element of order <= CUBE_ORDER and excess <= CUBE_EXCESS.
-- Thresholds above CUBE_EXCESS are reported as "> CUBE_EXCESS".  Env: CUBE_D, CUBE_P (0 for QQ), CUBE_ORDER, CUBE_EXCESS.
n=4;
d=value getenv "CUBE_D"; boundU=20*d-21; m=boundU-1;
charP=value getenv "CUBE_P"; ord=value getenv "CUBE_ORDER"; maxExc=value getenv "CUBE_EXCESS";
assert(ord<boundU);
B=(if charP==0 then QQ else ZZ/charP)[e_1..e_n,Degrees=>toList(1..n),MonomialOrder=>{Position=>Up,GRevLex}];
BT=B[T];
Z=matrix table(n,n,(i,j) -> if j<n-1 then (if i==j+1 then 1_B else 0_B) else (-1)^(n-i+1)*B_(n-i-1));
coeffMatrix=(M,j) -> matrix apply(entries M,row -> apply(row,v -> sub(coefficient(T^j,v),B)));
cubeBlocks=new MutableHashTable; cubeWeights=new MutableHashTable;
for s from 0 to min(n,d) do (
    inds:=subsets(n,s); rs:=#inds;
    Cs:=exteriorPower(s,id_(BT^n)+T*sub(Z,BT));
    hs:={id_(B^rs)};
    for j from 1 to m do hs=append(hs,(coeffMatrix(Cs,j)-sum(toList(1..j-1),i -> hs#i*hs#(j-i)))/2);
    cubeBlocks#s=hs; cubeWeights#s=apply(inds,I -> sum I-s*(s-1)//2);
);
rowData=flatten apply(toList(0..d//2),q -> flatten apply(toList(0..min(n,d-2*q)),s ->
    apply(toList(0..binomial(n,s)-1),j -> (q,s,j,(cubeWeights#s)#j))));
cubeMatrix=matrix apply(rowData,rw -> apply(toList(0..m),c -> if c<rw#0 then 0_B else ((cubeBlocks#(rw#1))#(c-rw#0))_(rw#2,0)));
phi=map(B^(apply(rowData,rw -> m-rw#0-rw#3)),B^(apply(toList(0..m),c -> m-c)),cubeMatrix);
assert isHomogeneous phi;
phiK=phi_(toList(0..ord));
degLimit=maxExc+ord-m;
<< "TRUNCATED_KERNEL char=" << char B << " d=" << d << " U=" << boundU << " order<=" << ord << " excess<=" << maxExc << " degree limit " << degLimit << " matrix " << numrows phiK << "x" << numcols phiK << endl << flush;
clock=cpuTime();
S=syz(phiK,DegreeLimit=>degLimit);
<< "SYZ cpu=" << cpuTime()-clock << " generators=" << numcols S << endl << flush;
G=if numcols S==0 then S else gens gb(S,DegreeLimit=>degLimit);
assert(phiK*G==0);
kerPairs=apply(toList(0..numcols G-1),j -> (
    rr:=last select(toList(0..ord),c -> G_(c,j)!=0);
    ee:=first degree G_(rr,j);
    {rr,ee}));
scan(sort unique kerPairs,p -> << "GENERATOR order=" << p#0 << " excess=" << p#1 << endl);
for mm from 0 to ord do (
    eligible:=select(kerPairs,p -> p#0<=mm and p#1<=maxExc);
    << "THRESHOLD char=" << char B << " m=" << mm << " excess=" << (if #eligible==0 then "> "|toString maxExc else toString min apply(eligible,p->p#1)) << endl;
);
<< "PASS char=" << char B << " cpu=" << cpuTime()-clock << endl;
exit 0;
