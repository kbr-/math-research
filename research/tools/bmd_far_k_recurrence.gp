\\ Recurrences in k for the merge far Wronskians (6 October 2026; cycle bmd-20261006-f).  Tested statement: the raw
\\ far Wronskian a_k = Wr_k(w0) of the space built in research/tools/bmd_far_discriminants.gp (before stripping powers
\\ of w, w-1 and content) satisfies a linear recurrence in k with coefficients polynomial in k (P-recursive), or has
\\ q-type growth (second differences of log|a_k| tending to a constant).  Either would bring in the Beraha-Kahane-Weiss
\\ theory of zeros of recursive families.  Env N (n), KMAX, W0 (list of rational points), W1 (reference point for the
\\ normalization-free ratio a_k(w0)/a_k(W1)), RMAX, SMAX, OUT.  Cases with too few equations are reported as skipped.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
closed(E, s) = {
  my(q = #E, phi = x -> prod(i = 1, q, x - E[i]));
  sum(r = 0, q, sum(i = 0, r, (-1)^(r - i) * binomial(r, i) * phi(s + i)) * binomial(1/2, r) * (-1)^r * 'w^r * (1 - 'w)^(q - r));
}
\\ raw Wronskian matrix value at w0 (derivatives taken symbolically, then evaluated)
rawwr(n, k, w0) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)));
  my(P3 = vector(k - 1, j, 'w^(j - 1) * closed(E, j - 1) / 'w^(P + 2)));
  my(P4 = vector(n, j, 'w^(j - 1) * closed(E, 1/2 - (n - 1) + j - 1) / 'w^((k - 1) * n)));
  my(gam = 3/2 - n + (k - 1) * n - P - 2, cls = [[0, P3], [gam, P4]]);
  my(d = (k - 1) + n, M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1]); foreach (c[2], f, row++; my(g = f);
    for (m = 1, d, M[row, m] = subst(g, 'w, w0); g = deriv(g, 'w) + (a / 'w) * g)));
  matdet(M);
}
\\ P-recursive guess: kernel of sum_{i<=r} sum_{j<=s} c_ij k^j a_{k+i} = 0 over the available k
guess(a, k0, r, s) = {
  my(L = #a - r, cols = (r + 1) * (s + 1));
  if (L <= cols, return(-1));
  my(M = matrix(L, cols, t, c, my(i = (c - 1) \ (s + 1), j = (c - 1) % (s + 1), kk = k0 + t - 1); kk^j * a[t + i]));
  #matker(M);
}
{
my(n = eval(getenv("N")), kmax = eval(getenv("KMAX")), rmax = eval(getenv("RMAX")), smax = eval(getenv("SMAX")));
W1 = eval(getenv("W1"));
emit(Str("parameters: N = ", n, ", KMAX = ", kmax, ", W0 = ", getenv("W0"), ", W1 = ", W1, ", RMAX = ", rmax, ", SMAX = ", smax));
foreach(eval(getenv("W0")), w0,
  my(a = vector(kmax - 2, t, rawwr(n, t + 2, w0)));
  emit(Str("n = ", n, ", w0 = ", w0, ", k = 3..", kmax));
  my(la = vector(#a, t, log(abs(a[t]) + 0.)));
  emit(Str("  log|a_k|: ", apply(x -> round(x * 100) / 100., la)));
  emit(Str("  second differences: ", vector(#la - 2, t, round((la[t + 2] - 2 * la[t + 1] + la[t]) * 100) / 100.)));
  for (r = 1, rmax, for (s = 0, smax, my(g = guess(a, 3, r, s));
    if (g < 0, emit(Str("  skipped: order ", r, ", degree ", s, " (equations ", #a - r, " <= unknowns ", (r + 1) * (s + 1), ")")),
      if (g > 0, emit(Str("  P-recursive candidate: order ", r, ", degree ", s, ", kernel dim ", g, " (equations ", #a - r, ")")),
        emit(Str("  tested, no relation: order ", r, ", degree ", s, " (equations ", #a - r, ", unknowns ", (r + 1) * (s + 1), ")"))))));
  my(w1 = W1, b = vector(kmax - 2, t, rawwr(n, t + 2, w1)), lr = vector(#a, t, la[t] - log(abs(b[t]) + 0.)));
  emit(Str("  normalization-free log|a_k(w0)/a_k(", w1, ")| second differences: ", vector(#lr - 2, t, round((lr[t + 2] - 2 * lr[t + 1] + lr[t]) * 100) / 100.))));
}
quit;
