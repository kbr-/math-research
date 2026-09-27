-- Relation length and Taylor defect (entry-2026-09-27-three-top-relations).
--
-- Tested statement.  For r tops tau_i = A_i^2 B_i whose 2r forms satisfy exactly one linear relation
-- A_1 + ... + A_r = 0 (the squared forms only), in the truncated algebra T_V of the (2r-1)-dimensional span (where the
-- square-free or weak algebra is free over T_V, its syzygies are those of T_V): the first total degree at which the
-- syzygies of (tau_1..tau_r) exceed the span of the Frobenius syzygies A_i e_i, B_i^2 e_i and the Koszul pairs, and the
-- first degree at which the last quotient T_V/(tau_1..tau_{r-1}) fails to be free over T_r (prop:sequential-freeness).
-- The question is whether the defect degree grows with r.
-- Usage: M2 --script relation_length_defects.m2 OUT RMAX
out := scriptCommandLine#1;
rmax := value scriptCommandLine#2;
f := openOut out;
kk := ZZ/3;
for r from 2 to rmax do (
    n := 2*r - 1;
    x := symbol x;
    S := kk[x_1..x_n];
    R := S / ideal apply(n, i -> x_(i+1)^3);
    use R;
    -- A_i = x_(2i-1) for i < r, B_i = x_(2i) for i < r, A_r = -(A_1 + ... + A_{r-1}), B_r = x_n
    As := apply(r-1, i -> x_(2*i+1)); Bs := apply(r-1, i -> x_(2*i+2));
    As = As | {-(sum As)}; Bs = Bs | {x_n};
    t := apply(r, i -> (As#i)^2 * Bs#i);
    F := R^(toList(r:-3));
    K := kernel map(R^1, F, matrix{t});
    unit := (i, c) -> apply(r, k -> if k == i then c else 0_R);
    tay := {};
    for i from 0 to r-1 do tay = tay | {unit(i, As#i), unit(i, (Bs#i)^2)};
    for i from 0 to r-1 do for j from i+1 to r-1 do tay = tay | {apply(r, k -> if k == i then t#j else if k == j then -(t#i) else 0_R)};
    Tay := image map(F, , transpose matrix tay);
    top := 2*n + 3;
    defect := select(toList(4..top), d -> hilbertFunction(d, K) != hilbertFunction(d, Tay));
    first := if #defect == 0 then -1 else min defect;
    dims := apply(defect, d -> hilbertFunction(d, K) - hilbertFunction(d, Tay));
    -- sequential hypothesis at the last step
    M := R^1 / ideal(take(t, r-1)); Q := R^1 / (ideal(take(t, r-1)) + ideal(As#(r-1), Bs#(r-1)));
    h := apply(toList(0..2*n), d -> hilbertFunction(d, M)); q := apply(toList(0..2*n), d -> hilbertFunction(d, Q));
    pred := apply(toList(0..2*n), d -> sum(toList(0..min(d,4)), e -> ({1,2,3,2,1})#e * q#(d-e)));
    fails := select(toList(0..2*n), d -> pred#d != h#d);
    seqFirst := if #fails == 0 then -1 else min fails;
    f << "{\"r\": " << r << ", \"first_taylor_defect\": " << first << ", \"defect_degrees\": [" << concatenate between(", ", apply(defect, toString)) << "]"
      << ", \"defect_dims\": [" << concatenate between(", ", apply(dims, toString)) << "]" << ", \"sequential_last_step_first_failure\": " << seqFirst << "}" << endl;
    );
close f;
