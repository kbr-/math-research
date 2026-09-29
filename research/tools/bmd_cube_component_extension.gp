\\ Master-function lead for component simplicity (29 September 2026; cycle bmd-20260929-zz).
\\ By Mukhin-Varchenko (math/0209017, Theorem 5.12 and (5.4)), the Weierstrass polynomial q of a space V is y_R for
\\ the flags through V of a space V' = V + <g>; the natural three-point form asks that V' be ramified only in the
\\ branch points {0, -1, infinity}. (Such an extension does not by itself make q squarefree; see the entry.)
\\ Tested statement: for the rigid caterpillar components (c = 1, l = 3/2)
\\   V = Pol_<P_n + phi Pol_<n + S^-3 Pol_<P_F(1/S) + S^-l phi Pol_<F(1/S) + S^-l <S^e : e in W>,
\\ there is g = w * L, with w one of the four class factors 1, phi, S^-l, S^-l phi and L a Laurent polynomial with
\\ exponents in [-K, K], such that Wr(V, g) = C S^j (1+S)^i (times the class factors), C != 0.
\\ Method: Wr(V, g) / (prod f * w) = sum_k x_k S^k d_k with d_k = Wr(V, w S^k) / (prod f * w S^k); after clearing the
\\ common denominator we ask whether span{P_k} contains S^j (1+S)^i for some i, j >= 0. Reports, per class, the
\\ dimension of span{P_k} and every (i, j) found (the least one is printed). Control: <1, S(1+S)> has Wronskian 1+2S
\\ and extends by g = S to Pol_<3, so it must reach a target in class 1.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wdet(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  matdet(P);
}
space(F, n, W) = {
  my(l = -3/2, ph = 1 + S, PF = F * (F - 1) / 2, Pn = n * (n - 1) / 2);
  concat([[[[S, k]] | k <- [0 .. Pn - 1]], [[[S, k], [ph, l]] | k <- [0 .. n - 1]], [[[S, -3 - k]] | k <- [0 .. PF - 1]],
          [[[S, l - k], [ph, l]] | k <- [0 .. F - 1]], [[[S, l + e]] | e <- W]]);
}
test(name, V, K) = {
  my(l = -3/2, cls = [[], [[1 + S, l]], [[S, l]], [[S, l], [1 + S, l]]], cname = ["1", "phi", "S^-l", "S^-l phi"]);
  emit(Str(name, ": dimension ", #V, "; Laurent range [", -K, ",", K, "]"));
  for (c = 1, 4,
    my(ds = vector(2 * K + 1, t, my(k = t - K - 1); S^k * wdet(concat(V, [concat([[S, k]], cls[c])]))));
    my(D = lcm(apply(denominator, ds)), P = apply(d -> d * D, ds));
    if (vecsum(apply(p -> denominator(p) != 1, P)), error("non-polynomial"));
    my(M = Mat(apply(p -> Colrev(p, 1 + vecmax(apply(poldegree, P))), P)), r = matrank(M), mx = #M[, 1] - 1, found = []);
    for (tot = 0, mx, for (i = 0, tot, my(j = tot - i, t = Colrev(S^j * (1 + S)^i, mx + 1)); if (matrank(concat(M, t)) == r, found = concat(found, [[i, j]]))));
    my(Dn = factor(denominator(D / 1)), Dsummary = Str(D));
    emit(Str("  class ", cname[c], ": span dimension ", r, " of ", 2 * K + 1, "; common denominator ", factor(D),
             "; monomial targets S^j(1+S)^i reached: ", #found, if (#found, Str(" (first [i,j] = ", found[1], ")"), ""))));
}
main() = {
  test("control <1, S(1+S)> (extends by g = S)", [[[S, 0]], [[S, 1], [S + 1, 1]]], 6);
  test("2x2 limit, window [-1,2]", space(2, 2, [-1 .. 2]), 30);
  test("2x2 limit, window [-2,1]", space(2, 2, [-2 .. 1]), 30);
  test("2x3, window [-2,3]", space(2, 3, [-2 .. 3]), 40);
}
main();
