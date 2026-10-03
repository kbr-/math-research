\\ Asymptotic phase of the reduced triple window (cycle bmd-20261009-cf, 9 October 2026).
\\ Claim tested (prop:cube-triple-window-phase): with u_ij = 1 - a_j/a_i and principal branches, the Darboux leading
\\ coefficients of the filtered rows are alpha = (u12^-lam u13^m, u21^-lam u23^m) on (E1, E2) for row (12), beta =
\\ (u13^-lam u12^m, u31^-lam u32^m) on (E1, E3) for row (13), gamma = (u23^-lam u21^m, u32^-lam u31^m) on (E2, E3) for row
\\ (23); the 3 x 3 determinant is -(a1 b3 g2 + a2 b1 g3), and the ratio (a1 b3 g2)/(a2 b1 g3) = Q^(m+lam) up to branch
\\ signs, with Q = u13 u32 u21 / (u12 u31 u23) = -1 identically. So the ratio is +-i for lam = 3/2 and the determinant
\\ never vanishes. Implemented: (1) exact identity Q = -1 symbolically; (2) the ratio with principal branches at random
\\ complex points, m = 2..12. No comparison with the actual U_3 is made here (see bmd_triple_window_torus_test.gp).
OUT = "research/results/bmd-20261009-cf/triple-window-phase.txt";
default(realprecision, 60);
lam = 3/2;
{
  my(Q = (1 - 'a3/'a1) * (1 - 'a2/'a3) * (1 - 'a1/'a2) / ((1 - 'a2/'a1) * (1 - 'a1/'a3) * (1 - 'a3/'a2)));
  write(OUT, "(1) Q simplifies to: ", simplify(Q));
  setrand(11);
  for (t = 1, 4, my(a = vector(3, i, random(1.) * 4 - 2 + I * (random(1.) * 4 - 2)), u(i, j) = 1 - a[j] / a[i], rs = List());
    for (m = 2, 12,
      my(al1 = u(1,2)^-lam * u(1,3)^m, al2 = u(2,1)^-lam * u(2,3)^m, b1 = u(1,3)^-lam * u(1,2)^m, b3 = u(3,1)^-lam * u(3,2)^m,
         g2 = u(2,3)^-lam * u(2,1)^m, g3 = u(3,2)^-lam * u(3,1)^m);
      listput(rs, al1 * b3 * g2 / (al2 * b1 * g3)));
    write(OUT, "(2) point ", t, ": ratio values for m = 2..12 (should be +-i): ", apply(z -> round(z * 10^6) / 10^6, Vec(rs))));
}
