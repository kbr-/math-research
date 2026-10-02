\\ Coalescence order of the cherry cross coordinates (8 October 2026; cycle bmd-20261008-zm), lambda = 3/2.
\\ Tested statement (proposed mechanism for conj:cube-tie-cluster-penalty-sharing in regime p = 1): for every coordinate
\\ set Lambda with exactly one negative index, every coefficient of eps^n in the cross Pluecker coordinate P_Lambda of
\\ rows V_s = (1+beta_s w)^(-lambda), Q_s = (U_eps - 1) V_s (thm:cube-cherry-lattice-splitting) is divisible by
\\ (beta_1 - beta_2)^4 (M = 2), resp. by Vand(beta)^4 (M = 3).  Prints, per p and per eps-order, the least
\\ multiplicity of (beta_1 - beta_2) over the sets Lambda in the column range, and for p = 0, 2 as controls.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
cc(n) = binomial(-3/2, n);
NE = 4;   \\ eps-orders above the least one
rows(M, T0, T1) = {
  my(nc = T1 - T0 + 1, P = matrix(2 * M, nc), bs = vector(M, s, eval(Str("b", s))));
  for (s = 1, M, for (j = 1, nc, my(t = T0 + j - 1);
    if (t >= 0, P[s, j] = cc(t) * bs[s]^t);
    P[M + s, j] = sum(m = max(1, -t), max(1, -t) + M + NE + 2, cc(m) * 'ep^m * cc(t + m) * bs[s]^(t + m))));
  P;
}
mult(f, M) = { my(m = 0, g = subst(f, b2, b1 + 'hh)); while (polcoef(g, 0, 'hh) == 0 && g != 0, g = g / 'hh; m++); if (g == 0, oo, m); }
record(key, mu) = { my(old); if (mapisdefined(RES, key, &old), mapput(RES, key, min(old, mu)), mapput(RES, key, mu)); }
onecoord(D, p) = {
  my(lo = valuation(D, 'ep));
  for (n = lo, lo + NE, my(cf = polcoef(D, n, 'ep)); if (cf != 0, record([p, n - lo], mult(cf, 2))));
}
run(M, T0, T1) = {
  my(P = rows(M, T0, T1), nc = T1 - T0 + 1); RES = Map();
  forsubset([nc, 2 * M], S,
    my(L = apply(j -> T0 + j - 1, Vec(S)), p = #select(t -> t < 0, L), D);
    if (p <= M, D = matdet(vecextract(P, "..", Vec(S))); if (D != 0, onecoord(D, p))));
  my(K = Mat(RES)); for (i = 1, matsize(K)[1],
    emit(Str("M = ", M, ", columns [", T0, ", ", T1, "]: p = ", K[i, 1][1], ", eps-order least+", K[i, 1][2], ": least multiplicity of (b1 - b2) = ", K[i, 2])));
}
{
  run(2, -2, 5);
}
quit
