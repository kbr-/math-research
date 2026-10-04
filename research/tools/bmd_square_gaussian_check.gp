\\ Jacobi-Trudi lead entry four (cycle kev, 9 October 2026): exact check at the square (M = 4, p = 2, k = 2) with
\\ Gaussian integers, replacing the invalid polmod evaluation of bmd_square_two_column_shift.gp: least coefficients
\\ tau_11 of {-2,-1} u {0..3} u {5,6} and tau_2 of {-2,-1} u {0..4} u {7}, divided by Vand^2, and H_(1,1), H_(2), H_(1).
\\ Prediction from the exact fit (two-column-fit.txt): tau_2 = 0 and tau_11 = 64 a, a = 21070924875/2^41.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2 * 10^9);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * ('x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * 'eps^r * ('x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, 'eps), A, 'x);
}
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
e1(Z) = vecsum(Z);
e2(Z) = sum(i = 1, #Z, sum(j = i + 1, #Z, Z[i] * Z[j]));
h2(Z) = sum(i = 1, #Z, sum(j = i, #Z, Z[i] * Z[j]));
HS(Y, k, f) = { my(s = 0); forsubset([#Y, k + 1], S, my(Z = vector(k + 1, i, Y[S[i]])); s += vand(Z)^2 * f(Z)); s; }
{
  my(Y = [1, I, -1, -I], M = 4, p = 2, k = 2, A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M, neg = [-2, -1], V2 = vand(Y)^2);
  my(t11 = coefat(Y, concat(concat(neg, [0 .. 3]), [5, 6]), A + 2, B) / V2, t2 = coefat(Y, concat(concat(neg, [0 .. 4]), [7]), A + 2, B) / V2);
  emit(Str("square: tau_11 = ", t11, " (64 a = ", 64 * 21070924875 / 2^41, "); tau_2 = ", t2, "; H_(1,1) = ", HS(Y, k, e2), "; H_(2) = ", HS(Y, k, h2), "; H_(1) = ", HS(Y, k, e1)));
}
quit;
