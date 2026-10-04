\\ NOTE (cycle kev): the coefficients this script prints are invalid. Its polmod (Q(zeta_M)) evaluation of coefat
\\ returned 0 for L_11 at the square, where exact Gaussian arithmetic (bmd_square_gaussian_check.gp) gives 64 a != 0.
\\ The H_mu values, computed without coefat, are correct. Output kept as square-two-column-polmod-invalid.txt.
\\ Jacobi-Trudi lead entry four (cycle kev, 9 October 2026): raises of two at regular polygons in Omega_k.
\\ For the M-th roots of unity (exact, Q(zeta_M)), every p with 2 <= k = M-p <= M-2 (so the polygon is in Omega_k by
\\ thm:cube-schur-hankel-termination), N = 2M-p, compute the least coefficients (x^(A_p+2) eps^(B_p)) of
\\   L_2  = window with its top column raised by 2: {-p..-1} u {0..N-2} u {N+1}
\\   L_11 = window with its top two columns raised by 1: {-p..-1} u {0..N-3} u {N-1, N}
\\ and the Schur-Hankel sums H_mu = sum_(|S|=k+1) Vand(y_S)^2 s_mu(y_S) for mu = (2), (1,1).
\\ Prediction: L_2 vanishes (all H_(b) vanish on Omega_k); L_11 is nonzero exactly when H_(1,1) is.
\\ Conventions of bmd_topup_identity_large.gp (lambda = 3/2).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2 * 10^9);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * ('x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * 'eps^r * ('x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, 'eps), A, 'x);
}
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
e2(Z) = sum(i = 1, #Z, sum(j = i + 1, #Z, Z[i] * Z[j]));
h2(Z) = sum(i = 1, #Z, sum(j = i, #Z, Z[i] * Z[j]));
HS(Y, k, f) = { my(s = 0); forsubset([#Y, k + 1], S, my(Z = vector(k + 1, i, Y[S[i]])); s += vand(Z)^2 * f(Z)); s; }
{
  for (M = 4, 6, my(Y = vector(M, j, Mod('w, polcyclo(M, 'w))^(j - 1)));
    for (p = 2, M - 2, my(k = M - p, N = 2 * M - p, A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M, neg = vector(p, i, -p - 1 + i));
      my(c2 = coefat(Y, concat(concat(neg, [0 .. N - 2]), [N + 1]), A + 2, B));
      my(c11 = coefat(Y, concat(concat(neg, [0 .. N - 3]), [N - 1, N]), A + 2, B));
      my(H2 = HS(Y, k, h2), H11 = HS(Y, k, e2));
      emit(Str("M=", M, " p=", p, " k=", k, ": L_2 coefficient ", lift(c2), "; L_11 coefficient ", lift(c11), "; H_(2) = ", lift(H2), "; H_(1,1) = ", lift(H11),
        "; ratio L_11/H_(1,1) = ", if (H11 != 0, lift(c11 / H11), "n/a")))));
}
quit;
