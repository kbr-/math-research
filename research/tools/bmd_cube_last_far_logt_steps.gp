\\ Nearest-neighbour steps of the last-step far roots in log t, t = x/(1+x) (3 October 2026; cycle bmd-20261003-zzd).
\\ Prediction (four-circle picture, N = n + 7/2): roots satisfy t^N = s_i(x) with s_i slowly varying, so in log t each root's
\\ nearest neighbour is a step D with |D| N/(2 pi) close to 1 and D nearly imaginary (along a circle |t| = const).
\\ For e = 4..9: quantiles of |D| N/(2 pi) and of |Re D|/|D| over all roots, and the share of roots with |D| N/(2 pi) in
\\ [0.8, 1.25] and |Re D|/|D| < 0.3.  (Replaces the |t|-gap grouping of bmd_cube_last_far_circles.gp, which split conjugate
\\ pairs into separate groups.)
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 3, "research/results/bmd-20261003-zl", if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz")));
q(v, p) = my(s = vecsort(v)); precision(s[max(1, round(p * #s))], 4) * 1.;
{
for (e = 4, 9,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), r = polroots(W), L = apply(x -> log(x / (1 + x)), r), N = Rn(e) + 7/2, m = #L, A = vector(m), B = vector(m));
  for (i = 1, m, my(best = 1e9, D = 0);
    for (j = 1, m, if (j != i, my(d = L[j] - L[i]); d -= 2 * Pi * I * round(imag(d) / (2 * Pi)); if (abs(d) < best, best = abs(d); D = d)));
    A[i] = abs(D) * N / (2 * Pi); B[i] = abs(real(D)) / abs(D));
  my(good = #select(i -> A[i] >= 0.8 && A[i] <= 1.25 && B[i] < 0.3, [1..m]));
  emit(Str("e=", e, ": roots ", m, ", N = ", N, "; |D| N/(2 pi) quantiles 10/50/90%: ", [q(A, 0.1), q(A, 0.5), q(A, 0.9)],
    "; |Re D|/|D| quantiles 10/50/90%: ", [q(B, 0.1), q(B, 0.5), q(B, 0.9)], "; share on-circle with unit step: ", good, "/", m)));
}
