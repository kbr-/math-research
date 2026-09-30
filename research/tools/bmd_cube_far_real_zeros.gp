\\ Real zeros and interlacing of the far polynomials (3 October 2026; cycle bmd-20261003-m)
\\ Question (orthogonal-polynomial lead): are the far polynomials R_(n,k) (lem:cube-far-u-space) real-rooted in (0,1),
\\ and do their zeros strictly interlace across k (R_(n,k), R_(n,k+1)) or across n?  If so, an interlacing induction
\\ could prove squarefreeness for every (n,k).  Prints, per (n,k): number of real zeros, how many lie in (0,1); and
\\ whether the real zeros of consecutive members interlace.  Construction as in
\\ research/tools/bmd_cube_far_modp_specialization.gp.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
stripw(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N; }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  stripw(numerator(matdet(M)));
}
far(n, k) = {
  my(hh = 1/2, C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, hh - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = hh); for (i = 1, q, p = thetastep(p, al, hh - (n - 1), E[i]); al--); p));
  my(R = wr([[0, 0, P3], [hh, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]));
  R / content(R);
}
realz(R) = { my(z = polroots(R), r = List()); for (i = 1, #z, if (abs(imag(z[i])) < 1e-40, listput(r, real(z[i])))); vecsort(Vec(r)); }
interlace(a, b) = { my(c = vecsort(concat(apply(x -> [x, 0], a), apply(x -> [x, 1], b)))); for (i = 2, #c, if (c[i][2] == c[i - 1][2], return(0))); 1; }
main() = {
  my(N = eval(getenv("NMAX")), K = eval(getenv("KMAX")), Z = Map());
  for (n = 2, N, for (k = 3, K, my(R = far(n, k), r = realz(R));
    mapput(Z, [n, k], r);
    emit(Str("(n,k)=", [n, k], ": deg ", poldegree(R), ", real zeros ", #r, ", in (0,1): ", #select(x -> x > 0 && x < 1, r),
      ", negative: ", #select(x -> x < 0, r), ", above 1: ", #select(x -> x > 1, r)))));
  for (n = 2, N, for (k = 3, K - 1, emit(Str("interlace in k: ", [n, k], " vs ", [n, k + 1], ": ", interlace(mapget(Z, [n, k]), mapget(Z, [n, k + 1]))))));
  for (n = 2, N - 1, for (k = 3, K, emit(Str("interlace in n: ", [n, k], " vs ", [n + 1, k], ": ", interlace(mapget(Z, [n, k]), mapget(Z, [n + 1, k]))))));
}
default(realprecision, 150);
default(parisizemax, 2000000000);
main();
quit
