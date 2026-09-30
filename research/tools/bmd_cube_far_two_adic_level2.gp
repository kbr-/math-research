\\ Second level of the 2-adic cluster tree of the far polynomials (cycle bmd-20260930-zzx).
\\ For each saved size, rescale the valuation-2 cluster at each special point:
\\   at 0: V(y) = W(4y);  at -1: V(y) = W(4y - 1);  at infinity: V(y) = y^d W(1/(4y)) (reversal of W(4x)... i.e. x = 1/(4y)).
\\ Take the primitive part; the roots of valuation exactly 2 at the point become 2-adic units y.  Report the
\\ reduction of V modulo 2 (which residues in Fbar_2 the unit roots take, and with what multiplicity), and the
\\ Newton polygon of V(y - r) at 2 for each residue r in F_2^* = {1} carrying unit roots.
prim(D) = { my(W = D / x^valuation(D, x)); while (subst(W, x, -1) == 0, W = W / (1 + x)); W / content(W); }
segs(W, p) = {
  my(v = newtonpoly(W, p), out = List(), i = 1);
  while (i <= #v, my(j = i); while (j < #v && v[j + 1] == v[i], j++); listput(out, [v[i], j - i + 1]); i = j + 1);
  Vec(out);
}
{
  foreach ([[1,1],[1,2],[2,1],[2,2],[1,3],[3,1]], el,
    my(e = el[1], l = el[2], W = prim(read(Str("research/results/bmd-20260930-zzw/det_", e, "_", l, ".gp"))), d = poldegree(W));
    print("(e,l) = (", e, ",", l, "), degree ", d);
    foreach ([["0", subst(W, x, 4*x)], ["-1", subst(W, x, 4*x - 1)], ["inf", subst(polrecip(W), x, 4*x)]], pt,
      my(V = pt[2] / content(pt[2]), f = factor(V * Mod(1, 2)), units = List());
      for (i = 1, #f~, my(g = lift(f[i, 1])); if (g != x, listput(units, [g, f[i, 2]])));
      print("   at ", pt[1], ": V mod 2 = ", lift(f), ";  segments of V(y+1) at 2: ", segs(subst(V, x, x + 1), 2))));
}
