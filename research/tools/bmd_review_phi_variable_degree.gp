\\ Falsification test of the goal-level route review of cycle kcy (9 October 2026).
\\ Question: the degree of the degree-two boundary determinant Phi_N in one root a_1 (roots 0, a_1, ..., a_n,
\\ N = n+1).  By the Nowicki lead of the cycle-kcr review, a characteristic-p Darboux factor of Phi_N that is not
\\ flow-invariant has u_1-degree at least p, and u_1-degree is at most deg_{a_1} Phi_N; so primes p > deg_{a_1} Phi_N
\\ need only squarefreeness of Phi_N mod p.  Prediction, stated before the run: deg_{a_1} Phi_N = 3 binom(N-1,3)
\\ (each root lies in binom(N-1,3) of the 4-subsets carrying the 3 binom(N,4) total degree).
\\ Method: the boundary determinant Delta = V^N Phi_N (check:cube-boundary-coprimality-lines) along the line where only
\\ a_1 = x varies, the other roots random in GF(p), p = 1000003; deg_x Delta - N(N-1) = deg_{a_1} Phi_N (V has
\\ a_1-degree N-1).  Random specialization can only lower the degree, so a value above the prediction falsifies it.

t = varhigher("t");

a1degree(N, p) = {
  my(o = Mod(1, p), n = N - 1, R = N * (N - 1) / 2, m = R + 2, a, rows = List(), M, D);
  a = concat([0 * o], vector(n, i, if(i == 1, 'x * o, random(p) * o)));
  listput(rows, vector(m, c, if(c == 1, o, 0 * o)));
  listput(rows, vector(m, c, if(c == 2, o, 0 * o)));
  for(i = 1, N, for(j = i + 1, N,
    my(ser = sqrt(o + (a[i] + a[j]) * t + a[i] * a[j] * t^2 + O(t^(m + 1))));
    listput(rows, vector(m, c, polcoef(ser, c - 1, t)))));
  M = matrix(m, m, r, c, rows[r][c]);
  D = matdet(M);
  poldegree(lift(D)) - N * (N - 1);
}

setrand(20261009);
for(N = 4, 8, print("N=", N, " deg_a1 Phi = ", a1degree(N, 1000003), " predicted ", 3 * binomial(N - 1, 3)));
quit;
