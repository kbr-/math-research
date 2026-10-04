\\ Newton/roots-of-unity lead entry one (cycle kex, 9 October 2026): the residue criterion for Schur-Hankel sums at
\\ regular polygons. H_mu = sum_(|S|=k+1) Vand(y_S)^2 s_mu(y_S) at the M-th roots of unity is predicted to be
\\ +-M^(k+1) when the set mu + delta (delta = (k, k-1, .., 0)) has residues exactly {0, -1, .., -k} mod M, and 0 otherwise.
\\ Exact test in Q(zeta_M) (bialternant Schur functions; no cross-coordinate routine) for M = 4, 5, every 1 <= k <= M-1,
\\ every partition mu with at most k+1 parts and |mu| <= 8.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
schur(Z, mu) = { my(n = #Z, m = concat(mu, vector(n - #mu)));
  matdet(matrix(n, n, i, j, Z[i]^(m[j] + n - j))) / matdet(matrix(n, n, i, j, Z[i]^(n - j))); }
HS(Y, k, mu) = { my(s = 0); forsubset([#Y, k + 1], S, my(Z = vector(k + 1, i, Y[S[i]])); s += vand(Z)^2 * schur(Z, mu)); s; }
{
  my(tot = 0, bad = 0, nonzero = List());
  for (M = 4, 5, my(Y = vector(M, j, Mod('w, polcyclo(M, 'w))^(j - 1)));
    for (k = 1, M - 1, for (wt = 0, 8, forpart(q = wt, my(mu = Vecrev(q), m = concat(mu, vector(k + 1 - #mu)), B = vector(k + 1, c, m[c] + k + 1 - c));
      my(pred = Set(apply(b -> b % M, B)) == Set(vector(k + 1, a, (-(a - 1)) % M)), v = HS(Y, k, mu));
      tot++; my(ok = if (pred, v == M^(k + 1) || v == -M^(k + 1), v == 0)); if (!ok, bad++; emit(Str("mismatch M=", M, " k=", k, " mu=", mu, ": ", lift(v))));
      if (pred, listput(nonzero, [M, k, mu, lift(v)])), , [0, k + 1]))));
  emit(Str("residue criterion: ", tot - bad, " of ", tot, " cases agree (M = 4, 5; every k; |mu| <= 8)"));
  emit(Str("nonzero cases [M, k, mu, value]: ", Vec(nonzero)));
}
quit;
