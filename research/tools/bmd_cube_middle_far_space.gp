\\ Middle-step far polynomials from the reduced space of cor:cube-middle-far-reduction (3 October 2026; cycle bmd-20261003-zzm).
\\ F_k (e = k-1, l = b-k, n = R_e): A = P_<n + (1+x)^(-7/2) P_<k1 + x^beta P_<k2 (k1 = 4e, k2 = 4el, beta = -7/2 + 4e - 4el) is
\\ removed; the complement B = <(1+x)^-3> + x^-(R_l+2) P_<R_l + (1+x)^(-5/2) x^(1/2-4l) P_<4l is mapped by d_x^n, then by
\\ mu = (1-t)^(a+k1-1) (a = -7/2 - n), then by D = d_t^k2 t^(k1-c) d_t^k1 with c = beta - n (t = x/(1+x)), which kills the
\\ image of A (two-class kernel P_<k1 + t^c P_<k2).  W_k = far part of the Wronskian in t, mapped back to x.
\\ Control: equals the far part of the full Wronskian (h-recursion, exact) for (b,k) with b <= 5; then reports degree and exact
\\ squarefreeness for larger b at l = 2, 3, writing research/results/bmd-20261003-zzm/W_mid_b<b>_k<k>.gp.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 6000000000);
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dxt(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
wront(V) = { my(d = #V, M = matrix(d, d)); for (i = 1, d, my(f = V[i]); for (m = 0, d - 1, M[i, m + 1] = f[3]; f = dt(f))); matdet(M); }
fart(P) = { P /= 't^valuation(P, 't); while (subst(P, 't, 1) == 0, P /= (1 - 't)); P; }
tox(Wt) = { my(m = poldegree(Wt), Wx = numerator(subst(Wt, 't, 'x / (1 + 'x)) * (1 + 'x)^m)); Wx / content(Wx); }
midW(b, k) = {
  my(e = k - 1, l = b - k, n = Rn(e), k1 = 4 * e, k2 = 4 * e * l, a = -7/2 - n, beta = -7/2 + 4 * e - 4 * e * l, c = beta - n);
  \\ B in t: (1+x)^-3 = (1-t)^3; x^(s) (1+x)^g = t^s (1-t)^(-s-g)
  my(B = concat([[0, 3, 1]], concat(vector(Rn(l), j, my(s = -(Rn(l) + 2) + j - 1); [s, -s, 1]), vector(4 * l, j, my(s = 1/2 - 4 * l + j - 1); [s, -s + 5/2, 1]))));
  my(Y = vector(#B));
  for (i = 1, #B, my(f = B[i]); for (r = 1, n, f = dxt(f)); f = [f[1], f[2] + a + k1 - 1, f[3]];
    for (r = 1, k1, f = dt(f)); f = [f[1] + k1 - c, f[2], f[3]]; for (r = 1, k2, f = dt(f)); Y[i] = f);
  tox(fart(wront(Y)));
}
\\ full Wronskian in x by the h-recursion (exact), for the control
d1(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 + 'x) * p + g * 'x * p + 'x * (1 + 'x) * deriv(p, 'x)];
farx(P) = { P /= 'x^valuation(P, 'x); while (subst(P, 'x, -1) == 0, P /= (1 + 'x)); P / content(P); }
fullW(b, k) = {
  my(e = k - 1, l = b - k, bl = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]], V = List());
  foreach (bl, B, for (j = 0, B[3] - 1, listput(V, [B[2] + j, B[1], 1])));
  my(d = #V, M = matrix(d, d)); for (i = 1, d, my(f = V[i]); for (m = 0, d - 1, M[i, m + 1] = f[3]; f = d1(f)));
  farx(matdet(M));
}
{
foreach ([[3, 2], [4, 2], [4, 3]], P, my(A = midW(P[1], P[2]), F = fullW(P[1], P[2]));
  emit(Str("control (b,k)=", P, ": reduced equals full up to sign: ", A == F || A == -F, " (degrees ", poldegree(A), ", ", poldegree(F), ")")));
foreach ([[6, 4], [7, 5], [8, 6], [7, 4]], P, my(t0 = getabstime(), W = midW(P[1], P[2]));
  write(Str("research/results/bmd-20261003-zzm/W_mid_b", P[1], "_k", P[2], ".gp"), W);
  emit(Str("(b,k)=", P, " (l=", P[1] - P[2], "): deg ", poldegree(W), ", squarefree ", poldegree(gcd(W, W')) == 0, ", time ", getabstime() - t0, " ms")));
}
