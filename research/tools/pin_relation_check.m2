-- Pinning inside a relation (entry-2026-09-27-pin-relation-defects).
--
-- Tested statement.  A pin l (a linear top, from pinning a block's designated form to a constant) with
-- l + A_1 + A_2 = 0, and two clause tops tau_i = A_i^2 B_i (B_i independent), in the truncated algebra of the span (the
-- free regime): the syzygy B_2 e_1 - B_1 e_2 + (A_1 - A_2) B_1 B_2 e_l has multiplier degree 1 on e_1 and is not in the
-- span of the Frobenius syzygies (A_i e_i, B_i^2 e_i, l^2 e_l) and the Koszul pairs, so pinning a block of a
-- related triple leaves a defect among the other two.  Controls: the same with l independent of A_1, A_2, and with both
-- related blocks pinned as well, at independent forms (no clause tops left).  Last family: the pin relates the two
-- clauses' linear prefix factors instead of their squared forms.
-- Usage: M2 --script pin_relation_check.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
S := kk[a1,a2,b1,b2,c,x,y];
R := S / ideal(a1^3, a2^3, b1^3, b2^3, c^3, x^3, y^3);
use R;
run1 := (label, tops, frob) -> (
    r := #tops;
    F := R^(apply(tops, x -> -(first degree x)));
    K := kernel map(R^1, F, matrix{tops});
    unit := (i, v) -> apply(r, k -> if k == i then v else 0_R);
    gens0 := {};
    for i from 0 to r-1 do for g in frob#i do gens0 = gens0 | {unit(i, g)};
    for i from 0 to r-1 do for j from i+1 to r-1 do gens0 = gens0 | {apply(r, k -> if k == i then tops#j else if k == j then -(tops#i) else 0_R)};
    Tay := image map(F, , transpose matrix gens0);
    ds := select(toList(0..14), d -> hilbertFunction(d, K) != hilbertFunction(d, Tay));
    dims := apply(ds, d -> hilbertFunction(d, K) - hilbertFunction(d, Tay));
    f << "{\"family\": \"" << label << "\", \"defect_degrees\": [" << concatenate between(", ", apply(ds, toString))
      << "], \"defect_dims\": [" << concatenate between(", ", apply(dims, toString)) << "]}" << endl);
l := -(a1 + a2);
v := {b2, -b1, (a1 - a2)*b1*b2};
if v#0 * a1^2*b1 + v#1 * a2^2*b2 + v#2 * l != 0 then error "not a syzygy";
run1("pin l = -(A1+A2) with clauses A1^2 B1, A2^2 B2", {l, a1^2*b1, a2^2*b2}, {{l^2}, {a1, b1^2}, {a2, b2^2}});
run1("control: pin c independent", {c, a1^2*b1, a2^2*b2}, {{c^2}, {a1, b1^2}, {a2, b2^2}});
run1("control: all three blocks pinned at independent forms", {a1, a2, c}, {{a1^2}, {a2^2}, {c^2}});
-- pin inside the prefixes: the pin relates the linear prefix factors x, y of the two clause tops A_1^2 x, A_2^2 y
m := -(x + y);
run1("pin m = -(x+y) with clauses A1^2 x, A2^2 y (x, y prefix factors)", {m, a1^2*x, a2^2*y}, {{m^2}, {a1, x^2}, {a2, y^2}});
close f;
