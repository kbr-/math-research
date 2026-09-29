\\ Newton polygon of the Wronskian numerator of the cluster degeneration in (eps, T).
\\
\\ Tested statement: for roots (eps*b_1,...,eps*b_M, 1, -1), the Wronskian numerator W(eps,T)
\\ (non-branch part, computed exactly with eps symbolic) has a lower Newton polygon in the
\\ (T-exponent, eps-exponent) plane whose edges of slope in (0,1) are the neck scales; the number of
\\ neck points at an edge is its horizontal length, and they are simple iff the edge polynomial is
\\ squarefree (away from T = 0). The script prints every lower edge: slope alpha (|T| ~ eps^(-alpha)),
\\ horizontal length, the edge polynomial (as a polynomial in T) and its squarefreeness.
\\ Rows as in bmd_cube_cluster_scales.gp; the determinant is computed with eps symbolic by
\\ interpolation in T over Q(eps)... here directly as a bivariate determinant.
default(parisizemax, 2000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));

numer(vals, R) = {
  my(Nv = #vals, Pi = prod(c = 1, Nv, 1 + vals[c] * 'T), rows = List());
  for (i = 1, Nv, for (j = i + 1, Nv, my(e = vector(Nv)); e[i] = -3/2; e[j] = -3/2; listput(rows, e)));
  my(P = matrix(R, R));
  for (i = 1, R,
    my(p = 1, e = rows[i]);
    for (k = 0, R - 1,
      P[i, k + 1] = p;
      p = deriv(p, 'T) * Pi + p * sum(c = 1, Nv, (e[c] - k) * vals[c] * (Pi / (1 + vals[c] * 'T)))));
  my(W = matdet(P));
  \\ remove the branch factors (1 + c T) for the outer roots +-1 and the cluster roots eps*b_i
  foreach (vals, c, while (subst(W, 'T, -1/c) == 0, W = W \ (1 + c * 'T)));
  W;
}

newton(W) = {
  \\ monomials e^a T^b of W (W polynomial in T with coefficients polynomial in 'e)
  my(pts = List());
  for (b = 0, poldegree(W, 'T), my(c = polcoeff(W, b, 'T)); if (c != 0, listput(pts, [b, valuation(c, 'e)])));
  pts = Vec(pts);
  \\ lower convex hull
  my(hull = List());
  foreach (pts, q,
    while (#hull >= 2 && (hull[#hull][1] - hull[#hull - 1][1]) * (q[2] - hull[#hull - 1][2]) - (hull[#hull][2] - hull[#hull - 1][2]) * (q[1] - hull[#hull - 1][1]) <= 0, listpop(hull));
    listput(hull, q));
  hull;
}

run(M, b) = {
  my(vals = concat(vector(M, i, 'e * b[i]), [1, -1]), R = binomial(M + 2, 2));
  my(W = numer(vals, R));
  emit(Str("M=", M, " N=", M + 2, " b=", b, " deg_T W=", poldegree(W, 'T), " deg_eps W=", poldegree(W, 'e)));
  my(H = newton(W));
  for (i = 1, #H - 1,
    my(p = H[i], q = H[i + 1], len = q[1] - p[1], slope = (p[2] - q[2]) / len);
    \\ edge polynomial: sum over monomials on the edge of the leading eps-coefficient
    my(E = sum(bb = p[1], q[1], my(c = polcoeff(W, bb, 'T), a = p[2] - slope * (bb - p[1]));
      if (c != 0 && denominator(a) == 1 && valuation(c, 'e) == a, polcoeff(c, a, 'e) * 'T^(bb - p[1]), 0)));
    my(E0 = E / 'T^valuation(E, 'T), sqf = (poldegree(gcd(E0, deriv(E0))) == 0));
    emit(Str("  edge T^", p[1], "..T^", q[1], ": |T| ~ eps^(-", slope, "), length ", len,
      ", edge polynomial ", E, ", squarefree off T=0: ", sqf)));
}
run(3, [1, 2, -3]);
run(4, [1, 2, -3, 5]);
