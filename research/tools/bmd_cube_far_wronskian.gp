\\ Exact far Wronskians of the peeling degeneration (cube-base-peeling), c = 1:
\\ F_k = P_{<R_e} + <(1+x)^-3> + x^{-(R_l+2)} P_{<R_l} + (1+x)^{-7/2} P_{<4e}
\\       + (1+x)^{-5/2} x^{1/2-4l} P_{<4l} + x^{-7/2+4e-4el} P_{<4el},   R_n = n(2n-1), e = k-1, l = b-k.
\\ Each function is x^al (1+x)^be p(x); f^(m) = x^(al-m) (1+x)^(be-m) p_m with
\\ p_{m+1} = (al-m)(1+x) p_m + (be-m) x p_m + x(1+x) p_m'.  W = prod x^al_i (1+x)^be_i (x(1+x))^(-binom(R,2)) det[p_{i,m}].
\\ Output: the polynomial part W_k (x and 1+x factors removed), its degree against #F_k = 4l(2e^2+6el-5e-4l+5),
\\ squarefreeness, and its factorization over Q (degrees), to look for classical (Jacobi-type) factors.
default(parisizemax, 4000000000);
Rn(n) = n*(2*n-1);
funcs(e, l) = {
  my(L = List());
  for (j = 0, Rn(e) - 1, listput(L, [0, 0, x^j]));
  listput(L, [0, -3, 1]);
  for (j = 0, Rn(l) - 1, listput(L, [-(Rn(l) + 2), 0, x^j]));
  for (j = 0, 4*e - 1, listput(L, [0, -7/2, x^j]));
  for (j = 0, 4*l - 1, listput(L, [1/2 - 4*l, -5/2, x^j]));
  for (j = 0, 4*e*l - 1, listput(L, [-7/2 + 4*e - 4*e*l, 0, x^j]));
  Vec(L);
}
farW(e, l) = {
  my(F = funcs(e, l), R = #F, M = matrix(R, R), Wp, v0, v1);
  if (R != Rn(e + l + 1), error("dimension ", R));
  for (i = 1, R, my(al = F[i][1], be = F[i][2], p = F[i][3]);
    for (m = 0, R - 1,
      M[i, m + 1] = p;
      p = (al - m)*(1 + x)*p + (be - m)*x*p + x*(1 + x)*deriv(p, x)));
  Wp = matdet(M);
  if (Wp == 0, return([0]));
  v0 = valuation(Wp, x); Wp = Wp / x^v0;
  v1 = 0; while (subst(Wp, x, -1) == 0, Wp = Wp / (1 + x); v1++);
  Wp;
}
\\ Arithmetic of W_k (cycle bmd-20260930-zzn): p-adic Newton polygon slopes and factorization degree patterns
\\ modulo small primes, for the known sizes; W_k is written to OUTDIR/W_e_l.gp.  Enabled by env ARITH=1.
arith(e, l, W) = {
  my(dir = getenv("OUTDIR"));
  if (dir != 0 && dir != "", write(Str(dir, "/W_", e, "_", l, ".gp"), W));
  my(Wi = W * denominator(content(W)));
  Wi = Wi / content(Wi);
  print("(e,l) = ", [e, l], ": deg ", poldegree(Wi), ", leading coefficient factored ", factor(pollead(Wi), 10^5), ", constant term factored ", factor(polcoef(Wi, 0), 10^5));
  foreach([2, 3, 5, 7, 11, 13], p,
    my(np = newtonpoly(Wi, p), segs = List(), cur = np[1], len = 1);
    for (i = 2, #np, if (np[i] == cur, len++, listput(segs, [cur, len]); cur = np[i]; len = 1));
    listput(segs, [cur, len]);
    print("  Newton polygon at ", p, " (slope, length): ", Vec(segs)));
  forprime(p = 17, 97,
    if (pollead(Wi) % p == 0, print("  mod ", p, ": leading coefficient vanishes"); next);
    my(f = factormod(Wi, p), degs = vecsort(vector(#f~, i, poldegree(lift(f[i, 1])))));
    if (#degs == 1 && f[1, 2] == 1, print("  mod ", p, ": IRREDUCIBLE of degree ", degs[1]), print("  mod ", p, ": factor degrees ", degs, " multiplicities ", vector(#f~, i, f[i, 2]))));
}
{ if (getenv("ARITH") == "1",
  foreach(if (getenv("SMALL") == "1", [[1,1],[1,2],[2,1]], [[1,1],[1,2],[2,1],[2,2]]), el, arith(el[1], el[2], farW(el[1], el[2])));
  quit); }
{
  foreach([[1,1],[1,2],[2,1],[2,2],[1,3],[3,1]], el,
    my(e = el[1], l = el[2], W = farW(e, l), cnt = 4*l*(2*e^2 + 6*e*l - 5*e - 4*l + 5));
    if (W == [0], print("(e,l) = ", el, ": Wronskian zero"); next);
    my(fa = factor(W));
    print("(e,l) = ", el, ": deg W_k ", poldegree(W), " (#F_k ", cnt, "), squarefree ", poldegree(gcd(W, W')) == 0,
      ", factor degrees ", vector(#fa~, i, [poldegree(fa[i,1]), fa[i,2]]),
      ", real roots ", polsturm(W), " (in (-1,0): ", polsturm(W, [-1, 0]), ", below -1: ", polsturm(W, [-oo, -1]), ", above 0: ", polsturm(W, [0, oo]), ")"));
}
