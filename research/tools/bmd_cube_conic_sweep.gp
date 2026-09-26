\\ Sweep of n = 2 degree vectors through the conic duality theorem (bmd-r135 route review).
\\
\\ Statement tested.  conj:cube-monotone-squarefree for n = 2: for every monotone nu (nu_00 >= nu_10, nu_01 >= nu_11,
\\ nu_00 >= nu_01, nu_10 >= nu_11), the part of Delta_nu prime to the collision forms is squarefree.  By
\\ thm:cube-conic-duality this holds iff the Wronskian W(S_nu) of the dual binomial series has only simple zeros off
\\ mu in {0, oo, +-1, +-i}.  For every nu in {-1..EMAX}^4 with N = sum(nu_r + 1) >= 2 the script computes W(S_nu),
\\ removes the powers of mu, mu - 1, mu + 1, mu^2 + 1, tests the rest for squarefreeness (gcd with its derivative), and
\\ tallies monotone and non-monotone vectors separately, printing every failure.
\\ Usage: a driver file setting EMAX=...; then read("research/tools/bmd_cube_conic_sweep.gp"); quit;
NUS = []; TRIPLEMAX = 0;
read("research/tools/bmd_cube_conic_dual.gp");
strip(P, f) = { while (P % f == 0, P = P / f); P };
{
  my(mono = [0, 0], other = [0, 0]);
  forvec(nu = vector(4, i, [-1, EMAX]),
    my(N = sum(i = 1, 4, nu[i] + 1), ismono, S, W, P, ok);
    if (N < 2, next);
    ismono = nu[1] >= nu[2] && nu[1] >= nu[3] && nu[2] >= nu[4] && nu[3] >= nu[4];
    S = dualS(nu)[2];
    if (#S == 0, next);
    W = wr(S); if (W == 0, print("zero Wronskian at ", nu); next);
    P = W / 'm^valuation(W, 'm);
    P = strip(strip(strip(P, 'm - 1), 'm + 1), 'm^2 + 1);
    ok = (poldegree(gcd(P, deriv(P, 'm))) == 0);
    if (ismono, mono[1]++; if (!ok, mono[2]++; print("MONOTONE FAILURE nu=", nu, " repeated factor ", factor(gcd(P, deriv(P, 'm)))[, 1]~)),
                other[1]++; if (!ok, other[2]++; print("non-monotone failure nu=", nu)));
  );
  print("EMAX=", EMAX, ": monotone vectors ", mono[1], ", failures ", mono[2], "; non-monotone vectors ", other[1], ", failures ", other[2]);
}
