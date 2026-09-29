\\ Two-double-root osculating limit (29 September 2026; cycle bmd-20260929-zzk).
\\ Tested statement (lem:cube-double-cluster-osculating-limit, case c = 2): for roots a_i = 0, a_j = mu t, a_k = 1,
\\ a_l = 1 + t and further distinct roots z, the pair row space (rows = coefficient vectors of phi(a)phi(b),
\\ phi(a) = (1 + aT)^(-3/2), columns T^0..T^M) has flat limit W0 + <mu^2 phi_0'' phi_1 + phi_0 phi_1''> at t = 0,
\\ whenever W0 (the span of the first-order rows) has dimension R - 1 and the added vector lies outside W0.
\\ First-order rows used: phi_0^2, phi_1^2, phi_0 phi_1, phi_0' phi_1, phi_0 phi_1' (phi_0' phi_1' is omitted as
\\ dependent); for each z: phi_0 phi_z, phi_0' phi_z, phi_1 phi_z, phi_1' phi_z; phi_z phi_w for pairs z, w.
\\ Part (a): exact flat limits by t-saturation over Q[t] (replace a row by (lambda . A)/t while A(0) has a left
\\ kernel vector lambda), compared with the formula; negative control: the same vector with nu = mu instead of mu^2.
\\ Part (b), N = 5 with the fifth root z symbolic: the limits over all mu form the pencil W0 + <nu U + V>, with
\\ U = phi_0'' phi_1, V = phi_0 phi_1''. Contact on the pencil at z means the projection to columns 0..R+1 of
\\ [W0; U; V] has rank at most R; printed: the gcd over z of its (R+1) x (R+1) minors, factored, and the ranks over
\\ Q(z). Part (c): at each rational root z0 of the gcd, the left kernel; where it is one-dimensional with a rational
\\ square ratio nu0, exact flat limits at mu = sqrt(nu0), with mu + 1 as control.
t; z;
c(n) = binomial(-3/2, n);
phid(a, r, M) = vector(M + 1, k, my(n = k - 1); if (n < r, 0, c(n) * n! / (n - r)! * a^(n - r)));
prodv(u, v, M) = vector(M + 1, k, sum(q = 1, k, u[q] * v[k + 1 - q]));
row(a, b, M) = prodv(phid(a, 0, M), phid(b, 0, M), M);
flat(A) =
{
  my(B = A, steps = 0);
  while (1,
    my(B0 = subst(B, t, 0), K = matker(B0~), l, r, v);
    if (#K == 0, return([B0, steps]));
    l = K[, 1]; r = 1; while (l[r] == 0, r++);
    v = l~ * B;
    if (subst(v, t, 0) != 0 * v, error("combination not divisible by t"));
    B[r, ] = v / t; steps++);
}
w0rows(zs, M) =
{
  my(p0 = phid(0, 0, M), p0d = phid(0, 1, M), p1 = phid(1, 0, M), p1d = phid(1, 1, M), L);
  \\ phi_0' phi_1' is omitted: it is a combination of phi_0' phi_1 and phi_0 phi_1' (lem:cube-cross-block-defect)
  L = List([prodv(p0, p0, M), prodv(p1, p1, M), prodv(p0, p1, M), prodv(p0d, p1, M), prodv(p0, p1d, M)]);
  for (m = 1, #zs, my(pz = phid(zs[m], 0, M));
    listput(L, prodv(p0, pz, M)); listput(L, prodv(p0d, pz, M)); listput(L, prodv(p1, pz, M)); listput(L, prodv(p1d, pz, M)));
  for (m = 1, #zs, for (m2 = m + 1, #zs, listput(L, row(zs[m], zs[m2], M))));
  matconcat(Col(Vec(L)));
}
wvec(nu, M) = nu * prodv(phid(0, 2, M), phid(1, 0, M), M) + prodv(phid(0, 0, M), phid(1, 2, M), M);
print("Part (a): exact flat limits against the osculating formula");
zall = [7/3, -5/2, 11/7];
{
  for (N = 5, 7,
    my(R = binomial(N, 2), M = R + 4, zs = zall[1 .. N - 4], W0 = w0rows(zs, M), rW0 = matrank(W0),
       rUV = matrank(matconcat([W0; wvec(1, M) - wvec(0, M); wvec(0, M)])));
    printf("N=%d R=%d M=%d: rank W0 = %d (R-1 = %d); rank W0+<U,V> = %d\n", N, R, M, rW0, R - 1, rUV);
    foreach ([2, 1/3, -3], mu,
      my(a = concat([0, mu * t, 1, 1 + t], zs), A, F, L, rL, rc, rneg, rcont);
      A = matconcat(Col(vector(R, e, 0)));
      A = Mat(0); my(rows = List());
      for (i = 1, N, for (j = i + 1, N, listput(rows, row(a[i], a[j], M))));
      A = matconcat(Col(Vec(rows)));
      F = flat(A); L = F[1]; rL = matrank(L);
      rc = matrank(matconcat([L; W0; wvec(mu^2, M)]));
      rneg = matrank(matconcat([L; wvec(mu, M)]));
      rcont = matrank(matrix(R, R + 2, r, s, L[r, s]));
      printf("  mu=%s: saturation steps %d, rank limit %d, rank limit+W0+w(mu^2) %d, control rank limit+w(mu) %d, rank on columns 0..R+1 %d\n",
        mu, F[2], rL, rc, rneg, rcont)));
}
print("Part (b): N = 5, fifth root z symbolic, contact on the pencil");
{
  my(R = 10, M = R + 1, W0 = w0rows([z], M), P, g, pw);
  P = matconcat([W0; prodv(phid(0, 2, M), phid(1, 0, M), M); prodv(phid(0, 0, M), phid(1, 2, M), M)]);
  g = 0; for (d = 1, R + 2, my(cols = [s | s <- [1 .. R + 2], s != d]); g = gcd(g, matdet(vecextract(P, "1..11", cols))));
  print("  gcd of the 11 x 11 minors of [W0; U; V] on columns 0..11: ", factor(g));
  print("  rank over Q(z): projected W0 ", matrank(matrix(9, R + 2, r, s, W0[r, s])), ", projected [W0; U; V] ", matrank(P));
  print("Part (c): at each rational root z0 of that gcd, the contact ratio nu0 (P(z0) nu-combination in W0);");
  print("  where nu0 is a rational square, exact flat limits at mu = sqrt(nu0) and at the control mu + 1");
  foreach (nfroots(, g), zz,
    my(K = matker(substpol(P, z, zz)~), v, mu);
    if (#K != 1 || K[11, 1] == 0, print("  z0=", zz, ": left kernel ", K~); next);
    v = K[10, 1] / K[11, 1];
    if (!issquare(v, &mu), print("  z0=", zz, ": nu0=", v, " is not a rational square"); next);
    foreach ([mu, mu + 1], m,
      my(a = [0, m * t, 1, 1 + t, zz], rows = List(), F, L);
      for (i = 1, 5, for (j = i + 1, 5, listput(rows, row(a[i], a[j], R + 4))));
      F = flat(matconcat(Col(Vec(rows)))); L = F[1];
      printf("  z=%s nu0=%s mu=%s: rank limit %d, rank on columns 0..11 %d\n", zz, v, m, matrank(L), matrank(matrix(R, R + 2, r, s, L[r, s])))));
}
