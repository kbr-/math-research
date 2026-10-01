\\ Cheap tests of the far-mechanism route review (3 October 2026; cycle bmd-20261003-zzx).
\\ (a) Polya-Mammana nesting (outside lead): at e = 4, for each j, the far roots of W_t(u1, u2, v_i (i != j)) (five-function
\\     Wronskian of the six-space) are binned by log|t| against the four far circles of P (hull slopes u_i): do they occupy
\\     three of the four circles (a nested factorization W(Z) = W(u1,u2,U) W(L_U v_j))?
\\ (b) G_p (arithmetic route, outside lead Dumas/Hensel): for e = 4..8 and every window prime max(d, 2n) < p <= 2n+8e+7,
\\     the largest multiplicity of an irreducible factor of W_(b-1) mod p other than x and 1+x (a triple root needs >= 3).
\\ (c) Root repulsion (log-gas bridge): at e = 4, 5 the minimal distance between roots of P(t) = (1-t)^d W(t/(1-t)), times N.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 100);
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", if (e <= 9, "research/results/bmd-20261003-zz", "research/results/bmd-20261003-zzb")));
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
wron(V) = { my(d = #V, M = matrix(d, d)); for (i = 1, d, my(f = V[i]); for (m = 0, d - 1, M[i, m + 1] = f[3]; f = dt(f))); matdet(M); }
common(V) = { my(G = vecmin(apply(f -> f[2], V))); apply(f -> [f[1], G, f[3] * (1 - 't)^(f[2] - G)], V); }
far(P) = { P /= 't^valuation(P, 't); while (subst(P, 't, 1) == 0, P /= (1 - 't)); P; }
{
\\ (a)
my(e = 4, n = Rn(e), k = 4 * e, a = -n - 7/2, B = concat([[0, 3, 1], [-3, 3, 1]], vector(4, j, [j - 1 - 7/2, 7 - j, 1])));
my(Y = vector(6, i, my(f = B[i]); for (r = 1, n, f = dx(f)); f = [f[1], f[2] + a + k - 1, f[3]]; for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f)); f));
my(U = [-3.195638353966949578, -1.2962331159331142386, 0.6050634462520645983, 2.563566012357988629] / 4);
for (j = 1, 4,
  my(V = vector(5, i, if (i <= 2, Y[i], Y[2 + if (i - 2 < j, i - 2, i - 1)])), Q = far(wron(common(V))), R = polroots(Q * 1.));
  my(cnt = vector(5));
  foreach (R, z, my(l = log(abs(z)), b = 5); for (i = 1, 4, if (abs(l - U[i]) < 0.12, b = i)); cnt[b]++);
  emit(Str("(a) e=4, v_", j - 1, " removed: far degree ", poldegree(Q), "; roots within 0.12 of circles 0..3 and elsewhere: ", cnt)));
\\ (b)
for (e = 4, 8,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), n = Rn(e), d = Rn(e + 2), lo = max(d, 2 * n), hi = 2 * n + 8 * e + 7, out = List());
  forprime (p = lo + 1, hi,
    my(Wp = W * Mod(1, p), F = factormod(W, p), mx = 0);
    if (polcoef(W, poldegree(W)) % p == 0, listput(out, [p, "lc"]); next);
    for (i = 1, #F~, my(g = lift(F[i, 1])); if (g != 'x && g != 'x + 1, mx = max(mx, F[i, 2])));
    listput(out, [p, mx]));
  emit(Str("(b) e=", e, ": window (", lo, ", ", hi, "], [prime, largest multiplicity of a factor other than x, x+1]: ", Vec(out))));
\\ (c)
for (e = 4, 5,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), dd = poldegree(W), P = numerator(subst(W, 'x, 't / (1 - 't)) * (1 - 't)^dd), R = polroots(P * 1.), N = Rn(e) + 7/2, md = oo);
  for (i = 1, #R, for (j = i + 1, #R, md = min(md, abs(R[i] - R[j]))));
  emit(Str("(c) e=", e, ": degree ", poldegree(P), ", minimal root distance ", precision(md, 4) * 1., ", times N: ", precision(md * N, 4) * 1.)));
}
