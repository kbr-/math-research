\\ Leaders of the cube-root cherry at rates near (1,1) (cycle bmd-20261009-am, 9 October 2026); part 2 of
\\ bmd_cherry_hankel.gp with arcs x = s^a, e = s^b instead of x = e = s.
\\ Tested statement (draft open-rate uniqueness): on every open set of rates the leading cross coordinate is unique.
\\ The cherry join x*D u {1, 1+e}, D = {1, w3, w3^2} (Hank_1(D) = 0), exact reparametrized roots eps = -e/(1+e),
\\ b = x y/(1 - x y); all 1716 cross-block Pluecker coordinates on 6-subsets of [-5, 7]; least s-valuation and its
\\ minimizers at (a, b) in {(1,1), (3,4), (4,3), (5,6), (6,5)}, all inside the regime 1/2 < a/b < 2 of the example.
\\ If two leaders persist at all these rates, they tie on an open set and the draft lemma fails in the cherry setting.
\\ Control: D = {1, 2, 5}.
OUT = "research/results/bmd-20261009-am/cube-root-open-rates.txt";
vv = [s, T]; vz = z;
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
{
my(w3 = Mod(z, z^2 + z + 1));
foreach([[[1, w3, w3^2], "cube roots of unity"], [[1, 2, 5], "control {1,2,5}"]], cas,
  foreach([[1, 1], [3, 4], [4, 3], [5, 6], [6, 5]], ab,
    my([a, bb] = ab, NS = 16 * max(a, bb) + 10, ys = cas[1], M = 3, cols = [-5 .. 7], rows = matrix(2*M, #cols), best = oo, arg = List());
    my(xx = s^a + O(s^NS), eps0 = -s^bb / (1 + s^bb) + O(s^NS));
    for (q = 1, M, my(b = xx * ys[q] / (1 - xx * ys[q]));
      for (u = 1, #cols, my(t = cols[u]);
        rows[q, u] = if (t >= 0, cc(t) * b^t, 0);
        rows[M + q, u] = sum(r = max(1, -t), NS, cc(r) * cc(t + r) * eps0^r * b^(t + r))));
    forsubset([#cols, 2*M], S, my(d = matdet(vecextract(rows, "..", Vec(S))), v = if (d == 0, oo, valuation(lift(d), s)));
      if (v < best, best = v; arg = List());
      if (v == best, listput(arg, apply(u -> cols[u], Vec(S)))));
    write(OUT, cas[2], ", (w_x, w_e) = ", ab, ": least valuation ", best, " at ", Vec(arg))));
}
