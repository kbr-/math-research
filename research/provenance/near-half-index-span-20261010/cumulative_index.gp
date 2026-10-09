\\ Graded and cumulative indices of the product series of clause rows.
\\ Statement computed (side notebook near-half-pc-degree, entry-2026-10-10-index-span): for
\\ S(z) = (1+z)^(n-k*m) * ((1+z)^k - z^k)^m, the graded index D* (first j with S[j] <= 0) and the
\\ cumulative index Dc (first D with sum_{j<=D} S[j] <= 0), at m = ceil(c * log(2) 2^k n) for c = 1, 2.
\\ Also the small measured systems (n, m, k) of series.jsonl.  A statement about power series only.
\\ Output lines: k n m Dstar Dc Dc/n.
default(parisize, 4000000000);
{
my(cases = List());
foreach([[16,40,2],[20,50,2],[24,60,2],[20,60,2],[24,72,2],[28,84,2],[16,88,3],[18,99,3]], v, listput(cases, v));
foreach([2,3,4,6,8], k, foreach([256, 1024], n, foreach([1,2], c, listput(cases, [n, ceil(c*log(2)*2^k*n), k]))));
foreach(Vec(cases), v,
  my(n = v[1], m = v[2], k = v[3], N = n + 2, S, d = -1, dc = -1, acc = 0);
  S = (1 + z + O(z^N))^(n - k*m) * ((1+z)^k - z^k + O(z^N))^m;
  for(j = 0, N-1, my(cf = polcoeff(S, j)); acc += cf; if(d < 0 && cf <= 0, d = j); if(acc <= 0, dc = j; break));
  print(k, " ", n, " ", m, " ", d, " ", dc, " ", precision(1.0*dc/n, 4)));
}
quit
