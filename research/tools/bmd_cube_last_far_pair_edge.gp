\\ Pair-Wronskian edge test (4 October 2026; cycle bmd-20261004-y).
\\ Hypothesis (pair edge): the edge roots of the last even-peeling far polynomial W_(b-1) (the 8e+4 roots outside the four
\\ sector circles) lie near the 8e far zeros of G_U = Wr_t(u_1, u_2), the integral class of the six-space
\\ (prop:cube-last-far-six-space), mapped to x = t/(1-t).  For each zero z of G_U: distance d1 to the nearest root of W,
\\ d2 to the second nearest, and d1/d2.  A match is d1/d2 < 0.1.  Reads the saved exact W_last_e*.gp (x variable).
\\ Also: the number of W roots within distance 0.1 |z| of some G_U zero, and |z| ranges.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
jacobi(k, al, be) = my(z = 1 - 2 * 't); sum(s = 0, k, binomial(k + al, k - s) * binomial(k + be, s) * ((z - 1) / 2)^s * ((z + 1) / 2)^(k - s));
far(P) = { P /= 't^valuation(P, 't); while (subst(P, 't, 1) == 0, P /= (1 - 't)); P; }
wfile(e) = { my(d = Map([1, "zl"; 2, "zl"; 3, "zl"; 4, "zw"; 5, "zw"; 6, "zw"; 7, "zy"; 8, "zz"; 9, "zz"]));
  Str("research/results/bmd-20261003-", mapget(d, e), "/W_last_e", e, ".gp"); }
default(realprecision, 80);
{
for (e = 2, 5,
  my(n = Rn(e), k = 4 * e, u1 = 't^(n + k + 3) * jacobi(k, n + 7/2, -k - 3/2), f = [1/2, -3/2, jacobi(k, -n - k - 3, -3/2)]);
  for (r = 1, k, f = dt(f));
  my(u2 = f[3], G = far(u1 * deriv(u2, 't) - deriv(u1, 't) * u2), zt = polroots(G), zx = apply(s -> s / (1 - s), zt));
  my(W = read(wfile(e)), rx = polroots(W), m = 0, out = List());
  for (i = 1, #zx, my(z = zx[i], dd = vecsort(apply(r -> abs(r - z), rx)));
    if (dd[1] / dd[2] < 0.1, m++);
    listput(out, [round(real(z) * 100) / 100., round(imag(z) * 100) / 100., dd[1] / dd[2]]));
  my(near = #select(r -> vecmin(apply(z -> abs(r - z) / abs(z), zx)) < 0.1, rx));
  emit(Str("e=", e, ": deg G_U far = ", poldegree(G), " (8e = ", 8 * e, "), deg W = ", poldegree(W), ", edge 8e+4 = ", 8 * e + 4,
    "; G_U zeros with d1/d2 < 0.1: ", m, "; W roots within 0.1|z| of a G_U zero: ", near,
    "; |z| range ", vecmin(apply(abs, zx)), " .. ", vecmax(apply(abs, zx))));
  emit(Str("  per zero [Re z, Im z, d1/d2]: ", Vec(out))));
}
