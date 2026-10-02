\\ Leading coefficient formula check (8 October 2026; cycle bmd-20261008-zv).
\\ Tested statement (lem:cube-cross-leading-coefficient): for every coordinate set Lambda of 2M columns with negative
\\ set -N (|N| = p <= M) and nonnegative part Lambda+, the least u-degree of P_Lambda (x = 1, eps = u, lambda = 3/2) is
\\ at least B = p(p-1)/2 + sum N + M - p, and its u^B coefficient equals
\\   +- H_N c_1^(M-p) prod_(e<p) c_e prod_(i in Lambda+) c_i (-1/2)^k Vand(y)^2 D,  k = M - p,
\\   D = det of the rows i in Lambda+: (h_(t+i-M+1)(y))_(t<M), (h_(t+i-M+2)(y)/(i+1))_(t<k),
\\ with H_N = det[c_(j-1+n)]_(j<=p, n in N) and h the complete homogeneous polynomials of y.
\\ Checked at one random integer point per (M, Lambda): |ratio| = 1 and the u-degrees below B vanish.
OUT = "research/results/bmd-20261008-zv/leading-coefficient-formula.txt";
c(n) = if(n < 0, 0, binomial(-3/2, n));
vand(Y) = prod(a = 1, #Y, prod(b = a + 1, #Y, Y[b] - Y[a]));
hcomp(Y, n) = if(n < 0, 0, polcoef(1 / prod(s = 1, #Y, 1 - Y[s] * 'q + O('q^(n + 1))), n, 'q));
check(Y, L) = {
  my(M = #Y, N = apply(t -> -t, select(t -> t < 0, L)), Lp = select(t -> t >= 0, L), p = #N, k = M - p);
  my(B = p * (p - 1) / 2 + vecsum(N) + M - p);
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), B + 1, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(Dt = matdet(X), low = sum(n = 0, B - 1, polcoef(Dt, n, 'u) != 0), lead = polcoef(Dt, B, 'u));
  my(HN = if(p, matdet(matrix(p, p, j, n, c(j - 1 + N[n]))), 1));
  my(D = matdet(matrix(2 * M - p, M + k, a, b, my(i = Lp[a]);
    if(b <= M, hcomp(Y, b - 1 + i - M + 1), hcomp(Y, (b - M - 1) + i - M + 2) / (i + 1)))));
  my(pred = HN * c(1)^k * prod(e = 0, p - 1, c(e)) * prod(a = 1, #Lp, c(Lp[a])) * (-1/2)^k * vand(Y)^2 * D);
  [low, if(pred == 0, if(lead == 0, 1, -1), abs(lead / pred))];
};
{
  setrand(8);
  for (M = 2, 4,
    my(Y = vector(M, s, random(41) - 20), cols = [-M .. 2 * M], tot = 0, good = 0);
    while(vand(Y) == 0, Y = vector(M, s, random(41) - 20));
    forsubset([#cols, 2 * M], S,
      my(L = vector(2 * M, i, cols[S[i]]));
      if(#select(t -> t < 0, L) <= M,
        my(r = check(Y, L));
        tot++;
        if(r[1] == 0 && r[2] == 1, good++)));
    write(OUT, "M=", M, " point ", Y, ": ", tot, " sets with p <= M; formula exact (no lower u-terms, |ratio| = 1): ", good));
}
