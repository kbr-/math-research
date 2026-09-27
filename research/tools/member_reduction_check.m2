-- Member square reduction: a check (entry-2026-09-27-member-square-reduction).
--
-- Tested statement.  For W-type normalized tops A_{b,i}^2 C_b (C_b the product of block b's prefix forms, prefix forms
-- jointly independent and independent of the outside forms A), in the truncated algebra of the span, the first Taylor
-- defect is at multiplier degree min over sets B of blocks of d_B + k(|B| - 1), d_B the first defect degree of the
-- squares of the outside forms of the blocks in B (prop:member-square-reduction).  Here two blocks with k = 2 prefix
-- forms and outside forms a1, a2 (block 1) and a3, a4 (block 2) with a4 = -(a1 + a3): the squares of {a1, a3, a4} carry
-- a relation of length 3 (d = 1), so the prediction is multiplier degree 1 + 2 = 3, total 3 + 4 = 7.  Control: a4
-- independent (no defect).  Taylor span: Frobenius syzygies, lcm pair syzygies within a block, Koszul pairs across.
-- Usage: M2 --script member_reduction_check.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
S := kk[a1,a2,a3,a5,c1,c2,c3,c4];
R := S / ideal(a1^3, a2^3, a3^3, a5^3, c1^3, c2^3, c3^3, c4^3);
use R;
run1 := (label, a4) -> (
    A := {a1, a2, a3, a4}; blk := {0, 0, 1, 1}; C := {c1*c2, c3*c4}; Cf := {{c1, c2}, {c3, c4}};
    t := apply(4, i -> (A#i)^2 * C#(blk#i));
    F := R^{-4,-4,-4,-4};
    K := kernel map(R^1, F, matrix{t});
    unit := (i, v) -> apply(4, k -> if k == i then v else 0_R);
    gens0 := {};
    for i from 0 to 3 do (gens0 = gens0 | {unit(i, A#i)}; for cf in Cf#(blk#i) do gens0 = gens0 | {unit(i, cf^2)});
    for i from 0 to 3 do for j from i+1 to 3 do (
        -- within a block the tops share C_b: lcm syzygy A_j^2 e_i - A_i^2 e_j; across blocks the Koszul pair
        if blk#i == blk#j then gens0 = gens0 | {apply(4, k -> if k == i then (A#j)^2 else if k == j then -(A#i)^2 else 0_R)}
        else gens0 = gens0 | {apply(4, k -> if k == i then t#j else if k == j then -(t#i) else 0_R)});
    Tay := image map(F, , transpose matrix gens0);
    ds := select(toList(0..20), d -> hilbertFunction(d, K) != hilbertFunction(d, Tay));
    dims := apply(ds, d -> hilbertFunction(d, K) - hilbertFunction(d, Tay));
    f << "{\"family\": \"" << label << "\", \"defect_degrees\": [" << concatenate between(", ", apply(ds, toString))
      << "], \"defect_dims\": [" << concatenate between(", ", apply(dims, toString)) << "]}" << endl);
run1("two blocks, k = 2, relation a1 + a3 + a4 = 0 across blocks", -(a1 + a3));
run1("control: a4 independent", a5);
close f;
