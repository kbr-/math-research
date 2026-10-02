\\ Leading term of the I-block minors with a double root (7 October 2026; cycle bmd-20261007-zx).
\\ Tested statement (lem:cube-double-node-alternant): rows psi = (1+beta w)^(-5/2) (entries e_t beta^t), w psi
\\ (e_(t-1) beta^(t-1)) for the double root, and V_q = (1+beta_q w)^(-3/2) (c_t beta_q^t) for simple roots, valuations
\\ pairwise distinct between roots.  For every column set N of size M (total multiplicity), det I[N] has valuation
\\ f*(N) = sum_i n_(i) mu_i - mu_dbl, where sorted columns go to roots by decreasing valuation (the double root takes two
\\ consecutive sorted columns at its rank pair), and leading coefficient +- prod c_t * g(t_a, t_b) * prod lc, with
\\ g(t, t') = e_t e_(t'-1) - e_(t') e_(t-1) != 0.  Checks all N within [0, 9] at three arcs (P-adic, exact), and the
\\ nonvanishing of g for 0 <= t < t' <= 40.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
cc(n) = if (n < 0, 0, binomial(-3/2, n));
ee(n) = if (n < 0, 0, binomial(-5/2, n));
gg(t, u) = ee(t) * ee(u - 1) - ee(u) * ee(t - 1);
P = 1000003;
{
my(bad = 0); for (t = 0, 40, for (u = t + 1, 40, if (gg(t, u) == 0, bad++)));
emit(Str("g(t,t') = 0 for 0 <= t < t' <= 40: ", bad, " cases"));
}
\\ roots: [inner valuation, leading coefficient, doubled?]
{
foreach([[[[0, 3, 1], [2, -2, 0]], 1], [[[0, 3, 0], [1, -2, 1], [3, 5, 0]], 1], [[[1, 3, 1], [0, -2, 0], [3, 5, 0]], 2]], c,
  my(roots = c[1], a = c[2], M = #roots + 1, ok = 0, tot = 0);
  forsubset([10, M], S, my(N = apply(x -> x - 1, Vec(S)), rows = List(), slots = List(), lc = 1, mud = 0);
    foreach(roots, r, my(bb = P^(a + r[1]) * r[2], mu = a + r[1]);
      listput(rows, vector(M, u, cc(N[u]) * bb^N[u]));
      if (r[3], rows[#rows] = vector(M, u, ee(N[u]) * bb^N[u]); listput(rows, vector(M, u, ee(N[u] - 1) * if (N[u] >= 1, bb^(N[u] - 1), 0)));
        listput(slots, [mu, r[2], 1]); listput(slots, [mu, r[2], 1]); mud = mu, listput(slots, [mu, r[2], 0])));
    my(D = matdet(Mat(Vec(rows)~)), v = if (D == 0, oo, valuation(D, P)));
    \\ predicted: slots sorted by decreasing valuation get sorted columns ascending
    my(sl = vecsort(Vec(slots), 1, 4), Ns = vecsort(N), pred = sum(i = 1, M, Ns[i] * sl[i][1]) - mud);
    tot++; if (v == pred, ok++));
  emit(Str("roots ", roots, ", a = ", a, ": column sets with exact valuation f*(N): ", ok, " of ", tot)));
}
quit
