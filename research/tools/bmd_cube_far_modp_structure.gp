\\ Structure of the far polynomials W_k modulo small primes (cycle bmd-20260930-zzv).
\\ A triple root of W over Qbar at a p-adic unit point reduces to a root of multiplicity >= 3 of W mod p
\\ (p not dividing the leading coefficient).  Question: modulo small primes, is W_k = x^A (1+x)^B H with H
\\ free of cubes (or squarefree), uniformly in (e,l)?  Reports, for each saved W_k and p <= 13, the
\\ degree drop, the multiplicities at 0 and -1, and the multiplicity pattern of the other irreducible factors.
{
  foreach (["1_1", "1_2", "2_1"], nm,
    my(W = read(Str("research/results/bmd-20260930-zzn/W_", nm, ".gp")));
    W = W / content(W);
    print("(e,l) = (", nm, "), deg ", poldegree(W));
    forprime (p = 2, 13,
      my(Wp = W * Mod(1, p), f, m0 = 0, m1 = 0, mult = List());
      if (Wp == 0, print("  p = ", p, ": W = 0 mod p"); next);
      f = factor(Wp);
      for (i = 1, #f~, my(g = lift(f[i, 1]), e = f[i, 2]);
        if (g == x, m0 = e, if (g == x + 1, m1 = e, listput(mult, [poldegree(g), e]))));
      my(maxe = if (#mult, vecmax(apply(v -> v[2], Vec(mult))), 0));
      print("  p = ", p, ": deg drop ", poldegree(W) - poldegree(Wp), ", mult at 0: ", m0, ", at -1: ", m1,
        ", other factors (degree, multiplicity) with max multiplicity ", maxe, ": ", Vec(mult))));
}
