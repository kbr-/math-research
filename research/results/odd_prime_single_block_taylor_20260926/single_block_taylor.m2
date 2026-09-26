-- Single-block randomized Taylor generation (thm:randomized-taylor-glue), weak monomial algebra.
-- Statement tested: for one randomized-prefix block with t = 1 (tops tau_i = l_i^2 q^2,
-- q = sum_k c_k l_k^2) in A = F_3[x_(i,j)]/(x^2, column collisions), the degree-s syzygies
-- (g_i in A_{s-6}, sum g_i tau_i = 0) equal the span of (F1) l_i e_i, (F2) q e_i and
-- (K1) l_k^2 e_i - l_i^2 e_k, for s = 7..N. Reports kernel dimension, generator rank, and
-- whether the generators lie in the kernel. Control: a duplicated form (l_2 = l_1).
kk = ZZ/3;
m = 3; N = value(getenv "SBT_N");
S = kk[x_(1,1)..x_(m,N)];
I = ideal(apply(gens S, v -> v^2)) + ideal flatten flatten apply(toList(1..N), j ->
      flatten apply(toList(1..m), i -> apply(toList(i+1..m), k -> x_(i,j)*x_(k,j))));
A = S/I;
out = openOut getenv "SBT_OUT";
rnd = () -> sum(gens A, v -> (random kk) * v);
stackCols = (h, i, Cmat, nd) -> (
    -- place the nd x c block Cmat in component i of an (h*nd) x c matrix
    c := numColumns Cmat;
    matrix apply(h, k -> {if k == i then Cmat else map(kk^nd, kk^c, 0)}));
coeffs = (polys, Bmat) -> sub(last coefficients(matrix{polys}, Monomials => Bmat), kk);
runCase = (label, ls, cs) -> (
    h := #ls;
    q := sum(h, k -> cs#k * (ls#k)^2);
    taus := apply(ls, l -> l^2 * q^2);
    out << label << " h=" << h << " tau_nonzero=" << toString(apply(taus, tt -> tt != 0)) << endl;
    for s from 7 to N do (
        Bd := basis(s - 6, A); nd := numColumns Bd; bd := flatten entries Bd;
        Bs := basis(s, A);
        Mat := fold((a, b) -> a | b, apply(h, i -> coeffs(apply(bd, b -> taus#i * b), Bs)));
        rk := rank Mat;
        kerdim := h * nd - rk;
        gensList := {};
        if s >= 7 then (
            b1 := flatten entries basis(s - 7, A);
            gensList = gensList | apply(h, i -> stackCols(h, i, coeffs(apply(b1, b -> ls#i * b), Bd), nd)));
        if s >= 8 then (
            b2 := flatten entries basis(s - 8, A);
            gensList = gensList | apply(h, i -> stackCols(h, i, coeffs(apply(b2, b -> q * b), Bd), nd));
            for i from 0 to h - 1 do for k from i + 1 to h - 1 do
                gensList = gensList | {stackCols(h, i, coeffs(apply(b2, b -> (ls#k)^2 * b), Bd), nd)
                                      - stackCols(h, k, coeffs(apply(b2, b -> (ls#i)^2 * b), Bd), nd)});
        Gm := fold((a, b) -> a | b, gensList);
        inKer := (Mat * Gm) == 0;
        grk := rank Gm;
        out << "  s=" << s << " domain=" << h * nd << " rankMap=" << rk << " kernel=" << kerdim
            << " genRank=" << grk << " gensInKernel=" << inKer << " taylor=" << (grk == kerdim) << endl;
        out << flush;
    ));
for seed from 1 to 3 do (
    setRandomSeed seed;
    ls := apply(4, i -> rnd());
    cs := apply(4, i -> random kk);
    runCase("random seed " | toString seed, ls, cs));
setRandomSeed 7;
l1 := rnd(); l3 := rnd(); l4 := rnd();
runCase("control duplicated form", {l1, l1, l3, l4}, {1_kk, 2_kk, 1_kk, 1_kk});
close out;
