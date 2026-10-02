\\ The k = 1 kernel determinants at M = 2 (cycle bmd-20261009-u, 9 October 2026).
\\ Computes D_j(u), j = 0..3, p = 1, symbolically in the roots a, b, written in e1 = a + b and d2 = (a - b)^2,
\\ to order B + TT, with D_T as in prop:cube-kernel-arc-reduction. Purpose: the shape of the u-Newton polygons,
\\ to test the candidate mechanism "every coefficient of D_j lies in the ideal (d2, u-shifted coefficients of D_0)".
OUT = "research/results/bmd-20261009-u/k1-two-roots.txt";
default(parisize, 400000000);
Zv = varhigher("zz");
c(n) = binomial(-3/2, n);
T1(F) = { my(d = poldegree(F, Zv)); sum(i = 0, d, polcoef(F, i, Zv) * c(i + 1) / c(i) * Zv^(i + 1)) };
{
  my(M = 2, p = 1, TT = 8, B = 2, NU = B + TT, JM = 3);
  my(P = (Zv - 'a) * (Zv - 'b));
  my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NU - n, c(m) * c(n + m) * 'u^(n + m) * Zv^m), P))); vector(M, s, polcoef(r, s - 1, Zv))));
  my(kcol = vector(JM + 1, i, my(F = P * Zv^(i - 1), col = vector(M));
    for (m = 1, NU, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, Zv) * 'u^m));
    col));
  for (j = 0, JM, my(D = matdet(matrix(M, M, r, jj, if(jj <= p, ncol[jj][r], kcol[j + 1][r]))));
    write(OUT, "j=", j, ":");
    for (n = 0, NU, my(a = polcoef(D, n, 'u)); if (a != 0,
      \\ rewrite in e1 = a + b, d2 = (a - b)^2 via symmetric reduction: substitute b = e1 - a and eliminate a^2
      my(g = subst(subst(a, 'b, 'e - 'a), 'a, ('e + 'w) / 2));
      write(OUT, "  u^", n, ": ", factor(substpol(g, 'w^2, 'd))))));
}
