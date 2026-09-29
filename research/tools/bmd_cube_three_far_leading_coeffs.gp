\\ Falsification test for the route review of 29 September 2026 (cycle bmd-20260929-zn): does every far-near window
\\ have a single leading monomial at caterpillar weights for F >= 3, as conj:cube-two-far-leading-monomial found for F = 2?
\\ Rows (i, j): coefficient of S^e in (1+s_i/S)^(-3/2)(1+t_j S)^(-3/2), s_i = c_i q^i (i = 1..3), t_j = d_j q^j (j = 1..3),
\\ q = 1000003. Windows [-p, 8-p], p = 2..6, with the valuations 48, 39, 38, 39, 48 measured in cycle bmd-20260929-zj.
\\ For each window and each of the six constants, det / q^v mod q is interpolated as a polynomial in that constant
\\ (others fixed) from 40 values and factored mod q. A single leading monomial makes every restriction a pure power.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
be(k) = binomial(-3/2, k);
lead(F, n, p, v, cc, dd) = {
  my(L = F * n, K = v + 1, s = vector(F, i, cc[i] * q^i), t = vector(n, j, dd[j] * q^j));
  my(ent(i, j, e) = sum(a = max(0, -e), K - max(0, e), be(a) * be(a + e) * s[i]^a * t[j]^(a + e)));
  my(A = matrix(L, L, rr, c, my(i = (rr - 1) \ n + 1, j = (rr - 1) % n + 1); ent(i, j, c - 1 - p)), d = matdet(A), x = d / q^v);
  if (denominator(x) % q == 0, error("valuation below v at p=", p));
  Mod(numerator(x), q) / Mod(denominator(x), q);
}
main() = {
  my(F = 3, n = 3, vals = [48, 39, 38, 39, 48], base = [3, -7, 11, 2, 13, -5], X = 'x, NP = 40);
  for (k = 1, 5, my(p = k + 1, v = vals[k]);
    emit(Str("3x3 window [", -p, ",", 8 - p, "], v=", v));
    for (vi = 1, 6,
      my(xs = vector(NP, u, u + 20), ys = vector(NP, u, my(c = base); c[vi] = xs[u]; lead(F, n, p, v, c[1 .. 3], c[4 .. 6])));
      my(P = polinterpolate(apply(z -> Mod(z, q), xs), ys, X), name = if (vi <= 3, Str("c", vi), Str("d", vi - 3)), fa = factor(P));
      my(pure = (#fa[, 1] == 1 && fa[1, 1] == X) || poldegree(P) == 0);
      emit(Str("  in ", name, ": degree ", poldegree(P), ", pure power: ", pure, if (!pure, Str(", factors ", fa), "")))));
}
main();
