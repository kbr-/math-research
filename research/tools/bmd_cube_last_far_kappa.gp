\\ Symbolic-exponent last even-peeling far space (3 October 2026; cycle bmd-20261003-zn).
\\ At the last step (l = 1) the far space is exact (prop:cube-peeling-last-far-mobius): in x (c = 1, doubles at x = 0 and -1),
\\   F(kappa) = P_<R_e + <(1+x)^-3> + <x^-3> + (1+x)^(-3-kappa) P_<4e + x^(-3-kappa) P_<4e + (1+x)^(-3+kappa) x^(-3-kappa) P_<4,
\\ which is F_(b-1) at kappa = 1/2.  Hypothesis tested (Jacobi-type discriminant): D(kappa) = disc_x W(kappa, x), W the
\\ non-branch part of W(F(kappa)), is a product of linear factors in kappa (explicit exceptional exponents).
\\ Method (mod q = 2^61 - 1): for f = x^b (1+x)^g p(x), f^(m) = x^(b-m) (1+x)^(g-m) h_m with h_0 = p and
\\   h_(m+1) = x(1+x) h_m' + (b(1+x) + g x - m(1+2x)) h_m;
\\ det[h_m^(i)] is a polynomial in x and kappa; strip the generic powers of x and 1+x; D(t) at many t in F_q, interpolated
\\ (two extra checks) and factored mod q.  A factor of degree > 1 mod q is of degree > 1 over Q, refuting the hypothesis.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
Rn(n) = n * (2 * n - 1);
blocks(e, t) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -3, 1], [-3 - t, 0, 4 * e], [0, -3 - t, 4 * e], [-3 + t, -3 - t, 4]];
detH(e, t) = {
  my(bl = blocks(e, t), d = sum(i = 1, #bl, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, B, my(g = B[1], b = B[2]); for (j = 0, B[3] - 1, row++; my(h = Mod(1, q) * 'x^j);
    for (m = 0, d - 1, M[row, m + 1] = h; h = 'x * (1 + 'x) * deriv(h, 'x) + (b * (1 + 'x) + g * 'x - m * (1 + 2 * 'x)) * h)));
  \\ the Wronskian of the f's is a power-prefactor times det of the h's (row operations are the same)
  matdet(M);
}
export(q, Rn, blocks, detH);
main() = {
  my(e = 1, t0 = Mod(12345, q), P0 = detH(e, t0), a = valuation(lift(P0), 'x), b = valuation(subst(P0, 'x, 'x - 1), 'x));
  my(W0 = P0 / ('x^a * (1 + 'x)^b), dx = poldegree(W0));
  emit(Str("e=1: generic stripped powers x^", a, " (1+x)^", b, ", deg_x W = ", dx));
  my(Wh = detH(e, Mod(1, q) / 2)); emit(Str("  at kappa = 1/2: x-valuation ", valuation(lift(Wh), 'x), ", (1+x)-valuation ", valuation(subst(Wh, 'x, 'x - 1), 'x),
    ", stripped degree ", poldegree(Wh) - valuation(lift(Wh), 'x) - valuation(subst(Wh, 'x, 'x - 1), 'x)));
  my(Dt(t) = my(P = detH(e, t), W = P / ('x^a * (1 + 'x)^b)); if (poldegree(W) < dx, return(0)); poldisc(W));
  my(N = 200, ok = 0, Dp);
  while (!ok && N <= 6400,
    my(ts = vector(N + 2, i, Mod(i + 3, q)), ys = parvector(N + 2, i, Dt(ts[i])));
    Dp = polinterpolate(ts[1..N], ys[1..N], 'k);
    ok = subst(Dp, 'k, ts[N + 1]) == ys[N + 1] && subst(Dp, 'k, ts[N + 2]) == ys[N + 2];
    if (!ok, N *= 2));
  if (!ok, emit("  interpolation of D(kappa) failed up to 6400 points"); return);
  my(F = factormod(lift(Dp), q));
  emit(Str("  D(kappa) mod q: degree ", poldegree(Dp), " (", N, " points); factor degrees and multiplicities: ", vecsort(vector(#F~, i, [poldegree(F[i, 1]), F[i, 2]]))));
  my(lin = select(i -> poldegree(F[i, 1]) == 1, [1..#F~]));
  emit(Str("  linear factors (roots kappa mod q, small rationals recognized): ",
    vector(#lin, j, my(r = -polcoef(F[lin[j], 1], 0) / polcoef(F[lin[j], 1], 1)); [bestappr(r, 10^6), F[lin[j], 2]])));
  emit(Str("  D(1/2) mod q ", if (subst(Dp, 'k, Mod(1, q) / 2) == 0, "ZERO", "nonzero")));
}
default(nbthreads, 12);
default(parisizemax, 8000000000);
main();
