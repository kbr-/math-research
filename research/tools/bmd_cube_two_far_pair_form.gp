\\ The quadratic Cauchy-Binet form of a two-far window at s_2 = 0 (29 September 2026; cycle bmd-20260929-zk;
\\ conj:cube-two-far-window-valuations).
\\ With s_2 = 0 the rows are the near span N (coefficients beta_b t_j^b at columns b >= 0) and f N, f = (1+s/S)^(-3/2).
\\ Cauchy-Binet gives P_E = sum_{K1, K2} B(K1, K2) Y_K1 Y_K2, Y the Pluecker vector of N, where B(K1, K2) is the
\\ determinant with rows e_k (k in K1, unit vector at column k) and (beta_(k-e) s^(k-e))_(e in E) (k in K2).
\\ Tested: (1) whether B(K1, K2) + B(K2, K1) = 0 for all K1 != K2 (so that P_E = sum_K B(K, K) Y_K^2 exactly);
\\ (2) whether B(K*, K*) != 0 for K* = {0..n-r-1} u {n-r+1, n-r+3, ..., n+r-1} on the window [-(n-r), n-1+r].
\\ Subsets K range over n-subsets of {0..M}, M = n + r + 2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(k) = if (k < 0, 0, binomial(-3/2, k));
Bf(E, K1, K2) = {
  my(L = #E, A = matrix(L, L));
  for (a = 1, #K1, for (c = 1, L, A[a, c] = (K1[a] == E[c])));
  for (a = 1, #K2, for (c = 1, L, A[#K1 + a, c] = be(K2[a] - E[c]) * 'x^max(0, K2[a] - E[c])));
  matdet(A);
}
main() = {
  foreach ([3, 4, 5], n,
    for (r = 0, n - 1,
      my(E = [-(n - r) .. n - 1 + r], M = n + r + 2, subs = List(), bad = 0, sym = 0, nz = 0);
      forsubset([M + 1, n], S, listput(subs, Vec(S) - vector(n, i, 1)));
      my(Bm = matrix(#subs, #subs, a, b, Bf(E, subs[a], subs[b])));
      for (a = 1, #subs, for (b = a + 1, #subs, my(u = Bm[a, b], v = Bm[b, a]); if (u != 0 || v != 0, nz++; if (u + v != 0, bad++; if (u == v, sym++)))));
      my(Ks = concat([0 .. n - r - 1], vector(r, i, n - r - 1 + 2 * i)), ia = 0);
      for (a = 1, #subs, if (subs[a] == Ks, ia = a));
      emit(Str("2x", n, " r=", r, ": off-diagonal pairs with a nonzero entry ", nz, ", not antisymmetric ", bad, " (of which symmetric ", sym, "); K* = ", Ks, ", B(K*,K*) = ", Bm[ia, ia]))));
}
main();
