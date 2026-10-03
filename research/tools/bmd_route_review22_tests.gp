\\ Goal-level review tests (cycle bmd-20261009-al, 9 October 2026); candidate and least-value method of
\\ bmd_cancellation_wide_support.gp (q = 1000081), trees with M <= 4 only.
\\ (1) Phase-rule test of conj:cube-cancellation-wide-support: nu <= (number of leaders) - 1, so nu <= 2 wherever at most
\\     three leaders tie. Per tree: the largest number of leaders at any of the 900 rates, and the number of pairs of
\\     candidate coordinates sharing a term (Sigma L + n, n, val) that is least for some rate ("shared leading terms",
\\     which tie on an open set of rates).
\\ (2) Lead test (Appell F1 transformation): for m = 2, 3 and a pair (a, b) = (2, 5), the rho-weighted pair series
\\     E~(T) = sum_k rho_k e_k T^k, rho_k = k!/Gamma(k + 3/2 - m + 1), e_k = [T^k]((1 + aT)(1 + bT))^(-3/2), equals
\\     T^(m - 3/2) D^m [ sum_k k!/Gamma(k + 5/2) e_k T^(k + 3/2) ] (the Riemann-Liouville form); compared to order 30.
OUT = "research/results/bmd-20261009-al/review-tests.txt";
default(parisizemax, 4 * 10^9);
default(threadsizemax, 4 * 10^8);
q = 1000081;
c(n) = if(n < 0, 0, binomial(-3/2, n));
NU = 20;
coordterms(Y, L) = {
  my(M = #Y, p = #select(t -> t < 0, L));
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(D = matdet(X), sL = vecsum(L), res = List());
  for (n = 0, NU, my(z = polcoef(D, n, 'u)); if(z != 0, listput(res, [sL + n, n, valuation(z, q)])));
  [L, L == [-p .. 2 * M - 1 - p], Vec(res)];
};
export(q, NU, c, coordterms);
run(name, Y) = {
  my(M = #Y, cols = [-M .. 2 * M], subs = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]])); if(#select(t -> t < 0, L) <= M, listput(subs, L)));
  my(R = parapply(L -> coordterms(Y, L), Vec(subs)));
  my(wt = List()); foreach(R, r, if(r[2], foreach(r[3], t, listput(wt, t))));
  my(cand = select(r -> r[2] || #select(a -> !#select(b -> b[1] <= a[1] && b[2] <= a[2] && b[3] <= a[3] && (b[1] < a[1] || b[2] < a[2] || b[3] < a[3]), Vec(wt)), r[3]), R));
  my(mx = 0, used = Set(), shared = List());
  foreach(concat(vector(30, a, vector(30, b, [a / 10, b / 10]))), w,
    my(best = vector(#cand, i, my(v = oo, tt = 0); foreach(cand[i][3], t, my(x = t[1] * w[1] + t[2] * w[2] + t[3]); if(x < v, v = x; tt = t)); [v, tt]));
    my(m = vecmin(apply(x -> x[1], best)), idx = select(i -> best[i][1] == m, [1 .. #cand]));
    mx = max(mx, #idx);
    for (i = 1, #idx, for (j = i + 1, #idx, if(best[idx[i]][2] == best[idx[j]][2],
      my(k = [cand[idx[i]][1], cand[idx[j]][1]]); if(!setsearch(used, k), used = setunion(used, Set([k])); listput(shared, [w, k, best[idx[i]][2]]))))));
  write(OUT, "(1) ", name, " (M = ", M, "): most leaders at one rate ", mx, "; pairs with a shared least term ", #shared);
  for (i = 1, min(#shared, 4), write(OUT, "     ", shared[i]));
};
{
  my(w = truncate((-1 + sqrt(-3 + O(q^30))) / 2), r2 = sqrt(-2 + O(q^30)));
  run("equilateral (1, w, w^2)", [1, w, w^2]);
  run("equilateral (3, 2+w, 2+w^2)", [3, 2 + w, 2 + w^2]);
  run("tie modulus (1+2sqrt(-2))/3", [truncate((1 + 2 * r2) / 3), 1, q, q + q^2]);
  run("tie modulus (1-2sqrt(-2))/3", [truncate((1 - 2 * r2) / 3), 1, q, q + q^2]);
  run("control c0 = 2, M = 4", [2, 1, q, q + q^2]);
  run("three-root level (1, w, w^2) over q", [1, w, w^2, q]);
  my(K = 30, a = 2, b = 5);
  my(E = ((1 + a * 'T + O('T^(K + 4))) * (1 + b * 'T))^(-3/2));
  for (m = 2, 3,
    my(lhs = sum(k = 0, K, k! / gamma(k + 5/2 - m) * polcoef(E, k, 'T) * 'T^k));
    \\ J = sum k!/Gamma(k + 5/2) e_k T^(k + 3/2); T^(m - 3/2) D^m J = sum k!/Gamma(k + 5/2) e_k (k + 3/2)_(m, falling) T^k
    my(rhs = sum(k = 0, K, k! / gamma(k + 5/2) * polcoef(E, k, 'T) * prod(i = 0, m - 1, k + 3/2 - i) * 'T^k));
    write(OUT, "(2) m = ", m, ": max |coefficient difference| through T^", K, " = ", vecmax(abs(Vec(lhs - rhs)))));
}
