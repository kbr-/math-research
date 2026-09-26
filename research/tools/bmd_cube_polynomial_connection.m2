-- Exact encoding audit for the polynomial Ore connection over symmetric B.
-- Every n=1..4, s=0..n, coefficient c=0..6; nilpotent jets include every
-- q allowed by d<=4.  Compare independently constructed divided connection
-- iterates with the established exterior square-root coefficient matrices.
-- Checks delta(e_j), exterior correction/sign, jet factorials and row grading.
auditBlocks=0; auditCoefficients=0;
for n from 1 to 4 do (
    B:=QQ[e_1..e_n,Degrees=>toList(1..n)];
    deltas:=apply(toList(0..n-1),j -> (if j<n-1 then (j+2)*B_(j+1) else 0_B)-B_0*B_j);
    deltaPoly:=f -> sum(toList(0..n-1),j -> diff(B_j,f)*deltas#j);
    Z:=matrix table(n,n,(i,j) -> if j<n-1 then (if i==j+1 then 1_B else 0_B) else (-1)^(n-i+1)*B_(n-i-1));
    Bzero:=-Z*diagonalMatrix apply(toList(0..n-1),j -> j*1_B);
    BT:=B[T];
    coeffMat:=(M,c) -> matrix apply(entries M,row -> apply(row,f -> sub(coefficient(T^c,f),B)));
    R:=QQ[a_1..a_n];
    es:=apply(toList(1..n),j -> sum(subsets(n,j),I -> product(I,i -> R_i)));
    toR:=map(R,B,es);
    for j from 0 to n-1 do assert(toR(deltas#j)==-sum(toList(0..n-1),i -> R_i^2*diff(R_i,es#j)));
    for s from 0 to n do (
        inds:=subsets(n,s); rs:=#inds;
        Cs:=exteriorPower(s,id_(BT^n)+T*sub(Z,BT));
        Ds:=exteriorPower(s,id_(BT^n)+T*sub(Bzero,BT));
        Ms:=coeffMat(Ds,1)+(s-1/2)*coeffMat(Cs,1);
        con:=v -> matrix apply(entries v,row -> apply(row,deltaPoly))+Ms*v;
        v0:=matrix table(rs,1,(i,j) -> if i==0 then 1_B else 0_B);
        hs:={id_(B^rs)};
        for c from 1 to 6 do hs=append(hs,(coeffMat(Cs,c)-sum(toList(1..c-1),j -> hs#j*hs#(c-j)))/2);
        kj:=max(1,(4-s)//2+1);
        jets:={v0}|apply(toList(1..kj-1),q -> 0*v0);
        for c from 0 to 6 do (
            for q from 0 to kj-1 do (
                expected:=if c<q then 0*v0 else hs#(c-q)*v0/(q!);
                assert(entries(jets#q/(c!))==entries expected);
                for i from 0 to rs-1 do (
                    val:=(jets#q)_(i,0); wt:=sum(inds#i)-s*(s-1)//2+q;
                    if val!=0 then assert(first degree val==c-wt);
                );
                auditCoefficients=auditCoefficients+1;
            );
            jets=apply(toList(0..kj-1),q -> con(jets#q)+(if q==0 then 0*v0 else jets#(q-1)));
        );
        if s>=2 then (
            wrongMs:=coeffMat(Ds,1)+(1/2)*coeffMat(Cs,1);
            assert(entries(wrongMs*v0)!=entries(hs#1*v0));
        );
        auditBlocks=auditBlocks+1;
        << "PASS n=" << n << " s=" << s << " exterior_rank=" << rs << " jet_length=" << kj << " c=0..6" << endl << flush;
    );
);
<< "PASS all_blocks=" << auditBlocks << " all_divided_iterate_identities=" << auditCoefficients << "; wrong Vandermonde correction rejected" << endl;
exit 0;
