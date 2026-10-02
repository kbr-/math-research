\\ Row-cost rule for kernel-block minors (cycle bmd-20261009-i, 9 October 2026).
\\ Kernel column of w: K_u(w) = sum_{m>=1} u^m c_m rem(T_1^m(P w), P), T_1 z^i = (c_{i+1}/c_i) z^{i+1},
\\ c_i = binom(-3/2, i), P = prod (z - y_s); a vector of coefficients of z^0..z^{M-1}.
\\ Tested statement (candidate lemma): for every k-tuple of polynomials w_j, every row set
\\ S = {s_1 < ... < s_k} of [0, M-1] and every tau >= 0,
\\   val [u^(k+tau)] det[K_u(w_j)]_{rows S} >= g(k - d),  d = max{d : s_1 + ... + s_d <= tau}
\\ (g as in the Hankel penalty; d counts levels lost; s_1 = 0 makes the first loss free).
\\ Monomial tuples w_j = z^{i_j}, 0 <= i_j <= 4, suffice by Cauchy-Binet. q-adic valuations, q = 1000003.
OUT = "research/results/bmd-20261009-i/row-cost.txt";
q = 1000003;
c(n) = binomial(-3/2, n);
vq(x) = if(x == 0, oo, valuation(x, q));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
g(Y, j) = { if(j < 0, return(0)); my(best = oo); forsubset([#Y, j + 1], S, best = min(best, 2 * vq(vand(vecextract(Y, Vec(S)))))); best };
T1(F) = { my(d = poldegree(F, 'z)); sum(i = 0, d, polcoef(F, i, 'z) * c(i + 1) / c(i) * 'z^(i + 1)) };
TAU = 6;
run(name, Y) = {
  my(M = #Y, P = prod(s = 1, M, 'z - Y[s]), gl = vector(M + 1, j, g(Y, j - 1)), cols = vector(5));
  for (i = 0, 4, my(F = P * 'z^i, col = vector(M));
    for (m = 1, TAU + 1, F = T1(F); my(r = lift(Mod(F, P)));
      for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, 'z) * 'u^m));
    cols[i + 1] = col);
  my(nt = 0, viol = 0, att = 0, ex = List());
  for (k = 1, M - 1,
    forsubset([5, k], T, forsubset([M, k], S,
      my(A = matrix(k, k, a, b, cols[T[b]][S[a]]), D = matdet(A), s = vector(k, a, S[a] - 1));
      for (tau = 0, TAU, my(cf = polcoef(D, k + tau, 'u)); if(cf == 0, next);
        my(d = 0, acc = 0); while(d < k && acc + s[d + 1] <= tau, acc += s[d + 1]; d++);
        my(bound = gl[k - d + 1], v = vq(cf)); nt++;
        if(v < bound, viol++; if(#ex < 8, listput(ex, [k, Vec(T) - [1, 1, 1][1..k], s, tau, v, bound])));
        if(v == bound, att++)))));
  write(OUT, name, " M=", M, ": g(0..M) = ", gl, "; nonzero coefficients tested ", nt, ", violations ", viol, ", attained ", att);
  for (i = 1, #ex, write(OUT, "   violation [k, monomials, rows, tau, val, bound] = ", ex[i]));
};
{
  my(e = q);
  my(cfg = [
    ["cherry top", [1, 1 + e, 2, 5]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3]],
    ["two separated cherries", [1, 1 + e, 2, 2 + e^2]],
    ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2]],
    ["cherry over deep cherry", [1, 1 + e, 2 * e^2, 3 * e^3]],
    ["caterpillar cluster", [1, 1 + e, 1 + e + e^2, 1 + e + e^2 + e^3]]]);
  for (i = 1, #cfg, run(cfg[i][1], cfg[i][2]));
}
