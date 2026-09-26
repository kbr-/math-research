-- Member-pair gluing in the form-value model (prop:single-block-falls, A3 for W_RS).
-- Two randomized-prefix blocks with forms affine in joint variables z (a basis of their joint
-- span); J_b = ideal(clauses of block b) + (z^3 - z) is the vanishing ideal of the block's
-- allowed preimage P_b. Statement tested: gr(J_1 + J_2) = gr J_1 + gr J_2 (no fall from
-- combining members). Reports the Hilbert functions of F[z]/(grJ1+grJ2) and F[z]/gr(J1+J2)
-- (whose total is |P_1 cap P_2|) and the degrees where they differ. gr is taken from the top
-- forms of a Groebner basis in a degree order (GRevLex), which generate gr.
kk = ZZ/3;
out = openOut getenv "MP_OUT";
grIdeal = I -> ideal apply(flatten entries gens gb I, f -> part(first degree f, f));
clauses = (Ls, cs) -> (
    gs := apply(Ls, L -> 1 - L^2);
    Q := product(cs, c -> 1 - (sum(#gs, k -> c#k * gs#k))^2);
    apply(gs, g -> g * Q));
hfs = (M, top) -> apply(toList(0..top), d -> hilbertFunction(d, M));
case1 = (label, r, L1, L2, c1, c2) -> (
    S := ring first L1;
    boole := ideal apply(gens S, v -> v^3 - v);
    J1 := ideal clauses(L1, c1) + boole;
    J2 := ideal clauses(L2, c2) + boole;
    G1 := grIdeal J1; G2 := grIdeal J2; G12 := grIdeal(J1 + J2);
    top := 2 * r;
    a := hfs(S / (G1 + G2), top);
    b := hfs(S / G12, top);
    diff := select(toList(0..top), d -> a#d != b#d);
    out << label << " r=" << r << " len(grJ1+grJ2)=" << sum a << " |P1capP2|=" << sum b
        << " fall=" << (a != b) << " degrees=" << toString diff
        << " excess=" << toString(apply(diff, d -> a#d - b#d)) << endl; out << flush);
rc = h -> apply(h, k -> random kk);
setRandomSeed 20260926;
h := 4;
for trial from 1 to 3 do (
    -- control: independent blocks on disjoint variables
    S0 := kk[z_1..z_(2*h), MonomialOrder => GRevLex];
    Z0 := gens S0;
    case1("independent", 2*h, apply(h, i -> Z0#i), apply(h, i -> Z0#(h+i)), {rc h}, {rc h});
    -- one shared form, equal constants / different constants
    S := kk[z_1..z_(2*h-1), MonomialOrder => GRevLex];
    Z := gens S;
    L1 := apply(h, i -> Z#i);
    for a from 0 to 2 do (
        L2 := {Z#0 + a_kk} | apply(h - 1, i -> Z#(h+i));
        case1("shared form, constant shift " | toString a, 2*h-1, L1, L2, {rc h}, {rc h}));
    -- one generic dependency: block 2's first form is a random combination of block 1's forms
    L2 := {sum(h, i -> (random kk) * Z#i) + (random kk)} | apply(h - 1, i -> Z#(h+i));
    case1("generic dependency", 2*h-1, L1, L2, {rc h}, {rc h}));
close out;
