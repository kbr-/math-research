\\ Cauchy-Sato lead, entry four (cycle kfg, 9 October 2026). Tested prediction of the raise triangularity
\\ theorem with the Schubert minimality of thm:cube-hankel-block-flow-orders: at a cluster y0 with distinct roots
\\ where Hank_k lies in a Hankel block (k = k0 + i, block length Nb), the least coefficient of the raise L_lambda
\\ (window [-p, 2M-1-p] with its top k columns raised by lambda, l(lambda) <= k) vanishes unless lambda contains
\\ R = (Nb - i)^i, and is nonzero at lambda = R. Cluster: the centred quintic z^5 + z^3 - z^2 + 57/40 z - 187/100
\\ of ex:cube-flow-order-ratio-law-block (block k0 = 1, Nb = 3): k = 2 (p = 3) has R = (2); k = 3 (p = 2) has
\\ R = (1, 1). All partitions with |lambda| <= 3 and l(lambda) <= k. Numerical, 120 digits: the eps^(B_p) coefficient by Fourier
\\ extraction over numerical determinants, divided by Vand^2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 120);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
\\ eps^B coefficient by Fourier extraction over K = 2MB + 1 roots of unity (the truncated determinant has degree < K)
coefB(Y, L, B) = {
  my(M = #Y, K = 2 * M * B + 1, s0 = 0);
  for (j = 0, K - 1, my(w = exp(2 * Pi * I * j / K), G = matrix(2 * M, 2 * M));
    for (s = 1, M, for (u = 1, 2 * M, my(t = L[u]);
      G[s, u] = if (t >= 0, cc(t) * Y[s]^t, 0);
      G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * w^r * Y[s]^(t + r))));
    s0 += matdet(G) * w^(-B));
  s0 / K;
}
parts(n) = { my(v = List()); forpart(x = n, listput(v, Vecrev(x))); Vec(v); }
{
  my(f = 'z^5 + 'z^3 - 'z^2 + 57/40 * 'z - 187/100, Y = polroots(f), M = 5, V = vand(Y)^2);
  emit(Str("cluster ", f, ", |disc| ", Strprintf("%.6g", abs(poldisc(f)))));
  foreach([[3, [2]], [2, [1, 1]]], case, my(p = case[1], R = case[2], k = M - p, N = 2 * M - p, B = p^2 - p + M);
    emit(Str("p=", p, " k=", k, " predicted rectangle R=", R));
    for (n = 0, 3, foreach(if (n == 0, [[]], parts(n)), lambda,
      if (#lambda > k, next);
      my(lk = concat(vector(k - #lambda), Vecrev(lambda)));  \\ lk[n+1] = lambda_(k-n), n = 0..k-1
      my(top = concat(vector(M, i, i - 1), vector(k, n, M + (n - 1) + lk[n])));
      my(L = concat(vector(p, i, -p - 1 + i), top), c = coefB(Y, L, B) / V);
      my(contains = #lambda >= #R && prod(i = 1, #R, lambda[i] >= R[i]));
      emit(Str("  lambda=", lambda, " contains R: ", contains, "  |least coefficient| = ", Strprintf("%.4g", abs(c)))))));
  quit;
}
