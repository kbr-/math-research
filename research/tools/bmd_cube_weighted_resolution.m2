-- Theorem tested: symmetric flat descent preserves the COMPLETE graded kernel
-- and marked top ideal.  New question at n=4,d=2,m=13 over QQ: is the first-step
-- curve arithmetically Cohen--Macaulay, so that its plane equations lift?
-- This computes the full resolution, not another degree-limited threshold scan.
-- Stages: assemble the 12x14 weighted companion matrix; compute kernel/top ideal;
-- resolve both; retain all generator and differential entries as certificates.
-- Usage: M2 --script research/tools/bmd_cube_weighted_resolution.m2
n=4; d=2; m=13;
B=QQ[e_1..e_n,Degrees=>toList(1..n)];
BT=B[T];
Z=matrix table(n,n,(i,j) -> if j<n-1 then (if i==j+1 then 1_B else 0_B) else (-1)^(n-i+1)*B_(n-i-1));
coeffMatrix=(M,j) -> matrix apply(entries M,row -> apply(row,v -> sub(coefficient(T^j,v),B)));
blocks=new MutableHashTable;
weights=new MutableHashTable;
for s from 0 to min(n,d) do (
    inds:=subsets(n,s); r:=#inds;
    C:=exteriorPower(s,id_(BT^n)+T*sub(Z,BT));
    H:={id_(B^r)};
    for j from 1 to m do H=append(H,(coeffMatrix(C,j)-sum(toList(1..j-1),i -> H#i*H#(j-i)))/2);
    blocks#s=H;
    weights#s=apply(inds,I -> sum I-s*(s-1)//2);
);
rowData=flatten apply(toList(0..d//2),q -> flatten apply(toList(0..min(n,d-2*q)),s ->
    apply(toList(0..binomial(n,s)-1),j -> (q,s,j,(weights#s)#j))));
A=matrix apply(rowData,rw -> apply(toList(0..m),c -> if c<rw#0 then 0_B else ((blocks#(rw#1))#(c-rw#0))_(rw#2,0)));
phi=map(B^(apply(rowData,rw -> m-rw#0-rw#3)),B^(apply(toList(0..m),c -> m-c)),A);
assert isHomogeneous phi;
assert(numrows phi==12 and numcols phi==14);
<< "SCOPE QQ n=4 d=2 m=13; B degrees=" << degrees B << "; matrix=" << numrows phi << "x" << numcols phi << endl << flush;
t0=cpuTime();
K=kernel phi;
G=mingens K;
assert(phi*G==0);
<< "K_GENERATOR_EXCESSES=" << degrees source G << " cpu=" << cpuTime()-t0 << endl << flush;
<< "K_GENERATOR_MATRIX=" << toString entries G << endl << flush;
I=ideal apply(toList(0..numcols G-1),j -> G_(m,j));
GI=mingens I;
I=ideal GI;
<< "TOP_GENERATOR_DEGREES=" << degrees source GI << " cpu=" << cpuTime()-t0 << endl << flush;
<< "TOP_GENERATORS=" << toString entries GI << endl << flush;
RK=res K;
<< "K_RESOLUTION_BETTI=" << betti RK << endl;
for j from 1 to length RK do << "K_DIFFERENTIAL_" << j << "=" << toString entries RK.dd_j << endl << flush;
Q=coker gens I;
RI=res Q;
<< "QUOTIENT_RESOLUTION_BETTI=" << betti RI << endl;
<< "QUOTIENT_DIMENSION=" << dim Q << " RESOLUTION_LENGTH=" << length RI << " cpu=" << cpuTime()-t0 << endl << flush;
for j from 1 to length RI do << "QUOTIENT_DIFFERENTIAL_" << j << "=" << toString entries RI.dd_j << endl;
for j from 2 to length RK do assert(RK.dd_(j-1)*RK.dd_j==0);
for j from 2 to length RI do assert(RI.dd_(j-1)*RI.dd_j==0);
<< "PASS complete weighted kernel and resolutions; total_cpu=" << cpuTime()-t0 << endl;
exit 0;
