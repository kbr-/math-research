\\ First-order coefficients G_X(D) of the far limit in the even peeling (3 October 2026; cycle bmd-20261003-zd).
\\ Companion of bmd_cube_far_first_order.gp.  Classes at the cluster in u = eps/x (= 1/z), rows scaled freely:
\\   A: u^3 (1+u/D_s)^-3, u^(6-j) (1+u/D_r)^-5/2 (1+u/D_s)^-7/2 (r<s, j<4); pivots u^3..u^(R_l+2); G_A = [u^(R_l+3)] of the last;
\\   B: u^j (1+u/D_s)^-7/2, j<4e; pivots u^0..u^(4el-1); G_B = [u^(4el)] of the last;   C: as B with 4 in place of 4e.
\\ Output: G at three fixed distinct rational D, and the rank of the 3 x 3 matrix, a lower bound for the dimension
\\ spanned by (G_A,G_B,G_C)(D).  G_A is not identically zero if it is nonzero at one D.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
ser(a, gs, Ds, P) = { my(f = 'u^a * prod(i = 1, #gs, (1 + 'u / Ds[i] + O('u^(P + 1)))^gs[i])); vector(P + 1, m, polcoef(f, m - 1, 'u)); }
tri(rows, piv, col) = { my(A = matrix(#rows, #rows[1], i, j, rows[i][j]), S = matrix(#rows, #piv, i, j, A[i, piv[j]]), B = S^(-1) * A); B[#piv, col]; }
Gvec(e, l, D) = {
  my(Rl = Rn(l), P = Rl + 4 * e * l + 8, rA = List(), rB = List(), rC = List());
  for (s = 1, l, listput(rA, ser(3, [-3], [D[s]], P)));
  for (r = 1, l, for (s = r + 1, l, for (j = 0, 3, listput(rA, ser(6 - j, [-5/2, -7/2], [D[r], D[s]], P)))));
  for (s = 1, l, for (j = 0, 4 * e - 1, listput(rB, ser(j, [-7/2], [D[s]], P))));
  for (s = 1, l, for (j = 0, 3, listput(rC, ser(j, [-7/2], [D[s]], P))));
  [tri(rA, vector(Rl, i, i + 3), Rl + 4), tri(rB, vector(4 * e * l, i, i), 4 * e * l + 1), tri(rC, vector(4 * l, i, i), 4 * l + 1)];
}
main() = {
  setrand(7);
  foreach ([[1, 2], [2, 1], [1, 3], [2, 2], [3, 1]], el,
    my(e = el[1], l = el[2], G = matrix(3, 3));
    my(DS = [[2, 5, 11, 17], [3, -7, 13, 19], [-2, 9, 4, 23]], dd = [3, 5, 7]); for (i = 1, 3, my(D = vector(l, s, DS[i][s] / dd[i])); my(g = Gvec(e, l, D)); for (j = 1, 3, G[i, j] = g[j]));
    emit(Str("(e,l)=", el, ": G_A at three D: ", G[, 1]~, "; G_B ", G[, 2]~, "; G_C ", G[, 3]~, "; rank ", matrank(G))));
}
main();
