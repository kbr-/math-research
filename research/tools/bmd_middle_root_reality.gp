\\ Real-root count of the five-root caterpillar middle Weierstrass polynomial q (c = -3, kappa = 1/100), the rigid
\\ component of ex:cube-middle-component-not-heine-stieltjes, and of q(i S) (the rotation that makes the binary-face
\\ Q_r real-rooted).  The non-crossing bridge needs all roots real after some fixed rotation.
\\ (Cycle bmd-20261009-kcl; the Wronskian helper is copied from bmd_cube_heine_stieltjes_test.gp.)
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
wronsk(fl) = {
  my(n = #fl, P = matrix(n, n));
  for (i = 1, n, my(L = sum(j = 1, #fl[i], fl[i][j][2] * deriv(fl[i][j][1], S) / fl[i][j][1]), p = 1); for (k = 1, n, P[k, i] = p; p = deriv(p, S) + p * L));
  numerator(matdet(P));
}

{
my(c = -3, l = -3/2, ph = 1 + c * S, kap = 1/100);
my(fl = [[[S, 0]], [[ph, l]], [[S, 1], [ph, l]], [[S, -3]], [[S, l], [ph, l]], [[S, l - 1], [ph, l]],
         [[S, l - 1]], [[S, l]], [[S, l + 1]], [[S, l - 2], [S^4 + kap, 1]]]);
my(q = wronsk(fl));
while (subst(q, S, 0) == 0, q = q / S);
while (subst(q, S, -1 / c) == 0, q = q / (S + 1 / c));
my(qi = subst(q, S, I * S));
print("degree ", poldegree(q), "; real roots of q: ", polsturm(q), "; real roots of q(iS) (real or imaginary part): ",
      polsturm(real(qi)) , "/", polsturm(imag(qi)), "; coefficients real: ", q == real(q));
}
quit;
