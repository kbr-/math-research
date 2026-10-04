\\ Padé block lead (cycle kfn, 9 October 2026): boundary values of a planted excess-two system.
\\ Tested: with f_1..f_5 the actual triple-window functions (1+a_iT)^(-3/2) (i = 1,2,3), ((1+a_1T)(1+a_2T))^(-3/2),
\\ ((1+a_1T)(1+a_3T))^(-3/2) at a = (2/7, -5/3, 1), m = 2, n = (1; 2,2,2; 1,1,1), and f_6 planted so that a form of
\\ order |n|+2 exists (excess two at n), every Hermite-Pade determinant H(N) with N <= n, N != n (the faces below n)
\\ stays nonzero, as for the true system (f_6 = ((1+a_2T)(1+a_3T))^(-3/2)). Convention of
\\ lem:cube-window-hermite-pade-frobenius: rows T^r f_g for the six non-polynomial g, r < N_g; Taylor columns
\\ N_0 .. |N|-1. Exact rational arithmetic. Also reports H on the excess-two simplex of the planted system (all 0).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
P = 30;
ser(e) = e + O('T^P);
H(F, N) = {
  my(rows = List(), c0 = N[1], c1 = vecsum(N));
  for (g = 1, 6, for (r = 0, N[g + 1] - 1, my(s = 'T^r * F[g]); listput(rows, vector(c1 - c0, j, polcoef(s, c0 + j - 1, 'T)))));
  if (#rows == 0, return(1));
  matdet(Mat(Vec(rows)~)~);
}
{
  my(a = [2/7, -5/3, 1], w = vector(3, i, ser((1 + a[i] * 'T)^(-3/2))));
  my(Ftrue = [w[1], w[2], w[3], w[1] * w[2], w[1] * w[3], w[2] * w[3]]);
  my(n = [1, 2, 2, 2, 1, 1, 1], N0 = vecsum(n));
  my(p = [3, 1 - 2*'T, 2 + 'T, -1 + 'T, 5, -2]);  \\ p_0 (deg < 1), p_1..p_3 (deg < 2), p_4, p_5 (deg < 1); p_6 = 1
  my(f6 = ser('T^(N0 + 2) - p[1] - sum(g = 1, 5, p[g + 1] * Ftrue[g])));
  my(Fpl = Ftrue); Fpl[6] = f6;
  my(nzT = 0, nzP = 0, tot = 0, zeroP = List());
  forvec(N = vector(7, g, [0, n[g]]), if (N == n, next); tot++;
    my(hT = H(Ftrue, N), hP = H(Fpl, N)); if (hT != 0, nzT++); if (hP != 0, nzP++, listput(zeroP, N)));
  emit(Str("faces below n (N <= n, N != n): ", tot, " indices; nonzero for the true system: ", nzT, "; for the planted system: ", nzP));
  if (#zeroP, emit(Str("planted zeros below n: ", Vec(zeroP))));
  my(cnt = 0, z = 0);
  forvec(d = vector(7, g, [0, 2]), if (vecsum(d) > 2, next); cnt++; if (H(Fpl, n + d) == 0, z++));
  emit(Str("planted excess-two simplex: ", z, " of ", cnt, " determinants vanish; true system H(n) = ", H(Ftrue, n) != 0));
  quit;
}
