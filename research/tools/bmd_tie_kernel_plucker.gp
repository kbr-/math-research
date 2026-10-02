\\ Plucker ramification of the kernel curve of the excess-one tie sub-window (8 October 2026; cycle bmd-20261008-d).
\\ V(c) = columns T^d..T^(d+3m+3) of W^c(c) (drop the last column); its kernel is spanned by a primitive x(c) in Q[c]^(3m+4)
\\ of degree nu.  The curve c -> [x(c)] in P^n (n + 1 = dim of the span of the coordinates x_j) is base-point free of
\\ degree nu, so by the Plucker formula sum over points P of sum_i (a_i(P) - i) = (n + 1)(nu - n), a_i(P) the vanishing
\\ sequence.  Question: is all ramification at c = 0, 1, oo?  Then nu, hence the absence of special values
\\ (nu = top minor degree - orders at 0 and 1), would follow from local data at 0, 1, oo.
\\ For m = 1..4: n, nu, the vanishing sequences' ramification R_0, R_1, R_oo, and (n+1)(nu - n) - R_0 - R_1 - R_oo.
default(parisizemax, 4 * 10^9);
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
\\ coefficient matrix (rows = coordinates, columns = Taylor degrees 0..nu) of the polynomials x_j(c + c0)
tcoef(x, c0, nu) = matrix(#x, nu + 1, j, t, polcoef(subst(x[j], 'c, 'c + c0), t - 1, 'c));
\\ vanishing sequence: the orders realized by the span = pivot columns of the row echelon form
vanseq(M) = {
  my(seq = List(), r0 = 0);
  for (t = 1, #M, my(r = matrank(vecextract(M, "..", [1 .. t]))); if (r > r0, listput(seq, t - 1); r0 = r));
  Vec(seq);
}
ram(s) = sum(i = 1, #s, s[i] - (i - 1));
{
for (m = 1, 4,
  my(W = winmat(m), V = vecextract(W, "..", [1 .. #W - 1]), K = matker(V), x, nu, n, Minf, s0, s1, sinf);
  x = K[, 1]; x = x * denominator(content(x)); x = x / content(x);
  nu = vecmax(apply(e -> poldegree(e, 'c), x));
  my(M0 = tcoef(x, 0, nu));
  n = matrank(M0) - 1;
  s0 = vanseq(M0); s1 = vanseq(tcoef(x, 1, nu));
  \\ at infinity: orders nu - deg, i.e. the Taylor expansion of c^nu x(1/c) at 0
  Minf = matrix(#x, nu + 1, j, t, polcoef(x[j], nu - (t - 1), 'c)); sinf = vanseq(Minf);
  my(tot = (n + 1) * (nu - n));
  emit(Str("m = ", m, ": n = ", n, ", nu = ", nu, ", (n+1)(nu-n) = ", tot, "; R_0 = ", ram(s0), ", R_1 = ", ram(s1), ", R_oo = ", ram(sinf),
    ", elsewhere = ", tot - ram(s0) - ram(s1) - ram(sinf), "; vanishing at 0: ", s0, ", at 1: ", s1, ", at oo: ", sinf)));
}
quit
