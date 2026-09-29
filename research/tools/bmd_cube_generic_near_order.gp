\\ Is the near-collision vanishing order of two-far windows generic? (29 September 2026; cycle bmd-20260929-zq;
\\ conj:cube-two-far-double-support). The size clause |nu| >= r(r+1) of the two-sided rule says: with the far roots s_1, s_2
\\ fixed (q-adic units) and the near roots t_j = q u_j shrinking together, the window coordinate of <f_1, f_2> N on
\\ E_r = [-(n-r), n-1+r] has q-adic valuation exactly n(n-1) + r(r+1) (Delta(t)^2 contributes n(n-1)).
\\ Test A (the actual family): N = span of (1+t_j S)^(-3/2). Test B (generic spans with the same weights): N spanned by
\\ g_b = S^b + sum_{m=n..M} gamma_(b,m) S^m with gamma_(b,m) = random unit * q^(m-b); the analogue of the claim is
\\ valuation exactly r(r+1) (no Vandermonde factor). If B gives r(r+1), the order is a Schubert-type property of
\\ <f_1, f_2> N near Pol_(<n); if B gives less, the proof must use the family (1+tS)^(-3/2).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
be(k) = if (k < 0, 0, binomial(-3/2, k));
setrand(20260929);
main() = {
  my(sv = [3, -7], K = 60);
  foreach ([3, 4, 5], n, for (r = 0, n - 1,
    my(m = n - r, E = [-m .. n - 1 + r], L = 2 * n, M = n + r * (r + 1) + 4);
    \\ Test A
    my(u = vector(n, j, [2, 13, -5, 7, 17][j]), t = q * u);
    my(A = matrix(L, L, rr, c, my(i = (rr - 1) \ n + 1, j = (rr - 1) % n + 1, e = E[c]); sum(a = max(0, -e), K, be(a) * be(a + e) * sv[i]^a * t[j]^(a + e))));
    my(dA = matdet(A), vA = if (dA == 0, oo, valuation(dA, q)));
    \\ Test B (two random draws)
    my(vB = vector(2, rep,
      my(G = matrix(n, M + 1, b, k, my(bb = b - 1, kk = k - 1); if (kk == bb, 1, if (kk >= n, (random(2 * q) - q) * q^(kk - bb), 0))));
      my(B = matrix(L, L, rr, c, my(i = (rr - 1) \ n + 1, b = (rr - 1) % n + 1, e = E[c]); sum(k = 0, M, G[b, k + 1] * be(k - e) * sv[i]^max(0, k - e))));
      my(dB = matdet(B)); if (dB == 0, oo, valuation(dB, q))));
    emit(Str("2x", n, " r=", r, ": family valuation ", vA, " (predicted ", n * (n - 1) + r * (r + 1), "); generic-span valuations ", vB, " (analogue ", r * (r + 1), ")"))));
}
main();
