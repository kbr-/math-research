\\ The five-root Taylor determinant on a random line (29 September 2026; route review bmd-20260929-zh, bridge test).
\\ P0(b) = det[[T^m] phi_(b_i) phi_(b_j)] (10 pairs, m = 0..9, phi = (1 + bT)^(-3/2)) has degree 45. On the line
\\ b = u + tau v it is interpolated exactly from 46 evaluations; dividing by Vand(b)^3 on the line leaves the
\\ degree-15 restriction of Q = P0 / Vand^3, which is factored over Q. An irreducible restriction proves Q
\\ irreducible; a splitting into five cubics would be consistent with a factorization over the 4-subsets.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
coef(x, y, m) = sum(k = 0, m, binomial(-3/2, k) * binomial(-3/2, m - k) * x^k * y^(m - k));
P0(b) = { my(R = List()); for (i = 1, 5, for (j = i + 1, 5, listput(R, vector(10, m, coef(b[i], b[j], m - 1))))); matdet(Mat(Vec(R)~)); }
main() = {
  my(u = [3, -7, 11, 2, -5], v = [1, 4, -2, 9, 6], pts = vector(46, k, k), vals = vector(46, k, P0(u + pts[k] * v)));
  my(P = polinterpolate(pts, vals, tau), b = u + tau * v);
  my(check = subst(P, tau, 47) == P0(u + 47 * v) && subst(P, tau, -3) == P0(u - 3 * v));
  my(V = prod(i = 1, 5, prod(j = i + 1, 5, b[i] - b[j])), Q = P / V^3);
  emit(Str("line interpolation degree ", poldegree(P), ", verified at two further points: ", check, "; Q restriction is a polynomial: ", type(Q) == "t_POL", ", degree ", poldegree(Q)));
  my(f = factor(Q));
  emit(Str("factor degrees and multiplicities of Q on the line: ", vector(#f~, i, [poldegree(f[i, 1]), f[i, 2]])));
}
main();
