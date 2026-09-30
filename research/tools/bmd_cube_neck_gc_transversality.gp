\\ Cross-check of the transversality form of the neck genericity determinant (30 September 2026; bmd-20260930-zj).
\\ Statement tested: for phi_s = (1 + beta_s y)^(-7/2), s < l, U = sum_s Pol_(<n) phi_s and Phi_(>=c) the combinations
\\ of the phi_s vanishing to order c at 0 (1 <= c < l), the space U + y^(-1) Phi_(>=c) is ordinary at 0 (G_c != 0)
\\ if and only if the map a -> (first c Taylor coefficients of sum_s P_s(0) phi_s) is injective on the (c-1)-dimensional
\\ space Z of g = sum_s P_s phi_s, deg P_s <= n, of order >= l(n+1) - c + 1.  Both sides are computed modulo 2^61 - 1
\\ at random and at structured beta; the script reports agreement, dim Z, and the counts of each outcome.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
lam = -7/2;
coefrow(s, p, bet, L) = vector(L, r, my(k = r - 1 - p); if (k >= 0, Mod(binomial(lam, k), q) * bet[s]^k, Mod(0, q)));
direct(l, n, c, bet) = {
  my(L = l * n + l - c, rows = List(), Vc = matrix(c, l, r, s, Mod(binomial(lam, r - 1), q) * bet[s]^(r - 1)), K = matker(Vc));
  for (s = 1, l, for (p = 0, n - 1, listput(rows, coefrow(s, p, bet, L))));
  for (t = 1, #K, my(v = vector(L + 1, r, sum(s = 1, l, K[s, t] * Mod(binomial(lam, r - 1), q) * bet[s]^(r - 1)))); listput(rows, v[2..L + 1]));
  matdet(Mat(Vec(rows)~)) != 0;
}
transv(l, n, c, bet) = {
  my(L0 = l * (n + 1) - c + 1, rows = List(), idx = List());
  for (s = 1, l, for (p = 0, n, listput(rows, coefrow(s, p, bet, L0)); listput(idx, [s, p])));
  my(A = Mat(Vec(rows)~), Z = matker(A~));
  my(Vc = matrix(c, l, r, s, Mod(binomial(lam, r - 1), q) * bet[s]^(r - 1)));
  my(P0 = matrix(l, #Z, s, t, Z[(s - 1) * (n + 1) + 1, t]));
  [#Z, matrank(Vc * P0) == #Z];
}
main() = {
  my(agree = 0, tot = 0, ngood = 0, nbad = 0, dimok = 1);
  setrand(20260930);
  my(betas = List());
  for (l = 2, 6, for (i = 1, 3, listput(betas, vector(l, s, Mod(1 + random(10^9), q))));
    listput(betas, vector(l, s, Mod((-1)^s * s, q))); listput(betas, vector(l, s, Mod(s, q))));
  foreach (betas, bet, my(l = #bet);
    foreach ([4, 8], n, for (c = 1, l - 1,
      my(d = direct(l, n, c, bet), t = transv(l, n, c, bet));
      tot++; if (t[1] != c - 1, dimok = 0); if (d == t[2], agree++); if (d, ngood++, nbad++; emit(Str("  G_c = 0 at l=", l, " n=", n, " c=", c, " beta=", lift(bet), " transversal=", t[2]))))));
  emit(Str("cases (l = 2..6, n = 4, 8, all c < l; 3 random and 2 structured beta per l): ", tot));
  emit(Str("dim Z = c - 1 in every case: ", dimok));
  emit(Str("direct and transversal outcomes agree: ", agree, " of ", tot, "; G_c != 0 in ", ngood, ", G_c = 0 in ", nbad));
}
\\ Exact check over Q of the structured zeros: G_c at beta = (1..l), l = 3, 5, n = 4, every c < l.
exactdirect(l, n, c, bet) = {
  my(L = l * n + l - c, rows = List(), Vc = matrix(c, l, r, s, binomial(lam, r - 1) * bet[s]^(r - 1)), K = matker(Vc));
  my(cr(s, p) = vector(L, r, my(k = r - 1 - p); if (k >= 0, binomial(lam, k) * bet[s]^k, 0)));
  for (s = 1, l, for (p = 0, n - 1, listput(rows, cr(s, p))));
  for (t = 1, #K, my(v = vector(L + 1, r, sum(s = 1, l, K[s, t] * binomial(lam, r - 1) * bet[s]^(r - 1)))); listput(rows, v[2..L + 1]));
  matdet(Mat(Vec(rows)~));
}
main();
foreach ([3, 5], l, for (c = 1, l - 1, emit(Str("exact over Q, beta = 1..", l, ", n = 4, c = ", c, ": G_c-type determinant is zero: ", exactdirect(l, 4, c, vector(l, s, s)) == 0))));
quit
