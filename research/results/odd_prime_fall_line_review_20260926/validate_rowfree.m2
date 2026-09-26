-- Cross-check of row_freeness.cpp on a dumped instance by Groebner bases (m = 2 rows): the weak base
-- (Booleanity, column collisions, occupancy sum x = m) plus the members' clauses generate I(Q); with
-- J = gr I(Q), A = S/J and r the row sum of row 1, prints dim ker(r: A_d -> A_{d+1}) - rank(r^2: A_{d-2} -> A_d)
-- for d = 0..Ncol-1, which is Tor_1^Lambda(F_3, A) in the kernel's indexing.
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
J = grIdeal I; Aq = S / J; r = sub(sum(Ncol, j -> X#j), Aq);
mult = (f, k, df) -> (Bk := basis(k, Aq); Bt := basis(k + df, Aq);
    if numColumns Bk == 0 or numColumns Bt == 0 then map(kk^(numColumns Bt), kk^(numColumns Bk), 0)
    else sub(last coefficients(f * Bk, Monomials => Bt), kk));
dimA = k -> if k < 0 then 0 else numColumns basis(k, Aq);
tor = apply(toList(0..Ncol-1), d -> (dimA d - rank mult(r, d, 1)) - (if d >= 2 then rank mult(r^2, d-2, 2) else 0));
print("M2 tor1ByDegree: " | toString tor | "  hilbQ: " | toString apply(toList(0..Ncol), d -> dimA d));
