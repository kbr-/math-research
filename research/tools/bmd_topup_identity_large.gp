\\ Top-up identity at M = 5, 6 (cycle bmd-20261009-au, 9 October 2026); conventions of bmd_topup_coefficient.gp.
\\ Tested statement (conj:cube-topup-flow-identity): tau_p = kappa_(M,p) (D + 2k e1) Hank_k, k = M - p, D = sum y_i^2 d_i,
\\ where Vand^2 tau_p is the coefficient of x^(A_p + 1) eps^(B_p) in the cross coordinate on [-p, 2M-2-p] u {2M-p}.
\\ Method: tau_p at four random integer clusters (exact rationals); kappa from the first, equality required at the other
\\ three. Also reports whether kappa != 0 and the identity's failure if any. 1 <= p <= M - 1.
OUT = "research/results/bmd-20261009-au/topup-large.txt";
default(parisizemax, 2 * 10^9);
default(threadsizemax, 1 * 10^9);
default(nbthreads, 5);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * ('x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * 'eps^r * ('x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, 'eps), A, 'x);
}
hank(Y, k) = { my(M = #Y, s = 0); forsubset([M, k + 1], S, my(v = prod(i = 1, k + 1, prod(j = i + 1, k + 1, Y[S[j]] - Y[S[i]]))); s += v^2); s; }
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
\\ (D + 2k e1) Hank_k at a numeric point, with D Hank_k computed from the symbolic form
flowval(M, k, P) = {
  my(ys = vector(M, i, eval(Str("y", i))), H = hank(ys, k), e1 = vecsum(ys));
  my(F = sum(i = 1, M, ys[i]^2 * deriv(H, ys[i])) + 2 * k * e1 * H);
  substvec(F, ys, P);
}
\\ worker: the top-up coefficient divided by Vand^2 at one numeric cluster (no symbolic variables in threads)
taunum(M, p, P) = {
  my(A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M);
  my(L = concat(concat(vector(p, i, -p - 1 + i), [0 .. 2*M - 2 - p]), [2*M - p]));
  coefat(P, L, A + 1, B) / vand(P)^2;
}
export(lam, cc, coefat, vand, taunum);
{
  setrand(20261009);
  foreach([5, 6], M,
    my(pts = vector(4, j, vector(M, i, random(40) - 20 + 41 * i)), jobs = List());
    for (p = 1, M - 1, for (j = 1, 4, listput(jobs, [p, j])));
    my(T = parapply(J -> taunum(M, J[1], pts[J[2]]), Vec(jobs)));
    for (p = 1, M - 1,
      my(k = M - p, r = vector(4, j, T[4 * (p - 1) + j] / flowval(M, k, pts[j])));
      write(OUT, "M = ", M, ", p = ", p, ", k = ", k, ": kappa at four clusters ", r, "; identity holds: ", #Set(r) == 1 && r[1] != 0)));
}
