\\ Reduction modulo small primes of the Weierstrass polynomials of rigid caterpillar components (29 September 2026;
\\ cycle bmd-20260929-zza). q = q_{F,n} is the primitive integer non-branch Wronskian polynomial of
\\   V = Pol_<P_n + phi Pol_<n + S^-3 Pol_<P_F(1/S) + S^-l phi Pol_<F(1/S) + S^-l <S^e : e in W>,
\\ l = 3/2, phi = (1+S)^-l, c = 1 (as in bmd_cube_review_zy_tests.gp). Tested statement: for p = 3, 5, 7, 11, 13,
\\ whether q mod p keeps its degree and is squarefree (either certifies squarefreeness over Q), and the degrees of
\\ the irreducible factors of q mod p. The prime 3 is singled out because (1+S)^(-3/2) = (1+S^3)^(-1/2) there.
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
report(name, fl) = {
  my(q = nb(fl), d = poldegree(q));
  emit(Str(name, ": degree ", d, "; leading coefficient ", factor(pollead(q)), "; constant term ", factor(polcoef(q, 0))));
  foreach ([3, 5, 7, 11, 13], p,
    my(qp = q * Mod(1, p), dp = poldegree(qp));
    if (dp < 0, emit(Str("  p=", p, ": q = 0 mod p")); next);
    my(sf = poldegree(gcd(qp, deriv(qp))) == 0, fa = factor(qp));
    emit(Str("  p=", p, ": degree ", dp, if (dp == d, " (kept)", " (drops)"), "; squarefree ", sf,
             "; factor degrees ", vecsort(apply(poldegree, fa[, 1]~)), " with multiplicities ", fa[, 2]~)));
  emit(Str("  q = ", q));
}
main() = {
  report("2x2 limit, window [-1,2]", space(2, 2, [-1 .. 2]));
  report("2x2 limit, window [-2,1]", space(2, 2, [-2 .. 1]));
  report("2x3, window [-2,3]", space(2, 3, [-2 .. 3]));
  report("2x4, window [-3,4]", space(2, 4, [-3 .. 4]));
  report("3x3, window [-4,4]", space(3, 3, [-4 .. 4]));
}
main();
