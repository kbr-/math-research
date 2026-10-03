\\ Boundary coprimality certificates (cycle kca, 9 October 2026).
\\ Statement applied: Phi_N and G' (reduced minors on columns 0..R-1 and 0..R-2, R) are maximal minors of the
\\ boundary pair matrix, so gcd(Phi_N, G') = 1 with Phi_N != 0 gives g = 1 and, by lem:cube-boundary-cofactor-threshold,
\\ the degree-two boundary threshold ell_0(3, binom(N,2)+2) = 3 binom(N,4) in characteristic p (no condition on p | m).
\\ Certificate: on a random line a_i = alpha_i + s beta_i (a_0 = 0) over GF(p^e), Delta = V^N Phi, Delta' = V^N G'.
\\ The script asserts deg_s Delta = N binom(N,2) + 3 binom(N,4) (full degree, so every factor of Phi keeps its degree
\\ on the line) and gcd(Delta(s), Delta'(s)) = V(s)^N exactly; together these prove gcd(Phi, G') = 1.
\\ A failure on one line is inconclusive.  Reported per N: primes certified, failures.  (Corrected after review.)

default(parisizemax, 2^31);
t = varhigher("t");  \\ series variable, of higher priority than the line variable x

lineminors(N, p, e) = {
  my(g = ffgen(p^e, 'y), o = g^0, n = N - 1, R = N * (N - 1) / 2, m = R + 2, al, be, a, rows = List(), M, D, Dp, V);
  al = vector(n, i, random(g)); be = vector(n, i, random(g));
  a = concat([0 * o], vector(n, i, al[i] + 'x * be[i]));
  listput(rows, vector(m + 1, c, if(c == 1, o, 0 * o)));
  listput(rows, vector(m + 1, c, if(c == 2, o, 0 * o)));
  for(i = 1, N, for(j = i + 1, N,
    my(ser = sqrt(o + (a[i] + a[j]) * t + a[i] * a[j] * t^2 + O(t^(m + 1))));
    listput(rows, vector(m + 1, c, polcoef(ser, c - 1, t)))));
  M = matrix(m, m + 1, r, c, rows[r][c]);
  D = matdet(matrix(m, m, r, c, M[r, c]));
  Dp = matdet(matrix(m, m, r, c, if(c < m, M[r, c], M[r, m + 1])));
  V = prod(i = 1, N, prod(j = i + 1, N, a[i] - a[j]));
  [D, Dp, V];
}

setrand(20261009);
{
for(N = 4, 7,
  my(m = N * (N - 1) / 2 + 2, full = N * N * (N - 1) / 2 + 3 * binomial(N, 4), ok = List(), fail = List());
  forprime(p = 3, 2^(N - 1),
    my(e = ceil(log(1e6) / log(p)), r = lineminors(N, p, e), D = r[1], Dp = r[2], V = r[3], gg);
    if(D == 0, listput(fail, [p, "Delta=0"]); next);
    if(poldegree(D) != full, listput(fail, [p, "degree", poldegree(D)]); next);
    gg = gcd(D, Dp);
    if(poldegree(gg) == N * poldegree(V), listput(ok, p), listput(fail, [p, poldegree(gg) - N * poldegree(V)])));
  print("N=", N, " m=", m, " full degree ", full, " certified p: ", Vec(ok), " failures: ", Vec(fail)));
}
quit;
