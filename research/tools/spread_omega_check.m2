-- Route-review test (subspace line review, design bridge): the regular spread of F_3^4 = F_9^2, ten pairwise
-- disjoint planes (the F_9-lines), and the rank of their squared-subspace tops omega_U in F_3[z_1..z_4]/(z^3).
-- A rank below 10 means a relation among pairwise disjoint spans; also tests whether that relation lies in the
-- pencil span (which it cannot use, since no two spread planes share a line).
kk = ZZ/3;
S = kk[z_1..z_4];
A = S/ideal(apply(gens S, v -> v^3));
form = row -> sum(4, j -> row#j * A_j);
spread = append(apply(flatten apply(3, a -> apply(3, b -> (a, b))), t -> {{1,0,t#0,t#1},{0,1,-t#1,t#0}}),
  {{0,0,1,0},{0,0,0,1}});
om = apply(spread, rows -> product(rows, r -> (form r)^2));
B = basis(4, A);
M = lift(last coefficients(matrix{om}, Monomials => B), kk);
print("spread planes: " | toString(#spread) | ", rank of their omegas: " | toString rank M);
K = gens ker M;
print("relation space dimension: " | toString(numcols K) | "; relation vector(s): " | toString entries transpose K);
exit 0
