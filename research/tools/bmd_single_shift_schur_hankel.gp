\\ Jacobi-Trudi lead entry two (cycle ket, 9 October 2026): exact check of the single-shift Schur-Hankel formula.
\\ Set L_t = {-p..-1} u {0..N-2} u {N-1+t} (the window with its top column raised by t; t = 1 is the top-up), N = 2M-p,
\\ k = M-p.  Prediction: the least coefficient (x^(A_p+t) eps^(B_p)) divided by the window's (x^(A_p) eps^(B_p)) is
\\   (c_(N-1+t)/c_(N-1)) * N * sum_(b<=t) alpha_b H_b / Hank_k,   alpha_b = sum_(s=b..t) h_(t-s)(y) V[b,s],
\\ V = U^-1, U the (t+1)x(t+1) upper triangular matrix with U[r,r] = N+r, U[r,q] = p_(q-r) (power sums of all y),
\\ H_b = sum_(|S|=k+1) Vand(y_S)^2 h_b(y_S), h_j complete homogeneous.  Exact rationals at two random integer clusters,
\\ M = 3, 4, every p, t = 1, 2, 3 (t = 1 reproduces thm:cube-topup-flow-identity-all).  Conventions of
\\ bmd_topup_identity_large.gp.
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
hcomp(Y, j) = if (j == 0, 1, my(s = 0); forvec(e = vector(#Y, i, [0, j]), if (vecsum(e) == j, s += prod(i = 1, #Y, Y[i]^e[i]))); s);
Hb(Y, k, b) = { my(s = 0); forsubset([#Y, k + 1], S, my(Z = vector(k + 1, i, Y[S[i]])); s += vand(Z)^2 * hcomp(Z, b)); s; }
{
  setrand(20261009);
  my(bad = 0, tot = 0);
  for (M = 3, 4, my(pts = vector(2, j, vector(M, i, random(30) - 15 + 31 * i)));
    for (p = 1, M - 1, my(N = 2 * M - p, k = M - p, A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M);
      foreach(pts, Y, my(pw(a) = sum(i = 1, M, Y[i]^a), base = concat(vector(p, i, -p - 1 + i), [0 .. N - 2]));
        my(W = coefat(Y, concat(base, [N - 1]), A, B));
        for (t = 1, 3, tot++;
          my(T = coefat(Y, concat(base, [N - 1 + t]), A + t, B));
          my(U = matrix(t + 1, t + 1, r, q, if (q == r, N + r - 1, if (q > r, pw(q - r), 0))), V = U^-1);
          my(pred = cc(N - 1 + t) / cc(N - 1) * N * sum(b = 0, t, sum(s = b, t, hcomp(Y, t - s) * V[b + 1, s + 1]) * Hb(Y, k, b)) / Hb(Y, k, 0));
          my(r = T / W);
          if (r != pred, bad++; emit(Str("M=", M, " p=", p, " t=", t, ": ratio ", r, " predicted ", pred, " quotient ", r / pred)))))));
  emit(Str("single-shift formula: ", tot - bad, " of ", tot, " exact comparisons agree (M = 3, 4; every p; t = 1, 2, 3; two clusters)"));
}
quit;
