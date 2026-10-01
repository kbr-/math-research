\\ Merging of the dense far-root chains (3 October 2026; cycle bmd-20261003-zz).
\\ Polynomials W_(b-1): e = 4..6 from research/results/bmd-20261003-zw/, e = 7 from research/results/bmd-20261003-zy/,
\\ e = 8, 9 computed here from the six-space (prop:cube-last-far-six-space) and written to research/results/bmd-20261003-zz/.
\\ For each e: exact squarefreeness; upper-half-plane chains (nearest neighbours within 2.5 x median NN distance); for the two
\\ longest chains: sizes, centroid distance, minimal distance between a point of one and a point of the other, and the overall
\\ minimal root distance; all distances also times e and e^2.  Question: does the chain approach saturate (avoided crossing)
\\ or continue to 0?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 100);
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
f4(z) = precision(z, 4) * 1.;
{
for (e = 4, 9,
  my(W);
  if (e <= 6, W = read(Str("research/results/bmd-20261003-zw/W_last_e", e, ".gp")),
    if (e == 7, W = read("research/results/bmd-20261003-zy/W_last_e7.gp"),
      W = farW(e); write(Str("research/results/bmd-20261003-zz/W_last_e", e, ".gp"), W)));
  my(sf = poldegree(gcd(W, W')) == 0, all = polroots(W), r = select(z -> imag(z) >= -1e-30, all), m = #r);
  my(nn = vector(m, i, vecmin(vector(#all, j, if (abs(r[i] - all[j]) < 1e-40, 1e9, abs(r[i] - all[j]))))), med = vecsort(nn)[(m + 1) \ 2], h = 2.5 * med);
  my(used = vector(m), chains = List());
  for (s = 1, m, if (used[s], next); used[s] = 1; my(C = List([s]));
    for (dir = 1, 2, my(cur = s);
      while (1, my(best = 0, bd = h);
        for (j = 1, m, if (!used[j] && abs(r[j] - r[cur]) < bd, bd = abs(r[j] - r[cur]); best = j));
        if (!best, break); used[best] = 1; listput(C, best); cur = best));
    listput(chains, Vec(C)));
  my(L = vecsort(Vec(chains), c -> -#c), A = L[1], B2 = L[2]);
  my(cA = sum(i = 1, #A, r[A[i]]) / #A, cB = sum(i = 1, #B2, r[B2[i]]) / #B2, dAB = vecmin(concat(vector(#A, i, vecmin(vector(#B2, j, abs(r[A[i]] - r[B2[j]])))))));
  my(mind = vecmin(nn));
  emit(Str("e=", e, ": deg ", poldegree(W), ", squarefree ", sf, ", chain sizes ", [#A, #B2], ", centroids ", [f4(cA), f4(cB)],
    ", centroid distance ", f4(abs(cA - cB)), " (x e: ", f4(abs(cA - cB) * e), "), min inter-chain distance ", f4(dAB), " (x e: ", f4(dAB * e), ", x e^2: ", f4(dAB * e^2), ")",
    ", min root distance ", f4(mind), " (x e^2: ", f4(mind * e^2), "), median NN x e^2 ", f4(med * e^2))));
}
