\\ Resultant of the first- and last-columns minors of the confluent tie window (7 October 2026; cycle bmd-20261007-zl).
\\ P_m = first-columns minor (drop the last two columns), Q_m = last-columns minor (drop the first two), both stripped of
\\ c and c-1 and made primitive.  Question: is Res_c(P_m, Q_m) a product of small primes (a product formula), m = 2..4?
\\ Prints the resultant's factorization with trial division up to 10^6 (a remaining cofactor is printed as such).
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1)); }
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
for (m = 2, 4,
  my(A = winmat(m), w = 3 * m + 5, P = strip01(matdet(vecextract(A, "..", [1 .. w - 2]))), Q = strip01(matdet(vecextract(A, "..", [3 .. w]))));
  my(R = polresultant(P, Q, 'c), F = factor(R, 10^6), big = select(x -> x > 10^6, F[, 1]~));
  emit(Str("m = ", m, ": degrees ", poldegree(P), ", ", poldegree(Q), "; |Res| has ", #Str(abs(R)), " digits; largest prime factor found ",
    vecmax(select(x -> x <= 10^6, F[, 1]~)), "; unfactored cofactors ", apply(x -> #Str(x), big), " digits; factors with exponents ",
    vector(#F[, 1], i, [F[i, 1], F[i, 2]]))));
}
quit
