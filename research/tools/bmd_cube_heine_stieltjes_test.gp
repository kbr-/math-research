\\ Heine-Stieltjes test for the Weierstrass polynomials of caterpillar components (29 September 2026; cycle
\\ bmd-20260929-zc). Tested question: does the non-branch Wronskian polynomial q of a component satisfy a second-order
\\ equation A q'' + B q' + C q = 0 of Fuchsian-at-infinity shape (deg B <= deg A - 1, deg C <= deg A - 2) whose
\\ leading coefficient A = S^al (1 + c S)^bt vanishes only at the branch values, with small deg A = d + 1?
\\ If so, q has simple zeros away from the branch values (a double zero at an ordinary point forces q = 0).
\\ For squarefree q of degree 12 such a solution always exists once d >= 11 (B is determined modulo q), so only
\\ d <= 10 is informative. Control: the binary-face polynomials Q_r with A = 1 - T^2, d = 1 (Gegenbauer).
\\ Prints, for d = 1..11 and every split (al, bt), whether a solution (B, C) exists (1 = yes). With A fixed the
\\ solution set is affine, and a single point when q is squarefree.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  numerator(matdet(P));
}
\\ existence (1) or not (0) of (B, C) with A q'' + B q' + C q = 0, deg B <= d, deg C <= d - 1
exists(q, A, d, v) = {
  my(unk = 2 * d + 1, cols = vector(unk, k, if (k <= d + 1, v^(k - 1) * deriv(q, v), v^(k - d - 2) * q)));
  my(rhs = -A * deriv(deriv(q, v), v), D = poldegree(A * deriv(deriv(q, v), v)) + 1);
  my(M = matrix(D + d + 2, unk + 1, r, k, polcoef(if (k <= unk, cols[k], rhs), r - 1, v)));
  my(K = matker(M)); #[w | w <- K, w[unk + 1] != 0] > 0;
}
Q(r) = { my(a = 1, b = 3 * T); if (r == 0, return(a)); for (k = 1, r - 1, [a, b] = [b, (2 * k + 3) * T * b + k * (k + 2) * (1 - T^2) * a]); b; }
main() = {
  emit(Str("control Q_3, A = 1 - T^2, d = 1: solution exists ", exists(Q(3), 1 - T^2, 1, T)));
  emit(Str("control Q_6, A = 1 - T^2, d = 1: solution exists ", exists(Q(6), 1 - T^2, 1, T)));
  my(c = -3, l = -3/2, ph = 1 + c * S, kap = 1/100);
  my(fl = [[[S, 0]], [[ph, l]], [[S, 1], [ph, l]], [[S, -3]], [[S, l], [ph, l]], [[S, l - 1], [ph, l]],
           [[S, l - 1]], [[S, l]], [[S, l + 1]], [[S, l - 2], [S^4 + kap, 1]]]);
  my(q = wronsk(fl));
  while (subst(q, S, 0) == 0, q = q / S);
  while (subst(q, S, -1 / c) == 0, q = q / (S + 1 / c));
  emit(Str("N=5 middle polynomial: degree ", poldegree(q), "; squarefree ", poldegree(gcd(q, deriv(q))) == 0));
  for (d = 1, 11, my(res = List());
    for (al = 0, d + 1, listput(res, [al, d + 1 - al, exists(q, S^al * ph^(d + 1 - al), d, S)]));
    emit(Str("N=5 middle, d=", d, ": [al, bt, solution exists] ", Vec(res))));
}
main();
