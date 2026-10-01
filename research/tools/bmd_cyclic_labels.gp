\\ Cyclic labels (5 October 2026; cycle bmd-20261005-i).  Unanchored mark determinant (no dummy label; Delta = V^N Phi_N,
\\ Phi_N translation invariant, thm:cube-odd-schur-hull) at a_i = zeta^i, zeta a primitive N-th root of unity in
\\ F_(3^K), K the order of 3 mod N (N coprime to 3).  Scaling a -> zeta a permutes pair rows and multiplies jet column k by
\\ zeta^k, so Delta factors over Fourier blocks indexed by k mod N.  Question: is Phi_N(zeta^i) != 0 mod 3, so that the
\\ block factorization can carry a proof?  Output per N: Delta != 0 or = 0, and the block sizes.  Env NS.
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
foreach(eval(getenv("NS")), N,
  if (N % 3 == 0, next);
  my(K = znorder(Mod(3, N)), g = ffgen(ffinit(3, K, 'a), 'a), z = g^((3^K - 1) / N), t0 = getwalltime());
  if (z^N != 1 || (N > 1 && #Set(vector(N, i, z^i)) < N), error("no primitive root"));
  my(dl = mark(vector(N, i, z^i), g^0), D = N * (N - 1) / 2 + 2);
  emit(Str("N = ", N, " (field 3^", K, "): Delta at cyclic labels ", if(dl == 0, "= 0", "!= 0"), "; jet columns per residue mod N: ",
    vector(N, r, #select(k -> (k - 1) % N == r - 1, [1..D])), " (", getwalltime() - t0, " ms)")));
}
quit;
