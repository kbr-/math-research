-- Sequential freeness for three tops with one linear relation (entry-2026-09-27-three-top-relations).
--
-- Tested statements.  Three tops tau_i = A_i^2 B_i whose six forms satisfy exactly one linear relation, with support
-- meeting all three tops (so each pair of tops has four independent forms).  With signs absorbed, the relation is
-- sum of the forms in a pattern P = (P_1, P_2, P_3), P_i a nonempty subset of {A_i, B_i}; up to permuting the tops
-- there are 10 patterns.  Where the square-free algebra is free over the truncated algebra T_V of the 5-dimensional
-- span (thm:column-support-freeness, prop:group-freeness), its syzygies and quotients are those of T_V, so both
-- questions are asked in T_V = F_3[five basis forms]/(cubes):
--   (1) the Taylor defect: first degree where the syzygies of (tau_1, tau_2, tau_3) exceed the span of the Frobenius
--       syzygies A_i e_i, B_i^2 e_i and the Koszul pairs tau_j e_i - tau_i e_j (-1 if none);
--   (2) prop:sequential-freeness's hypothesis for each ordering (i, j, l): first degree where T_V/(tau_i) fails to be
--       free over T_j, or T_V/(tau_i, tau_j) over T_l (Hilbert-function test of prop:syzygies-as-tor; -1 if free).
-- Usage: M2 --script three_top_sequential.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
S := kk[x1,x2,x3,x4,x5];
R := S / ideal(x1^3, x2^3, x3^3, x4^3, x5^3);
use R;
maxDeg := 11;
hf := (M) -> apply(toList(0..maxDeg), d -> hilbertFunction(d, M));
firstFree := (I, A, B) -> (
    -- first failure of R/I as a module over F_3[A,B]/(A^3,B^3), -1 if free
    M := R^1 / I; Q := R^1 / (I + ideal(A, B));
    h := hf M; q := hf Q;
    pred := apply(toList(0..maxDeg), d -> sum(toList(0..min(d,4)), e -> ({1,2,3,2,1})#e * (if d-e >= 0 then q#(d-e) else 0)));
    diffs := select(toList(0..maxDeg), d -> pred#d != h#d);
    if #diffs == 0 then -1 else min diffs);
-- patterns: for each top a nonempty subset of {A,B}: 1 = {A}, 2 = {B}, 3 = {A,B}; multisets of size 3; the first
-- pattern {1,0,1} (A3 = -A1, top 2 outside the relation) is the positive control of a shared form (lem:shared-direction-pure-tops)
pats := {{1,0,1},{1,1,1},{1,1,2},{1,1,3},{1,2,2},{1,2,3},{1,3,3},{2,2,2},{2,2,3},{2,3,3},{3,3,3}};
for p in pats do (
    -- basis x1..x5 = A1, B1, A2, B2 and one form of top 3 not eliminated; the eliminated form is the last one in
    -- top 3's part of the pattern and equals minus the sum of the other forms of the pattern
    A1 := x1; B1 := x2; A2 := x3; B2 := x4;
    other := 0_R;
    if p#0 == 1 or p#0 == 3 then other = other + A1;
    if p#0 == 2 or p#0 == 3 then other = other + B1;
    if p#1 == 1 or p#1 == 3 then other = other + A2;
    if p#1 == 2 or p#1 == 3 then other = other + B2;
    A3 := 0_R; B3 := 0_R;
    if p#2 == 1 then (A3 = -other; B3 = x5);
    if p#2 == 2 then (B3 = -other; A3 = x5);
    if p#2 == 3 then (A3 = x5; B3 = -(other + x5));
    forms := {{A1,B1},{A2,B2},{A3,B3}};
    t := apply(forms, ab -> (ab#0)^2 * ab#1);
    F := R^{-3,-3,-3};
    phi := map(R^1, F, matrix{t});
    K := kernel phi;
    -- Taylor span generators as coordinate lists (Frobenius syzygies and Koszul pairs)
    unit := (i, c) -> apply(3, k -> if k == i then c else 0_R);
    tay := {};
    for i from 0 to 2 do tay = tay | {unit(i, forms#i#0), unit(i, (forms#i#1)^2)};
    for i from 0 to 2 do for j from i+1 to 2 do tay = tay | {apply(3, k -> if k == i then t#j else if k == j then -(t#i) else 0_R)};
    Tay := image map(F, , transpose matrix tay);
    defect := select(toList(0..maxDeg+3), d -> hilbertFunction(d, K) != hilbertFunction(d, Tay));
    firstDefect := if #defect == 0 then -1 else min defect;
    seqs := {};
    for o in {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}} do (
        i := o#0; j := o#1; l := o#2;
        s1 := firstFree(ideal(0_R), forms#i#0, forms#i#1);
        s2 := firstFree(ideal(t#i), forms#j#0, forms#j#1);
        s3 := firstFree(ideal(t#i, t#j), forms#l#0, forms#l#1);
        seqs = seqs | {"[" | toString(s1) | ", " | toString(s2) | ", " | toString(s3) | "]"});
    f << "{\"pattern\": [" << concatenate between(", ", apply(p, toString)) << "], \"first_taylor_defect\": " << firstDefect
      << ", \"sequential_first_failures\": [" << concatenate between(", ", seqs) << "]}" << endl;
    );
close f;
