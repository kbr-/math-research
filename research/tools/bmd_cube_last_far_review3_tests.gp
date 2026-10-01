\\ Cheap tests of the third far-input route review (3 October 2026; cycle bmd-20261003-zy).
\\ Polynomials W_(b-1): e = 4, 5, 6 from research/results/bmd-20261003-zw/; e = 7 computed here from the six-space.
\\ (1) Dense chains: centroid of each of the two long upper-half-plane chains (same linking rule as
\\     bmd_cube_last_far_root_chains.gp) and its distance to omega = -1/2 + i sqrt(3)/2 (|x| = |1+x| = 1).
\\ (2) Sparse bulk: roots outside the long chains; mean log-distance to the balance curves Re x = -1/2, |1+x| = 1, |x| = 1.
\\ (3) Level repulsion in the sparse bulk: fraction of sparse nearest-neighbour distances below 0.3 x their median
\\     (Poisson points in the plane: about 0.08; strong repulsion: near 0).
\\ (4) Reach of exact verification: e = 7 from the six-space, squarefree over Q, with the time used.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 100);
default(parisizemax, 4000000000);
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
nnd(P) = { my(m = #P); vector(m, i, vecmin(vector(m, j, if (j == i, 1e9, abs(P[i] - P[j]))))); }
logdist(z) = my(a = log(abs(z)), c = log(abs(1 + z))); vecmin([abs(a - c), abs(c), abs(a)]);
{
my(omega = -1/2 + I * sqrt(3) / 2);
for (e = 4, 6,
  my(W = read(Str("research/results/bmd-20261003-zw/W_last_e", e, ".gp")), all = polroots(W), r = select(z -> imag(z) >= -1e-30, all), m = #r);
  my(nn = vector(m, i, vecmin(vector(#all, j, if (abs(r[i] - all[j]) < 1e-40, 1e9, abs(r[i] - all[j]))))), med = vecsort(nn)[(m + 1) \ 2], h = 2.5 * med);
  my(used = vector(m), chains = List());
  for (s = 1, m, if (used[s], next); used[s] = 1; my(C = List([s]));
    for (dir = 1, 2, my(cur = s);
      while (1, my(best = 0, bd = h);
        for (j = 1, m, if (!used[j] && abs(r[j] - r[cur]) < bd, bd = abs(r[j] - r[cur]); best = j));
        if (!best, break); used[best] = 1; listput(C, best); cur = best));
    listput(chains, Vec(C)));
  my(L = vecsort(Vec(chains), c -> -#c), inchain = vector(m));
  my(cents = vector(2, c, my(C = L[c]); foreach (C, i, inchain[i] = 1); sum(i = 1, #C, r[C[i]]) / #C));
  my(sparse = select(i -> !inchain[i], [1..m]), S = vector(#sparse, i, r[sparse[i]]), Sfull = concat(S, conj(S)));
  my(snn = nnd(Sfull), smed = vecsort(snn)[(#snn + 1) \ 2]);
  emit(Str("e=", e, ": chain centroids ", apply(z -> precision(z, 5), cents), ", distances to omega ", apply(z -> precision(abs(z - omega), 5) * 1., cents),
    "; sparse roots (upper half) ", #S, ", mean log-distance to balance curves ", precision(vecsum(apply(logdist, S)) / max(1, #S), 5) * 1.,
    "; sparse NN median ", precision(smed, 5) * 1., ", fraction of sparse NN < 0.3 median ", precision(#select(t -> t < 0.3 * smed, snn) / #snn * 1., 4))));
my(t0 = getabstime(), W7 = farW(7), sf = poldegree(gcd(W7, W7')) == 0);
write("research/results/bmd-20261003-zy/W_last_e7.gp", W7);
emit(Str("e=7: deg ", poldegree(W7), " (4(2e^2+e+1) = ", 4 * (2 * 49 + 7 + 1), "), squarefree ", sf, ", time ", getabstime() - t0, " ms"));
}
