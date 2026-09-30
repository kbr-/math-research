\\ Two-adic factorization type of the far polynomials (cycle bmd-20260930-zzv): degrees of the irreducible
\\ factors over Q_2 and, for each, the 2-adic valuation of its roots relative to the nearest of 0, -1, infinity.
{
  foreach (["1_1", "1_2", "2_1"], nm,
    my(W = read(Str("research/results/bmd-20260930-zzn/W_", nm, ".gp")), f, out = List());
    W = W / content(W);
    f = factorpadic(W, 2, 80);
    for (i = 1, #f~, my(g = f[i, 1], d = poldegree(g), v0, v1, vi);
      v0 = newtonpoly(liftall(g), 2); v1 = newtonpoly(subst(liftall(g), x, x - 1), 2);
      listput(out, [d, f[i, 2], vecmax(v0), vecmax(v1), vecmin(v0)]));
    print("(e,l) = (", nm, "), deg ", poldegree(W), ": ", #out, " factors over Q_2 [degree, multiplicity, max val at 0, max val at -1, min val (neg = near infinity)]:");
    print("   ", Vec(out)));
}
