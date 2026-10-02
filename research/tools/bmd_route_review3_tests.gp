\\ Tests of the route review after the confluent cherry theorem (7 October 2026; cycle bmd-20261007-zg).
\\ Objects: the confluent tie window W^c(c) of bmd_confluent_tie_window.gp (lambda = 3/2) and its pure block, the first
\\ 3m columns of the 3m single-series rows, whose determinant is kappa c^e (c-1)^f H_m(c).
\\ (F) Falsification attempt on conj:cube-confluent-tie-window-full-rank at the first unchecked size m = 6: gcd of maximal
\\     minors, stripped of c and c-1 (constant means full rank for every c outside {0,1}).
\\ (L1) Confluent limit c -> 0 and c -> oo: H_m(0) and the leading coefficient of H_m, factored, m = 2..6.  A product of
\\     small primes for every m would point to an explicit formula (de Bruin-type), hence H_m != 0 for every m.
\\ (L2) Real zeros of H_m in (-oo,0), (0,1), (1,oo) for m = 6; the pattern at m = 2..5 was (0,0,0), (0,2,0), (0,0,0), (0,4,0).
\\ (L3) log|H_m(-1)| / m^2 for m = 2..6 (strong-asymptotics prediction: tends to a constant).
\\ (B1) Every complex zero of H_m (m = 2..6) has positive real part (two-species log-gas prediction).
\\ (B2) Superregularity of the lower-triangular Toeplitz matrices [binom(-a, i-j)], a = 5/2 and 3/2, size 7: every minor
\\     that is not identically zero by its zero pattern is nonzero.
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
winmat(m) = my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1));
pure(m) = my(d = m * (m - 1) / 2); matrix(3 * m, 3 * m, r, j, rowco(r, m, d + j - 1));
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
my(Hs = vector(6));
for (m = 2, 6, my(D = matdet(pure(m))); Hs[m] = strip01(D);
  emit(Str("(L1) m = ", m, ": deg H_m = ", poldegree(Hs[m], 'c), ", H_m(0) = ", factor(subst(Hs[m], 'c, 0)), ", lead = ", factor(pollead(Hs[m], 'c)))));
my(H = Hs[6]);
emit(Str("(L2) m = 6: real roots of H_6 in (-oo,0), (0,1), (1,oo): ", polsturm(H, [-1 - vecmax(apply(abs, Vec(H))) / abs(pollead(H)), 0]),
  ", ", polsturm(H, [0, 1]), ", ", polsturm(H, [1, 1 + vecmax(apply(abs, Vec(H))) / abs(pollead(H))])));
default(realprecision, 60);
for (m = 2, 6, my(v = subst(Hs[m] / pollead(Hs[m]), 'c, -1));
  emit(Str("(L3) m = ", m, ": sign H_m(-1)/lead = ", sign(v), ", log|H_m(-1)/lead| / m^2 = ", log(abs(v)) / m^2, ", log|H_m(-1)/content-normalized| / m^2 = ", log(abs(subst(Hs[m], 'c, -1))) / m^2)));
for (m = 2, 6, my(R = polroots(Hs[m])); emit(Str("(B1) m = ", m, ": min Re of the zeros of H_m = ", vecmin(apply(real, R)), ", zeros with Re <= 0: ", #select(z -> real(z) <= 0, R))));
}
{
foreach([5/2, 3/2], a,
  my(n = 7, T = matrix(n, n, i, j, bn(-a, i - j)), bad = 0, tot = 0);
  for (k = 1, n, forsubset([n, k], R, forsubset([n, k], C,
    my(r = Vec(R), cc = Vec(C), triv = 0);
    \\ trivially zero iff some i has r_i < c_i (lower-triangular pattern, Gessel-Viennot): sorted rows below columns fail
    for (i = 1, k, if (r[i] < cc[i], triv = 1; break));
    if (!triv, tot++; if (matdet(vecextract(T, r, cc)) == 0, bad++)))));
  emit(Str("(B2) a = ", a, ", size 7: ", tot, " minors not trivially zero, ", bad, " of them zero")));
}
{
my(m = 6, A = winmat(m), nr = 3 * m + 3, w = 3 * m + 5, g = 0, used = 0);
forsubset([w, nr], S, used++; g = gcd(g, matdet(vecextract(A, "..", Vec(S)))); if (g != 0 && poldegree(strip01(g), 'c) == 0, break));
emit(Str("(F) m = 6: minors used ", used, " of ", binomial(w, nr), "; gcd stripped of c, c-1: ", strip01(g)));
}
