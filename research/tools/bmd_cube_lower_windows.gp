\\ Lower singular windows: zero-locus test (30 September 2026).
\\ Tested statement (thm:cube-lower-singular-windows, lambda = 3/2): for P = prod_(i<=a)(x-u_i)^2 Q,
\\ K = prod_l (x-u_l)^3 Q^2, I_m(u) = int_0^u x^m K, and 3 <= n <= a,
\\   val det C[:,W_(M-n)] >= (M-n)(M-n+1) + 2(a-n+1), with equality exactly when
\\   I_n = det[ u_i^r (0 <= r <= n-2) | I_m(u_i) (0 <= m <= a-n) ]_(i=1..a) != 0.
\\ Prediction: at a point with I_n = 0 (the other I_n' nonzero) exactly the window W_(M-n) rises
\\ above k(k+1) + 2 c_k; at a generic control no window does. The identities are algebraic, so
\\ the test runs over F_p (p the least prime above 2^61 with p = 1 mod 4): u_a is a root in F_p
\\ of I_n as a polynomial in u_a, the other roots fixed. Neck matrix as in
\\ bmd_cube_multi_double_window_excess.gp.
lam = 3/2;
p = nextprime(2^61); while (p % 4 != 1, p = nextprime(p + 1));
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-lam, j);
Gp(P, m, n) = polcoeff(lift(Mod(x^n, P)), m, x);
G(P, m, n) = my(M = poldegree(P)); if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * Gp(P, m, n)));
Gam(P, k) = my(M = poldegree(P)); matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1); G(P, m, D + 1) - G(P, m - 1, D) - G(P, m, M) * G(P, M - 1, D));
winval(P, k, NN) = {
  my(M = poldegree(P), J = NN - 1, rows = List(), S);
  my(tv = vector(J, j, polcoeff(truncate(-tanh(lam * atanh(y + O(y^(J + 2))))), j, y)));
  for (m = 0, M - 1,
    my(u = T^m + sum(n = M, NN, G(P, m, n) * e^(n - m) * T^n));
    my(w = sum(j = 1, J, tv[j] * T^(J - j)) * u);
    listput(rows, [vector(3 * M, c, polcoeff(u, c - 1 - M, T)), vector(3 * M, c, polcoeff(w, c - 1 - M + J, T))]));
  S = vector(2 * M, i, i - (M - k) - 1);
  my(A = matrix(2 * M, 2 * M, r, c, my(m = (r - 1) % M, typ = (r - 1) \ M); rows[m + 1][typ + 1][S[c] + M + 1]));
  my(V = NN - M, As = matrix(2 * M, 2 * M, r, c, A[r, c] * Mod(1, p) + O(e^V)));
  my(d = matdet(As));
  if (d == 0 || valuation(d, e) >= V - 2, error("precision"));
  valuation(d, e);
}
\\ I_n for n = 1..a (n = 1, 2 are the three top windows' determinants, same formula).
In(us, Q, n) = {
  my(a = #us, K = prod(l = 1, a, (x - us[l])^3) * Q^2);
  my(I(m, u) = subst(intformal(x^m * K, x), x, u));
  matdet(matrix(a, a, i, c, if (c <= n - 1, us[i]^(c - 1), I(c - n, us[i]))));
}
run(label, us, Q, NN) = {
  my(a = #us, P = prod(i = 1, a, (x - us[i])^2) * Q, M = poldegree(P));
  for (i = 1, a, if (us[i] == 0 || subst(Q, x, us[i]) == 0, error("hypotheses"));
    for (l = i + 1, a, if (us[i] == us[l], error("hypotheses"))));
  if (subst(Q, x, 0) == 0 || poldegree(gcd(Q, deriv(Q))) > 0, error("hypotheses"));
  my(zs = vector(a, n, In(us, Q, n) == 0));
  my(rk = vector(M, k, matrank(Gam(P, k))));
  my(pred = vector(M + 1, i, my(k = i - 1); k * (k + 1) + if (k, 2 * (k - rk[k]), 0)));
  my(v1 = vector(M + 1, i, winval(P, i - 1, NN)), v2 = vector(M + 1, i, winval(P, i - 1, NN + 20)));
  if (v1 != v2, error("truncation"));
  emit(Str(label, ": a=", a, " M=", M, "; I_1..I_a zero: ", zs, "; valuations ", v1,
    "; k(k+1)+2c_k ", pred, "; excess ", v1 - pred));
  [zs, v1 - pred];
}
froot(f, bad) = {
  my(r = polrootsmod(f * Mod(1, p)));
  for (i = 1, #r, if (!setsearch(Set(bad), r[i]), return(r[i])));
  0;
}
main() = {
  my(bad = 0);
  \\ Cases: a = 3, M = 7 (Q linear), n = 3; a = 4, M = 8 (Q = 1), n = 3, 4. The fixed roots are
  \\ shifted by s = 0, 1, ... until I_n has an admissible root u_a in F_p.
  foreach ([[[3, -5], (x - 7), [3]], [[2, -3, 5], 1, [3, 4]]], cs,
    my(Q = cs[2], a = #cs[1] + 1, M = 2 * a + poldegree(Q), NN = 3 * M + M * M + 20);
    my(fix = cs[1], us0 = concat(fix, [11]));
    my(r0 = run("generic", us0 * Mod(1, p), Q * Mod(1, p), NN));
    if (r0[1] != vector(a, i, 0) || r0[2] != vector(M + 1, i, 0), bad++);
    foreach (cs[3], n,
      \\ If no shift s <= 30 gives a root, move to the next prime = 1 mod 4 (the non-branch factor
      \\ of I_a has no real roots, and for a = 4 had no F_p-root at the first prime).
      my(s = 0, f, forb, r, fx, p0 = p);
      while (1,
        fx = fix + vector(a - 1, i, s);
        f = In(concat(fx, [t]), Q, n);
        forb = concat(concat(fx, [0]) * Mod(1, p), if (poldegree(Q) > 0, Vec(polrootsmod(Q * Mod(1, p))), []));
        if (vecmin(apply(abs, fx)) > 0 && poldegree(f, t) > 0, r = froot(f, forb); if (r != 0, break));
        s++; if (s > 30, s = 0; p = nextprime(p + 1); while (p % 4 != 1, p = nextprime(p + 1));
          if (p > p0 + 10^6, error("no admissible root"))));
      if (p != p0, emit(Str("  (prime changed to ", p, ")")));
      my(us = concat(fx * Mod(1, p), [r]));
      my(res = run(Str("I", n, "=0 (shift ", s, ")"), us, Q * Mod(1, p), NN));
      \\ only I_n may vanish, and only W_(M-n) (vector entry M-n+1) may rise
      for (i = 1, a, if ((i == n) != res[1][i], bad++));
      for (i = 1, M + 1, if ((i == M - n + 1 && res[2][i] <= 0) || (i != M - n + 1 && res[2][i] != 0), bad++))));
  emit(Str("mismatches: ", bad));
}
main();
