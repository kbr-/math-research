\\ Test of conj:cube-far-two-adic-shape at (e,l) = (2,2) (cycle bmd-20260930-zzw).  Reads the exact determinants
\\ det[q] written by bmd_cube_far_wronskian_flint.c, strips the factors x and 1+x, takes the primitive part.
\\ Validation: at (1,1) the result must equal the saved primitive W_1_1 of cycle bmd-20260930-zzn (up to sign).
\\ Test: is W_2_2 = c x^A (1+x)^B mod 2?  Also: squarefree, degree, 2-adic segments at 0, -1, infinity.
prim(D) = { my(W = D / x^valuation(D, x)); while (subst(W, x, -1) == 0, W = W / (1 + x)); W / content(W); }
segs(W, p) = {
  my(v = newtonpoly(W, p), out = List(), i = 1);
  while (i <= #v, my(j = i); while (j < #v && v[j + 1] == v[i], j++); listput(out, [v[i], j - i + 1]); i = j + 1);
  Vec(out);
}
{
  my(W11 = prim(read("research/results/bmd-20260930-zzw/det_1_1.gp")), S11 = read("research/results/bmd-20260930-zzn/W_1_1.gp"));
  S11 = S11 / content(S11);
  print("validation (1,1): equal up to sign: ", W11 == S11 || W11 == -S11, ", degree ", poldegree(W11));
  foreach ([[1,1],[1,2],[2,1],[2,2],[1,3],[3,1]], el,
    my(e = el[1], l = el[2], W = prim(read(Str("research/results/bmd-20260930-zzw/det_", e, "_", l, ".gp"))), W2 = W * Mod(1, 2), sh = factor(W2), ok = 1);
    for (i = 1, #sh~, if (lift(sh[i, 1]) != x && lift(sh[i, 1]) != x + 1, ok = 0));
    print("(e,l) = (", e, ",", l, "): degree ", poldegree(W), ", squarefree: ", poldegree(gcd(W, W')) == 0,
      ", W = c x^A (1+x)^B mod 2: ", ok, ", mod-2 factorization ", lift(sh));
    my(c = [#select(s -> s > 0, newtonpoly(W, 2)), #select(s -> s > 0, newtonpoly(subst(W, x, x - 1), 2)), #select(s -> s > 0, newtonpoly(polrecip(W), 2))]);
    print("   roots near 0, -1, infinity (2-adically): ", c, ", total ", vecsum(c));
    print("   segments at 2 (slope, length): W(x) ", segs(W, 2), "; W(x-1) ", segs(subst(W, x, x - 1), 2), "; reversal ", segs(polrecip(W), 2)));
}
