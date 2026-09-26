-- Single-direction test of a truncated Dade lemma for the weak base (27 September 2026).
-- G = F[x_(i,c)]/(x_(i,c) x_(j,c), s) on m rows and N columns (s = sum of all cells), over GF(81).
-- Lambda-Tor_1 over the row sums r_1..r_(m-1) (r_i^3 = 0) versus Tor_1 over k[u]/(u^3) for single
-- directions u = sum_i alpha_i r_i. Tested statement: the base's first degree of non-freeness over
-- Lambda is detected by some single direction (all of P^(m-2)(F_9) and random GF(81) directions).
-- Tor_1^{k[u]/(u^3)}(G)_d = dim G_(d-1) - rank(u: G_(d-1) -> G_d) - rank(u^2: G_(d-3) -> G_(d-1)).
m = value getenv "SD_M"; N = value getenv "SD_N"; D = value getenv "SD_D";
k = GF(81, Variable => a);
R = k[x_(0,0)..x_(m-1,N-1)];
I = ideal flatten flatten apply(N, c -> flatten apply(m, i -> apply(toList(i..m-1), j -> x_(i,c)*x_(j,c)))) +
    ideal(sum flatten apply(m, i -> apply(N, c -> x_(i,c))));
S = R/I;
r = apply(m, i -> sum apply(N, c -> sub(x_(i,c), S)));
B = d -> if d < 0 then null else basis(d, S);
dimS = d -> if d < 0 then 0 else numColumns B(d);
mult = (f, e, d) -> (  -- matrix of multiplication by f from degree d-e to degree d
    if d - e < 0 or dimS(d-e) == 0 or dimS(d) == 0 then return null;
    last coefficients(f * B(d-e), Monomials => B(d)));
rk = M -> if M === null then 0 else rank M;
print("m=" | toString m | " N=" | toString N | " hilb=" | toString apply(D+1, d -> dimS d));
-- Lambda-Tor_1 over r_1..r_(m-1): H at G_(d-1)^(m-1) of G_(d-3)^(m-1) + G_(d-2)^binom(m-1,2) -> G_(d-1)^(m-1) -> G_d
lambdaTor = d -> (
    gens1 = drop(r, 1); q = #gens1;
    if dimS(d-1) == 0 then return 0;
    phi = if dimS(d) == 0 then null else fold((A,Bm) -> A | Bm, apply(gens1, g -> mult(g, 1, d)));
    cols = {};
    for i from 0 to q-1 do if dimS(d-3) > 0 then (
        blk = apply(q, j -> if j == i then mult(gens1#i^2, 2, d-1) else map(k^(dimS(d-1)), k^(dimS(d-3)), 0));
        cols = append(cols, fold((A,Bm) -> A || Bm, blk)));
    for i from 0 to q-1 do for j from i+1 to q-1 do if dimS(d-2) > 0 then (
        blk = apply(q, l -> if l == i then mult(gens1#j, 1, d-1) else if l == j then -mult(gens1#i, 1, d-1)
                            else map(k^(dimS(d-1)), k^(dimS(d-2)), 0));
        cols = append(cols, fold((A,Bm) -> A || Bm, blk)));
    psi = if #cols == 0 then null else fold((A,Bm) -> A | Bm, cols);
    q * dimS(d-1) - rk phi - rk psi);
singleTor = (u, d) -> dimS(d-1) - rk mult(u, 1, d) - rk mult(u^2, 2, d-1);
print("LambdaTor1 by degree 1.." | toString D | ": " | toString apply(toList(1..D), lambdaTor));
F9 = select(apply(toList(0..80), e -> a^e), z -> z^8 == 1) | {0_k};  -- the subfield F_9 inside GF(81)
dirs = if m == 3 then ({{1_k, 0_k}} | apply(F9, z -> {z, 1_k})) else {};
setRandomSeed 7;
dirs = dirs | apply(4, i -> apply(m-1, j -> random k));
for alpha in dirs do (
    u = sum apply(m-1, i -> alpha#i * r#(i+1));
    print("direction " | toString alpha | " singleTor by degree: " | toString apply(toList(1..D), d -> singleTor(u, d))));
