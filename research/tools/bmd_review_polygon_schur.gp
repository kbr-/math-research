\\ Route review (cycle kew, 9 October 2026): Schur-Hankel sums at regular polygons, and the free-fermion identity.
\\ (a) For the M-th roots of unity, M = 5, 6, and every k with the polygon in Omega_k (2 <= k <= M-2): for each
\\     rotation-allowed weight w <= 6 (k(k+1) + w = 0 mod M), the values H_mu = sum_(|S|=k+1) Vand(y_S)^2 s_mu(y_S) for all
\\     partitions mu of w with at most k+1 parts (exact in Q(zeta_M), no coefat involved).
\\ (b) On the M-th roots of unity, M <= 8, every subset S: Vand(y_S)^2 = (-1)^(C(|S|,2)) |Vand(y_S)|^2 (prod_S y)^(|S|-1).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
\\ Schur function via the bialternant: s_mu(Z) = det[z_i^(mu_j + n - j)] / Vand-type determinant, n = #Z
schur(Z, mu) = { my(n = #Z, m = concat(mu, vector(n - #mu)));
  matdet(matrix(n, n, i, j, Z[i]^(m[j] + n - j))) / matdet(matrix(n, n, i, j, Z[i]^(n - j))); }
HS(Y, k, mu) = { my(s = 0); forsubset([#Y, k + 1], S, my(Z = vector(k + 1, i, Y[S[i]])); s += vand(Z)^2 * schur(Z, mu)); s; }
parts(w, l) = { my(L = List()); forpart(q = w, listput(L, Vecrev(q)), , [1, l]); Vec(L); }
{
  for (M = 5, 6, my(Y = vector(M, j, Mod('w, polcyclo(M, 'w))^(j - 1)));
    for (k = 2, M - 2, for (w = 0, 6, if ((k * (k + 1) + w) % M, next);
      my(P = if (w == 0, [[]], parts(w, k + 1)), vals = vector(#P, i, lift(HS(Y, k, P[i]))));
      emit(Str("(a) M=", M, " k=", k, " allowed weight ", w, ": H_mu for mu in ", P, " = ", vals)))));
  my(ok = 1, tot = 0);
  for (M = 2, 8, my(Y = vector(M, j, exp(2 * Pi * I * (j - 1) / M)));
    forsubset(M, S, if (#S < 2, next); tot++; my(Z = vector(#S, i, Y[S[i]]), v = vand(Z), n = #S);
      if (abs(v^2 - (-1)^(n * (n - 1) / 2) * abs(v)^2 * prod(i = 1, n, Z[i])^(n - 1)) > 1e-20, ok = 0)));
  emit(Str("(b) free-fermion identity on ", tot, " subsets (M <= 8, |S| >= 2): ", ok));
}
quit;
