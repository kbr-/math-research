\\ Heine-Stieltjes test for the far components of the base peeling (30 September 2026; cycle bmd-20260930-zd).
\\ Question (Outside lead of the route review): does the Weierstrass polynomial W_k of F_k satisfy a Fuchsian
\\ second-order equation A W'' + B W' + C W = 0 with deg A <= dA, deg B <= dA - 1, deg C <= dA - 2, for some
\\ small dA (dA = 2 is the hypergeometric/Jacobi case with singular points 0, -1/c, infinity)?  Such an equation
\\ with A nonzero at the roots would force simple roots, for every b.  The kernel dimension of the linear system
\\ in the coefficients of A, B, C is printed for dA = 2..6; W_k is computed as in bmd_cube_base_peeling_far.gp,
\\ modulo q = 2^61 - 1 with c = CS[k].  A trivial kernel for every dA falsifies the lead in this form.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
sum0(e, l) = -sum(j = 3, Rn(l) + 2, j) + sum(j = 0, Rn(e) + 4 * e, j) + sum(i = 4 * e - 4 * e * l, 4 * e + 4 * l - 1, i - 7/2);
sumatinf(e, l) = -binomial(Rn(e), 2) + sum(j = 3, Rn(l) + 4 * l + 3, j) + sum(i = -4 * e * l, 4 * e - 1, 7/2 - i);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
rowf(ga, be, j, c, x0, R, q) = {
  my(u = vector(R, a, Mod(binomial(be + j, a - 1), q) * x0^(j - a + 1)), r = Mod(c, q) / (1 + c * x0));
  my(v = vector(R, s, Mod(binomial(ga, s - 1), q) * r^(s - 1)));
  vector(R, m, sum(a = 1, m, u[a] * v[m + 1 - a]));
}
Dval(e, l, c, x0, q) = {
  my(R = Rn(e + l + 1), rows = List());
  foreach (blocks(e, l), bl, for (j = 0, bl[3] - 1, listput(rows, rowf(bl[1], bl[2], j, c, x0, R, q))));
  matdet(Mat(Vec(rows)~));
}
export(Rn, blocks, rowf, Dval);
Wpoly(b, k, q) = {
  my(CS = [2, -3, 5, -7, 11], N = 2 * b, R = Rn(b), B = binomial(R, 2), Sc = md(N, 7/2), e = k - 1, l = b - k, c = CS[k]);
  my(w0 = sum0(e, l) - B, wc = Sc - B, nF = B - Sc - sum0(e, l) - sumatinf(e, l));
  my(Sb = sum(i = 1, 6, blocks(e, l)[i][2] * blocks(e, l)[i][3]), Sg = sum(i = 1, 6, blocks(e, l)[i][1] * blocks(e, l)[i][3]));
  my(xs = vector(nF + 3, i, Mod(i + 1, q)));
  my(ys = parvector(nF + 3, i, Dval(e, l, c, lift(xs[i]), q) * xs[i]^(Sb - w0) * (1 + c * xs[i])^(Sg - wc)));
  my(P = polinterpolate(xs[1..nF + 1], ys[1..nF + 1], 'x));
  if (subst(P, 'x, xs[nF + 2]) != ys[nF + 2] || poldegree(P) != nF, error("interpolation"));
  [P, c];
}
main() = {
  my(q = 2^61 - 1);
  foreach ([[3, 2], [4, 2], [4, 3]], bk,
    my(Pc = Wpoly(bk[1], bk[2], q), P = Pc[1], d = poldegree(P), out = List());
    for (dA = 2, 6,
      my(nu = 3 * dA, cols = List());
      for (i = 0, dA, listput(cols, 'x^i * deriv(deriv(P))));
      for (i = 0, dA - 1, listput(cols, 'x^i * deriv(P)));
      for (i = 0, dA - 2, listput(cols, 'x^i * P));
      my(Mt = matrix(d + dA + 1, #cols, r, j, polcoef(cols[j], r - 1, 'x)));
      listput(out, [dA, #cols - matrank(Mt)]));
    emit(Str("b=", bk[1], " k=", bk[2], " c=", Pc[2], " deg W_k=", d, ": [dA, kernel dimension] ", Vec(out))));
}
default(nbthreads, 12);
default(parisizemax, 2000000000);
main();
