-- Rank-three kernel of the excess-one tie sub-window (8 October 2026; cycle bmd-20261008-f).
-- For m = 2, 3, 4 (files research/results/bmd-20261008-f/k3-m<M>.m2 from research/tools/bmd_tie_k3_export.gp):
-- G = the c-free rows and the g-rows (3m+1 rows), P = the two product rows, over QQ[c].  K = a basis of ker G
-- (free of rank 3 over the PID QQ[c]); prints its column degrees; then the three 2 x 2 minors of P K: degrees,
-- orders at c = 0 and c = 1, and the degree of their gcd with the powers of c and c - 1 removed (0 = no special value
-- off {0, 1}, by lem:cube-tie-two-by-three-reduction where G has constant rank).  K is a generating set of the free
-- rank-3 module ker G, possibly not minimal; the ideal of 2 x 2 minors of P K is the same for every generating set.
R = QQ[c];
strip = f -> (g := f; while g % c == 0 do g = g // c; while g % (c - 1) == 0 do g = g // (c - 1); g);
ordAt = (f, l) -> (k := 0; g := f; while g % l == 0 do (g = g // l; k = k + 1); k);
for mm from 2 to 4 do (
    load ("research/results/bmd-20261008-f/k3-m" | toString mm | ".m2");
    K := gens trim ker G;
    degs := apply(numcols K, j -> max apply(numrows K, i -> (e := K_(i, j); if e == 0 then -1 else first degree e)));
    Q := P * K;
    mins := select(apply(subsets(numcols Q, 2), s -> det submatrix(Q, , s)), f -> f != 0);
    gg := gcd mins;
    print("m = " | toString mm | ": rank of ker G = " | toString numcols K | ", column degrees of K = " | toString degs
        | "; 2x2 minors of P K: degrees " | toString apply(mins, f -> if f == 0 then -1 else first degree f)
        | ", c-orders " | toString apply(mins, f -> ordAt(f, c)) | ", (c-1)-orders " | toString apply(mins, f -> ordAt(f, c - 1))
        | "; gcd: degree " | toString(first degree gg) | ", c-order " | toString ordAt(gg, c) | ", (c-1)-order "
        | toString ordAt(gg, c - 1) | ", degree off {0,1} " | toString(first degree strip gg));
    );
exit 0
