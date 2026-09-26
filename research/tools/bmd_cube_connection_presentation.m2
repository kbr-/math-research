-- Export the already audited symmetric polynomial connection as a Plural
-- module presentation. Env CUBE_N (3 or 4), CUBE_PRESENTATION_OUT (new file).
-- Fixed d=2; no coefficient localization, truncation or modular lifting.
n=value getenv "CUBE_N";
outPath=getenv "CUBE_PRESENTATION_OUT";
assert(n==3 or n==4);
B=QQ[e_1..e_n,Degrees=>toList(1..n)]; BT=B[T];
deltas=apply(toList(0..n-1),j -> (if j<n-1 then (j+2)*B_(j+1) else 0_B)-B_0*B_j);
deltaPoly=f -> sum(toList(0..n-1),j -> diff(B_j,f)*deltas#j);
Z=matrix table(n,n,(i,j) -> if j<n-1 then (if i==j+1 then 1_B else 0_B) else (-1)^(n-i+1)*B_(n-i-1));
Bzero=-Z*diagonalMatrix apply(toList(0..n-1),j -> j*1_B);
coeffMat=(M,c) -> matrix apply(entries M,row -> apply(row,f -> sub(coefficient(T^c,f),B)));
matBlocks={}; vBlocks={}; basisWeights={};
for s from 0 to 2 do (
    inds:=subsets(n,s); rs:=#inds; kj:=(2-s)//2+1;
    Cs:=exteriorPower(s,id_(BT^n)+T*sub(Z,BT));
    Ds:=exteriorPower(s,id_(BT^n)+T*sub(Bzero,BT));
    Ms:=coeffMat(Ds,1)+(s-1/2)*coeffMat(Cs,1);
    big:=matrix table(rs*kj,rs*kj,(i,j) ->
        if i//rs==j//rs then Ms_(i%rs,j%rs)
        else if i//rs==j//rs+1 and i%rs==j%rs then 1_B else 0_B);
    matBlocks=append(matBlocks,big);
    vBlocks=append(vBlocks,matrix table(rs*kj,1,(i,j) -> if i==0 then 1_B else 0_B));
    wts:=flatten apply(toList(0..kj-1),q -> apply(inds,I -> sum I-s*(s-1)//2+q));
    basisWeights=basisWeights|wts;
    -- New assembled block must reproduce every jet column through c=6.
    hs:={id_(B^rs)};
    for c from 1 to 6 do hs=append(hs,(coeffMat(Cs,c)-sum(toList(1..c-1),j -> hs#j*hs#(c-j)))/2);
    jet:=last vBlocks;
    for c from 0 to 6 do (
        for q from 0 to kj-1 do for i from 0 to rs-1 do
            assert(jet_(q*rs+i,0)/(c!)==(if c<q then 0_B else (hs#(c-q))_(i,0)/(q!)));
        jet=matrix apply(entries jet,row -> apply(row,deltaPoly))+big*jet;
    );
);
connection=directSum matBlocks;
vector0=fold((a,b)->a||b,vBlocks);
nr=numrows connection;
assert(nr==2+n+binomial(n,2));
for i from 0 to nr-1 do for j from 0 to nr-1 do
    if connection_(i,j)!=0 then assert(first degree connection_(i,j)==1+basisWeights#j-basisWeights#i);
sink=openOut outPath;
sink << "// Generated exact weighted symmetric connection, n=" << n << ", d=2.\n";
sink << "LIB \"nctools.lib\";\nring comm=0,(D," << concatenate between(",",apply(gens B,toString)) << "),(lp(1),wp(" << concatenate between(",",apply(toList(1..n),toString)) << "));\n";
sink << "matrix corrections[" << n+1 << "][" << n+1 << "];\n";
for j from 0 to n-1 do sink << "corrections[1," << j+2 << "]=" << toString(-deltas#j) << ";\n";
sink << "def ore=nc_algebra(1,corrections); setring ore;\noption(redSB); option(redTail);\n";
sink << "int cubeN=" << n << "; int connectionRank=" << nr << ";\n";
sink << "intvec parameterWeights=" << concatenate between(",",apply(toList(1..n),toString)) << ";\n";
sink << "matrix relations[" << nr << "][" << nr << "];\n";
for i from 0 to nr-1 do for j from 0 to nr-1 do (
    val:=(if i==j then "D" else "0")|"-("|toString connection_(i,j)|")";
    sink << "relations[" << i+1 << "," << j+1 << "]=" << val << ";\n";
);
sink << "matrix distinguished[" << nr << "][1];\n";
for i from 0 to nr-1 do if vector0_(i,0)!=0 then sink << "distinguished[" << i+1 << ",1]=1;\n";
sink << "print(\"PRESENTATION n=" << n << " d=2 rank=" << nr << " weighted symmetric coefficients\");\n";
sink << "<\"research/tools/bmd_cube_connection_annihilator.sing\";\n";
close sink;
<< "PASS rank=" << nr << "; all assembled jet columns c=0..6 and weighted connection degrees; wrote " << outPath << endl;
exit 0;
