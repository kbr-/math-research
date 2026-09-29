\\ Three top windows: zero-locus test (30 September 2026).
\\ Tested statement (thm:cube-three-top-windows, lambda = 3/2): for P = prod_(i<=a)(x-u_i)^2 Q,
\\ with K = prod_l (x-u_l)^3 Q^2 and I_m(u) = int_0^u x^m K,
\\   val det C[:,W_(M-1)] = (M-1)M + 2a      exactly when  I1 = det[I_m(u_i)]_(m=0..a-1) != 0,
\\   val det C[:,W_(M-2)] = (M-2)(M-1) + 2(a-1) exactly when  I2 = det[1 | I_m(u_i)]_(m=0..a-2) != 0,
\\ and W_M is governed by det[I_(m+1)(u_i)]_(m=0..a-1) (the multi-double top window theorem).
\\ Predictions: at a generic point every window has k(k+1) + 2 c_k; at a point with I1 = 0 (and the
\\ other two determinants nonzero) only W_(M-1) rises; at a point with I2 = 0 only W_(M-2) rises.
\\ The identities are algebraic, so the test runs over F_p, p the least prime above 2^61 with
\\ p = 1 mod 4: u_a is a root in F_p of
\\ I1 or I2 as a polynomial in u_a, the other parameters fixed; hypotheses asserted over F_p.
\\ The neck matrix C is that of bmd_cube_multi_double_window_excess.gp.
lam = 3/2;
\\ p = 1 mod 4: at a = 2, I2 is -(u_2-u_1)^7 times a positive integral for real data, and its
\\ quadratic factor has discriminant -(square), so it has roots only when -1 is a square mod p.
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
\\ The three integral determinants at roots us (entries in Q[t] or F_p) and fixed Q.
dets(us, Q) = {
  my(a = #us, K = prod(l = 1, a, (x - us[l])^3) * Q^2);
  my(I(m, u) = subst(intformal(x^m * K, x), x, u));
  [matdet(matrix(a, a, i, j, I(j - 1, us[i]))),
   matdet(matrix(a, a, i, j, if (j == 1, 1, I(j - 2, us[i])))),
   matdet(matrix(a, a, i, j, I(j, us[i])))];
}
run(label, us, Q, NN) = {
  my(a = #us, P = prod(i = 1, a, (x - us[i])^2) * Q, M = poldegree(P), D = dets(us, Q));
  for (i = 1, a, if (us[i] == 0 || subst(Q, x, us[i]) == 0, error("hypotheses"));
    for (l = i + 1, a, if (us[i] == us[l], error("hypotheses"))));
  if (subst(Q, x, 0) == 0 || poldegree(gcd(Q, deriv(Q))) > 0, error("hypotheses"));
  my(rk = vector(M, k, matrank(Gam(P, k))));
  my(pred = vector(M + 1, i, my(k = i - 1); k * (k + 1) + if (k, 2 * (k - rk[k]), 0)));
  my(v1 = vector(M + 1, i, winval(P, i - 1, NN)), v2 = vector(M + 1, i, winval(P, i - 1, NN + 20)));
  if (v1 != v2, error("truncation"));
  emit(Str(label, ": a=", a, " M=", M, "; [I1,I2,Itop] zero: ", apply(z -> z == 0, D),
    "; valuations ", v1, "; generic rule ", pred, "; excess over rule ", v1 - pred));
  v1 - pred;
}
\\ A root in F_p of f(t), avoiding forbidden values.
froot(f, bad) = {
  my(r = polrootsmod(f * Mod(1, p)));
  for (i = 1, #r, if (!setsearch(Set(bad), r[i]), return(r[i])));
  0;
}
main() = {
  my(bad = 0);
  \\ Cases a = 2, 3 (fixed u_1..u_(a-1), Q); the fixed roots are shifted by s = 0, 1, ...
  \\ until both I1 and I2 have an admissible root u_a in F_p. (A case a = 4, M = 8, Q = 1 found
  \\ no such roots for s <= 30 in a first run and was dropped.)
  foreach ([[[3], (x - 7)], [[3, -5], (x - 7)]], cs,
    my(Q = cs[2], a = #cs[1] + 1, M = 2 * a + poldegree(Q), NN = 3 * M + M * M + 20);
    my(fix, Dt, forb, s = 0);
    while (1,
      fix = cs[1] + vector(a - 1, i, s);
      Dt = dets(concat(fix, [t]), Q);
      forb = concat(concat(fix, [0]) * Mod(1, p), if (poldegree(Q) > 0, Vec(polrootsmod(Q * Mod(1, p))), []));
      if (vecmin(apply(abs, fix)) > 0 && poldegree(Dt[1], t) > 0 && poldegree(Dt[2], t) > 0
          && froot(Dt[1], forb) != 0 && froot(Dt[2], forb) != 0, break);
      s++; if (s > 30, error("no admissible roots")));
    my(us0 = concat(fix, [11]));
    emit(Str("case a=", a, ": fixed roots ", fix, ", Q = ", Q));
    \\ generic: rational point; I1 = 0; I2 = 0 (each with the other determinants checked).
    my(e0 = run("generic", us0 * Mod(1, p), Q * Mod(1, p), NN));
    if (e0 != vector(M + 1, i, 0), bad++);
    foreach ([[1, M], [2, M - 1]], ch,
      my(which = ch[1], kk = ch[2]);
      my(f = Dt[which], r = froot(f, forb), us = concat(fix * Mod(1, p), [r]));
      my(D = dets(us, Q * Mod(1, p)));
      if (D[which] != 0 || D[3 - which] == 0 || D[3] == 0, error("zero locus point"));
      my(ex = run(Str("I", which, "=0"), us, Q * Mod(1, p), NN));
      \\ window W_(M-which) is entry kk of the vector (k = M - which).
      for (i = 1, M + 1, if ((i == kk && ex[i] <= 0) || (i != kk && ex[i] != 0), bad++)));
  );
  emit(Str("mismatches: ", bad));
}
main();
