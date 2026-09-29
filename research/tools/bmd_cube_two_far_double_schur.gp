\\ Exact double Schur coefficients of two-far windows with both far roots live (29 September 2026;
\\ cycle bmd-20260929-zp; lem:cube-far-near-double-schur-reduction, conj:cube-two-far-leading-monomial).
\\ Rows (i, j), i = 1, 2, j = 1..n: coefficient of S^e in (1+s_i/S)^(-3/2)(1+t_j S)^(-3/2). By Cauchy-Binet over one
\\ exponent pair (a_e, a_e + e) per column, P_E = sum over selections of prod_e beta_(a_e) beta_(a_e+e) times the grid
\\ determinant det[s_i^(a_e) t_j^(a_e+e)], homogeneous of degree sum_e (2 a_e + e); all selections up to degree D give
\\ P_E exactly up to degree D. Then Q = P_E / (Delta(s)^n Delta(t)^2), and c_(kappa,nu) is the coefficient of
\\ s^(kappa+delta_2) t^(nu+delta_n) in Q Delta(s) Delta(t).
\\ Tested: at weights s = (1, 2), t = (1..n), the least weight in the support is attained by one pair only, namely
\\ (kappa*, nu*) = (((n-1-r)(n-r)), (2r, ..., 2)), which gives the leading monomial s_1^(n+(n-1-r)(n-r)) prod t_j^(2(n-j)+2(r+1-j)_+)
\\ of conj:cube-two-far-leading-monomial, with no s_2. Computes and prints the support up to weight w_min + slack
\\ (slack 4 at n = 3, 3 at n = 4).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(k) = if (k < 0, 0, binomial(-3/2, k));
S = [s1, s2];
gridP = 0; gE = []; gn = 0; gT = []; gsel = [];
rec(idx, budget) = {
  if (idx > #gE,
    my(L = #gE, M = matrix(L, L, r, c, my(i = (r - 1) \ gn + 1, j = (r - 1) % gn + 1); S[i]^gsel[c] * gT[j]^(gsel[c] + gE[c])));
    my(w = prod(c = 1, L, be(gsel[c]) * be(gsel[c] + gE[c])));
    gridP += w * matdet(M); return);
  my(e = gE[idx], a0 = max(0, -e));
  for (a = a0, a0 + budget, gsel[idx] = a; rec(idx + 1, budget - (a - a0)));
}
run(n, r, slack) = {
  my(m = n - r, E = [-m .. n - 1 + r], L = 2 * n, T = vector(n, j, eval(Str("t", j))));
  my(v0 = n^2 + 2 * binomial(n + 1, 3) - 2 * n * r + r * (r + 1) * (r + 5) / 3, vd = n * 1 + 2 * binomial(n + 1, 3), wmin = v0 - vd);
  my(dD = n * 1 + 2 * binomial(n, 2), D = wmin + slack + dD, SE = vecsum(E), amin = sum(c = 1, L, max(0, -E[c])));
  my(budget = (D - SE) \ 2 - amin);
  gE = E; gn = n; gT = T; gsel = vector(L); gridP = 0;
  rec(1, budget);
  my(Ds = s1 - s2, Dt = prod(i = 1, n, prod(j = i + 1, n, T[i] - T[j])), Q = gridP / (Ds^n * Dt^2));
  if (type(Q) != "t_POL" && type(Q) != "t_INT" && type(Q) != "t_FRAC", error("not divisible"));
  my(A = Q * Ds * Dt, res = List());
  my(dn = vector(n, j, n - j));
  for (ks = 0, wmin + slack, forpart(kp = ks, my(ka = vector(2)); for (i = 1, #kp, ka[i] = kp[#kp + 1 - i]);
    for (ns = 0, wmin + slack - ks, forpart(np = ns, my(nu = vector(n)); for (i = 1, #np, nu[i] = np[#np + 1 - i]);
      my(w = ka[1] + 2 * ka[2] + sum(j = 1, n, j * nu[j])); if (w <= wmin + slack,
      my(co = polcoef(polcoef(A, ka[1] + 1, s1), ka[2], s2)); for (j = 1, n, co = polcoef(co, nu[j] + dn[j], T[j]));
      if (co != 0, listput(res, [w, ka, nu, co]))), , [0, n])), , [0, 2]));
  res = vecsort(Vec(res), 1);
  my(mw = if (#res, res[1][1], oo), atm = select(z -> z[1] == mw, res));
  emit(Str("2x", n, " r=", r, " window ", [E[1], E[L]], ": predicted least weight ", wmin, "; found ", mw, " at ", apply(z -> [z[2], z[3]], atm)));
  for (i = 1, #res, if (res[i][1] <= mw + 4, emit(Str("    w=", res[i][1], " kappa=", res[i][2], " nu=", res[i][3], " c=", res[i][4]))));
}
main() = { for (r = 0, 2, run(3, r, 4)); for (r = 0, 3, run(4, r, 3)); }
main();
