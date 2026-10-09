\\ Indices (first non-positive coefficient) of two series for m clauses of width k on n variables:
\\ product series (1+z)^(n-k*m) * ((1+z)^k - z^k)^m, which counts the forced relations l*f = 0, and
\\ the generic series (1+z)^n / (1+z^k)^m of conj:parity-clause-semiregular-degree.
\\ m = ceil(log(2) * 2^k * n).  Statement about power series only.  Output: k n m product generic.
default(parisize, 2000000000);
idx(S, N) = { my(d = -1); for(j = 0, N-1, if(polcoeff(S, j) <= 0, d = j; break)); d };
{
forstep(k = 2, 6, 1, if(k == 5, next);
  foreach([256, 1024], n,
    my(m = ceil(log(2)*2^k*n), N = n\2 + 2, a, b);
    a = idx((1 + z + O(z^N))^(n - k*m) * ((1+z)^k - z^k + O(z^N))^m, N);
    b = idx((1 + z + O(z^N))^n * (1 + z^k + O(z^N))^(-m), N);
    print(k, " ", n, " ", m, " ", a, " ", b, " ", precision(1.*a/n, 4), " ", precision(1.*b/n, 4))));
}
quit
