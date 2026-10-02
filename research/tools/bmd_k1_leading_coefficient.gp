\\ The k = 1 leading kernel coefficient (cycle bmd-20261009-u, 9 October 2026).
\\ Checks for lem:cube-k1-kernel-leading-coefficient, p = M - 1:
\\  (a) [u^B] D_{j} = kappa_M * [y_1..y_M] I(P z^j) (divided difference over the roots, I = integration from 0),
\\      with kappa_M independent of j, against the full determinant, symbolically, M = 2, 3, j = 0..3;
\\  (b) [y_1..y_M] I(P) = -sum_{i<j} (y_i - y_j)^2 / (M (M^2 - 1)), symbolically, M = 2..7;
\\  (c) the Hankel determinant H_p = det[c_{n+m}]_{1<=n<=p, 0<=m<=p-1} is nonzero, p = 1..12, with factorizations;
\\  (d) Q = sum_{i<j} (y_i - y_j)^2 does not divide [y_1..y_M] I(P z), M = 3..6 (pseudo-remainder in y_1 nonzero).
OUT = "research/results/bmd-20261009-u/k1-leading-coefficient.txt";
default(parisize, 400000000);
Zv = varhigher("zz");
c(n) = binomial(-3/2, n);
T1(F) = { my(d = poldegree(F, Zv)); sum(i = 0, d, polcoef(F, i, Zv) * c(i + 1) / c(i) * Zv^(i + 1)) };
roots(M) = vector(M, s, eval(Str("y", s)));
divdiff(f, P) = polcoef(lift(Mod(f, P)), poldegree(P, Zv) - 1, Zv);
hI(P, j) = intformal(P * Zv^j, Zv);
{
  \\ (a)
  for (M = 2, 3, my(Y = roots(M), P = prod(s = 1, M, Zv - Y[s]), p = M - 1, B = p * (p + 1) / 2 + p * (p - 1) / 2 + 1, NU = B);
    my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NU - n, c(m) * c(n + m) * 'u^(n + m) * Zv^m), P))); vector(M, s, polcoef(r, s - 1, Zv))));
    my(rat = vector(4));
    for (j = 0, 3, my(F = P * Zv^j, col = vector(M));
      for (m = 1, NU, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, Zv) * 'u^m));
      my(D = matdet(matrix(M, M, r, jj, if(jj <= p, ncol[jj][r], col[r]))));
      rat[j + 1] = polcoef(D, B, 'u) / divdiff(hI(P, j), P);
      if (polcoef(D, B - 1, 'u) != 0, rat[j + 1] = "lower order nonzero"));
    write(OUT, "(a) M=", M, " B=", B, ": [u^B] D_{j} / divided difference of I(P z^j), j = 0..3: ", rat));
  \\ (b)
  for (M = 2, 7, my(Y = roots(M), P = prod(s = 1, M, Zv - Y[s]), Q = sum(i = 1, M, sum(j = i + 1, M, (Y[i] - Y[j])^2)));
    write(OUT, "(b) M=", M, ": divided difference of I(P) + Q/(M(M^2-1)) = ", divdiff(hI(P, 0), P) + Q / (M * (M^2 - 1))));
  \\ (c)
  for (p = 1, 12, my(H = matdet(matrix(p, p, n, m, c(n + m - 1)))); write(OUT, "(c) p=", p, ": H_p = ", H, " = ", factor(H)));
  \\ (d)
  for (M = 3, 6, my(Y = roots(M), P = prod(s = 1, M, Zv - Y[s]), Q = sum(i = 1, M, sum(j = i + 1, M, (Y[i] - Y[j])^2)));
    my(f = divdiff(hI(P, 1), P), r = f % Q);
    write(OUT, "(d) M=", M, ": remainder of [y] I(P z) modulo Q in the main y-variable is nonzero (1 = yes): ", r != 0));
}
