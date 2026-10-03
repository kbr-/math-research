\\ Test of the Hankel-block law for flow orders (cycle bmd-20261009-bj, 9 October 2026).
\\ Prediction (thm:cube-hankel-block-flow-orders): if H_(k0)(y) != 0, H_(k0+1)(y) = ... = H_(k0+N-1)(y) = 0, H_(k0+N)(y) != 0,
\\ then for k = k0 + i (0 < i < N) the flow order of H_k is i(N - i) and the leading coefficients satisfy
\\ c_(k+1) c_(k-1) / c_k^2 = -S(i+1, N-i-1, 2k+2) S(i-1, N-i+1, 2k-2) / S(i, N-i, 2k)^2 with
\\ S(r, c, n) = prod_(boxes (a,b) of the r x c rectangle) (n + b - a)/(a + b - 1) = s_(c^r)(1^n).
\\ The ratio law conj:cube-flow-order-ratio-law, -a(a + 2k^2)/(4k^2(4k^2 - 1)), is the case k0 = 0.
\\ Test point: M = 5, centred quintic z^5 + z^3 - z^2 + e4 z - e5 with Hank_2 = 0 (e4 = 57/40) and Hank_3 = 0
\\ (e5 an exact algebraic root), so the block is k0 = 1, N = 3. Exact arithmetic over the number field of e5.
OUT = "research/results/bmd-20261009-bj/hankel-block-test.txt";
default(parisizemax, 2 * 10^9);
S(r, c, n) = prod(a = 1, r, prod(b = 1, c, (n + b - a) / (a + b - 1)));
psums(cf, M, n) = {  \\ cf = [e1..eM]; power sums p_1..p_n by Newton
  my(p = vector(n));
  for (j = 1, n, my(s = if (j <= M, (-1)^(j - 1) * j * cf[j], 0)); for (i = 1, min(j - 1, M), s += (-1)^(i - 1) * cf[i] * p[j - i]); p[j] = s);
  p;
}
hank(p, M, k) = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, p[i + j - 2])));
flowhank(P, M, k, T) = {
  my(Q = subst(P, 'z, 'x / (1 + 'tt * 'x)) * (1 + 'tt * 'x)^M + O('tt^T));
  Q = Q / polcoeff(Q, M, 'x);
  my(a = vector(M, j, polcoeff(Q, M - j, 'x)), pw = vector(2*k + 1));
  for (j = 1, 2*k, my(s = if (j <= M, j * a[j], 0)); for (i = 1, min(j - 1, M), s += a[i] * pw[j - i]); pw[j] = -s);
  matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2]))) + O('tt^T);
}
{
  my(M = 5, e2 = 1, e3 = 1, e4 = (12*e2^3 + 45*e3^2) / (40*e2), w = varlower("w"));
  my(h3 = hank(psums([0, e2, e3, e4, w], M, 6), M, 3), fa = factor(h3)[, 1]);
  write(OUT, "Hank_3 as a polynomial in e5 factors as: ", factor(h3));
  foreach(fa, f, if (poldegree(f, w) >= 1,
    \\ (a first run used Mod(w, f) also for linear f; the polmod wrapper broke the valuations)
    my(e5 = if (poldegree(f, w) == 1, -polcoeff(f, 0, w) / polcoeff(f, 1, w), Mod(w, f)), cf = [0, e2, e3, e4, e5], p = psums(cf, M, 10));
    my(Hy = vector(M, k, hank(p, M, k - 1)));  \\ H_0..H_4 at y
    my(P = 'z^5 + e2*'z^3 - e3*'z^2 + e4*'z - e5, T = 20);
    write(OUT, "factor ", f, ": H_0..H_4 at y zero? ", apply(h -> h == 0, Hy));
    my(Hs = vector(M, k, flowhank(P, M, k - 1, T)), ord = apply(h -> valuation(h, 'tt), Hs));
    my(c = vector(M, k, polcoeff(Hs[k], ord[k], 'tt)));
    write(OUT, "   flow orders j_0..j_4 = ", ord, " (predicted [0, 0, 2, 2, 0] for k0 = 1, N = 3)");
    foreach([[2, 1], [3, 2]], ki, my([k, i] = ki, N = 3, a = i * (N - i));
      my(obs = c[k + 2] * c[k] / c[k + 1]^2, pred = -S(i + 1, N - i - 1, 2*k + 2) * S(i - 1, N - i + 1, 2*k - 2) / S(i, N - i, 2*k)^2);
      my(law = -a * (a + 2*k^2) / (4*k^2 * (4*k^2 - 1)));
      write(OUT, "   k = ", k, " (i = ", i, "): c_(k+1) c_(k-1)/c_k^2 = ", obs, "; block prediction ", pred, ", equal: ", obs == pred,
            "; (a,k)-law ", law, ", equal: ", obs == law))));
}
