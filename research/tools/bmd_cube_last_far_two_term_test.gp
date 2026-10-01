\\ Test of conj:cube-last-far-two-term-law at e = 10, 11 (3 October 2026; cycle bmd-20261003-zzb).
\\ W_(b-1) from the six-space (prop:cube-last-far-six-space), exact squarefreeness, then the real-axis crossing x_e of the dense
\\ chain: for even e the real root in (-0.5, -0.4) (pattern at e = 6, 8), for odd e the conjugate pair x_e +- i h_e (Newton from
\\ the extrapolated position).  Neighbours on the vertical line by Newton from x_e + i(2j+1)h or x_e + 2ij h.  Compares the
\\ observed half-spacing with h_e = pi |x_e(1+x_e)|/(n+7/2) and reports e^2 * 2h_e (predicted limit pi/4 = 0.7854).
\\ Superseded for the neighbour measurement by bmd_cube_last_far_two_term_local.gp: Newton diverged to distant roots.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 120);
default(parisizemax, 6000000000);
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
normf(f) = { my(b = f[1], g = f[2], p = f[3], v); if (p == 0, return(f)); v = valuation(p, 't); p /= 't^v; b += v;
  v = 0; while (subst(p, 't, 1) == 0, p /= (1 - 't); v++); [b, g + v, p]; }
far(P) = { P /= 't^valuation(P, 't); while (subst(P, 't, 1) == 0, P /= (1 - 't)); P; }
farW(e) = {
  my(n = Rn(e), k = 4 * e, a = -n - 7/2, B = concat([[0, 3, 1], [-3, 3, 1]], vector(4, j, [j - 1 - 7/2, 7 - j, 1])), Y = vector(6));
  for (i = 1, 6, my(f = B[i]); for (r = 1, n, f = dx(f)); f = [f[1], f[2] + a + k - 1, f[3]];
    for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f)); Y[i] = normf(f));
  my(G = vecmin(apply(f -> f[2], Y)), V = apply(f -> [f[1], G, f[3] * (1 - 't)^(f[2] - G)], Y), M = matrix(6, 6));
  for (i = 1, 6, my(f = V[i]); for (m = 0, 5, M[i, m + 1] = f[3]; f = dt(f)));
  my(Wt = far(matdet(M)), m = poldegree(Wt), Wx = numerator(subst(Wt, 't, 'x / (1 + 'x)) * (1 + 'x)^m));
  Wx / content(Wx);
}
newton(W, z) = { my(D = W'); for (i = 1, 200, my(s = subst(W, 'x, z) / subst(D, 'x, z)); z -= s; if (abs(s) < 1e-100, break)); z; }
f6(z) = precision(z, 6) * 1.;
{
for (e = 10, 11,
  my(W = farW(e), n = Rn(e), N = n + 7/2, sf = poldegree(gcd(W, W')) == 0);
  write(Str("research/results/bmd-20261003-zzb/W_last_e", e, ".gp"), W);
  my(xe, h, obs);
  if (e % 2 == 0,
    my(rr = select(z -> z > -0.5 && z < -0.4, polrootsreal(W)));
    if (#rr != 1, emit(Str("e=", e, ": real roots in (-0.5,-0.4): ", rr)); next);
    xe = rr[1]; h = Pi * abs(xe * (1 + xe)) / N;
    my(z1 = newton(W, xe + 2 * I * h)); obs = abs(z1 - xe) / 2;
    emit(Str("e=", e, ": deg ", poldegree(W), ", squarefree ", sf, ", real crossing x_e = ", f6(xe), ", neighbour ", f6(z1),
      "; observed half-spacing x e^2 ", f6(obs * e^2), ", formula h_e x e^2 ", f6(h * e^2), ", e^2 x 2h_e ", f6(2 * h * e^2)))
  ,
    my(x0 = -0.455 + 0.0 * I, z0 = newton(W, x0 + I * Pi * abs(x0 * (1 + x0)) / N));
    xe = real(z0); h = Pi * abs(xe * (1 + xe)) / N; obs = abs(imag(z0));
    my(z1 = newton(W, xe + 3 * I * h));
    emit(Str("e=", e, ": deg ", poldegree(W), ", squarefree ", sf, ", crossing pair x_e +- i h = ", f6(z0), ", next ", f6(z1), " (offset ratio ", f6(imag(z1) / imag(z0)), ")",
      "; observed h x e^2 ", f6(obs * e^2), ", formula h_e x e^2 ", f6(h * e^2), ", e^2 x 2h_e ", f6(2 * h * e^2)))));
}
