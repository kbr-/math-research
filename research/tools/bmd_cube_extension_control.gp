\\ Control for bmd_cube_component_extension.gp (29 September 2026; cycle bmd-20260929-zz): the extensions of
\\ <1, S(1+S)> in class S^-l phi, l = -3/2 (the Remark of the Bethe extension entry). Prints each target [i,j], the
\\ coefficients x_k of L (k = -6..6) and the factored combination.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wdet(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  matdet(P);
}
l = -3/2; V = [[[S, 0]], [[S, 1], [S + 1, 1]]]; K = 6; w = [[S, l], [1 + S, l]];
ds = vector(2 * K + 1, t, my(k = t - K - 1); S^k * wdet(concat(V, [concat([[S, k]], w)])));
D = lcm(apply(denominator, ds)); P = apply(d -> d * D, ds);
mx = vecmax(apply(poldegree, P)); M = Mat(apply(p -> Colrev(p, mx + 1), P));
for (tot = 0, mx, for (i = 0, tot, my(j = tot - i, t = Colrev(S^j * (1 + S)^i, mx + 1)); if (matrank(concat(M, t)) == matrank(M), x = matsolve(M~ * M, M~ * t); emit(Str([i, j], " x=", x~)); emit(Str("check combination: ", factor(sum(k = 1, #P, x[k] * P[k])))))));
\\ Direct check of the target [2,8] (x indexed by k = -6..6): L = -S^2 (1+S)^2 (1+2S), so g = -S^(1/2) (1+S)^(1/2) (1+2S).
wr(fl) = factor(numerator(wdet(fl)));
emit(Str("direct: Wr(1, S(1+S), S^(1/2)(1+S)^(1/2)(1+2S)) / prod f has numerator ", wr(concat(V, [[[S, 1/2], [1 + S, 1/2], [1 + 2*S, 1]]]))));
emit(Str("direct: Wr(1, S(1+S), S^(-1/2)(1+S)^(1/2)(1+2S)) / prod f has numerator ", wr(concat(V, [[[S, -1/2], [1 + S, 1/2], [1 + 2*S, 1]]])), " (not an extension)"));
