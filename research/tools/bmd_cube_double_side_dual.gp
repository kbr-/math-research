\\ The double-double sides of the limit determinant Delta_U through the conic duality (bmd-r137).
\\
\\ Statement checked.  Along the side a1 = a3 of the a-plane (points (1 : x : 1)), the flat limit of the transported
\\ space is, on the rigid conic (mu-coordinate of thm:cube-conic-duality, w~3 <-> mu - 1/mu, w~2 <-> mu + 1/mu),
\\     L_d = F[Th]_{<=2d-1} + w~3 F[Th]_{<=2d-1} + w~2 w~3^2 F[Th]_{<=2d-3} + w~2 w~3 F[Th]_{<=2d-3},
\\ of dimension 8d - 4, with c = 4d - 1.  Its apolar dual in Poly_{8d-2} is the 3-dimensional series
\\     S~_d = < mu - mu^(8d-3),  1 + mu^(8d-2),  (mu + 1)^(8d-2) + (mu - 1)^(8d-2) >,
\\ and the non-collision factor G_d of the leading eps-coefficient of Delta_U(1 + eps, x, 1) should be the image of
\\ the zeros of W(S~_d) off {0, oo, +-1, +-i} under x = 1 - ((mu^2 - 1)/(mu^2 + 1))^2.  For each d in DS the script
\\ prints the factors of W(S~_d), their image in x, and (for d in GS) the exact factorization of the leading
\\ coefficient from bmd_cube_limit_sides.gp, so the two can be compared.  For d in 2..QMAX it prints, for the
\\ non-special part of W(S~_d), its degree, whether it is squarefree, and its value at the special points.
\\ Usage: a driver file setting DS=[...]; GS=[...]; QMAX=...; then read(this file); quit;  run with gp -s 2000000000.
DS0 = DS; DS = [];
read("research/tools/bmd_cube_limit_sides.gp");
DS = DS0;
dk(p, k) = { my(q = p); for (t = 1, k, q = deriv(q, 'm)); q };
wr(v) = { my(s = #v); matdet(matrix(s, s, i, j, dk(v[j], i - 1))) };
dualDD(d) = { my(N = 8*d - 2); ['m - 'm^(N - 1), 1 + 'm^N, ('m + 1)^N + ('m - 1)^N] };
\\ strip the special factors mu, mu^2 - 1, mu^2 + 1
nonspecial(W) = {
  my(P = W / 'm^valuation(W, 'm));
  foreach([('m - 1), ('m + 1), ('m^2 + 1)], f, while (P % f == 0, P = P / f));
  P;
}
{
  for (t = 1, #DS, my(d = DS[t], W, P, R, F);
    W = wr(dualDD(d)); P = nonspecial(W); F = factor(W);
    print("d=", d, " W(S~) degree ", poldegree(W), ", factors ", F[, 1]~, " mult ", F[, 2]~);
    R = factor(polresultant(P, ('m^2 + 1)^2 * (1 - 'x) - ('m^2 - 1)^2, 'm));
    print("   image x = 1 - ((m^2-1)/(m^2+1))^2 of the non-special zeros: ", R[, 1]~, " mult ", R[, 2]~));
  for (t = 1, #GS, my(d = GS[t], L);
    L = lead(deltaU(d, [1 + 'e, 'x, 1]));
    print("d=", d, " leading coefficient on a = (1+eps, x, 1): eps-valuation ", L[1], ", factors ", factor(L[2])));
  for (d = 2, QMAX, my(W = wr(dualDD(d)), P = nonspecial(W));
    \\ closed form: W = N(N-1) [ M m^(M-1) (1+m^2) ((m-1)^M - (m+1)^M) - (m^M - 1)^2 ((m-1)^M + (m+1)^M) ], M = N - 2
    my(N = 8*d - 2, M = N - 2, CF);
    CF = N*(N-1) * (M*'m^(M-1)*(1 + 'm^2)*(('m - 1)^M - ('m + 1)^M) - ('m^M - 1)^2*(('m - 1)^M + ('m + 1)^M));
    if (W != CF, error("closed form fails at d=", d));
    print("QMAX d=", d, ": closed form holds; special orders at 0,1,-1,i: ", [valuation(W, 'm), valuation(W, 'm - 1), valuation(W, 'm + 1),
          valuation(W, 'm^2 + 1)], ", deg W = ", poldegree(W), ", deg nonspecial = ", poldegree(P),
          ", squarefree: ", poldisc(P) != 0));
}
