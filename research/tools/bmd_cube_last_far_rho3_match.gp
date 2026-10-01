\\ Do the far roots on the third circle coincide with the roots of rho_3? (3 October 2026; cycle bmd-20261003-zzi)
\\ For e = 6..9: roots of the block-IV six-space polynomial rho_3 (prop:cube-last-far-six-space) and of P(t) = (1-t)^d W(t/(1-t))
\\ (saved W_(b-1)), both in t = x/(1+x).  For each root of rho_3 with | e log|t| - 0.41..0.53 | small (on its long-edge circle,
\\ |e log|t| - e u_3| < 0.5 with e u_3 the rho_3 edge value), the distance to the nearest root of P in units of the local
\\ spacing 2 pi |t|/N (N = n + 7/2).  Reports how many rho_3 roots lie on the circle, and quantiles of the scaled distance
\\ (much less than 1: P is close to rho_3 times a cofactor there).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz"));
q(v, p) = my(s = vecsort(v)); precision(s[max(1, round(p * #s))], 4) * 1.;
{
for (e = 6, 9,
  my(n = Rn(e), k = 4 * e, a = -n - 7/2, N = n + 7/2, f = [3 - 7/2, 3, 1]);
  for (r = 1, n, f = dx(f)); f = [f[1], f[2] + a + k - 1, f[3]];
  for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f));
  my(p = f[3]); p /= 't^valuation(p, 't);
  my(rz = polroots(p), lr = apply(z -> e * log(abs(z)), rz), mid = vecsort(lr)[(#lr + 1) \ 2]);
  my(on = select(i -> abs(lr[i] - mid) < 0.5, [1..#rz]));
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), d = poldegree(W), P = numerator(subst(W, 'x, 't / (1 - 't)) * (1 - 't)^d), pz = polroots(P));
  my(dist = apply(i -> vecmin(abs(pz - vector(#pz, j, rz[i])~)) / (2 * Pi * abs(rz[i]) / N), on));
  emit(Str("e=", e, ": rho_3 degree ", poldegree(p), ", median e log|t| ", precision(mid, 4) * 1., ", roots on that circle ", #on,
    "; distance to nearest root of P in local spacings: quantiles 10/50/90% ", [q(dist, 0.1), q(dist, 0.5), q(dist, 0.9)], ", max ", precision(vecmax(dist), 4) * 1.)));
}
