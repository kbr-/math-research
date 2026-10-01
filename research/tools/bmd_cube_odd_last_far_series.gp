\\ Odd last-step far polynomials W_b from the (2e+2)-dimensional reduction (3 October 2026; cycle bmd-20261003-zzk).
\\ lem:cube-odd-last-far-reduction: W_b is the far part of W(L_A(III + IV)), III = x^(-3/2) P_<2e, IV = (1+x)^(-5/2) x^(-3/2) P_<2,
\\ L_A ~ ((1+x) d + 4e - 1/2) d^(4e) (1+x)^N d^n, n = R_e, N = n + 7/2, e = b - 1.  Functions are triples [b, g, p] =
\\ x^b (1+x)^g p(x).  Control: at e = 1, 2 the result equals the far part of the full Wronskian of F_b (exact, h-recursion).
\\ For e = 1..10: degree (expected deg of F_b's far part: 6, 26, 62, 114 at e <= 4), exact squarefreeness over Q; polynomials
\\ written to research/results/bmd-20261003-zzk/W_odd_e<e>.gp.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 6000000000);
Rn(n) = n * (2 * n - 1);
d1(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 + 'x) * p + g * 'x * p + 'x * (1 + 'x) * deriv(p, 'x)];
first(f, c) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g, b * (1 + 'x) * p + g * 'x * p + 'x * (1 + 'x) * deriv(p, 'x) + c * 'x * p];
normf(f) = { my(b = f[1], g = f[2], p = f[3], v); if (p == 0, return(f)); v = valuation(p, 'x); p /= 'x^v; b += v;
  v = 0; while (subst(p, 'x, -1) == 0, p /= (1 + 'x); v++); [b, g + v, p]; }
farx(P) = { P /= 'x^valuation(P, 'x); while (subst(P, 'x, -1) == 0, P /= (1 + 'x)); P / content(P); }
wron(V) = {
  \\ each row keeps its own exponents: f^(m) = x^(b_i - m) (1+x)^(g_i - m) h_(i,m), and the row and column factors come out
  my(d = #V, M = matrix(d, d));
  for (i = 1, d, my(f = V[i]); for (m = 0, d - 1, M[i, m + 1] = f[3]; f = d1(f)));
  matdet(M);
}
oddW(e) = {
  my(n = Rn(e), N = n + 7/2, F = concat(vector(2 * e, j, [j - 1 - 3/2, 0, 1]), vector(2, j, [j - 1 - 3/2, -5/2, 1])), Y = vector(#F));
  for (i = 1, #F, my(f = F[i]); for (r = 1, n, f = d1(f)); f = [f[1], f[2] + N, f[3]]; for (r = 1, 4 * e, f = d1(f)); f = first(f, 4 * e - 1/2); Y[i] = normf(f));
  farx(wron(Y));
}
fullW(e) = {
  my(n = Rn(e), bl = [[0, 0, n], [-3, 0, 1], [-7/2, 0, 4 * e], [-5/2, -3/2, 2], [0, -3/2, 2 * e]], V = List());
  foreach (bl, B, for (j = 0, B[3] - 1, listput(V, [B[2] + j, B[1], 1])));
  farx(wron(Vec(V)));
}
{
for (e = 1, 2, my(A = oddW(e), B = fullW(e)); emit(Str("control e=", e, ": reduction equals full far part up to sign: ", A == B || A == -B, " (degrees ", poldegree(A), ", ", poldegree(B), ")")));
for (e = 1, 10,
  my(t0 = getabstime(), W = oddW(e));
  write(Str("research/results/bmd-20261003-zzk/W_odd_e", e, ".gp"), W);
  emit(Str("e=", e, " (b = ", e + 1, ", N = 2b+1 = ", 2 * e + 3, "): deg ", poldegree(W), ", squarefree ", poldegree(gcd(W, W')) == 0, ", time ", getabstime() - t0, " ms")));
}
