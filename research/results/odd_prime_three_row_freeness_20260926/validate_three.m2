-- Cross-check of three_row_freeness.cpp on a dumped instance by Groebner bases (m = 3 rows): J = gr I(Q),
-- A = S/J, Lambda = F_3[r1, r2]/(r^3) by the row sums of rows 1 and 2; Tor_1 by the linear-algebra routine
-- of degeneration_tor.m2 (cycles of A_{d-1}^2 -> A_d modulo Koszul and Frobenius boundaries), d = 1..dmax.
kk = ZZ/3;
mr = value getenv "V_MR"; Ncol = value getenv "V_NCOL"; N = mr * Ncol; h = value getenv "V_H"; t = value getenv "V_T";
S = kk[x_0..x_(N-1), MonomialOrder => GRevLex]; X = gens S;
boole = ideal(apply(X, v -> v^2 - v)) + ideal(flatten flatten apply(Ncol, c -> apply(mr, r -> apply(toList(r+1..mr-1), s -> X#(r*Ncol + c) * X#(s*Ncol + c))))) + ideal(sum X - mr);
grIdeal = I -> ideal apply(flatten entries gens gb I, f -> part(first degree f, f));
lines' = select(lines get getenv "V_IN", l -> l != "");
blocks = {}; i := 0;
while i < #lines' do (
    i = i + 1;
    A := apply(h, k -> select(apply(separate(" ", lines'#(i+k)), w -> if w == "" then null else value w), w -> w =!= null));
    C := apply(t, k -> select(apply(separate(" ", lines'#(i+h+k)), w -> if w == "" then null else value w), w -> w =!= null));
    blocks = blocks | {(A, C)}; i = i + h + t);
I = boole + sum(apply(blocks, bc -> (
    (A, C) := bc;
    Ls := apply(A, r -> sum(N, j -> (r#j)_kk * X#j) + (r#N)_kk);
    gs := apply(Ls, L -> 1 - L^2);
    Q := product(C, c -> 1 - (sum(h, k -> (c#k)_kk * gs#k))^2);
    ideal(apply(gs, g -> g * Q)))) | {ideal(0_S)});
J = grIdeal I; Aq = S / J;
R1 = sub(sum(Ncol, j -> X#j), Aq); R2 = sub(sum(Ncol, j -> X#(Ncol + j)), Aq);
dmax = value getenv "V_DMAX";
mult = (f, k, df) -> (Bk := basis(k, Aq); Bt := basis(k + df, Aq);
    if numColumns Bk == 0 or numColumns Bt == 0 then map(kk^(numColumns Bt), kk^(numColumns Bk), 0)
    else sub(last coefficients(f * Bk, Monomials => Bt), kk));
dimA = k -> if k < 0 then 0 else numColumns basis(k, Aq);
tor = apply(toList(1..dmax), d -> (
    phi := mult(R1, d-1, 1) | mult(R2, d-1, 1);
    kerDim := 2 * dimA(d-1) - rank phi;
    bd := {};
    if d >= 2 and dimA(d-2) > 0 then bd = bd | {mult(R2, d-2, 1) || (- mult(R1, d-2, 1))};
    if d >= 3 and dimA(d-3) > 0 then (
        z := map(kk^(dimA(d-1)), kk^(dimA(d-3)), 0);
        bd = bd | {mult(R1^2, d-3, 2) || z, z || mult(R2^2, d-3, 2)});
    kerDim - (if #bd == 0 then 0 else rank fold((a, b) -> a | b, bd))));
print("M2 tor1ByDegree: " | toString tor | "  hilbQ: " | toString apply(toList(0..dmax), d -> dimA d));
