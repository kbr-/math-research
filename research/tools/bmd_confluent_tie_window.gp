\\ Confluent tie window (7 October 2026; cycle bmd-20261007-m).  Tested statement: for lambda = 3/2, m >= 1 and every
\\ c not in {0,1}, the (3m+3) x (3m+5) matrix of the coefficients of T^d..T^(d+3m+4), d = binom(m,2), of the rows
\\ (1+T)^(-5/2) T^i (i < 2m), T^n (1+cT)^(-3/2) (n < m), (1+T)^(-3), ((1+T)(1+cT))^(-3/2), T (1+T)^(-5/2) (1+cT)^(-3/2)
\\ has full rank: the gcd of its maximal minors (polynomials in c) has no root outside {0,1}.  Prints the gcd with the
\\ powers of c and c-1 stripped, its factorization, and the number of minors used (the gcd stops early once trivial).
\\ Also prints the square-window determinant (first 3m+3 window columns) factored.
default(parisizemax, 2 * 10^9); default(seriesprecision, 200);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
\\ explicit coefficients of T^k in each row (variable c), to avoid series expansion of rational functions
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m) = {
  my(d = m * (m - 1) / 2, w = 3 * m + 5);
  matrix(3 * m + 3, w, r, j, rowco(r, m, d + j - 1));
}
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
\\ REAL=1 (cycle bmd-20261007-p): for each m in MS, the number of real roots of the square-window minor in each of
\\ (-oo,0), (0,1), (1,oo) (Sturm sequences on the factor stripped of c and c-1); a test of an AT-type sign pattern.
{
if (getenv("REAL") == "1",
  foreach(eval(getenv("MS")), m,
    my(A = winmat(m), nr = 3 * m + 3, sq = strip01(matdet(vecextract(A, "..", vector(nr, j, j)))));
    emit(Str("REAL m = ", m, ": real roots of the square minor in (-oo,0), (0,1), (1,oo): ",
      polsturm(sq, [-oo, 0]), ", ", polsturm(sq, [0, 1]), ", ", polsturm(sq, [1, +oo]), " (degree ", poldegree(sq, 'c), ")"))); quit);
}
\\ SCAN=1 (cycle bmd-20261007-n): instead, list the maximal minors (window column sets, 0-based offsets from d) whose
\\ determinant is c^a (c-1)^b times a nonzero constant, i.e. that alone prove full rank off {0,1}.
{
if (getenv("SCAN") == "1",
  foreach(eval(getenv("MS")), m,
    my(A = winmat(m), nr = 3 * m + 3, w = 3 * m + 5, hits = List(), tot = 0);
    forsubset([w, nr], S, tot++; my(D = matdet(vecextract(A, "..", Vec(S))));
      if (D != 0 && poldegree(strip01(D), 'c) == 0, listput(hits, [apply(x -> x - 1, Vec(S)), valuation(D, 'c), valuation(D, 'c - 1)])));
    emit(Str("SCAN m = ", m, ": ", #hits, " monomial minors of ", tot, ": ", Vec(hits)))); quit);
}
{
my(MS = eval(getenv("MS")));
foreach(MS, m,
  my(A = winmat(m), nr = 3 * m + 3, w = 3 * m + 5, g = 0, used = 0, sq);
  sq = matdet(vecextract(A, "..", vector(nr, j, j)));
  forsubset([w, nr], S, used++; g = gcd(g, matdet(vecextract(A, "..", Vec(S)))); if (g != 0 && poldegree(strip01(g), 'c) == 0, break));
  emit(Str("m = ", m, ": minors used ", used, " of ", binomial(w, nr), "; gcd stripped of c, c-1: ", strip01(g)));
  emit(Str("   square window: ", if (sq == 0, "0", Str("c^", valuation(sq, 'c), " (c-1)^", valuation(sq, 'c - 1), " * factors of degrees ", apply(poldegree, factor(strip01(sq))[, 1]~))))));
}
