\\ Top-up least coefficient (cycle bmd-20261009-at, 9 October 2026); conventions of bmd_bottom_shift_proportionality.gp.
\\ For M = 3, 4 and 1 <= p <= M - 1, the top-up T_p = [-p, 2M-2-p] u {2M-p} has least term x^(A_p + 1) eps^(B_p);
\\ tau_p = (its coefficient) / Vand(y)^2 as a symmetric polynomial in symbolic roots y. Reported: tau_p in power sums
\\ (via its values), whether Hank_(M-p) divides it, and the common zeros of tau_p and Hank_(M-p) on the test clusters
\\ (equilateral, square) and by a resultant in the normalized coordinates (0, 1, a[, b]).
OUT = "research/results/bmd-20261009-at/topup.txt";
default(parisizemax, 4 * 10^9);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * (x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * eps^r * (x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, eps), A, x);
}
hank(Y, k) = { my(M = #Y, s = 0); forsubset([M, k + 1], S, my(v = prod(i = 1, k + 1, prod(j = i + 1, k + 1, Y[S[j]] - Y[S[i]]))); s += v^2); s; }
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
{
  for (M = 3, 4,
    my(ys = vector(M, i, eval(Str("y", i))));
    for (p = 1, M - 1,
      my(A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M, plus = concat([0 .. 2*M - 2 - p], [2*M - p]));
      my(L = concat(vector(p, i, -p - 1 + i), plus), W = concat(vector(p, i, -p - 1 + i), [0 .. 2*M - 1 - p]));
      my(tau = coefat(ys, L, A + 1, B) / vand(ys)^2, win = coefat(ys, W, A, B) / vand(ys)^2, H = hank(ys, M - p));
      my(r = win / H, quot = tau / H);
      write(OUT, "M = ", M, ", p = ", p, ": window / Hank_", M - p, " = ", r, "; tau_p total degree ", poldegree(substvec(tau, ys, vector(M, i, 't * ys[i])), 't),
            "; Hank divides tau: ", type(quot) == "t_POL" || type(quot) == "t_INT" || type(quot) == "t_FRAC" && denominator(quot) == 1);
      \\ fit tau = a e1 Hank + b D(Hank), D = sum y_i^2 d/dy_i, from four random points, then test exactly
      my(e1 = sum(i = 1, M, ys[i]), DH = sum(i = 1, M, ys[i]^2 * deriv(H, ys[i])), vars = [e1 * H, DH]);
      my(pts = vector(4, k, vector(M, i, random(50) + 1)), ev(f, P) = substvec(f, ys, P));
      my(Mx = matrix(4, 2, k, j, ev(vars[j], pts[k])), rhs = vector(4, k, ev(tau, pts[k]))~, sl = matinverseimage(Mx, rhs));
      my(fits = #sl && tau == sl[1] * vars[1] + sl[2] * vars[2]);
      write(OUT, "     tau_p = a e1 Hank + b D(Hank)? ", fits, if (fits, Str(" with (a, b) = ", sl~), ""));
      my(w3 = Mod(z, z^2 + z + 1), sq = [1, I, -1, -I]);
      if (M == 3, write(OUT, "     at the equilateral point: tau = ", substvec(tau, ys, [1, w3, w3^2]), ", Hank = ", substvec(H, ys, [1, w3, w3^2])));
      if (M == 4, write(OUT, "     at the square: tau = ", substvec(tau, ys, sq), ", Hank = ", substvec(H, ys, sq), ", D(Hank) = ", substvec(DH, ys, sq)))));
}
