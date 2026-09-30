\\ Schur-type test (route review bmd-20260930-zzo): Newton polygons of the far polynomials at the large
\\ primes that divide their extreme coefficients exactly once (17 for (1,1); 29, 31 for (1,2) and (2,1)).
\\ Slopes as root valuations (PARI newtonpoly); consecutive equal values grouped into segments.
segs(W, p) = {
  my(np = newtonpoly(W, p), S = List(), cur = np[1], len = 1);
  for (i = 2, #np, if (np[i] == cur, len++, listput(S, [cur, len]); cur = np[i]; len = 1));
  listput(S, [cur, len]); Vec(S);
}
{
  foreach([["research/results/bmd-20260930-zzn/W_1_1.gp", [17, 19, 23]],
           ["research/results/bmd-20260930-zzn/W_1_2.gp", [29, 31, 37]],
           ["research/results/bmd-20260930-zzn/W_2_1.gp", [29, 31, 37]]], c,
    my(W = read(c[1]), Wi = W * denominator(content(W))); Wi = Wi / content(Wi);
    print(c[1], ": degree ", poldegree(Wi));
    foreach(c[2], p, print("  p = ", p, ": v_p(lc) = ", valuation(pollead(Wi), p), ", v_p(a_0) = ", valuation(polcoef(Wi, 0), p), ", segments ", segs(Wi, p))));
}
