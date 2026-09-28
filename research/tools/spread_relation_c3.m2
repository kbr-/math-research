-- Sanity check of the spread relation for c = 3: the Desarguesian spread of F_3^6 = F_27^2 (28 three-dimensional
-- F_3-subspaces, the F_27-lines), with F_27 = F_3[a]/(a^3 - a - 1); rank of their squared-subspace tops omega_U in
-- F_3[z_1..z_6]/(z^3) and whether the all-ones vector is a relation.
kk = ZZ/3;
S = kk[z_1..z_6];
A = S/ideal(apply(gens S, v -> v^3));
-- F_27 elements as coefficient vectors (x0, x1, x2) of x0 + x1 a + x2 a^2; multiplication by a:
-- a * (x0 + x1 a + x2 a^2) = x2 + (x0 + x2) a + x1 a^2   (a^3 = a + 1)
mulA = v -> {v#2, v#0 + v#2, v#1};
-- the F_27-line through (1, t) has F_3-basis w, a w, a^2 w with w = (1, t) in F_27^2 = F_3^6
lineBasis = w -> (w1 := w; w2 := {mulA(w#0), mulA(w#1)}; w3 := {mulA(w2#0), mulA(w2#1)};
  apply({w1, w2, w3}, u -> flatten u));
els = flatten flatten apply(3, x -> apply(3, y -> apply(3, zz -> {x, y, zz})));
spread = append(apply(els, t -> lineBasis({{1,0,0}, t})), lineBasis({{0,0,0}, {1,0,0}}));
form = row -> sum(6, j -> row#j * A_j);
om = apply(spread, rows -> product(rows, r -> (form r)^2));
B = basis(6, A);
M = lift(last coefficients(matrix{om}, Monomials => B), kk);
print("spread size: " | toString(#spread) | ", ranks of bases: " | toString unique apply(spread, b -> rank matrix(kk, b)) |
  ", rank of omegas: " | toString rank M | ", all-ones relation: " | toString(sum om == 0));
exit 0
