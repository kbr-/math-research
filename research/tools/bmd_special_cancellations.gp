\\ Special cancellations on the collision cone (7 October 2026; cycle bmd-20261007-y).  Tests lem:cube-special-cancellation-trees:
\\ a_m = F(q^m), F = (x-q^i)(x-q^j)(x-r), r = q^rho (1 + u q^eta), rho an integer not in {i,j}, eta >= 1 an integer,
\\ u a unit, q = Q = 1000003.  A = a_i = a_j = 0.  Predictions (val = Q-adic valuation):
\\   rho < j: s1 = min(i,rho), h(m) = m + min(2m, m+s1, rho+i); for points P, Q other than a_rho, with mu(A) = j and
\\     mu(a_m) = m, val(P-Q) = h(min mu); val(a_rho - A) = h(rho) + eta; val(a_rho - a_n) = min(h(rho)+eta, h(min(n,j)))
\\     when the two differ (equality: tie or cherry, decided by leading coefficients; reported, not predicted).
\\   rho > j: h(m) = m + min(2m, m+i, i+j); for simple points P, Q other than a_rho, val = h(min mu); val(a_n - A) = h(n)
\\     for n < rho and V = i+j+rho for n > rho; val(a_rho - A) = V + eta; val(a_rho - a_n) = h(n) (n < rho), V (n > rho).
\\ Counts the pairs checked, mismatches, and the equality (coincidence) pairs, over all i < j, rho, eta in 1..3, N = 8.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Q = 1000003; vq(x) = valuation(x, Q);
{
my(N = 8, tot = 0, bad = 0, coin = 0, ex = List());
for (i = 1, N, for (j = i + 1, N, for (rho = 1, N, if (rho == i || rho == j, next);
  for (eta = 1, 3, foreach([1, -2, 5], u,
    my(r = Q^rho * (1 + u * Q^eta), F = x -> (x - Q^i) * (x - Q^j) * (x - r), a = vector(N, m, F(Q^m)), pred);
    my(S = select(m -> m != i && m != j && m != rho, [1 .. N]));
    if (rho < j,
      my(s1 = min(i, rho), h = m -> m + min(min(2*m, m + s1), rho + i), D = h(rho) + eta);
      \\ pairs among A and simple points other than a_rho
      foreach(S, m, tot++; if (vq(a[m]) != h(min(m, j)), bad++; listput(ex, [i, j, rho, eta, u, "A", m])));
      for (x1 = 1, #S, for (x2 = x1 + 1, #S, tot++; if (vq(a[S[x1]] - a[S[x2]]) != h(min(S[x1], S[x2])), bad++; listput(ex, [i, j, rho, eta, u, S[x1], S[x2]]))));
      tot++; if (vq(a[rho]) != D, bad++; listput(ex, [i, j, rho, eta, u, "rhoA"]));
      foreach(S, n, my(hn = h(min(n, j)));
        if (hn == D, coin++, tot++; if (vq(a[rho] - a[n]) != min(D, hn), bad++; listput(ex, [i, j, rho, eta, u, "rho", n])))),
      my(h = m -> m + min(min(2*m, m + i), i + j), V = i + j + rho);
      foreach(S, m, tot++; if (vq(a[m]) != if (m < rho, h(m), V), bad++; listput(ex, [i, j, rho, eta, u, "A", m])));
      for (x1 = 1, #S, for (x2 = x1 + 1, #S, tot++; if (vq(a[S[x1]] - a[S[x2]]) != h(min(S[x1], S[x2])), bad++; listput(ex, [i, j, rho, eta, u, S[x1], S[x2]]))));
      tot++; if (vq(a[rho]) != V + eta, bad++; listput(ex, [i, j, rho, eta, u, "rhoA"]));
      foreach(S, n, tot++; if (vq(a[rho] - a[n]) != if (n < rho, h(n), V), bad++; listput(ex, [i, j, rho, eta, u, "rho", n])))))))));
emit(Str("N = 8: ", tot, " predicted pairs, ", bad, " mismatches, ", coin, " coincidence pairs (tie or cherry, not predicted)"));
if (#ex, emit(Str("first mismatches: ", Vec(ex)[1 .. min(10, #ex)])));
}
