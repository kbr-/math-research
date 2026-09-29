\\ Leading coefficients of the two-far product windows as functions of the constants (29 September 2026;
\\ cycle bmd-20260929-zk; conj:cube-two-far-window-valuations).
\\ Rows (i, j): coefficient of S^e in (1+s_i/S)^(-3/2)(1+t_j S)^(-3/2), s_i = c_i q^i (i = 1, 2), t_j = d_j q^j (j = 1..n),
\\ q = 1000003 playing eps. For the window [-(n-r), n-1+r] the conjectured valuation is
\\ v0 = n^2 + 2 binom(n+1,3) - 2 n r + r(r+1)(r+5)/3. With integer constants, det / q^v0 mod q is the eps^v0 coefficient
\\ L_r(c, d) of the determinant evaluated mod q (the lower coefficients vanish identically if the conjecture holds;
\\ a non-integral quotient would refute it and is reported). Truncation at K = v0 + 1 changes only valuations > v0 + 1.
\\ For each variable x in (c1, c2, d1..dn), with the others fixed, L_r is interpolated as a polynomial in x mod q from
\\ 40 values and factored mod q; the output lists the degree and the factorization, to identify the surviving terms.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
be(k) = binomial(-3/2, k);
v0(n, r) = n^2 + 2 * binomial(n + 1, 3) - 2 * n * r + r * (r + 1) * (r + 5) / 3;
lead(n, r, cc, dd) = {
  my(p = n - r, L = 2 * n, v = v0(n, r), K = v + 1, s = vector(2, i, cc[i] * q^i), t = vector(n, j, dd[j] * q^j));
  my(ent(i, j, e) = sum(a = max(0, -e), K - max(0, e), be(a) * be(a + e) * s[i]^a * t[j]^(a + e)));
  my(A = matrix(L, L, rr, c, my(i = (rr - 1) \ n + 1, j = (rr - 1) % n + 1); ent(i, j, c - 1 - p)), d = matdet(A), x = d / q^v);
  if (denominator(x) % q == 0, error("valuation below v0 at n=", n, " r=", r));
  Mod(numerator(x), q) / Mod(denominator(x), q);
}
main() = {
  my(base = [3, -7, 2, 13, -5, 7, 17], X = 'x, NP = 40);
  foreach ([3, 4], n,
    for (r = 0, n - 1,
      my(cd = base[1 .. 2 + n]);
      emit(Str("2x", n, " r=", r, " (window [", -(n - r), ",", n - 1 + r, "], v0=", v0(n, r), ")"));
      for (vi = 1, 2 + n,
        my(xs = vector(NP, k, k + 20), ys = vector(NP, k, my(c = cd); c[vi] = xs[k]; lead(n, r, c[1 .. 2], c[3 .. 2 + n])));
        my(P = polinterpolate(apply(z -> Mod(z, q), xs), ys, X), name = if (vi <= 2, Str("c", vi), Str("d", vi - 2)));
        my(fa = factor(P), others = cd);
        emit(Str("  in ", name, ": degree ", poldegree(P), "; factors ", fa, "; other constants ", others)))));
}
main();
