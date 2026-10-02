\\ Staircase pairings of the confluent tie window (8 October 2026; cycle bmd-20261008-o).
\\ On the window columns T^d..T^(d+3m+4), the pure rows (3m) have a 5-dimensional kernel spanned by the staircase
\\ functionals y^(M), M = d..d+4: y^(M) is the Cramer vector of the pure block on the 3m+1 columns M..M+3m
\\ (component r = (-1)^r times the minor omitting column M+r), zero elsewhere.  By thm:cube-tie-pure-wide-normality
\\ each is nonzero off {0, 1}, and they are independent (staircase supports).  The window has full rank at c iff the
\\ 3 x 5 matrix E(c)_(a, M) = sum_r y^(M)_r e_a(M + r) has rank 3 (e_a = coefficients of the three extra rows).
\\ Prints, for m = 2, 3: each entry's degree, orders at c = 0 and c = 1, and the degrees of its other irreducible
\\ factors; and the gcd of the 3 x 3 minors of E off {0, 1}.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
pure(r, m, k) = if (r <= 2 * m, bn(-5/2, k - (r - 1)), my(n = r - 2 * m - 1); bn(-3/2, k - n) * 'c^max(k - n, 0));
extra(a, k) = {
  if (a == 1, return(bn(-3, k)));
  if (a == 2, return(sum(t = 0, k, bn(-3/2, t) * bn(-3/2, k - t) * 'c^(k - t))));
  sum(t = 0, k - 1, bn(-5/2, t) * bn(-3/2, k - 1 - t) * 'c^(k - 1 - t));
}
st(q) = { q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q; }
oc1(q) = { my(k = 0); while (subst(q, 'c, 1) == 0, q = q / ('c - 1); k++); k; }
{
foreach([2, 3], m, my(d = m * (m - 1) / 2, E = matrix(3, 5), info = List());
  for (Mi = 1, 5, my(M = d + Mi - 1, B = matrix(3 * m, 3 * m + 1, r, j, pure(r, m, M + j - 1)), y);
    y = vector(3 * m + 1, j, (-1)^(j - 1) * matdet(vecextract(B, "..", select(t -> t != j, [1 .. 3 * m + 1]))));
    for (a = 1, 3, E[a, Mi] = sum(j = 1, 3 * m + 1, y[j] * extra(a, M + j - 1))));
  for (a = 1, 3, for (Mi = 1, 5, my(e = E[a, Mi]);
    listput(info, if (e == 0, [a, Mi, "zero"], [a, Mi, poldegree(e, 'c), valuation(e, 'c), oc1(e), apply(f -> poldegree(f, 'c), factor(st(e))[, 1]~)]))));
  \\ ratios along each row: is E[a, M+1] / E[a, M] a constant times a power of c?
  for (a = 1, 3, emit(Str("m = ", m, ", row ", a, ": ratios E[a, M+1]/E[a, M] = ", vector(4, t, my(q = E[a, t + 1] / E[a, t]); if (type(q) == "t_RFRAC", "not a polynomial", if (q == polcoef(q, poldegree(q, 'c), 'c) * 'c^poldegree(q, 'c), Str(polcoef(q, poldegree(q, 'c), 'c), " c^", poldegree(q, 'c)), q))))));
  emit(Str("m = ", m, ", row 1, its factor off {0,1} at M = d: ", st(E[1, 1])));
  my(g = 0); forsubset([5, 3], S, g = gcd(g, matdet(vecextract(E, "..", Vec(S)))));
  emit(Str("m = ", m, ": entries [row a, M - d + 1, degree, c-order, (c-1)-order, other factor degrees] = ", Vec(info)));
  emit(Str("m = ", m, ": gcd of the 3 x 3 minors of E: c-order ", valuation(g, 'c), ", (c-1)-order ", oc1(g), ", degree off {0,1} ", poldegree(st(g), 'c))));
}
quit
