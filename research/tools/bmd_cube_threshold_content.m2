-- Content of the order-14, excess-9 coefficient system of the dimension-four degree-two bounded kernel
-- (5 October 2026; cycle bmd-20261005-y).  Over QQ the system has only the zero solution (threshold 11 at order 14);
-- modulo p a solution exists iff p divides the gcd of maximal minors (product of Smith invariant factors).
-- Prediction: the odd prime divisors are exactly the observed order-14 exceptions 5, 11, 17, 31, 43, 83 (plus primes
-- where a lower order already changes, e.g. 3, 7).  Env ORDER (default 14), EXCESS (default 9).
<< "start" << endl << flush; n=4; d=2; boundU=19; m=boundU-1;
ord=if getenv "ORDER"=="" then 14 else value getenv "ORDER";
exc=if getenv "EXCESS"=="" then 9 else value getenv "EXCESS";
B=QQ[e_1..e_n,Degrees=>toList(1..n)];
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
<< "blocks done" << endl << flush; rowData=flatten apply(toList(0..d//2),q -> flatten apply(toList(0..min(n,d-2*q)),s ->
    apply(toList(0..binomial(n,s)-1),j -> (q,s,j,(cubeWeights#s)#j))));
cubeMatrix=matrix apply(rowData,rw -> apply(toList(0..m),c -> if c<rw#0 then 0_B else ((cubeBlocks#(rw#1))#(c-rw#0))_(rw#2,0)));
phi=map(B^(apply(rowData,rw -> m-rw#0-rw#3)),B^(apply(toList(0..m),c -> m-c)),cubeMatrix);
<< "phi done" << endl << flush; phiK=phi_(toList(0..ord));
<< "source degrees " << degrees source phiK << endl << flush; D=exc+(degrees source phiK)#ord#0;
<< "order " << ord << ", excess " << exc << ", source degree " << D << endl;
-- coefficient matrix of phiK on the degree-D piece: columns = monomial basis of the source piece
srcBasis=basis(D,source phiK); << "src basis " << numcols srcBasis << endl << flush; tgtBasis=basis(D,target phiK); << "tgt basis " << numcols tgtBasis << endl << flush;
A=last coefficients(phiK*srcBasis,Monomials=>tgtBasis);
A=lift(A*(lcm apply(flatten entries A,a->denominator lift(a,QQ))),ZZ);
<< "integer matrix " << numrows A << "x" << numcols A << ", rank over QQ " << rank A << endl;
<< "INTEGER_MATRIX=" << toString entries A << endl;
exit 0;
