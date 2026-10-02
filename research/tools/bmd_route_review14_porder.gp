\\ Route review lead test (8 October 2026; cycle bmd-20261008-zu).
\\ Tested statement (Bhargava p-orderings, applied to window penalties): for a finite set Y of p-adic integers,
\\ g(k) = min over (k+1)-subsets S of v_p(prod_{a<b in S} (y_a - y_b)) has nondecreasing increments in k, and the
\\ first k+1 points of a greedy p-ordering attain it. Then k -> val Hank_k = 2 g(k) is convex for every tree of roots.
\\ Brute force over all subsets, 200 random sets of 8 integers with many shared 3-adic digits, p = 3.
OUT = "research/results/bmd-20261008-zu/porder-test.txt";
vv(S) = sum(a = 1, #S, sum(b = a + 1, #S, valuation(S[b] - S[a], 3)));
{
  my(fails_conv = 0, fails_greedy = 0, n = 8);
  setrand(14);
  for (trial = 1, 200,
    my(Y = vector(n, i, sum(d = 0, 5, random(2) * 3^(random(4) + d)) + 3^12 * i));
    my(g = vector(n, k, oo));
    forsubset(n, T, my(k = #T); if (k >= 1, g[k] = min(g[k], vv(vecextract(Y, Vec(T))))));
    \\ greedy p-ordering from each start point; best greedy prefix values
    my(gr = vector(n, k, oo));
    for (s0 = 1, n, my(ord = [Y[s0]], rest = vecextract(Y, setminus([1..n], [s0])));
      gr[1] = 0;
      for (k = 2, n, my(best = oo, bi = 0);
        for (i = 1, #rest, my(c = sum(a = 1, #ord, valuation(rest[i] - ord[a], 3))); if (c < best, best = c; bi = i));
        ord = concat(ord, rest[bi]); rest = vecextract(rest, setminus([1..#rest], [bi]));
        gr[k] = min(gr[k], vv(ord))));
    for (k = 2, n - 1, if (g[k + 1] - g[k] < g[k] - g[k - 1], fails_conv++));
    for (k = 1, n, if (gr[k] != g[k], fails_greedy++)));
  write(OUT, "200 random sets of 8 points, p = 3: convexity failures ", fails_conv, "; greedy-prefix mismatches ", fails_greedy);
}
