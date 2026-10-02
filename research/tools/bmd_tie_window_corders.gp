\\ c-orders of the maximal minors of the confluent tie window (7 October 2026; cycle bmd-20261007-zi).
\\ W^c(c) as in bmd_confluent_tie_window.gp: (3m+3) x (3m+5), columns T^d..T^(d+3m+4), d = binom(m,2).  For each pair
\\ {p < q} of dropped columns (0-based offsets from d), prints the c-order of the minor and the factored lowest
\\ coefficient, m = 1..5.  Question: which minors have least c-order, and is their lowest coefficient a product of
\\ binomial Schur values (a single lattice term), as for the pure block (lem:cube-tie-pure-extreme-coefficients)?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1)); }
{
for (m = 1, 5,
  my(A = winmat(m), w = 3 * m + 5, res = List(), best = oo);
  for (p = 1, w, for (q = p + 1, w,
    my(D = matdet(vecextract(A, "..", select(j -> j != p && j != q, [1 .. w]))));
    if (D != 0, my(v = valuation(D, 'c)); listput(res, [p - 1, q - 1, v]); best = min(best, v))));
  my(mins = select(x -> x[3] == best, Vec(res)));
  emit(Str("m = ", m, ": least c-order ", best, " at dropped pairs ", apply(x -> [x[1], x[2]], mins), "; nonzero minors ", #res, " of ", binomial(w, 2)));
  foreach(mins, x, my(D = matdet(vecextract(A, "..", select(j -> j != x[1] + 1 && j != x[2] + 1, [1 .. w]))));
    emit(Str("   drop ", [x[1], x[2]], ": lowest coefficient ", factor(polcoef(D, best, 'c)), ", degree ", poldegree(D, 'c), ", (c-1)-order ", valuation(D, 'c - 1)))));
}
quit
