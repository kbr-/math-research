\\ Torsion test of the elliptic bridge for the triple window (cycle bmd-20261009-ch, 9 October 2026).
\\ Hypothesis tested: on a fixed curve C: Y^2 = (1+c1 T)(1+c2 T)(1+T) (fixed cross-ratio lambda of the branch points
\\ -1/c1, -1/c2, -1, infinity, i.e. on the conic c2 = lambda c1 / (lambda c1 - c1 + 1)), the zeros of a single maximal
\\ minor D_S of U_3 (lem:cube-level-window-gegenbauer-form; same normalization as bmd_triple_window_export.gp) put the
\\ point P0 = (T = 0, Y = 1) at torsion points of C, relative to the origin at T = infinity. For m = 2, 3, S = {1,2,3} and
\\ {3,4,5}, lambda = 3 and 2 + i: solve D_S = 0 on the conic, discard roots on the excluded locus, map P0 to C/Lambda by
\\ ellpointtoz on the Weierstrass model Y'^2 = X^3 + b X^2 + c k X + k^2 (k = c1 c2, T = X/k, Y = Y'/k), write z = u w1 + v w2,
\\ and report the least n <= 60 with n (u, v) in Z^2 (to 1e-30), or 0; also the number of pairs of zeros whose elliptic
\\ logarithms differ or sum to a torsion class of order <= 60 (a coset B + E[n] would show up there).
OUT = "research/results/bmd-20261009-ch/triple-window-torsion-test.txt";
default(realprecision, 120);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
cc(n) = binomial(-lam, n);
U3sym(m) = {
  my(a = ['x, 'y, 1], d = m * (m - 1) / 2, N0 = d + m, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  for (r = 1, 3, my([i, j, k] = prs[r], top = N0 + 4);
    my(e = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
    for (col = 1, 5, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rq(-m, n - l) * e[n - l + 1], 0))));
  U;
}
torsorder(c1, c2) = {
  my(k = c1 * c2, b = c1 * c2 + c1 + c2, c = c1 + c2 + 1);
  \\ (1+c1 T)(1+c2 T)(1+T) = k T^3 + b T^2 + c T + 1
  my(E = ellinit([0, b, 0, c * k, k^2]), z = ellpointtoz(E, [0, k]), w = E.omega);
  my(M = [real(w[1]), real(w[2]); imag(w[1]), imag(w[2])], uv = matsolve(M, [real(z), imag(z)]~));
  uv;
}
tord(uv) = { for (n = 1, 60, my(t = n * uv); if (abs(t[1] - round(t[1])) < 1e-30 && abs(t[2] - round(t[2])) < 1e-30, return(n))); 0; }
\\ positive control: on the same model, the 2-torsion point T = -1 (X = -k, Y' = 0) and a 3-torsion point from elldivpol
torsctl(c1, c2) = {
  my(k = c1 * c2, b = c1 * c2 + c1 + c2, c = c1 + c2 + 1, E = ellinit([0, b, 0, c * k, k^2]), w = E.omega);
  my(M = [real(w[1]), real(w[2]); imag(w[1]), imag(w[2])], ord(P) = my(z = ellpointtoz(E, P), uv = matsolve(M, [real(z), imag(z)]~));
    for (n = 1, 60, my(t = n * uv); if (abs(t[1] - round(t[1])) < 1e-30 && abs(t[2] - round(t[2])) < 1e-30, return(n))); 0);
  my(x3 = polroots(elldivpol(E, 3))[1], P3 = [x3, ellordinate(E, x3)[1]]);
  [ord([-k, 0]), ord(P3)];
}
{
  write(OUT, "control (c1, c2) = (2/7, -5/3): orders of the 2-torsion point and a 3-torsion point: ", torsctl(2/7, -5/3));
  foreach([2, 3], m, my(U = U3sym(m));
    foreach([[1, 2, 3], [3, 4, 5]], S, my(D = matdet(matrix(3, 3, r, t, U[r, S[t]])));
      foreach([3, 2 + I], L,
        my(c2 = L * 'x / (L * 'x - 'x + 1), num = numerator(subst(D, 'y, c2)), rts = polroots(num), res = List());
        foreach(rts, c1,
          my(cc2 = subst(c2, 'x, c1));
          if (abs(c1) < 1e-20 || abs(c1 - 1) < 1e-20 || abs(cc2) < 1e-20 || abs(cc2 - 1) < 1e-20 || abs(c1 - cc2) < 1e-20
              || abs(L * c1 - c1 + 1) < 1e-20, next);
          listput(res, torsorder(c1, cc2)));
        \\ pairwise sums and differences (the lattice basis is canonical up to sign at generic j)
        my(np = 0);
        for (i = 1, #res, for (j = i + 1, #res, if (tord(res[i] - res[j]) || tord(res[i] + res[j]), np++)));
        write(OUT, "m = ", m, ", S = ", S, ", lambda = ", L, ": deg ", poldegree(num), ", admissible roots ", #res,
          ", torsion orders ", apply(tord, Vec(res)), ", torsion pairs (sum or difference, order <= 60) ", np))));
}
