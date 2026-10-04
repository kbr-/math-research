\\ Cycle keq (9 October 2026), hypothesis (I) of lem:cube-triple-window-constraint-criterion: rank of the three pair
\\ sequences g_ij on M = 3m..3m+7, m = 2..5, two root triples, modulo p = 1000003 (rank 3 mod p implies rank 3 over Q).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
p = 1000003;
lam = 3/2;
seqs(av, m, N) = {
  my(P = prod(l = 1, 3, (1 + av[l] * 'T)^m), pr = [[1, 2], [1, 3], [2, 3]]);
  vector(3, w, my(a = av[pr[w][1]], b = av[pr[w][2]], s = ((1 + a * 'T) * (1 + b * 'T) + O('T^N))^(-lam), rho = Mod(1, p), c = vector(N));
    for(k = 0, N - 1, if(k > 0, rho *= Mod(k, p) / Mod(k + lam - m, p)); c[k + 1] = rho * Mod(polcoef(s, k, 'T), p));
    my(S = Mod(1, p) * P * Ser(c, 'T)); vector(N, k, polcoef(S, k - 1, 'T)));
}
{
  foreach([[2, 5, -3], [1/3, -4, 7/2]], av, for(m = 2, 5, my(X = seqs(av, m, 60));
    emit(Str("roots ", av, " m=", m, ": rank of g_ij on M = ", 3 * m, "..", 3 * m + 7, ": ", matrank(matrix(3, 8, i, c, X[i][3 * m + c]))))));
}
quit;
