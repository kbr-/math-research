\\ The 3x3 center leading coefficients as functions of lambda (29 September 2026; cycle bmd-20260929-zw;
\\ conj:cube-far-near-collision-bound-sharp). At the window [-4,4] the leading form (eps^38) is
\\ A1 * M1 + A2 * M2, M1 = c1^12 c2^3 d1^10 d2^5 and its mirror M2 = c1^10 c2^5 d1^12 d2^3 (A1 = +-c_{(6),(4,2)}).
\\ For each integer lambda = 1..NL, det/q^38 mod q is computed q-adically (s_i = c_i q^i, t_j = d_j q^j, q = 1000003,
\\ truncation K = 60 > 38) at two constant sets, A1 and A2 are solved mod q, and a third set checks them. A1(lambda) is then
\\ interpolated over F_q and factored; roots are reported as small rationals when possible. Control: the 2x3 window
\\ [-2,3] (valuation 15, single leading monomial) treated the same way. Also single-pair windows predicted by the
\\ collision bound: 3x3 [-2,6] (val 48, monomial c1^6 c2^3 d1^18 d2^9) and 3x4 [-5,6] (val 72, pair ((9,2),(9,2)),
\\ monomial c1^17 c2^6 d1^18 d2^8 d3^3); their coefficient is L / M at one constant set, cross-checked at a second.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 1000003;
K = 60;
lead(F, n, p, v, lam, cc, dd) = {
  my(be(k) = binomial(-lam, k), L = F * n, s = vector(F, i, cc[i] * q^i), t = vector(n, j, dd[j] * q^j));
  my(ent(i, j, e) = sum(a = max(0, -e), K - max(0, e), be(a) * be(a + e) * s[i]^a * t[j]^(a + e)));
  my(A = matrix(L, L, rr, c, my(i = (rr - 1) \ n + 1, j = (rr - 1) % n + 1); ent(i, j, c - 1 - p)), x = matdet(A) / q^v);
  if (denominator(x) % q == 0, error("valuation below v"));
  Mod(numerator(x), q) / Mod(denominator(x), q);
}
ratrec(r) = {
  my(best = 0);
  for (b = 1, 6, for (a = -80, 80, if (Mod(a, q) == r * b, best = a / b; break(2))));
  if (best === 0 && r != 0, "?", best);
}
report(name, vals) = {
  my(NL = #vals, P = polinterpolate(vector(NL, i, Mod(i, q)), vals, 'x), fa = factor(P), roots = List());
  for (i = 1, #fa[, 1], my(f = fa[i, 1]); if (poldegree(f) == 1, listput(roots, [ratrec(-polcoef(f, 0) / polcoef(f, 1)), fa[i, 2]]), listput(roots, [Str("deg ", poldegree(f)), fa[i, 2]])));
  emit(Str(name, ": degree ", poldegree(P), " (from ", NL, " values); roots [value, multiplicity]: ", Vec(roots)));
}
main() = {
  my(NL = 40);
  \\ control: 2x3 window [-2,3], single leading monomial c1^5 d1^6 d2^2 (from the two-far leading-coefficient data)
  my(cvals = vector(NL, lam, lead(2, 3, 2, 15, lam, [3, -7], [2, 13, -5]) / (Mod(3, q)^5 * Mod(2, q)^6 * Mod(13, q)^2)));
  report("control 2x3 [-2,3] leading coefficient", cvals);
  my(sets = [[[3, -7, 11], [2, 13, -5]], [[5, 2, -3], [7, -4, 9]], [[-2, 9, 4], [3, 5, -6]]]);
  my(M1(cd) = Mod(cd[1][1], q)^12 * Mod(cd[1][2], q)^3 * Mod(cd[2][1], q)^10 * Mod(cd[2][2], q)^5);
  my(M2(cd) = Mod(cd[1][1], q)^10 * Mod(cd[1][2], q)^5 * Mod(cd[2][1], q)^12 * Mod(cd[2][2], q)^3);
  my(a1 = vector(NL), a2 = vector(NL), bad = 0);
  for (lam = 1, NL,
    my(Ls = vector(3, u, lead(3, 3, 4, 38, lam, sets[u][1], sets[u][2])));
    my(S = matrix(2, 2, i, j, if (j == 1, M1(sets[i]), M2(sets[i]))), sol = matsolve(S, [Ls[1]; Ls[2]]));
    a1[lam] = sol[1, 1]; a2[lam] = sol[2, 1];
    if (sol[1, 1] * M1(sets[3]) + sol[2, 1] * M2(sets[3]) != Ls[3], bad++));
  emit(Str("3x3 [-4,4]: two-monomial form inconsistent at ", bad, " of ", NL, " lambda values"));
  report("3x3 [-4,4] A1 = +-c_{(6),(4,2)}", a1);
  report("3x3 [-4,4] A2 = +-c_{(4,2),(6)}", a2);
  my(single(F, n, p, v, ex, name, NL) = my(c1 = [3, -7, 11], d1 = [2, 13, -5, 7], c2 = [5, 2, -3], d2 = [7, -4, 9, 3], okc = 1, vals = vector(NL));
    my(mon(c, d) = prod(i = 1, F, Mod(c[i], q)^ex[1][i]) * prod(j = 1, n, Mod(d[j], q)^ex[2][j]));
    for (lam = 1, NL, my(u = lead(F, n, p, v, lam, c1[1 .. F], d1[1 .. n]) / mon(c1, d1), w = lead(F, n, p, v, lam, c2[1 .. F], d2[1 .. n]) / mon(c2, d2)); vals[lam] = u; if (u != w, okc = 0));
    emit(Str(name, ": single monomial confirmed at a second constant set: ", okc)); report(name, vals));
  single(3, 3, 2, 48, [[6, 3, 0], [18, 9, 0]], "3x3 [-2,6] leading coefficient", NL);
  single(3, 4, 5, 72, [[17, 6, 0], [18, 8, 3, 0]], "3x4 [-5,6] leading coefficient (80 values)", 80);
}
main();
