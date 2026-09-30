\\ Control for the neck indeterminacy theorem at (2,2): the leading Pluecker form along rays.
\\ (Outcome recorded 30 September 2026: the leading coefficients have constant gcd, so no ray
\\ is a tie; the tie branch below then does nothing.)
\\ Statement tested: the leading Plücker form of the (2,2) neck along rays x = (-l, l),
\\ y = r (-l, l) is phi(r) v with a scalar phi having nonzero roots (tie ratios), and along a
\\ tie ray bent at second order the flat limit differs from the generic one.
t; z; r; c;
T = 14; DEN = 14;
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator ", denominator(p))); Vecrev(p, 2*DEN + 2);
flatlim(E) = {
  my(k = #E, rows = vector(k, i, E[i]), cost = vector(k), M, K, cc, piv, nr);
  for(iter = 1, 300,
    M = matrix(k, 2*DEN+2, i, j, vecz(polcoef(rows[i], 0, t))[j]);
    K = matker(M~);
    if(#K == 0, return([cost, vector(k, i, vecz(polcoef(rows[i], 0, t)))]));
    cc = K[,1];
    piv = 0; for(i = 1, k, if(cc[i] != 0 && (piv == 0 || cost[i] > cost[piv]), piv = i));
    nr = sum(i = 1, k, cc[i]*rows[i]);
    if(polcoef(nr, 0, t) != 0, error("relation not zero"));
    rows[piv] = nr/t; cost[piv]++);
  error("no convergence");
}
samespace(A, B) = matrank(matconcat([Mat(A~); Mat(B~)])) == matrank(Mat(A~)) && matrank(Mat(A~)) == matrank(Mat(B~));
Af(x) = sqrt(1 - x/z + O(t^(T+1)));
Bf(y) = sqrt(1 - y/(z-1) + O(t^(T+1)));
\\ naive basis from divided differences at x = (x1, x2), y = (y1, y2)
naive(x1, x2, y1, y2) = my(A0 = Af(x1), A1 = (Af(x1) - Af(x2))/(x1 - x2), B0 = Bf(y1), B1 = (Bf(y1) - Bf(y2))/(y1 - y2)); [A0*B0, A1*B0, A0*B1, A1*B1];
{
  my(E = naive(-t, t, -r*t, r*t), Ms, cols, phi = 0, D, ord);
  \\ t-expansion of the 4 x (2 DEN + 2) coefficient matrix
  Ms = matrix(4, 2*DEN + 2, i, j, sum(k = 0, 10, vecz(polcoef(E[i], k, t))[j]*t^k) + O(t^11));
  my(Dl = List(), vmin = oo);
  forsubset([2*DEN + 2, 4], S,
    D = matdet(matrix(4, 4, i, j, Ms[i, S[j]]));
    if(D != 0, listput(Dl, D); vmin = min(vmin, valuation(D, t))));
  print("minimal t-valuation of the 4x4 minors (naive basis): ", vmin);
  foreach(Dl, D, phi = gcd(phi, polcoef(D, vmin, t)));
  print("gcd of the leading Pluecker coefficients: ", factor(phi));
  \\ tie ratios: nonzero roots of phi
  my(P = phi / r^valuation(phi, r), f = factor(P)[, 1], gen);
  gen = flatlim(naive(-t, t, -(3/11)*t, (3/11)*t));
  print("generic (r = 3/11) costs ", gen[1]);
  for(i = 1, #f, if(poldegree(f[i], r) > 0,
    my(r0 = Mod(r, f[i]), res);
    print("tie factor ", f[i]);
    res = flatlim(naive(-t, t, -r0*t, r0*t));
    print("  straight tie ray: costs ", res[1], " same as generic: ", samespace(res[2], gen[2]));
    foreach([1, 2, -1], cc,
      res = flatlim(naive(-t, t, -(r0 + cc*t)*t, (r0 + cc*t)*t));
      print("  bent tie ray r = r0 + ", cc, " t: costs ", res[1], " same as generic: ", samespace(res[2], gen[2])));
    res = flatlim(naive(-t, t, -(r0 + t)*t, (r0 + t)*t));
    my(res2 = flatlim(naive(-t, t, -(r0 + 2*t)*t, (r0 + 2*t)*t)));
    print("  bends 1 and 2 give the same space: ", samespace(res[2], res2[2]))));
}
