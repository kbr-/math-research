-- Exact audit of the exterior-companion descent for cube coefficient kernels.
-- Every n=1..4, every exterior block s=0..n, and all coefficients T^0..T^6,
-- over QQ, GF(3), GF(5).  Tests the full polynomial intertwining identity,
-- square-root recurrence, all subset Vandermondes, and modular Artin dimensions.
-- Also exhibits the failure of arbitrary collision-specialization equivalence.
-- All matrix operations use Macaulay2; no dependency installation is required.
-- Usage: M2 --script research/tools/bmd_cube_companion_descent.m2

coeffMatrix = (M,T,j,R) -> matrix apply(entries M, row -> apply(row, v -> sub(coefficient(T^j,v),R)));
sameEntries = (A,B) -> entries A == entries B; -- inferred map shifts are not this audit's grading
maxjet = 6;
totalBlocks = 0; totalCoefficients = 0;
for prime in {0,3,5} do for n from 1 to 4 do (
    kk := if prime == 0 then QQ else ZZ/prime;
    R := kk[a_1..a_n];
    es := apply(toList(1..n), j -> sum(subsets(n,j), I -> product(I, i -> R_i)));
    Z := matrix table(n,n,(i,j) -> if j < n-1 then (if i==j+1 then 1_R else 0_R) else (-1)^(n-i+1)*es#(n-i-1));
    E := matrix table(n,n,(i,j) -> R_i^j);
    assert sameEntries(E*Z,diagonalMatrix(toList gens R)*E);
    assert(det E != 0);
    artin := R/(ideal es);
    assert(degree artin == product(toList(1..n)));
    RT := R[T];
    scalarRoots := apply(n, i -> (
        cs := {1_R};
        for j from 1 to maxjet do cs = append(cs, ((if j==1 then R_i else 0_R)-sum(toList(1..j-1), v -> cs#v*cs#(j-v)))/2);
        sum(toList(0..maxjet), j -> sub(cs#j,RT)*T^j)));
    for s from 0 to n do (
        subsetsS := subsets(n,s);
        rankS := #subsetsS;
        C := exteriorPower(s,id_(RT^n)+T*sub(Z,RT));
        Cc := apply(toList(0..maxjet), j -> coeffMatrix(C,T,j,R));
        H := {id_(R^rankS)};
        for j from 1 to maxjet do H = append(H,(Cc#j-sum(toList(1..j-1), v -> H#v*H#(j-v)))/2);
        for j from 0 to maxjet do assert sameEntries(sum(toList(0..j), v -> H#v*H#(j-v)),Cc#j);
        Es := exteriorPower(s,E);
        assert(det Es != 0);
        v0 := matrix table(rankS,1,(i,j) -> if i==0 then 1_R else 0_R);
        productsS := apply(subsetsS, I -> sub(product(I, i -> scalarRoots#i),RT));
        for j from 0 to maxjet do (
            scalarCoeff := apply(productsS, f -> sub(coefficient(T^j,f),R));
            if not sameEntries(Es*H#j,diagonalMatrix scalarCoeff*Es) then (
                << "INTERTWINING_FAILURE n=" << n << " s=" << s << " j=" << j
                   << " left=" << entries(Es*H#j) << " right=" << entries(diagonalMatrix scalarCoeff*Es) << endl;
                error "intertwining identity failed";
            );
            assert sameEntries(Es*H#j*v0,matrix table(rankS,1,(i,k) -> scalarCoeff#i*(Es*v0)_(i,0)));
            for i from 0 to rankS-1 do (
                entry := (H#j*v0)_(i,0);
                wt := sum(subsetsS#i)-s*(s-1)//2;
                if entry != 0 then assert(first degree entry == j-wt);
            );
            totalCoefficients = totalCoefficients + 1;
        );
        for i from 0 to rankS-1 do (
            I := subsetsS#i;
            vand := product(subsets(s,2), ij -> R_(I#(ij#1))-R_(I#(ij#0)));
            assert((Es*v0)_(i,0)==vand);
        );
        if s>0 then assert(Es*H#1 != 0); -- wrong constant square root fails
        totalBlocks = totalBlocks + 1;
        << "PASS field=" << prime << " n=" << n << " s=" << s << " rank=" << rankS
           << " coefficients=0.." << maxjet << " Artin_rank=" << degree artin << endl << flush;
    );
);
-- A degree-two repeated-root collision: raw evaluation loses rank, while the
-- companion lattice keeps a derivative direction.  This is deliberately NOT
-- asserted to preserve specialized kernels.
Rc = QQ[a];
Zc = matrix{{0,-a^2},{1,2*a}};
vc = matrix{{1},{0}};
comp = vc | (Zc*vc/2) | (-Zc^2*vc/8);
raw = matrix{{1,a/2,-a^2/8},{1,a/2,-a^2/8}};
assert(rank comp==2 and rank raw==1);
<< "COLLISION_CONTROL raw_rank=" << rank raw << " companion_rank=" << rank comp << endl;
<< "PASS total_blocks=" << totalBlocks << " total_polynomial_coefficient_identities=" << totalCoefficients << endl;
exit 0;
