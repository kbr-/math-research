\\ Balance radii of the idealized block-IV expansion terms (3 October 2026; cycle bmd-20261003-zzv).
\\ Tested statement (conj:cube-last-far-ideal-balance): the far circles of the last step are the balance circles of the
\\ idealized terms T_m = A_m * Pi_m * W_m (m = 0..4 block-IV functions in their (1+x)-part), where
\\   A_m  = det of the 4x4 matrix with rows binom(-5/2, k-j+i) (i < 4-m) and (-1)^j binom(j-7/2, k-1+i) (i < m), j = 0..3
\\          (Laplace expansion over the subsets S: X-minor(S^c) * Y-minor(S), exact up to a phase),
\\   Pi_m = prod_{i<4-m} (g0+i)_n * prod_{i<m} (g0+i)_n,  g0 = k - 7/2 (falling factorials; IV residual amplitudes),
\\   W_m  = Wronskian of x^(-n-3), x^(-n-7/2+i) (i < k+4-m), (1+x)^(-n-3), (1+x)^(-n-7/2+i) (i < k+m)
\\ (lem:block-pair-wronskian; evaluated numerically). For circle i the mean over |t| = r of log|T_(i+1)/T_i| is solved
\\ for r (secant in log r); the predicted slope u_pred = log r is compared with the actual hull slope u_i of
\\ P(t) = (1-t)^d W_(b-1)(t/(1-t)) (block-logderiv-2.txt), in units of log N / N. Falsifier: |u_pred - u_i| N / log N
\\ not small (say > 0.5) or not decreasing in e.
OUT = getenv("OUT");
\\ optional controls: PREC (digits, default 150), EMIN/EMAX (default 4..8), GRID (points per circle, default 48)
getd(s, d) = my(v = getenv(s)); if (v == 0 || v == "", d, eval(v));
PREC = getd("PREC", 150); EMIN = getd("EMIN", 4); EMAX = getd("EMAX", 8); GRID = getd("GRID", 48); AONLY = getd("AONLY", 0);
\\ AONLY = 1: report only log|A_m| / log k (with and without the column signs (-1)^j of the Y rows), no balance radii
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, PREC);
ff(a, r) = prod(s = 0, r - 1, a - s);
lpoch(g, n) = real(lngamma(g + 1) - lngamma(g + 1 - n));
{
my(actual = Map());
my(F = readstr("research/results/bmd-20261003-zzp/block-logderiv-2.txt"), cur = 0, L = List());
foreach (F, line,
  my(cv = Vec(line)); if (#cv >= 2 && cv[1] == "e" && cv[2] == "=", if (cur, mapput(actual, cur, Vec(L))); cur = eval(strsplit(strsplit(line, ":")[1], "=")[2]); L = List(),
    my(s = strsplit(line, "e*u = ")); if (#s >= 2, listput(L, eval(strsplit(s[2], ",")[1])))));
if (cur, mapput(actual, cur, Vec(L)));
for (e = EMIN, EMAX,
  my(n = e * (2 * e - 1), k = 4 * e, g0 = k - 7/2, N = n + 7/2, U = mapget(actual, e) / e);
  my(lA = vector(5), lPi = vector(5), ex = vector(5), ey = vector(5));
  for (m = 0, 4,
    my(Mx = matrix(4, 4, i, j, if (i <= 4 - m, binomial(-5/2, k - (j - 1) + (i - 1)), (-1)^(j - 1) * binomial(j - 1 - 7/2, k - 1 + (i - 1 - (4 - m))))));
    lA[m + 1] = log(abs(matdet(Mx)));
    lPi[m + 1] = sum(i = 0, 3 - m, lpoch(g0 + i, n)) + sum(i = 0, m - 1, lpoch(g0 + i, n));
    ex[m + 1] = concat([-n - 3], vector(k + 4 - m, i, -n - 7/2 + i - 1));
    ey[m + 1] = concat([-n - 3], vector(k + m, i, -n - 7/2 + i - 1)));
  if (AONLY,
    my(lA2 = vector(5, mm, my(m = mm - 1, Mx = matrix(4, 4, i, j, if (i <= 4 - m, binomial(-5/2, k - (j - 1) + (i - 1)), binomial(j - 1 - 7/2, k - 1 + (i - 1 - (4 - m)))))); log(abs(matdet(Mx)))));
    emit(Str("e=", e, ": log|A_m|/log k, m = 0..4: ", apply(v -> precision(v / log(k), 4) * 1., lA), "; without the signs (-1)^j: ", apply(v -> precision(v / log(k), 4) * 1., lA2), "; log Pi_m / log N relative to m = 0: ", apply(v -> precision((v - lPi[1]) / log(N), 4) * 1., lPi)));
    next);
  my(lW(m, x) = my(E1 = ex[m + 1], E2 = ey[m + 1], K = #E1 + #E2, M = matrix(K, K, r, c, if (c <= #E1, ff(E1[c], r - 1) * x^(1 - r), ff(E2[c - #E1], r - 1) * (1 + x)^(1 - r))));
    log(abs(matdet(M))) + vecsum(E1) * log(abs(x)) + vecsum(E2) * log(abs(1 + x)));
  my(lT(m, x) = lA[m + 1] + lPi[m + 1] + lW(m, x));
  my(G = GRID, f(i, lr) = sum(s = 0, G - 1, my(t = exp(lr + I * 2 * Pi * (s + 1/3) / G), x = t / (1 - t)); lT(i + 1, x) - lT(i, x)) / G);
  my(res = vector(4));
  for (i = 0, 3,
    my(a0 = U[i + 1] - 0.05, a1 = U[i + 1] + 0.05, f0 = f(i, a0), f1 = f(i, a1), it = 0);
    while (it < 8 && abs(a1 - a0) > 1e-6, my(a2 = a1 - f1 * (a1 - a0) / (f1 - f0)); a0 = a1; f0 = f1; a1 = a2; f1 = f(i, a1); it++);
    res[i + 1] = [precision(U[i + 1] * N / log(N), 4) * 1., precision(a1 * N / log(N), 4) * 1., precision((a1 - U[i + 1]) * N / log(N), 4) * 1.]);
  emit(Str("e=", e, " (precision ", PREC, ", grid ", GRID, "): per circle [actual u N/log N, predicted, difference]: ", res)));
}
