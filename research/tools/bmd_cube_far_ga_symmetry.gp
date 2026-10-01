\\ Symmetry of the first-order coefficients G_X of the even-peeling far limit (4 October 2026; cycle bmd-20261004-m).
\\ Classes at the cluster in u = eps/x (as in bmd_cube_far_first_order_g.gp), with w_s = 1/D_s:
\\   A: u^3 (1+w_s u)^-3 (s <= l), u^(6-j) (1+w_r u)^-5/2 (1+w_s u)^-7/2 (r < s, j < 4); pivots u^3..u^(R_l+2);
\\      G_A = [u^(R_l+3)] of the last triangular element;
\\   B: u^j (1+w_s u)^-7/2 (j < 4e), pivots u^0..u^(4el-1); C: as B with j < 4.
\\ Tested statement (lem:cube-far-ga-asymmetry): G_B and G_C are symmetric in w (their spans are), and G_A is not:
\\ G_A(w_1, w_2, ...) - G_A(w_2, w_1, ...) != 0 for l >= 2. Mode SYM: G_A symbolically at l = 2 in w1, w2, and its
\\ antisymmetric part; mode NUM: G_A at random rational w and the swapped w, for l = 2..LMAX.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
uu = varhigher("uu");
default(parisizemax, 4000000000);
ser(a, gs, ws, P) = { my(f = uu^a * prod(i = 1, #gs, (1 + ws[i] * uu + O(uu^(P + 1)))^gs[i])); vector(P + 1, m, polcoef(f, m - 1, uu)); }
tri(rows, piv, col) = { my(A = matrix(#rows, #rows[1], i, j, rows[i][j]), S = matrix(#rows, #piv, i, j, A[i, piv[j]]), B = S^(-1) * A); B[#piv, col]; }
GA(l, w) = {
  my(Rl = Rn(l), P = Rl + 4, rA = List());
  for (s = 1, l, listput(rA, ser(3, [-3], [w[s]], P)));
  for (r = 1, l, for (s = r + 1, l, for (j = 0, 3, listput(rA, ser(6 - j, [-5/2, -7/2], [w[r], w[s]], P)))));
  tri(rA, vector(Rl, i, i + 3), Rl + 4);
}
\\ NUM mode: G_A at distinct rational w_s = (2s+1)/(s+3) and with w_1, w_2 swapped, for l in NUML (exact over Q)
{
if (getenv("NUML") != "" && getenv("NUML") != 0,
  foreach (eval(getenv("NUML")), l,
    my(w = vector(l, s, (2 * s + 1) / (s + 3)), w2 = w);
    w2[1] = w[2]; w2[2] = w[1];
    my(g1 = GA(l, w), g2 = GA(l, w2));
    emit(Str("NUM l=", l, ": w = ", w, ", G_A = ", g1, ", G_A with w_1, w_2 swapped = ", g2, ", asymmetric: ", g1 != g2)));
  quit);
}
{
my(LS = eval(getenv("SYML")));
foreach (LS, l,
  my(W = vector(l, s, eval(Str("w", s))), g = GA(l, W), h = g, lin = 1);
  \\ G_A is homogeneous of degree 1 in w (scaling u); test linearity and print the coefficient of each w_s
  for (s = 1, l, if (poldegree(g, W[s]) > 1, lin = 0));
  emit(Str("SYM l=", l, ": G_A = ", g, "; polynomial and linear in w: ", type(g) == "t_POL" && lin,
    "; coefficients of w_1..w_l: ", if (type(g) == "t_POL" && lin, vector(l, s, polcoef(g, 1, W[s])), "n/a"))));
}
