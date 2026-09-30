\\ Far polynomials with a symbolic half-integer shift (3 October 2026; cycle bmd-20261003-k)
\\ Question (outside lead of the neck atoms review): the far polynomial R_(n,k)(w) of research/tools/bmd_cube_far_u_space.gp
\\ is built from the shift 1/2 (P3, P4 by theta steps with alpha starting at 1/2, P4 exponent 1/2 - (n-1), half-integral
\\ exponent run).  Replace 1/2 by a symbol h everywhere; R_(n,k)(h, w) is then a polynomial in h and w that equals the
\\ recorded far polynomial at h = 1/2 (checked).  Is disc_w R(h, .) a product of linear factors in h (hypergeometric-type
\\ discriminant), and does h = 1/2 avoid its roots?  Reports the factorization of the w-discriminant and of the leading
\\ coefficient in w, over Q, at small (n, k).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
stripw(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N; }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  stripw(numerator(matdet(M)));
}
far(n, k, hh) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, hh - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, hh - (n - 1), E[i]); al--); p));
  wr([[0, 0, P3], [hh, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]);
}
main() = {
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[2, 3], [2, 4], [3, 3]]));
  foreach(cases, v, my(n = v[1], k = v[2]);
    my(Rh = far(n, k, 'h), R0 = far(n, k, 1/2));
    my(R0n = R0 / pollead(R0, 'w), Rhs = subst(Rh, 'h, 1/2), Rhsn = if (Rhs == 0, 0, Rhs / pollead(Rhs, 'w)));
    emit(Str("(n,k)=", v, ": deg_w R(h) = ", poldegree(Rh, 'w), ", deg_w R(1/2) = ", poldegree(R0, 'w),
      "; R(h) at h=1/2 matches the direct construction: ", Rhsn == R0n));
    my(lc = pollead(Rh, 'w), D = poldisc(Rh, 'w));
    emit(Str("  leading coefficient in w: ", factor(lc)));
    my(F = factor(D));
    emit(Str("  discriminant in w: degree ", poldegree(D, 'h), " in h; factors (degree, multiplicity): ",
      vector(#F~, i, [poldegree(F[i, 1], 'h), F[i, 2]])));
    emit(Str("  linear factors: ", select(x -> poldegree(x, 'h) == 1, F[, 1]~)));
    emit(Str("  value at h = 1/2 nonzero: ", subst(D, 'h, 1/2) != 0)));
}
default(parisizemax, 4000000000);
main();
quit
