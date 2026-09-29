\\ Neck Newton polygon of the cluster degeneration, computed modulo p.
\\
\\ Tested statement: for roots (eps*b_1,...,eps*b_M, 1, -1), the cleared Wronskian polynomial
\\   P(eps,t) = det[ [X^j] (f_r / pi_r)(t + X) ]_{r,j<R} * prod_c (1 + c t)^E,  E = binom(R,2),
\\ (rows f_r = ((1+a_i T)(1+a_j T))^(-3/2) over pairs; pi_r the powers of (1+c t)) has lower
\\ Newton-polygon edges with slopes in (0,1) (neck scales |T| ~ eps^(-slope)); conjecture: slopes
\\ j/M, j = 1..M-1, each of horizontal length 2M, with binomial edge polynomials.
\\ P is a polynomial of degree <= M*E in eps and <= (M+2)*E in t with Z[1/2] coefficients; it is
\\ computed modulo p by evaluation on a grid and exact interpolation in both variables (checked at
\\ extra points). Branch factors (1+eps b t) and (1 +- t) contribute only slopes 1 and 0, so the neck
\\ edges of P are those of the Wronskian numerator. Reduction mod p can only raise valuations of
\\ individual coefficients; the edges found are checked against the exact M=3 result.
default(parisizemax, 4000000000);
p = 2^61 - 1;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bc(al, m) = Mod(binomial(al, m), p);
serpow(u, al, L) = vector(L, m, bc(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));

Pval(vals, t, R, E) = {
  my(n = #vals, us = vector(n, c, vals[c] / (1 + vals[c] * t)), S = vector(n, c, serpow(us[c], -3/2, R)), rows = List());
  for (i = 1, n, for (j = i + 1, n, listput(rows, mul(S[i], S[j], R))));
  matdet(matrix(R, R, r, k, rows[r][k])) * prod(c = 1, n, (1 + vals[c] * t)^E);
}

run(M, b) = {
  my(R = binomial(M + 2, 2), E = binomial(R, 2), De = M * E, Dt = (M + 2) * E);
  my(es = vector(De + 2, k, Mod(k + 1, p)), ts = vector(Dt + 2, k, Mod(k + 1000, p)));
  \\ for each eps value, interpolate in t
  my(rowsT = vector(De + 2));
  for (k = 1, De + 2,
    my(vals = concat(vector(M, i, es[k] * b[i]), [Mod(1, p), Mod(-1, p)]));
    my(ys = vector(Dt + 2, l, Pval(vals, ts[l], R, E)));
    my(Q = polinterpolate(ts[1..Dt+1], ys[1..Dt+1], 't));
    if (subst(Q, 't, ts[Dt+2]) != ys[Dt+2], error("t-interpolation check failed"));
    rowsT[k] = Q);
  \\ interpolate each t-coefficient in eps
  my(P = sum(d = 0, Dt, my(cs = vector(De + 2, k, polcoeff(rowsT[k], d, 't)));
    my(C = polinterpolate(es[1..De+1], cs[1..De+1], 'e));
    if (subst(C, 'e, es[De+2]) != cs[De+2], error("eps-interpolation check failed"));
    C * 't^d));
  emit(Str("M=", M, " N=", M + 2, " b=", b, " p=", p, " deg_t P=", poldegree(P, 't), " deg_eps P=", poldegree(substpol(P, 't, 1), 'e)));
  \\ lower Newton polygon in (t-exponent, eps-valuation)
  my(pts = List());
  for (d = 0, poldegree(P, 't), my(c = polcoeff(P, d, 't)); if (c != 0, listput(pts, [d, valuation(lift(c), 'e)])));
  my(hull = List());
  foreach (Vec(pts), q,
    while (#hull >= 2 && (hull[#hull][1] - hull[#hull-1][1]) * (q[2] - hull[#hull-1][2]) - (hull[#hull][2] - hull[#hull-1][2]) * (q[1] - hull[#hull-1][1]) <= 0, listpop(hull));
    listput(hull, q));
  for (i = 1, #hull - 1,
    my(a = hull[i], q = hull[i + 1], len = q[1] - a[1], slope = (q[2] - a[2]) / len);
    if (slope > 0 && slope < 1,
      my(terms = [], Epol = 0);
      for (d = a[1], q[1], my(v = a[2] + slope * (d - a[1]), c = lift(polcoeff(P, d, 't)));
        if (denominator(v) == 1 && c != 0 && valuation(c, 'e) == v, terms = concat(terms, [d - a[1]]); Epol += Mod(polcoeff(c, v, 'e), p) * 'z^(d - a[1])));
      my(sqf = (poldegree(gcd(Epol, deriv(Epol))) == 0));
      emit(Str("  neck edge: slope ", slope, ", length ", len, ", edge monomial exponents ", terms, ", squarefree ", sqf))));
}
MM = eval(getenv("MM"));
if (MM == 3, run(3, [1, 2, -3]));
if (MM == 4, run(4, [1, 2, -3, 5]));
