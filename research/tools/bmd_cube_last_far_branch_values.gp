\\ Branch values of the last even-peeling far polynomial (3 October 2026; cycle bmd-20261003-zq).
\\ Claim tested: for F = F_(b-1) (blocks (1+x)^g x^b P_<cnt, [g,b,cnt] = [0,0,R_e],[-3,0,1],[0,-3,1],[-7/2,0,4e],
\\ [0,-7/2,4e],[-5/2,-7/2,4]) the local leading coefficient of W(F) at a point P in {0, -1, oo} is
\\   L_P = (prod over exponent classes mod Z of the pivot minor of the Taylor matrix) * Vandermonde(local exponents),
\\ so W_(b-1)(0) / lc(W_(b-1)) = +- L_0 / L_oo and W_(b-1)(-1) / lc = +- L_(-1) / L_oo.  Compared with the saved
\\ W_last_e*.gp (e = 1, 2, 3); the factors (pivot minors, Vandermonde) are printed factored.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
blocks(e) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -3, 1], [-7/2, 0, 4 * e], [0, -7/2, 4 * e], [-5/2, -7/2, 4]];
\\ local data at a point: each function as [mu, h(u)] with h a power series (u local parameter, h(0) may vanish)
localfuns(e, P, N) = {
  my(L = List());
  foreach (blocks(e), B, my(g = B[1], b = B[2]);
    for (j = 0, B[3] - 1,
      if (P == 0, listput(L, [b + j, (1 + 'u + O('u^N))^g]));
      if (P == -1, listput(L, [g, (-1 + 'u + O('u^N))^(b + j)]));   \\ x = -1 + u: (1+x)^g = u^g, x^(b+j) = (u-1)^(b+j)
      if (P == oo, listput(L, [-(g + b + j), (1 + 'u + O('u^N))^g]))));  \\ x = 1/u: (1+x)^g x^(b+j) = u^(-g-b-j) (1+u)^g
  Vec(L);
}
leading(e, P) = {
  my(N = 4 * Rn(e + 2) + 20, F = localfuns(e, P, N), cls = List(), exps = List(), dets = List());
  foreach (F, f, my(c = frac(f[1])); if (!setsearch(Set(cls), c), listput(cls, c)));
  foreach (cls, c,
    my(G = select(f -> frac(f[1]) == c, F), m = vecmin(apply(f -> f[1], G)), M = matrix(#G, N - 5), piv = List(), r = 0);
    for (i = 1, #G, my(s = G[i][2] * 'u^(G[i][1] - m)); for (k = 0, N - 6, M[i, k + 1] = polcoef(s, k, 'u)));
    for (k = 1, N - 5, my(r2 = matrank(M[, 1..k])); if (r2 > r, listput(piv, k); r = r2); if (r == #G, break));
    if (r < #G, error("rank deficient class"));
    listput(dets, matdet(matrix(#G, #G, i, j, M[i, piv[j]])));
    foreach (piv, k, listput(exps, m + k - 1)));
  my(ex = vecsort(Vec(exps)), V = prod(i = 1, #ex, prod(j = i + 1, #ex, ex[j] - ex[i])));
  [prod(i = 1, #dets, dets[i]), V, Vec(dets), ex];
}
{
for (e = 1, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), A0 = leading(e, 0), Am = leading(e, -1), Ai = leading(e, oo));
  my(r0 = A0[1] * A0[2] / (Ai[1] * Ai[2]), rm = Am[1] * Am[2] / (Ai[1] * Ai[2]));
  emit(Str("e=", e, ": |W(0)/lc| = |L_0/L_oo|: ", abs(polcoef(W, 0) / pollead(W)) == abs(r0),
    "; |W(-1)/lc| = |L_-1/L_oo|: ", abs(subst(W, 'x, -1) / pollead(W)) == abs(rm)));
  foreach ([[0, A0], [-1, Am], [oo, Ai]], Q, my(A = Q[2]);
    emit(Str("  at ", Q[1], ": exponents ", A[4]));
    emit(Str("    class pivot minors ", apply(t -> factor(t), A[3]), "; Vandermonde ", factor(A[2])))));
}
