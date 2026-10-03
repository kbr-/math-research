\\ Exact proof of the top-up identity at M = 5 by interpolation (cycle bmd-20261009-ax, 9 October 2026);
\\ conventions of bmd_topup_identity_large.gp.
\\ Statement (conj:cube-topup-flow-identity at M = 5): R_p = tau_p - kappa (D + 2k e1) Hank_k = 0, k = 5 - p, with
\\ kappa = -(lambda + 2M - p - 1) c_(M,p) / (2k(M + k + 1)) (lem:cube-topup-translation-equation), c_(M,p) = W_p/(Vand^2 Hank_k).
\\ R_p is a symmetric polynomial, homogeneous of degree n0 = k(k+1) + 1, so it lies in the span of the products
\\ e1^a1 ... e5^a5 with a1 + 2 a2 + ... + 5 a5 = n0 (a basis in 5 variables). If R_p vanishes at points where this
\\ basis has an injective evaluation map (full column rank), then R_p = 0. The script evaluates R_p exactly at
\\ dim + 5 random integer clusters and checks both conditions.
OUT = "research/results/bmd-20261009-ax/topup-m5.txt";
default(parisizemax, 2 * 10^9);
default(threadsizemax, 5 * 10^8);
default(nbthreads, 12);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * ('x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * 'eps^r * ('x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, 'eps), A, 'x);
}
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
hnum(Y, k) = { my(M = #Y, s = 0); forsubset([M, k + 1], S, my(v = prod(i = 1, k + 1, prod(j = i + 1, k + 1, Y[S[j]] - Y[S[i]]))); s += v^2); s; }
\\ (D + 2k e1) Hank_k at a numeric point, D Hank_k by the chain rule on each pair term
flownum(Y, k) = {
  my(M = #Y, s = 0, e1 = vecsum(Y));
  forsubset([M, k + 1], S, my(V2 = prod(i = 1, k + 1, prod(j = i + 1, k + 1, (Y[S[j]] - Y[S[i]])^2)));
    \\ D V2 = V2 * sum over pairs 2 (y_j + y_i) since D (y_j - y_i) = (y_j - y_i)(y_j + y_i)
    my(dl = sum(i = 1, k + 1, sum(j = i + 1, k + 1, 2 * (Y[S[j]] + Y[S[i]]))));
    s += V2 * (dl + 2 * k * e1));
  s;
}
taunum(M, p, P) = {
  my(A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M);
  my(L = concat(concat(vector(p, i, -p - 1 + i), [0 .. 2*M - 2 - p]), [2*M - p]));
  coefat(P, L, A + 1, B) / vand(P)^2;
}
cnum(M, p, P) = {
  my(A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M, W = concat(vector(p, i, -p - 1 + i), [0 .. 2*M - 1 - p]));
  coefat(P, W, A, B) / vand(P)^2 / hnum(P, M - p);
}
esym(P) = { my(v = Vec(prod(i = 1, #P, 'z + P[i]))); vector(#P, j, v[j + 1]); }
export(lam, cc, coefat, vand, taunum);
{
  my(M = 5);
  setrand(424242);
  for (p = 1, M - 1,
    my(k = M - p, n0 = k * (k + 1) + 1, alphas = List());
    forvec(a = vector(M, j, [0, n0 \ j]), if (sum(j = 1, M, j * a[j]) == n0, listput(alphas, a)));
    my(dim = #alphas, npts = dim + 5, pts = vector(npts, j, vector(M, i, random(60) - 30 + 61 * i)));
    my(c = cnum(M, p, pts[1]), kappa = -(lam + 2*M - p - 1) * c / (2 * k * (M + k + 1)));
    my(T = parapply(P -> taunum(M, p, P), pts));
    my(res = vector(npts, j, T[j] - kappa * flownum(pts[j], k)));
    my(E = matrix(npts, dim, j, l, my(e = esym(pts[j])); prod(i = 1, M, e[i]^alphas[l][i])));
    my(rk = matrank(E), zero = res == vector(npts));
    write(OUT, "M = 5, p = ", p, ", k = ", k, ", degree ", n0, ": basis size ", dim, ", points ", npts, ", rank ", rk,
          "; remainder zero at all points: ", zero, "; identity proved: ", zero && rk == dim));
}
