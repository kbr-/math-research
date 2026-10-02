\\ Counterexample check (cycle bmd-20261009-l, 9 October 2026): standard-negative and monomial minimality at roots
\\ with e_1 of positive valuation. M = 2, roots (1, -1 + eta), eta = q = 1000003; also M = 3, roots (1, -1 + eta, 3)
\\ shifted so e_1 = eta: (1, -4 + eta, 3). Computes the penalty sequences (t = 0..3) of the window Lambda_1 and of every
\\ coordinate with standard negatives {1} in columns [-M, 2M], and of the kernel monomial sets D_i, i <= 3 (k = 1 when
\\ M = 2). Reports violations of: penalty(Lambda, t) >= penalty(window, t); val [u^n] D_T >= val [u^n] D_{T0}.
OUT = "research/results/bmd-20261009-l/symmetric-roots.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
TMAX = 3;
pens(Y, L) = {
  my(M = #Y, N = apply(t -> -t, select(t -> t < 0, L)), p = #N, k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k, NU = B + TMAX);
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(D = matdet(X), V2 = 2 * vq(vand(Y)));
  vector(TMAX + 1, j, my(cf = polcoef(D, B + j - 1, 'u)); if(cf == 0, oo, vq(cf) - V2))
};
run(name, Y) = {
  my(M = #Y, cols = [-M .. 2 * M], w = pens(Y, [-1 .. 2 * M - 2]), bad = 0, tot = 0);
  write(OUT, name, " M=", M, ", e_1 valuation ", vq(vecsum(Y)), ": window Lambda_1 penalties t=0..", TMAX, ": ", w);
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), N = select(t -> t < 0, L));
    if(N == [-1] && L != [-1 .. 2 * M - 2], tot++; my(v = pens(Y, L));
      for (t = 0, TMAX, if(v[t + 1] < w[t + 1], bad++; write(OUT, "   violation: Lambda = ", L, " t = ", t, " penalty ", v[t + 1], " < window ", w[t + 1])))));
  write(OUT, "  coordinates with negatives {1}: ", tot, ", violations of standard-negative minimality: ", bad);
};
{
  my(e = q);
  run("symmetric pair", [1, -1 + e]);
  run("symmetric pair plus a root", [1, -4 + e, 3]);
  run("control (e_1 a unit)", [1, 1 + e]);
}
