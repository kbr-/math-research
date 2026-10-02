\\ Exact eta-adic check of ex:cube-standard-negative-minimality-fails (cycle bmd-20261009-l, 9 October 2026).
\\ eta (the variable w in the code, since eta is a PARI builtin) is a formal variable (valuation ring Q[eta]_(eta), which contains Q). Factors the t = 1 coefficient
\\ [u^(B+1)] P_Lambda of the window Lambda_1 and of a violating coordinate with negatives {1}, at roots (1, -1+eta)
\\ (M = 2) and (1, -4+eta, 3) (M = 3), and the M = 2 kernel cofactor 9 y1^2 + 17 y1 y2 + 9 y2^2 at eta = 0.
OUT = "research/results/bmd-20261009-l/symmetric-roots-exact.txt";
c(n) = if(n < 0, 0, binomial(-3/2, n));
coef(Y, L, t) = {
  my(M = #Y, N = apply(x -> -x, select(x -> x < 0, L)), p = #N, k = M - p, B = p * (p - 1) / 2 + vecsum(N) + k, NU = B + t);
  my(X = matrix(2 * M, 2 * M, r, i, my(a = L[i]);
    if(r <= M, if(a >= 0, c(a) * Y[r]^a, 0),
      my(s = r - M); sum(m = max(1, -a), NU, c(m) * c(a + m) * Y[s]^(a + m) * 'u^m))));
  polcoef(matdet(X), B + t, 'u)
};
{
  my(Y2 = [1, -1 + 'w], Y3 = [1, -4 + 'w, 3]);
  foreach([[Y2, [-1, 0, 1, 2], "M=2 window [-1,2]"], [Y2, [-1, 0, 1, 3], "M=2 {-1,0,1,3}"],
           [Y3, [-1, 0, 1, 2, 3, 4], "M=3 window [-1,4]"], [Y3, [-1, 0, 1, 2, 3, 5], "M=3 {-1,0,1,2,3,5}"]], cs,
    my(f = coef(cs[1], cs[2], 1));
    write(OUT, cs[3], ", t = 1: factor = ", factor(f), "; value at w = 0: ", subst(f, 'w, 0),
      "; w-adic valuation (w = eta) ", valuation(f, 'w)));
  write(OUT, "M=2 kernel cofactor 9 y1^2 + 17 y1 y2 + 9 y2^2 at (1, -1): ", 9 - 17 + 9);
}
