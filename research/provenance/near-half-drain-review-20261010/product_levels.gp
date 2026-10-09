\\ Level sizes of the product series just below its index, against the thin-closure bound.
\\ Statement computed (side notebook near-half-pc-degree, entry-2026-10-10-drain-review): for
\\ S(z) = (1+z)^(n-k*m) * ((1+z)^k - z^k)^m at m = ceil(log(2) 2^k n), with index D* (first non-positive
\\ coefficient) and K = D* - 1, print for j = K, K-1, K-2, K-5, K-10, K-20 the values log2 S[j] and
\\ log2 binomial(2K+2, j): the thin-closure transfer needs level sizes at most binomial(X, j) with X about
\\ 2K just below the cutoff.  A statement about power series only.
\\ Output lines: k n m Dstar j log2(S[j]) log2(binomial(2K+2,j)).
default(parisize, 2000000000);
{
foreach([2,3,4,6], k,
  foreach([256, 1024], n,
    my(m = ceil(log(2)*2^k*n), N = n\2 + 2, S, d = -1, K);
    S = (1 + z + O(z^N))^(n - k*m) * ((1+z)^k - z^k + O(z^N))^m;
    for(j = 0, N-1, if(polcoeff(S, j) <= 0, d = j; break));
    K = d - 1;
    foreach([0,1,2,5,10,20], t,
      if(K - t >= 1,
        print(k, " ", n, " ", m, " ", d, " ", K-t, " ", precision(log(polcoeff(S, K-t))/log(2), 6), " ",
              precision(log(binomial(2*K+2, K-t))/log(2), 6))))));
}
quit
