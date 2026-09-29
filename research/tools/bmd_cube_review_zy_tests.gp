\\ Route review bmd-20260929-zy (29 September 2026): cheap tests of the review's leads and bridges on the
\\ Weierstrass polynomials q_{F,n} of caterpillar middle components (prop:cube-caterpillar-component-count,
\\ cor:cube-far-near-limits-small). A component with a monomial window W is
\\   Pol_<P_n + phi Pol_<n + S^-3 Pol_<P_F(1/S) + S^-l phi Pol_<F(1/S) + S^-l <S^e : e in W>,
\\ l = 3/2, phi = (1 + c S)^-l. Rescaling S -> S / c maps every piece to itself up to constants, so for monomial
\\ windows the Weierstrass points are c^-1 times those at c = 1: the component has no modulus. We use c = 1.
\\ Tests, on 2x3 [-2,3] (N=6), 2x4 [-3,4] and 3x3 [-4,4] (N=7), and on the 2x2 tie limits kappa -> 0, infinity:
\\  (a) degree and squarefreeness of q (for the tie limits: does the degree stay 12, so that squarefreeness at the
\\      limit gives simplicity for generic kappa);
\\  (b) smoothness of disc(q): a product of linear factors lambda + k with small k and small constants would make it
\\      a product of small primes (Shapovalov/Varchenko determinant lead);
\\  (c) 2-adic and 3-adic Newton polygons: all edges of length one would force distinct roots (p-adic bridge);
\\  (d) moduli and arguments of the roots: on one circle or one line (Lee-Yang bridge);
\\  (e) an equation A q''' + B q'' + C q' + D q = 0 of hypergeometric type, A = S^a (1+S)^(3-a), deg B <= 2,
\\      deg C <= 1, deg D = 0 (Jacobi-Pineiro multiple orthogonal polynomial lead).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  numerator(matdet(P));
}
nb(fl) = {
  my(q = wronsk(fl));
  while (subst(q, S, 0) == 0, q = q / S);
  while (subst(q, S, -1) == 0, q = q / (S + 1));
  q / content(q);
}
space(F, n, W) = {
  my(l = -3/2, ph = 1 + S, PF = F * (F - 1) / 2, Pn = n * (n - 1) / 2);
  concat([[[[S, k]] | k <- [0 .. Pn - 1]], [[[S, k], [ph, l]] | k <- [0 .. n - 1]], [[[S, -3 - k]] | k <- [0 .. PF - 1]],
          [[[S, l - k], [ph, l]] | k <- [0 .. F - 1]], [[[S, l + e]] | e <- W]]);
}
hyp3(q) = {
  my(best = []);
  for (a = 0, 3,
    my(A = S^a * (1 + S)^(3 - a), U = vector(7, i, eval(Str("u", i))),
       E = A * deriv(deriv(deriv(q))) + (U[1] + U[2] * S + U[3] * S^2) * deriv(deriv(q)) + (U[4] + U[5] * S) * deriv(q) + U[6] * q,
       M = matrix(poldegree(q) + 3, 7));
    \\ E is affine in u1..u6: the constant part comes from A q'''.
    my(E0 = subst(subst(subst(subst(subst(subst(E, u1, 0), u2, 0), u3, 0), u4, 0), u5, 0), u6, 0));
    for (i = 1, 6, my(Ei = subst(E, U[i], 1) - subst(E, U[i], 0)); Ei = subst(subst(subst(subst(subst(subst(Ei, u1, 0), u2, 0), u3, 0), u4, 0), u5, 0), u6, 0);
      for (r = 0, poldegree(q) + 2, M[r + 1, i] = polcoef(Ei, r, S)));
    for (r = 0, poldegree(q) + 2, M[r + 1, 7] = polcoef(E0, r, S));
    \\ solvable iff the last column lies in the span of the first six
    best = concat(best, [[a, matrank(M[, 1 .. 6]) == matrank(M)]]));
  best;
}
report(name, fl) = {
  my(q = nb(fl), d = poldegree(q), z = polroots(q), D = poldisc(q), f = factor(D, 10^6));
  my(big = [p | p <- f[, 1]~, p > 10^6 || !isprime(p)]);
  emit(Str(name, ": dimension ", #fl, "; non-branch degree ", d, "; squarefree ", poldegree(gcd(q, deriv(q))) == 0));
  emit(Str("  (b) |disc| has ", #Str(abs(D)), " digits; prime factors below 10^6: ", [p | p <- f[, 1]~, p < 10^6],
           "; unfactored cofactors: ", #big, if (#big, Str(" (largest ", #Str(vecmax(big)), " digits)"), "")));
  foreach ([2, 3], p, my(sl = newtonpoly(q, p)); emit(Str("  (c) ", p, "-adic slopes: ", #Set(sl), " distinct among ", d, " roots")));
  my(mo = apply(abs, z), ar = apply(w -> arg(w), z));
  emit(Str("  (d) moduli from ", round(vecmin(mo) * 1000) / 1000., " to ", round(vecmax(mo) * 1000) / 1000.,
           "; real roots ", #[w | w <- z, abs(imag(w)) < 1e-20], "; roots with real part -1/2: ", #[w | w <- z, abs(real(w) + 1/2) < 1e-20]));
  emit(Str("  (e) order-3 hypergeometric equation, by a = 0..3: ", hyp3(q)));
}
main() = {
  report("2x2 tie, kappa -> 0, window [-1,2]", space(2, 2, [-1 .. 2]));
  report("2x2 tie, kappa -> infinity, window [-2,1]", space(2, 2, [-2 .. 1]));
  report("2x3, window [-2,3]", space(2, 3, [-2 .. 3]));
  report("2x4, window [-3,4]", space(2, 4, [-3 .. 4]));
  report("3x3, window [-4,4]", space(3, 3, [-4 .. 4]));
}
main();
