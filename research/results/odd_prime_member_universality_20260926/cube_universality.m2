-- Member universality for random dense randomized-prefix blocks on the Boolean cube.
-- N Boolean variables over F_3; block b: h random dense affine forms, t random prefix rows (CU_T, default 1);
-- J_b = clauses + (x^2 - x) = I(P_b), P_b the block's allowed cube points. Statement tested
-- (thread review 5): gr(sum_b J_b) = sum_b gr J_b (no cross-member falls) while M h <= N/2,
-- with falls expected only near or past the fill point. Reports, for M = 1.. , the excess
-- length of F[x]/(sum gr J_b) over |cap P_b| and its degrees; a single-block row is the control
-- (excess 0 by definition).
kk = ZZ/3;
out = openOut getenv "CU_OUT";
N = value(getenv "CU_N"); h = value(getenv "CU_H"); Mmax = value(getenv "CU_M");
tt = if getenv "CU_T" == "" then 1 else value(getenv "CU_T");  -- prefix rows t
S = kk[x_1..x_N, MonomialOrder => GRevLex];
X = gens S;
boole = ideal apply(X, v -> v^2 - v);
grIdeal = I -> ideal apply(flatten entries gens gb I, f -> part(first degree f, f));
dense = () -> sum(X, v -> (random kk) * v) + random kk;
clauses = (Ls, cs) -> (
    gs := apply(Ls, L -> 1 - L^2);
    Q := product(cs, c -> 1 - (sum(#gs, k -> c#k * gs#k))^2);
    apply(gs, g -> g * Q));
hf = I -> apply(toList(0..N), d -> hilbertFunction(d, S / I));
setRandomSeed 20260926;
for trial from 1 to 3 do (
    Js := {}; grs := {};
    for M from 1 to Mmax do (
        J := ideal clauses(apply(h, i -> dense()), apply(tt, j -> apply(h, k -> random kk))) + boole;
        Js = Js | {J}; grs = grs | {grIdeal J};
        a := hf(sum grs); b := hf(grIdeal(sum Js));
        diff := select(toList(0..N), d -> a#d != b#d);
        out << "N=" << N << " h=" << h << " t=" << tt << " trial=" << trial << " M=" << M << " Mh=" << M*h
            << " |capP|=" << sum b << " excess=" << (sum a - sum b) << " degrees=" << toString diff
            << " byDegree=" << toString(apply(diff, d -> a#d - b#d)) << endl; out << flush));
close out;
