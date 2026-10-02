-- Pure split of the excess-one tie sub-window (8 October 2026; cycle bmd-20261008-g).
-- For m = 2, 3, 4 (rows from research/results/bmd-20261008-f/k3-m<M>.m2, written by research/tools/bmd_tie_k3_export.gp):
-- the pure rows S = the first 3m rows of G (T^i (1+T)^(-5/2), i < 2m, and T^n (1+cT)^(-3/2), n < m) and the three extra
-- rows E = ((1+T)^(-3), the last row of G, and the two product rows P), on the columns T^d..T^(d+3m+3).
-- Prints: the gcd of the maximal minors of S (orders at 0 and 1, degree off {0, 1}); the gcd of the 3 x 3 minors of
-- E K, K generating the rank-4 kernel of S (orders, degree off {0, 1}).  By lem:cube-tie-block-minor-factorization
-- the sub-window's gcd is the product of the two.
R = QQ[c];
strip = f -> (g := f; while g % c == 0 do g = g // c; while g % (c - 1) == 0 do g = g // (c - 1); g);
ordAt = (f, l) -> (k := 0; g := f; while g % l == 0 do (g = g // l; k = k + 1); k);
report = (name, mins) -> (gg := gcd mins;
    name | ": gcd c-order " | toString ordAt(gg, c) | ", (c-1)-order " | toString ordAt(gg, c - 1)
        | ", degree off {0,1} " | toString(first degree strip gg));
for mm from 2 to 4 do (
    load ("research/results/bmd-20261008-f/k3-m" | toString mm | ".m2");
    n := numrows G;
    S := submatrix(G, toList(0 .. n - 2), );
    E := submatrix(G, {n - 1}, ) || P;
    mS := apply(subsets(numcols S, numrows S), s -> det submatrix(S, , s));
    K := gens trim ker S;
    Q := E * K;
    mQ := apply(subsets(numcols Q, 3), s -> det submatrix(Q, , s));
    print("m = " | toString mm | ": kernel rank " | toString numcols K | "; " | report("pure rows", select(mS, f -> f != 0))
        | "; " | report("extra rows on the pure kernel", select(mQ, f -> f != 0)));
    );
exit 0
