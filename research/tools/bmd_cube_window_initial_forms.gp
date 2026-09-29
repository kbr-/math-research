\\ Initial forms of window Pluecker coordinates of a product of two clusters, by evaluation (29 September 2026;
\\ cycle bmd-20260929-za). Rows (1 + h s_i/S)^(-3/2)(1 + h t_j S)^(-3/2), i <= F, j <= n, at random integer
\\ points (s, t) with one symbolic scale h. For each consecutive window [-p, q] of length F n, the lowest
\\ h-coefficient of the window minor is the initial form (lowest total degree part) evaluated at (s, t).
\\ Tested statement (conj:cube-window-initial-forms): the initial form is C * Vand(s)^A * Vand(t)^B for
\\ exponents A, B >= 0 depending on (F, n, p). The script finds, for each window, the lowest degree v and
\\ all pairs (A, B) with A binom(F,2) + B binom(n,2) = v for which the ratio is the same at six points.
\\ The symbolic version of this computation timed out at 600 s for 2 x 3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(n) = binomial(-3/2, n);
ent(s, t, ee, D) = sum(a = max(0, -ee), D, my(b = a + ee); if (a + b > D, 0, be(a) * be(b) * (h * s)^a * (h * t)^b));
vand(v) = prod(i = 1, #v, prod(j = i + 1, #v, v[j] - v[i]));
initial(F, n, p, sv, tv, D) = {
  my(A = matrix(F * n, F * n, r, c, my(i = (r - 1) \ n + 1, j = (r - 1) % n + 1); ent(sv[i], tv[j], c - 1 - p, D)));
  my(d = matdet(A), v = valuation(d, h)); [v, polcoef(d, v, h)];
}
run(F, n, D) = {
  setrand(F * 100 + n);
  my(pts = vector(6, k, [vector(F, i, random(200) - 100), vector(n, j, random(200) - 100)]));
  for (p = F - 1, F * n - n,
    my(vals = vector(6, k, initial(F, n, p, pts[k][1], pts[k][2], D)), v = vals[1][1], fits = List());
    if (#Set(vector(6, k, vals[k][1])) > 1, emit(Str(F, "x", n, " p=", p, ": lowest degree varies between points")); next);
    for (A = 0, v, my(rest = v - A * binomial(F, 2), Bn = binomial(n, 2));
      if (rest < 0, break);
      if ((Bn == 0 && rest == 0) || (Bn > 0 && rest % Bn == 0),
        my(B = if (Bn, rest / Bn, 0), r = vector(6, k, vals[k][2] / (vand(pts[k][1])^A * vand(pts[k][2])^B)));
        if (#Set(r) == 1, listput(fits, [A, B, r[1]]))));
    emit(Str(F, "x", n, " window [", -p, ",", F * n - 1 - p, "]: lowest degree ", v, "; fitting [A, B, C]: ", Vec(fits))));
}
run(2, 2, 8);
run(2, 3, 12);
run(3, 2, 12);
