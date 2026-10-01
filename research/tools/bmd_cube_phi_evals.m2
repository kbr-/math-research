-- Evaluations of the dimension-four bounded operator matrix phi at random points of F_p^4 (6 October 2026; cycle
-- bmd-20261006-a), for the compiled evaluation kernel research/tools/bmd_eval_kernel.cpp.  phi is built exactly as in
-- research/tools/bmd_cube_bounded_operator_kernel_d.m2 (cutoff U = 20d-21).  The two rows with s = 0 read W_q = 0
-- (q = 0, 1); this is asserted, and only the remaining rows and columns 2..CUBE_ORDER are written.
-- Env: CUBE_D, CUBE_P, CUBE_ORDER, CUBE_POINTS, CUBE_SEED, CUBE_OUT.
-- Output: "HEADER d m ord p rows points", one "ROW q s j w" line per kept row, then per point "P e1 e2 e3 e4" and one line per row with columns 2..ord.
n=4;
d=value getenv "CUBE_D"; boundU=20*d-21; m=boundU-1;
charP=value getenv "CUBE_P"; ord=value getenv "CUBE_ORDER"; npts=value getenv "CUBE_POINTS";
setRandomSeed(value getenv "CUBE_SEED");
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
cubeMatrix=matrix apply(rowData,rw -> apply(toList(0..m),c -> if c<rw#0 then 0_B else ((cubeBlocks#(rw#1))#(c-rw#0))_(rw#2,0)));
keep=select(toList(0..#rowData-1),i -> (rowData#i)#1!=0);
scan(select(toList(0..#rowData-1),i -> (rowData#i)#1==0),i -> (
    q:=(rowData#i)#0; assert(q<=1);
    assert all(toList(0..m),c -> cubeMatrix_(i,c)==(if c==q then 1_B else 0_B))));
P=cubeMatrix^keep_(toList(2..ord));
<< "phi built: " << numrows P << " rows, columns 2.." << ord << endl << flush;
f=openOut getenv "CUBE_OUT";
f << "HEADER " << d << " " << m << " " << ord << " " << charP << " " << numrows P << " " << npts << endl;
scan(keep,i -> f << "ROW " << (rowData#i)#0 << " " << (rowData#i)#1 << " " << (rowData#i)#2 << " " << (rowData#i)#3 << endl);
for k from 1 to npts do (
    pt:=apply(4,i->random(ZZ/charP));
    f << "P " << concatenate between(" ",apply(pt,x->toString lift(x,ZZ))) << endl;
    V:=sub(P,matrix{pt});
    scan(entries V,row -> f << concatenate between(" ",apply(row,x->toString lift(x,ZZ))) << endl);
);
close f;
<< "wrote " << npts << " points" << endl;
exit 0;
