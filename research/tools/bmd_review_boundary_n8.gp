\\ Falsification test of the goal-level route review of cycle kcd (9 October 2026).
\\ Claim tested: the degree-two boundary threshold equals 3 binom(N,4) at small odd primes (certified for N <= 7 by
\\ check:cube-boundary-coprimality-lines).  Here N = 8 (n = 7) at p = 3, 5, 7, 11, 13 with the same deterministic
\\ line certificate (full degree of Delta and gcd(Delta, Delta') = V^N).  A failure is inconclusive.

default(parisizemax, 2^32);
t = varhigher("t");


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
my(N = 8, full = N * N * (N - 1) / 2 + 3 * binomial(N, 4));
foreach([3, 5, 7, 11, 13], p,
  my(e = ceil(log(1e6) / log(p)), t0 = getabstime(), r = lineminors(N, p, e), D = r[1], Dp = r[2], V = r[3], ok);
  ok = D != 0 && poldegree(D) == full && poldegree(gcd(D, Dp)) == N * poldegree(V);
  print("N=8 p=", p, " certified: ", ok, " deg Delta ", poldegree(D), " (full ", full, ") time ", (getabstime() - t0) \ 1000, " s"));
}
quit;
