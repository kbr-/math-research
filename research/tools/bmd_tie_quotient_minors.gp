\\ Quotient minors of the tie window with exponent parameter (8 October 2026; cycle bmd-20261008-b).
\\ W(L, c) as in research/tools/bmd_tie_lambda_family.gp.  The maximal minors divided by their gcd G in Q[L, c] equal,
\\ up to one common constant and sign, the 2 x 2 minors of a minimal right kernel basis (Forney), so they are canonical.
\\ Question: do they factor into a Pochhammer part in L times a part in c (a closed form contiguity could prove)?
\\ For each pair (i, j) of dropped columns at m = 2: the factorization pattern of D_ij / G (factors in L only, in c only,
\\ mixed), with total degrees; and the kernel basis over Q(L)(c) normalized to polynomial entries, with factored entries.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k, L) = {
  if (r <= 2 * m, return(bn(-L - 1, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-L, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-2 * L, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-L, a) * bn(-L, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-L - 1, a) * bn(-L, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m, L) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1, L)); }
st(q) = { q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q; }
kind(f) ={ my(dl = poldegree(f, 'L), dc = poldegree(f, 'c)); if (dc == 0, "L", if (dl == 0, "c", "mixed")); }
{
my(m = 2, W = winmat(m, 'L), w = #W, D = Map(), G = 0);
for (i = 1, w, for (j = i + 1, w, my(x = matdet(vecextract(W, "..", select(t -> t != i && t != j, [1 .. w]))));
  mapput(D, [i, j], x); G = gcd(G, x)));
for (i = 1, w, for (j = i + 1, w, my(q = mapget(D, [i, j]) / G, F = factor(q), pat = List());
  for (t = 1, #F[, 1], listput(pat, [kind(F[t, 1]), poldegree(F[t, 1], 'L), poldegree(F[t, 1], 'c), F[t, 2]]));
  emit(Str("m = 2, dropped columns ", [i, j], ": [kind, deg_L, deg_c, multiplicity] of the factors of D/G = ", Vec(pat)))));
\\ Second question: is the resultant in c of two quotient minors (stripped of c and c - 1), a polynomial in L, a product of
\\ linear forms at exceptional L?  Then those two minors alone exclude special values at every other L.
foreach([[[9, 11], [10, 11]], [[1, 2], [10, 11]], [[1, 2], [1, 3]]], pr,
  my(R = polresultant(st(mapget(D, pr[1]) / G), st(mapget(D, pr[2]) / G), 'c), F = factor(R));
  emit(Str("m = 2, resultant in c of the quotient minors ", pr, ": L-degree ", poldegree(R, 'L), ", factors [factor, multiplicity] = ", F));
  \\ a nonlinear factor h of R gives a common finite root in c unless both leading c-coefficients vanish at its roots
  my(l1 = pollead(st(mapget(D, pr[1]) / G), 'c), l2 = pollead(st(mapget(D, pr[2]) / G), 'c));
  for (t = 1, #F[, 1], if (poldegree(F[t, 1], 'L) > 1,
    my(h = F[t, 1], a = polroots(h)[1], q1 = subst(st(mapget(D, pr[1]) / G), 'L, a), q2 = subst(st(mapget(D, pr[2]) / G), 'L, a));
    emit(Str("  factor of L-degree ", poldegree(h, 'L), ": gcd with leading coefficients ", [poldegree(gcd(h, l1), 'L), poldegree(gcd(h, l2), 'L)],
      "; at its root L = ", a, " the closest pair of c-roots of the two minors differs by ",
      vecmin(concat(apply(r -> apply(s -> abs(r - s), Vec(polroots(q2))), Vec(polroots(q1))))))))));
}
quit
