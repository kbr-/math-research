\\ Two-double limit trees (7 October 2026; cycle bmd-20261007-s).  For each N and each pair of disjoint index pairs
\\ {i<j}, {k<l} in 1..N with D = q^k+q^l-q^i-q^j != 0, the cone point with a_i = a_j and a_k = a_l is
\\ a_m = F(q^m), F = (x-q^i)(x-q^j)(x-r), r = q^k + P(q^l)/D, P(x) = (x-q^i)(x-q^j).  With q = Q (prime), the q -> 0
\\ limit tree is read from Q-adic valuations of differences of the N-2 distinct points (A and B counted once).  A
\\ tree is a "chain" when every split separates exactly one point from the rest (bottom: two points).  Prints, per N,
\\ the number of quadruples, of chains, and every non-chain split pattern with an example.  It also tests the exact
\\ formula val(P-Q) = h(min(mu(P),mu(Q))) of lem:cube-two-double-cone-chains, with mu(A) = j, mu(B) = l, mu(a_m) = m
\\ and h(m) = m + min(2m, i+m, i+k), and counts the pairs off the formula.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Q = 1000003;
vd(x, y) = valuation(x - y, Q);
\\ split a set (vector of [label, value]) at its smallest pairwise valuation; return the clusters
clusters(S) = {
  my(n = #S, mv = oo, comp = vector(n, t, t), cl = List());
  for (a = 1, n, for (b = a + 1, n, mv = min(mv, vd(S[a][2], S[b][2]))));
  for (a = 1, n, for (b = a + 1, n, if (vd(S[a][2], S[b][2]) > mv,
    my(ca = comp[a], cb = comp[b]); if (ca != cb, for (t = 1, n, if (comp[t] == cb, comp[t] = ca))))));
  foreach(Set(comp), c, listput(cl, vector(#select(t -> t == c, comp), u, S[select(t -> t == c, comp, 1)[u]])));
  Vec(cl);
}
\\ returns a string describing non-chain splits ("" if chain)
pattern(S) = {
  my(out = "", cur = S);
  while (#cur > 2,
    my(cl = clusters(cur), sizes = vecsort(apply(c -> #c, cl)));
    if (#cl == 2 && sizes[1] == 1, cur = if (#cl[1] == 1, cl[2], cl[1]),
      out = Str(out, " split ", sizes, " with labels ", apply(c -> apply(e -> e[1], c), cl)); break));
  out;
}
{
for (N = 5, 9,
  my(tot = 0, chains = 0, bad = 0, pats = Map());
  for (i = 1, N, for (j = i + 1, N, for (k = 1, N, for (l = k + 1, N,
    if (k == i || k == j || l == i || l == j || k < i, next);
    my(D = Q^k + Q^l - Q^i - Q^j); if (D == 0, next);
    my(P = x -> (x - Q^i) * (x - Q^j), r = Q^k + P(Q^l) / D, F = x -> P(x) * (x - r), S = List());
    listput(S, ["A", F(Q^i), j]); listput(S, ["B", F(Q^k), l]);
    for (m = 1, N, if (m != i && m != j && m != k && m != l, listput(S, [Str(m), F(Q^m), m])));
    S = Vec(S);
    my(okd = 1); for (a = 1, #S, for (b = a + 1, #S, if (S[a][2] == S[b][2], okd = 0)));
    if (!okd, emit(Str("N=", N, " (", i, j, ",", k, l, "): further coincidence")); next);
    tot++; my(pt = pattern(S), h = t -> t + min(min(2 * t, i + t), i + k));
    for (a = 1, #S, for (b = a + 1, #S, if (vd(S[a][2], S[b][2]) != h(min(S[a][3], S[b][3])), bad++)));
    if (pt == "", chains++, if (!mapisdefined(pats, pt), mapput(pats, pt, Str("(i,j,k,l) = (", i, ",", j, ",", k, ",", l, ")"))))))));
  emit(Str("N = ", N, ": ", tot, " two-double points (i < k), ", chains, " chains, ", bad, " pairs off the formula"));
  foreach(Mat(pats)~, row, emit(Str("   non-chain:", row[1], "  e.g. ", row[2]))));
}
