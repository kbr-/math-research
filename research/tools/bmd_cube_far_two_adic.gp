\\ Two-adic three-cluster exclusion of cubed factors for the far polynomials (cycle bmd-20260930-zzv).
\\ Observation (bmd_cube_far_modp_structure.gp): W_k = c x^A (1+x)^B mod 2 (after the degree drop), so every
\\ root is 2-adically close to 0, -1 or infinity.  If W = G^r H, Dumas' theorem applies to W(x), W(x-1) and the
\\ reversal x^d W(1/x), each with G replaced accordingly.  In W(x) the roots near 0 are those of positive slope
\\ (root valuation > 0); in W(x-1) those near -1; in the reversal those near infinity.  A factor G takes from a
\\ segment of slope a/b (lowest terms) and length L a length l with b | l and r l <= L.  So
\\   deg G = g0 + g1 + ginf,  g0 in S(W(x), slopes > 0),  g1 in S(W(x-1), slopes > 0),  ginf in S(rev, slopes > 0).
\\ Report the positive degrees of G not excluded, for r = 2, 3.  Also check the mod-2 shape.
segs(W, p) = {
  my(v = newtonpoly(W, p), out = List(), i = 1);
  while (i <= #v, my(j = i); while (j < #v && v[j + 1] == v[i], j++); listput(out, [v[i], j - i + 1]); i = j + 1);
  Vec(out);
}
posset(W, p, r) = {
  my(S = [0]);
  foreach (segs(W, p), sg, if (sg[1] > 0, my(b = denominator(sg[1]), L = sg[2], T = List());
    foreach (S, t, forstep (l = 0, L \ r, b, listput(T, t + l)));
    S = Set(Vec(T))));
  S;
}
{
  foreach (["1_1", "1_2", "2_1"], nm,
    my(W = read(Str("research/results/bmd-20260930-zzn/W_", nm, ".gp")), d, W1, Wr, cnt);
    W = W / content(W); d = poldegree(W);
    W1 = subst(W, x, x - 1); Wr = polrecip(W);
    my(W2 = W * Mod(1, 2), sh = factor(W2), okshape = 1);
    for (i = 1, #sh~, if (lift(sh[i, 1]) != x && lift(sh[i, 1]) != x + 1, okshape = 0));
    cnt = [#select(s -> s > 0, newtonpoly(W, 2)), #select(s -> s > 0, newtonpoly(W1, 2)), #select(s -> s > 0, newtonpoly(Wr, 2))];
    print("(e,l) = (", nm, "), deg ", d, ": W = c x^A (1+x)^B mod 2: ", okshape, "; roots near 0, -1, infinity (2-adically): ", cnt, ", total ", vecsum(cnt));
    print("   segments at 2 (slope, length): W(x) ", segs(W, 2), "; W(x-1) ", segs(W1, 2), "; reversal ", segs(Wr, 2));
    foreach ([2, 3], r,
      my(A = posset(W, 2, r), B = posset(W1, 2, r), C = posset(Wr, 2, r), D = List());
      foreach (A, u, foreach (B, v, foreach (C, w, listput(D, u + v + w))));
      print("   r = ", r, ": positive degrees of G not excluded at p = 2: ", setminus(Set(Vec(D)), [0]))));
}
