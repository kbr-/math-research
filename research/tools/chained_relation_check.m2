-- Chained relations: are relation defects local? (entry-2026-09-27-global-step-review)
--
-- Tested statement.  Four tops tau_i = A_i^2 B_i with two chained relations among their squared forms,
-- A_3 = A_1 + A_2 and A_4 = A_2 + A_3, B_i independent, in the truncated algebra T_V of the span (the free regime).
-- Is every syzygy in the span of the Frobenius syzygies, the Koszul pairs, and the relation syzygies of
-- prop:relation-length-syzygy supported on triples (with their T_V-multiples)?  The four A's are the four points of
-- P^1(F_3), so all four triples are related; both the two planted and all four triple syzygies are tried.
-- Output: defect dimensions without and with the two relation syzygies.  A nonzero residual means a non-local defect.
-- Usage: M2 --script chained_relation_check.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
S := kk[a1,a2,b1,b2,b3,b4];
R := S / ideal(a1^3, a2^3, b1^3, b2^3, b3^3, b4^3);
use R;
a3 := a1 + a2; a4 := a2 + a3;
As := {a1, a2, a3, a4}; Bs := {b1, b2, b3, b4};
t := apply(4, i -> (As#i)^2 * Bs#i);
F := R^{-3,-3,-3,-3};
K := kernel map(R^1, F, matrix{t});
unit := (i, c) -> apply(4, k -> if k == i then c else 0_R);
tay := {};
for i from 0 to 3 do tay = tay | {unit(i, As#i), unit(i, (Bs#i)^2)};
for i from 0 to 3 do for j from i+1 to 3 do tay = tay | {apply(4, k -> if k == i then t#j else if k == j then -(t#i) else 0_R)};
-- relation syzygy for a triple (i, j, l) whose squared forms satisfy Ai + Aj + Al' = 0 with Ai = +-A_i, Aj = +-A_j,
-- Al' = +-A_l (signs do not change the tops): multipliers (-Aj B_j B_l, Ai B_i B_l, Aj B_i B_j) on (tau_i, tau_j, tau_l).
-- The four forms a1, a2, a1 + a2, a1 + 2 a2 are the four points of P^1(F_3), so every triple is related:
-- A1 + A2 - A3 = 0, A2 + A3 - A4 = 0, A1 - A2 - A4 = 0, A1 + A3 + A4 = 0.
rel := (i, j, l, Ai, Aj) -> apply(4, k -> if k == i then -Aj*(Bs#j)*(Bs#l) else if k == j then Ai*(Bs#i)*(Bs#l)
    else if k == l then Aj*(Bs#i)*(Bs#j) else 0_R);
rs := {rel(0, 1, 2, a1, a2), rel(1, 2, 3, a2, a3), rel(0, 1, 3, a1, -a2), rel(0, 2, 3, a1, a3)};
for v in rs do if sum(4, k -> (v#k) * (t#k)) != 0 then error "not a syzygy";
r1 := rs#0; r2 := rs#1;
Tay := image map(F, , transpose matrix tay);
Loc := image map(F, , transpose matrix (tay | {r1, r2}));
Loc4 := image map(F, , transpose matrix (tay | rs));
report := (label, M) -> (
    ds := select(toList(0..18), d -> hilbertFunction(d, K) != hilbertFunction(d, M));
    dims := apply(ds, d -> hilbertFunction(d, K) - hilbertFunction(d, M));
    f << "{\"span\": \"" << label << "\", \"defect_degrees\": [" << concatenate between(", ", apply(ds, toString))
      << "], \"defect_dims\": [" << concatenate between(", ", apply(dims, toString)) << "]}" << endl);
report("Frobenius and Koszul", Tay);
report("plus the two planted relation syzygies", Loc);
report("plus all four triple relation syzygies", Loc4);
close f;
