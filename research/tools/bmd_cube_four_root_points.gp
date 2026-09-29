\\ Explicit Weierstrass points of the four-root pair space, and failure at five roots (29 September 2026;
\\ cycle bmd-20260929-zg). Tested statements: (a) for N = 4 roots b, the non-branch Wronskian polynomial of the pair
\\ space <phi_i phi_j>, phi = (1 + bT)^(-3/2), is a constant times the product over the three matchings
\\ {i,j}|{k,l} of the quadratic numerator of b_i/(1+b_i t) + b_j/(1+b_j t) - b_k/(1+b_k t) - b_l/(1+b_l t);
\\ (b) for N = 5 the analogous product over the 15 matchings of 4-subsets (degree 30) is NOT proportional to the
\\ non-branch Wronskian polynomial (so the pair-sum Vandermonde form fails for five roots). Random rational roots.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], T) / fl[i][j][1]), q = 1); for (k = 1, n, P[k, i] = q; q = deriv(q, T) + q * L));
  numerator(matdet(P));
}
nonbranch(b) = {
  my(fl = List());
  for (i = 1, #b, for (j = i + 1, #b, listput(fl, [[1 + b[i] * T, -3/2], [1 + b[j] * T, -3/2]])));
  my(W = wronsk(Vec(fl)));
  foreach (b, x, while (subst(W, T, -1 / x) == 0, W = W / (T + 1 / x)));
  W / pollead(W);
}
quad(b, i, j, k, l) = numerator(b[i] / (1 + b[i] * T) + b[j] / (1 + b[j] * T) - b[k] / (1 + b[k] * T) - b[l] / (1 + b[l] * T));
predicted(b) = {
  my(P = 1, n = #b);
  forsubset(n, S, if (#S == 4, my(v = Vec(S)); P *= quad(b, v[1], v[2], v[3], v[4]) * quad(b, v[1], v[3], v[2], v[4]) * quad(b, v[1], v[4], v[2], v[3])));
  P / pollead(P);
}
main() = {
  setrand(4);
  for (rep = 1, 3,
    my(b = vector(4, i, (random(200) - 100) / (random(9) + 1)), W = nonbranch(b), P = predicted(b));
    emit(Str("N=4 sample ", rep, ": deg W = ", poldegree(W), ", deg predicted = ", poldegree(P), ", equal = ", W == P)));
  my(b = [2, -3, 5, 7/2, -1/3], W = nonbranch(b), P = predicted(b));
  emit(Str("N=5: deg W = ", poldegree(W), ", deg predicted = ", poldegree(P), ", equal = ", W == P, ", gcd degree ", poldegree(gcd(W, P))));
}
main();
