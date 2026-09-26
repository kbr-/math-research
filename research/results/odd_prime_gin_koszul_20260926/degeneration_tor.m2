-- Does Groebner degeneration preserve row freeness? (route review's generic-initial-ideal lead)
-- Board: m = 3 rows, N = DT_N columns (5 unless set) over F_3; P = column-injective assignments with total
-- occupancy = m = 0 mod 3; Q = P cut by randomized-prefix blocks (t = 1, h = 3, dense forms).
-- gr F^Q = S/J, J the top-form ideal of I(Q) (degree-order Groebner basis). Lambda =
-- F_3[r_1, r_2]/(r^3) acts by the row sums of rows 1, 2 (thm:global-closure-gluing, lem:defect-gluing).
-- Statement tested: Tor_1^Lambda(F_3, S/J) against Tor_1^Lambda(F_3, S/in(J)) for monomial
-- initial ideals in(J) (flat degeneration, so Tor can only grow); the lead needs no growth in
-- the degrees that matter. Reports the Hilbert functions of both Tor_1 modules.
kk = ZZ/3;
out = openOut getenv "DT_OUT";
m = 3; N = value(getenv "DT_N");
S = kk[x_(1,1)..x_(m,N), MonomialOrder => GRevLex];
X = gens S;
cell = (i, j) -> x_(i,j);
base = ideal(apply(X, v -> v^2 - v)) + ideal(flatten flatten apply(toList(1..N), j ->
          apply(toList(1..m), i -> apply(toList(i+1..m), k -> cell(i,j) * cell(k,j))))) + ideal(sum X);
rowsum = i -> sum(toList(1..N), j -> cell(i,j));
RS1 = rowsum 1; RS2 = rowsum 2;  -- fixed as elements of S before other rings rebind the names
Lam = kk[r_1, r_2] / ideal(r_1^3, r_2^3);
grIdeal = I -> ideal apply(flatten entries gens gb I, f -> part(first degree f, f));
-- Tor_1^Lambda(F_3, S/J) degree by degree, from the minimal resolution of F_3 over Lambda:
-- kernel of A_{d-1}^2 -> A_d, (a,b) -> r_1 a + r_2 b, modulo the Koszul relation (r_2 a, -r_1 a)
-- and the Frobenius relations (r_1^2 a, 0), (0, r_2^2 a).
tor1 = (J, f1, f2) -> (
    A := S / J;
    R1 := sub(f1, A); R2 := sub(f2, A);
    mult := (f, k, df) -> (
        Bk := basis(k, A); Bt := basis(k + df, A);
        if numColumns Bk == 0 or numColumns Bt == 0 then map(kk^(numColumns Bt), kk^(numColumns Bk), 0)
        else sub(last coefficients(f * Bk, Monomials => Bt), kk));
    dimA := k -> if k < 0 then 0 else numColumns basis(k, A);
    apply(toList(0..N+1), d -> (
        if d < 1 or dimA(d-1) == 0 then 0 else (
            phi := mult(R1, d-1, 1) | mult(R2, d-1, 1);
            kerDim := 2 * dimA(d-1) - rank phi;
            bd := {};
            if d >= 2 and dimA(d-2) > 0 then bd = bd | {mult(R2, d-2, 1) || (- mult(R1, d-2, 1))};
            if d >= 3 and dimA(d-3) > 0 then (
                z := map(kk^(dimA(d-1)), kk^(dimA(d-3)), 0);
                bd = bd | {mult(R1^2, d-3, 2) || z, z || mult(R2^2, d-3, 2)});
            bdRank := if #bd == 0 then 0 else rank fold((a, b) -> a | b, bd);
            kerDim - bdRank))));
dense = () -> sum(X, v -> (random kk) * v) + random kk;
clauses = (Ls, c) -> (
    gs := apply(Ls, L -> 1 - L^2);
    Q := 1 - (sum(#gs, k -> c#k * gs#k))^2;
    apply(gs, g -> g * Q));
report = (label, cons) -> (
    I := base + ideal(cons);
    J := grIdeal I;
    npts := sum(toList(0..2*m*N), d -> hilbertFunction(d, S / J));
    t0 := tor1(J, RS1, RS2);
    J1 := monomialIdeal leadTerm gb J;
    t1 := tor1(ideal J1, RS1, RS2);
    Sl := kk[gens S, MonomialOrder => Lex];
    Jl := sub(ideal leadTerm gb sub(J, Sl), S);
    t2 := tor1(Jl, RS1, RS2);
    -- generic initial ideal: random coordinates g, then grevlex; Lambda acts through g(r_i)
    Gm := random(kk^(#X), kk^(#X));
    while det Gm == 0 do Gm = random(kk^(#X), kk^(#X));  -- the coordinate change must be invertible
    g := map(S, S, flatten entries (matrix{X} * sub(Gm, S)));
    gJ := g J;
    t3 := tor1(ideal leadTerm gb gJ, g RS1, g RS2);
    t4 := tor1(gJ, g RS1, g RS2);  -- sanity: isomorphic module, must equal t0
    out << label << " |Q|=" << npts << " Tor1(grF^Q)=" << toString t0
        << " Tor1(in_grevlex)=" << toString t1 << " Tor1(in_lex)=" << toString t2
        << " Tor1(gin)=" << toString t3 << " jump=" << (t0 != t1 or t0 != t2) << " ginJump=" << (t0 != t3) << " isoCheck=" << (t4 == t0) << endl; out << flush);
setRandomSeed 20260926;
if getenv "DT_ONLYBASE" == "1" then (report("full P (control)", {}); close out; exit 0);
report("full P (control)", {});
for trial from 1 to 3 do (
    L := apply(3, i -> dense());
    report("one block", clauses(L, apply(3, k -> random kk)));
    -- connected triangle family: block 2 shares a form with block 1, block 3 with both
    L2 := {L#0 + random kk, dense(), dense()};
    L3 := {L2#1 + random kk, L#1 + random kk, dense()};
    report("triangle family", clauses(L, apply(3, k -> random kk)) | clauses(L2, apply(3, k -> random kk))
        | clauses(L3, apply(3, k -> random kk))));
close out;
