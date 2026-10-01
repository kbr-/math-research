\\ Explicit six-space of the last-step far polynomial (3 October 2026; cycle bmd-20261003-zu).
\\ Verifies prop:cube-last-far-six-space at e = 1, 2 exactly over Q.  In t = x/(1+x) (x = t/(1-t), 1+x = 1/(1-t)), a function
\\ is a triple [b, g, p] = t^b (1-t)^g p(t).  Steps (k = 4e, n = R_e, a = -n-7/2):
\\   B' in t: (1+x)^-3 = (1-t)^3, x^-3 = t^-3 (1-t)^3, IV_j = x^(j-7/2) (1+x)^(-5/2) = t^(j-7/2) (1-t)^(6-j), j < 4;
\\   d_x^n with d_x = (1-t)^2 d_t; multiply by mu = (1-t)^(a+k-1); apply D2 = d_t^k t^(k-a) d_t^k.
\\ Claims checked: (i) the images are t^(n+7/2) (1-t)^(-k-3/2) * (Jacobi P_k^(n+7/2, -k-3/2)(1-2t) up to a constant),
\\ t^(1/2-k) (1-t)^(-k-3/2) Q(t) and (1-t)^(-k-3/2) rho_j(t) with polynomials Q, rho_j; (ii) the far part of their Wronskian in t
\\ equals (1-t)^(deg W) W_(b-1)(t/(1-t)) up to a constant (saved W_last_e*.gp).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
normf(f) = { my(b = f[1], g = f[2], p = f[3], v); if (p == 0, return(f)); v = valuation(p, 't); p /= 't^v; b += v;
  v = 0; while (subst(p, 't, 1) == 0, p /= (1 - 't); v++); [b, g + v, p]; }
jacobi(k, al, be) = my(z = 1 - 2 * 't); sum(s = 0, k, binomial(k + al, k - s) * binomial(k + be, s) * ((z - 1) / 2)^s * ((z + 1) / 2)^(k - s));
wron(V) = {
  my(d = #V, M = matrix(d, d));
  for (i = 1, d, my(f = V[i]); for (m = 0, d - 1, M[i, m + 1] = f[3]; f = dt(f)));
  \\ row i carries t^(b_i) (1-t)^(g_i), column m carries t^-m (1-t)^-m: they are factored out; det is the rest
  matdet(M);
}
far(P) = { P /= 't^valuation(P, 't); while (subst(P, 't, 1) == 0, P /= (1 - 't)); P; }
{
for (e = 1, 2,
  my(n = Rn(e), k = 4 * e, a = -n - 7/2, B = concat([[0, 3, 1], [-3, 3, 1]], vector(4, j, [j - 1 - 7/2, 7 - j, 1])), Y = vector(6));
  for (i = 1, 6, my(f = B[i]); for (r = 1, n, f = dx(f)); f = [f[1], f[2] + a + k - 1, f[3]];
    for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f)); Y[i] = normf(f));
  emit(Str("e=", e, ": exponents [b, g] of the six images ", apply(f -> [f[1], f[2]], Y), "; polynomial degrees ", apply(f -> poldegree(f[3]), Y)));
  my(J = jacobi(k, n + 7/2, -k - 3/2), P1 = Y[1][3]);
  emit(Str("  first image proportional to t^(n+7/2) (1-t)^(-k-3/2) P_k^(n+7/2,-k-3/2)(1-2t): ",
    Y[1][1] == n + 7/2 && Y[1][2] == -k - 3/2 && poldegree(P1) == poldegree(J) && P1 * pollead(J) == J * pollead(P1)));
  \\ common factor: bring all to the same g by multiplying polynomial parts (only branch factors change)
  my(G = vecmin(apply(f -> f[2], Y)), V = apply(f -> [f[1], G, f[3] * (1 - 't)^(f[2] - G)], Y), Wt = far(wron(V)));
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), Wx = far(substpol(W, 'x, 't) * 0 + subst(W, 'x, 't / (1 - 't)) * (1 - 't)^poldegree(W)));
  Wx = far(numerator(Wx));
  emit(Str("  far part of W_t(six images): degree ", poldegree(Wt), "; proportional to (1-t)^m W_(b-1)(t/(1-t)): ",
    poldegree(Wt) == poldegree(Wx) && Wt * pollead(Wx) == Wx * pollead(Wt))));
}
