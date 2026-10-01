\\ Exact block-IV split terms of the last-step far Wronskian in the six-space (3 October 2026; cycle bmd-20261003-zzw).
\\ Tested statement (conj:cube-last-far-split-balance): split each block-IV image after d_x^n by t-degree of its polynomial
\\ part, S_j = S_j^X (degree < c, the x = 0 side) + S_j^Y (degree >= c), push both parts through mu and D2 (as in
\\ prop:cube-last-far-six-space), and let T_m = sum_{|S| = m} W_t(u1, u2, v_j^Y (j in S), v_j^X (j not in S)). Then
\\ sum_m T_m = W_t(six images) exactly (checked), and on the i-th far circle of P (i = 0..3, 0-based; the code's
\\ 1-based loop index i compares T[i] and T[i+1], i.e. T_(i-1), T_i) the two largest terms (mean log modulus
\\ over the circle) are T_i and T_(i+1), whose balance radius matches the hull slope u_i; the result does not depend on c
\\ (two cuts, c = n/2 and c = n/3). Falsifier: other dominant pairs, or balance radii off by >= 1 unit of log N/N.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
dt(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 - 't) * p - g * 't * p + 't * (1 - 't) * deriv(p, 't)];
dx(f) = my(h = dt(f)); [h[1], h[2] + 2, h[3]];
\\ raw Wronskian determinant of triples with equal g; rows carry t^b_i, columns t^-m (1-t)^-m
wron(V) = { my(d = #V, M = matrix(d, d)); for (i = 1, d, my(f = V[i]); for (m = 0, d - 1, M[i, m + 1] = f[3]; f = dt(f))); matdet(M); }
\\ bring triples to a common b (integer shifts within the class) and common g
common(V) = { my(G = vecmin(apply(f -> f[2], V))); apply(f -> [f[1], G, f[3] * (1 - 't)^(f[2] - G)], V); }
{
my(actual = Map(), F = readstr("research/results/bmd-20261003-zzp/block-logderiv-2.txt"), cur = 0, L = List());
foreach (F, line, my(cv = Vec(line)); if (#cv >= 2 && cv[1] == "e" && cv[2] == "=", if (cur, mapput(actual, cur, Vec(L))); cur = eval(strsplit(strsplit(line, ":")[1], "=")[2]); L = List(),
    my(s = strsplit(line, "e*u = ")); if (#s >= 2, listput(L, eval(strsplit(s[2], ",")[1])))));
if (cur, mapput(actual, cur, Vec(L)));
for (e = 4, 6,
  my(n = Rn(e), k = 4 * e, a = -n - 7/2, N = n + 7/2, B = concat([[0, 3, 1], [-3, 3, 1]], vector(4, j, [j - 1 - 7/2, 7 - j, 1])));
  my(op(f) = for (r = 1, k, f = dt(f)); f = [f[1] + k - a, f[2], f[3]]; for (r = 1, k, f = dt(f)); f);
  my(H = vector(6, i, my(f = B[i]); for (r = 1, n, f = dx(f)); [f[1], f[2] + a + k - 1, f[3]]));
  my(Y6 = vector(6, i, op(H[i])), Wfull = wron(common(Y6)));
  my(U = if (mapisdefined(actual, e), mapget(actual, e) / e, []));
  foreach ([n \ 2, n \ 3], c,
    my(VX = vector(4), VY = vector(4));
    for (j = 1, 4, my(h = H[2 + j], p = h[3], pX = sum(d = 0, min(c - 1, poldegree(p)), polcoef(p, d, 't) * 't^d), pY = p - pX);
      VX[j] = op([h[1], h[2], pX]); VY[j] = op([h[1], h[2], pY]));
    my(T = vector(5), tot = 0);
    forsubset (4, S, my(Sv = Vec(S), V = vector(6, i, if (i <= 2, Y6[i], if (setsearch(Sv, i - 2), VY[i - 2], VX[i - 2]))));
      my(w = wron(common(V))); T[#Sv + 1] += w; tot += w);
    my(ok = (tot == Wfull));
    my(lm(P, lr) = my(G = 64); sum(s = 0, G - 1, log(abs(subst(P, 't, exp(lr + I * 2 * Pi * (s + 1/3) / G))) + 1e-300)) / G);
    my(rep = vector(#U));
    for (i = 1, #U,
      my(lr = U[i], ml = vector(5, m, if (T[m] == 0, -10^9, lm(T[m], lr))), ord = vecsort(ml, , 5));
      \\ balance of T_(i-1), T_i (0-based) : scan lr + [-0.6, 0.6] in 25 steps for sign changes, then bisect the one
      \\ nearest to lr (50 steps); report the number of sign changes found
      my(fb(x) = lm(T[i + 1], x) - lm(T[i], x), xs = vector(25, s, lr - 0.6 + 1.2 * (s - 1) / 24), fs = apply(fb, xs), roots = List());
      for (s = 1, 24, if (sign(fs[s]) != sign(fs[s + 1]), my(lo = xs[s], hi = xs[s + 1], flo = fs[s]);
        for (q = 1, 50, my(mid = (lo + hi) / 2, fm = fb(mid)); if (sign(fm) == sign(flo), lo = mid; flo = fm, hi = mid)); listput(roots, (lo + hi) / 2)));
      my(best = if (#roots, vecsort(Vec(roots), x -> abs(x - lr))[1], oo));
      rep[i] = [ord[1] - 1, ord[2] - 1, if (best == oo, "none", precision((best - lr) * N / log(N), 4) * 1.), #roots]);
    emit(Str("e=", e, " cut c=", c, ": sum_m T_m = W(six images) exactly: ", ok, "; per circle i [two largest m at the actual radius, balance offset of T_i/T_(i+1) nearest to it in units of log N/N, number of balance points within 0.6 in log r]: ", rep))));
}
