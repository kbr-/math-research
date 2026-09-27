-- Relations sharing one top: are defects local? (entry-2026-09-27-global-step-review)
--
-- Tested statement.  Five tops tau_i = A_i^2 B_i with A_3 = A_1 + A_2 and A_5 = A_3 + A_4 (A_1, A_2, A_4 free, B_i
-- independent): two three-term relations sharing only top 3, a tree of two triangles, plus their sum, the four-term
-- relation A_1 + A_2 + A_4 - A_5 = 0 (conjectured defect at multiplier degree 4, total 7).  In the truncated algebra of
-- the span (free regime): the defect dimensions with the Frobenius and Koszul span, and after adding the two triple
-- relation syzygies of prop:relation-length-syzygy.  Locality predicts no residual below total degree 7.
-- Usage: M2 --script tree_relation_check.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
S := kk[a1,a2,a4,b1,b2,b3,b4,b5];
R := S / ideal(a1^3, a2^3, a4^3, b1^3, b2^3, b3^3, b4^3, b5^3);
use R;
a3 := a1 + a2; a5 := a3 + a4;
As := {a1, a2, a3, a4, a5}; Bs := {b1, b2, b3, b4, b5};
n := 5;
t := apply(n, i -> (As#i)^2 * Bs#i);
F := R^(toList(n:-3));
K := kernel map(R^1, F, matrix{t});
unit := (i, c) -> apply(n, k -> if k == i then c else 0_R);
tay := {};
for i from 0 to n-1 do tay = tay | {unit(i, As#i), unit(i, (Bs#i)^2)};
for i from 0 to n-1 do for j from i+1 to n-1 do tay = tay | {apply(n, k -> if k == i then t#j else if k == j then -(t#i) else 0_R)};
-- relation syzygy for Ai + Aj + Al' = 0 (signed forms): multipliers (-Aj B_j B_l, Ai B_i B_l, Aj B_i B_j)
rel := (i, j, l, Ai, Aj) -> apply(n, k -> if k == i then -Aj*(Bs#j)*(Bs#l) else if k == j then Ai*(Bs#i)*(Bs#l)
    else if k == l then Aj*(Bs#i)*(Bs#j) else 0_R);
rs := {rel(0, 1, 2, a1, a2), rel(2, 3, 4, a3, a4)};
for v in rs do if sum(n, k -> (v#k) * (t#k)) != 0 then error "not a syzygy";
Tay := image map(F, , transpose matrix tay);
Loc := image map(F, , transpose matrix (tay | rs));
report := (label, M) -> (
    ds := select(toList(0..22), d -> hilbertFunction(d, K) != hilbertFunction(d, M));
    dims := apply(ds, d -> hilbertFunction(d, K) - hilbertFunction(d, M));
    f << "{\"span\": \"" << label << "\", \"defect_degrees\": [" << concatenate between(", ", apply(ds, toString))
      << "], \"defect_dims\": [" << concatenate between(", ", apply(dims, toString)) << "]}" << endl);
report("Frobenius and Koszul", Tay);
report("plus the two triple relation syzygies", Loc);
close f;
