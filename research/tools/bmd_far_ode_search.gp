\\ Low-order linear ODEs for the merge far polynomials (6 October 2026; cycle bmd-20261006-c).  Tested statement: does
\\ R = R_(n,k) satisfy sum_{i<=r} a_i(w) R^(i) = 0 with deg a_i <= s and gcd(a_r, R) = 1?  Such an equation gives simple
\\ roots (a double root forces all derivatives to vanish there), as for Bessel and Laguerre polynomials.  Trivial
\\ equations always exist once a_r may share factors with R, so only those with gcd(a_r, R) = 1 are reported.
\\ It also reports the number of real roots (Sturm), a test of real-rootedness as a simplicity mechanism, and with
\\ ROOTS=1 lists the roots (cycle bmd-20261006-d: do they lie on few curves, as zeros of exponential sums do?).
\\ R_(n,k) is built exactly as in research/tools/bmd_far_discriminants.gp.  Env NK (list of [n,k]), RMAX, SMAX, OUT.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
closed(E, s) = {
  my(q = #E, phi = x -> prod(i = 1, q, x - E[i]));
  sum(r = 0, q, sum(i = 0, r, (-1)^(r - i) * binomial(r, i) * phi(s + i)) * binomial(1/2, r) * (-1)^r * 'w^r * (1 - 'w)^(q - r));
}
strip(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / content(N); }
wr2(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][2]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1]); foreach (c[2], f, row++; my(g = f);
    for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w) * g)));
  strip(numerator(matdet(M)));
}
farR(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)));
  my(P3 = vector(k - 1, j, 'w^(j - 1) * closed(E, j - 1) / 'w^(P + 2)));
  my(P4 = vector(n, j, 'w^(j - 1) * closed(E, 1/2 - (n - 1) + j - 1) / 'w^((k - 1) * n)));
  my(gam = 3/2 - n + (k - 1) * n - P - 2);
  wr2([[0, P3], [gam, P4]]);
}
\\ kernel of the linear map (a_0..a_r) -> sum a_i R^(i), a_i of degree <= s
odes(R, r, s) = {
  my(D = vector(r + 1, i, if (i == 1, R, 0)));
  for (i = 2, r + 1, D[i] = deriv(D[i - 1], 'w));
  my(cols = List());
  for (i = 0, r, for (j = 0, s, listput(cols, 'w^j * D[i + 1])));
  my(top = poldegree(R) + s, M = matrix(top + 1, #cols, a, b, polcoef(cols[b], a - 1, 'w)));
  my(K = matker(M));
  [K, #cols];
}
{
my(rmax = eval(getenv("RMAX")), smax = eval(getenv("SMAX")));
foreach(eval(getenv("NK")), v,
  my(R = farR(v[1], v[2]));
  emit(Str("(n,k) = ", v, ": deg R ", poldegree(R), ", real roots ", polsturm(R), ", real roots in (0,1) ", polsturm(R, [0, 1])));
  if (getenv("NEWTON") == "1",
    \\ Archimedean Newton polygon: lower convex hull of (j, -log|a_j|); a segment of slope s and length l predicts
    \\ l roots near |w| = exp(s); compare with the number of actual roots with modulus in the segment's annulus.
    \\ NEWTONVAR=u uses u = w/(1-w), the variable of the Bernstein-type basis w^r (1-w)^(q-r) of closed().
    if (getenv("NEWTONVAR") == "u", R = numerator(subst(R, 'w, 'w / (1 + 'w)) * (1 + 'w)^poldegree(R)));
    my(D = poldegree(R), pts = List(), hull = List(), z = polroots(R));
    for (j = 0, D, my(c = polcoef(R, j)); if (c != 0, listput(pts, [j, -log(abs(c))])));
    foreach(pts, P, while (#hull >= 2 && (hull[#hull][2] - hull[#hull - 1][2]) * (P[1] - hull[#hull - 1][1]) >= (P[2] - hull[#hull - 1][2]) * (hull[#hull][1] - hull[#hull - 1][1]), listpop(hull)); listput(hull, P));
    my(slopes = vector(#hull - 1, i, (hull[i + 1][2] - hull[i][2]) / (hull[i + 1][1] - hull[i][1])));
    for (i = 1, #hull - 1,
      my(lo = if (i == 1, 0, sqrt(exp(slopes[i - 1]) * exp(slopes[i]))), hi = if (i == #hull - 1, 10^100, sqrt(exp(slopes[i]) * exp(slopes[i + 1]))));
      emit(Str("  segment j=", hull[i][1], "..", hull[i + 1][1], " length ", hull[i + 1][1] - hull[i][1], " predicted |w| ", round(exp(slopes[i]) * 1000) / 1000.,
        ", actual roots in annulus ", sum(t = 1, #z, abs(z[t]) > lo && abs(z[t]) <= hi)))));
  if (getenv("ROOTS") == "1",
    my(z = vecsort(polroots(R), x -> arg(x)));
    foreach(z, x, emit(Str("  root |w| ", round(abs(x) * 10^4) / 10^4., " arg/pi ", round(arg(x) / Pi * 10^4) / 10^4., " |w-1| ", round(abs(x - 1) * 10^4) / 10^4.))));
  for (r = 1, rmax, for (s = 0, smax,
    my(res = odes(R, r, s), K = res[1], good = 0, ex = 0);
    for (c = 1, #K, my(ar = sum(j = 0, s, K[r * (s + 1) + j + 1, c] * 'w^j));
      if (ar != 0 && poldegree(gcd(ar, R)) == 0, good++; if (ex == 0, ex = ar)));
    if (#K, emit(Str("  order ", r, ", coefficient degree <= ", s, ": kernel dim ", #K, ", with gcd(a_r,R)=1 in basis: ", good,
      if (good, Str(", example a_r = ", factor(ex)), "")))))));
}
quit;
