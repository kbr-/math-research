\\ Is the N = 8 symmetric locus (branch set {+-x_1, ..., +-x_4}, involution z -> -z fixing the mark infinity)
\\ inside E'?  Exact over Q.  Contact criterion setting: V = <1, z, w_ij>, R = binom(N,2), M = R + 4,
\\ S = ker J_M = {s in V : s = O(z^(1-M))}, W_M = {f in k[z]_{<= M-3} : [z^-1](w_ij f) = 0 for all i<j},
\\ b_i(s,f) = 1/2 sum_{j != i} c_ij [w_ij f]_+(a_i)  (derived from (JF) for every M).
\\ Also a control: a generic configuration (not in K, S = 0).
u; x;
wser(a, b, P) = (1/u) * sqrt((1 - a*u) * (1 - b*u) + O(u^(P + 3)));
run(a) = {
  my(N = #a, R = N*(N-1)/2, M = R + 4, P = M + 4, pairs = List(), W, rows, S, F, Wm, B);
  for (i = 1, N, for (j = i + 1, N, listput(pairs, [i, j])));
  W = vector(#pairs, k, wser(a[pairs[k][1]], a[pairs[k][2]], P));
  \\ s = c0 + c1 z + sum c_k w_k ; conditions: coefficients of u^e, e = -1 .. M-2, vanish (s = O(z^(1-M)) = O(u^(M-1)))
  my(nv = 2 + #pairs, A = matrix(M, nv));
  for (e = -1, M - 2,
    A[e + 2, 1] = if (e == 0, 1, 0);
    A[e + 2, 2] = if (e == -1, 1, 0);
    for (k = 1, #pairs, A[e + 2, 2 + k] = polcoef(W[k], e, u)));
  S = matker(A);
  print("N = ", N, ": dim S = ", #S);
  \\ W_M: f = sum_{d=0}^{M-3} f_d z^d; [z^-1](w_k f) = [u^1](w_k f(1/u)) = sum_d f_d [u^(1+d)] w_k
  my(C = matrix(#pairs, M - 2, k, d, polcoef(W[k], d, u)));
  F = matker(C);
  print("dim W_M = ", #F);
  if (#S == 0, return);
  \\ covector matrix for s = S[,1] against a basis of W_M
  my(s = S[, 1], c = matrix(N, N));
  for (k = 1, #pairs, my(i = pairs[k][1], j = pairs[k][2]); c[i, j] = s[2 + k]; c[j, i] = s[2 + k]);
  B = matrix(N, #F, i, t,
    my(f = sum(d = 0, M - 3, F[d + 1, t] * u^(-d)), tot = 0);
    for (j = 1, N, if (j != i,
      my(k = 0); for (kk = 1, #pairs, if (pairs[kk] == [min(i, j), max(i, j)], k = kk));
      my(g = W[k] * f, val = 0);
      for (e = -(M + 2), 0, val += polcoef(g, e, u) * a[i]^(-e));
      tot += c[i, j] * val));
    tot / 2);
  print("rank of the N x dim W covector matrix: ", matrank(B), "  (column sums zero: ", vector(#F, t, sum(i = 1, N, B[i, t])) == vector(#F), ", first moments zero: ", vector(#F, t, sum(i = 1, N, a[i] * B[i, t])) == vector(#F), ")");
  print("covector matrix:"); print(B);
}
{
  run([1, -1, 2, -2, 5/3, -5/3, 7/2, -7/2]);
  run([1, -1, 3, -3, 4/7, -4/7, 11/5, -11/5]);
  run([1, -2, 3, 5/2, -7/3, 11/4, -1/5, 13/6]);
  \\ N = 9 (one branch point fixed at 0) and N = 10, symmetric under z -> -z
  run([0, 1, -1, 2, -2, 5/3, -5/3, 7/2, -7/2]);
  run([1, -1, 2, -2, 5/3, -5/3, 7/2, -7/2, 3/11, -3/11]);
}
