\\ Phi_N mod 3 on a random line (5 October 2026; cycle bmd-20261005-h).  Question: does Phi_N factor modulo 3 with a
\\ large cube (Frobenius) part, Phi = G^3 H?  Labels x = p + t d with p, d random in F_(3^K); Phi(t) = Delta(t) / V(t)^N
\\ computed exactly in F_(3^K)[t] and factored; reports the multiplicity profile of its irreducible factors.
\\ Env NS, K, SEED.
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
mark(lab, one) = {
  my(N = #lab, D = N * (N - 1) / 2 + 2, bh = vector(D, j, lift(binomial(1/2, j - 1) * Mod(1, 3))), M = matrix(D, D), row = 2);
  M[1, 1] = one; M[2, 2] = one;
  for (i = 1, N, for (j = i + 1, N, row++;
    for (kk = 1, D, M[row, kk] = one * sum(u = 0, kk - 1, bh[u + 1] * bh[kk - u] * lab[i]^u * lab[j]^(kk - 1 - u)))));
  matdet(M);
}
{
my(K = eval(getenv("K")), g = ffgen(ffinit(3, K, 'a), 'a), t = 't);
setrand(eval(getenv("SEED")));
foreach(eval(getenv("NS")), N,
  my(t0 = getwalltime(), lab = vector(N, i, random(g) + t * random(g)), V = prod(i = 1, N, prod(j = i + 1, N, lab[j] - lab[i])));
  my(phi = mark(lab, g^0) / V^N, fa = factor(phi), prof = Map());
  for (i = 1, #fa[, 1], my(m = fa[i, 2], d = poldegree(fa[i, 1]), old = 0); if (mapisdefined(prof, m, &old), , old = 0); mapput(prof, m, old + d));
  emit(Str("N = ", N, ": deg Phi on the line ", poldegree(phi), " (expected 3 binom(N,4) = ", 3 * binomial(N, 4), "); total degree by multiplicity [multiplicity, degree]: ", Mat(prof), " (", getwalltime() - t0, " ms)")));
}
quit;
