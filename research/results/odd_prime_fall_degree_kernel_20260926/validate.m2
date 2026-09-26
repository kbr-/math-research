-- Cross-check of fall_degree.cpp on a dumped instance by Groebner bases (as in cube_universality.m2).
-- Reads blocks (h rows of N+1 coefficients, last the constant; then t rows of C) and prints the
-- excess by degree dim gr(sum J)_d - dim(sum gr J)_d.
kk = ZZ/3;
N = value getenv "V_N"; h = value getenv "V_H"; t = value getenv "V_T";
S = kk[x_0..x_(N-1), MonomialOrder => GRevLex]; X = gens S;
boole = ideal apply(X, v -> v^2 - v);
grIdeal = I -> ideal apply(flatten entries gens gb I, f -> part(first degree f, f));
lines' = select(lines get getenv "V_IN", l -> l != "");
blocks = {}; i := 0;
while i < #lines' do (
    i = i + 1;
    A := apply(h, k -> apply(separate(" ", lines'#(i+k)), w -> if w == "" then null else value w));
    A = apply(A, r -> select(r, w -> w =!= null));
    C := apply(t, k -> select(apply(separate(" ", lines'#(i+h+k)), w -> if w == "" then null else value w), w -> w =!= null));
    blocks = blocks | {(A, C)}; i = i + h + t);
Js = apply(blocks, bc -> (
    (A, C) := bc;
    Ls := apply(A, r -> sum(N, j -> (r#j)_kk * X#j) + (r#N)_kk);
    gs := apply(Ls, L -> 1 - L^2);
    Q := product(C, c -> 1 - (sum(h, k -> (c#k)_kk * gs#k))^2);
    ideal(apply(gs, g -> g * Q)) + boole));
a = apply(toList(0..N), d -> hilbertFunction(d, S / sum apply(Js, grIdeal)));
b = apply(toList(0..N), d -> hilbertFunction(d, S / grIdeal(sum Js)));
print("M2 excess by degree (d=1..N): " | toString(apply(toList(1..N), d -> a#d - b#d)) | "  |capP|=" | toString(sum b));
