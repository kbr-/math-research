-- Symbolic verification of kernel vectors written by research/tools/bmd_eval_kernel.cpp (6 October 2026; cycle
-- bmd-20261006-a).  Rebuilds phi exactly as research/tools/bmd_cube_bounded_operator_kernel_d.m2 over ZZ/p, forms
-- W = (0, 0, W_2, ..., W_ord) from each VECTOR line, and checks phi_(0..ord) * W == 0 exactly, with W_ord != 0 and
-- each W_c homogeneous of weighted degree excess + ord - c.  Env: CUBE_D, CUBE_VECTORS.
n=4;
d=value getenv "CUBE_D"; boundU=20*d-21; m=boundU-1;
L=lines get getenv "CUBE_VECTORS";
hdr=separate(" ",first L);
ord=value hdr#3; exc=value hdr#5; charP=value hdr#7;
B=(ZZ/charP)[e_1..e_n,Degrees=>toList(1..n)];
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
cubeMatrix=matrix apply(rowData,rw -> apply(toList(0..ord),c -> if c<rw#0 then 0_B else ((cubeBlocks#(rw#1))#(c-rw#0))_(rw#2,0)));
-- QVECTOR lines (cycle bmd-20261006-b) give Q_k, k = 2..ord-4, and W_c = (chi Q)_c / binom(1/2, c) with
-- chi(a) = a^4 - e_1 a^3 + e_2 a^2 - e_3 a + e_4.
chiCoeff={e_4,-e_3,e_2,-e_1,1_B};
gammaB=c -> (g:=product(toList(0..c-1),i->1/2-i)/c!; Fp:=ZZ/charP; promote(((numerator g)*1_Fp)*((denominator g)*1_Fp)^(-1),B));
vecs=select(drop(L,1),l->(#l>6 and substring(0,6,l)=="VECTOR") or (#l>7 and substring(0,7,l)=="QVECTOR"));
<< "vectors to verify: " << #vecs << endl;
scan(vecs,l -> (
    W:=new MutableList from toList(ord+1:0_B);
    isQ:=substring(0,1,l)=="Q";
    Qk:=new MutableList from toList(ord+1:0_B);
    scan(drop(separate(" ",l),1),tok -> (
        parts:=separate(":",tok); c:=value parts#0; ex:=apply(separate(",",parts#1),value); v:=value parts#2;
        mono:=v*e_1^(ex#0)*e_2^(ex#1)*e_3^(ex#2)*e_4^(ex#3);
        if isQ then Qk#c=Qk#c+mono else W#c=W#c+mono));
    if isQ then scan(toList(2..ord),c -> W#c=(gammaB(c))^(-1)*sum(toList(max(2,c-4)..min(c,ord-4)),k -> chiCoeff#(c-k)*Qk#k));
    assert(W#ord!=0);
    scan(toList(2..ord),c -> if W#c!=0 then assert(isHomogeneous W#c and first degree W#c==exc+ord-c));
    res:=cubeMatrix*transpose matrix{toList W};
    << "VERIFIED_KERNEL_VECTOR order=" << ord << " excess=" << exc << " exact=" << (res==0) << endl;
));
exit 0;
