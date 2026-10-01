\\ Review tests on the last even-peeling far polynomials W_(b-1) (3 October 2026; cycle bmd-20261003-zg).
\\ W_(b-1) = non-branch part of the Wronskian of F_(b-1) (l = 1, e = b-2), computed exactly over Q with c = 1
\\ (F_k(x; c) is F_k(cx; 1) up to constants), factors x and 1+x removed.
\\ (1) Heine-Stieltjes order bound: does W satisfy a Fuchsian equation of order r <= 3 with singular points only
\\     x = 0, -1, infinity (sum_j (x(1+x))^(r-j) q_j W^(r-j) = 0, deg q_j <= j, q_0 = const)?  Order 3 would exclude
\\     triple roots.  Kernel dimension printed (0 falsifies); positive control: a Jacobi polynomial in 2x+1 (order 2).
\\ (2) Krein-Adler setting: number of real roots of W in (-1, 0), in x < -1 and in x > 0, out of deg W.
\\ (3) Squarefreeness and irreducibility over Q (context; the input needs no triple roots).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
farW(e, l, c) = {
  my(bl = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]]);
  my(d = sum(i = 1, 6, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, b, for (j = 0, b[3] - 1, row++; my(g = 'x^j);
    for (m = 1, d, M[row, m] = g; g = deriv(g, 'x) + (b[2] / 'x + b[1] * c / (1 + c * 'x)) * g)));
  my(N = numerator(matdet(M)));
  while (subst(N, 'x, 0) == 0, N = N / 'x); while (subst(N, 'x, -1/c) == 0, N = N / (1 + c * 'x));
  N / pollead(N);
}
fuchs(W, r) = {
  my(s = 'x * (1 + 'x), D = vector(r + 1), cols = List());
  D[1] = W; for (j = 2, r + 1, D[j] = deriv(D[j - 1], 'x));
  listput(cols, s^r * D[r + 1]);
  for (j = 1, r, for (t = 0, j, listput(cols, s^(r - j) * 'x^t * D[r - j + 1])));
  my(dm = vecmax(apply(poldegree, Vec(cols))), M = matrix(dm + 1, #cols, a, b, polcoef(cols[b], a - 1, 'x)), K = matker(M));
  my(lead = 0); for (c = 1, #K, if (K[1, c] != 0, lead = 1));
  [#K, lead];
}
main() = {
  my(J = subst(pollegendre(8), 'x, 2 * 'x + 1));
  emit(Str("control Legendre P8(2x+1): order 2 ", fuchs(J, 2), ", order 3 ", fuchs(J, 3)));
  for (e = 1, 3,
    my(W = farW(e, 1, 1), d = poldegree(W), rr = polrootsreal(W));
    emit(Str("b=", e + 2, " (e,l)=(", e, ",1): deg W ", d, " (predicted 4(2e^2+e+1) = ", 4 * (2 * e^2 + e + 1), "); Fuchs order 2 [kernel, lead] ",
      fuchs(W, 2), ", order 3 ", fuchs(W, 3), "; real roots in (-1,0): ", #select(t -> t > -1 && t < 0, rr), ", x<-1: ",
      #select(t -> t < -1, rr), ", x>0: ", #select(t -> t > 0, rr), "; squarefree ", issquarefree(W), ", irreducible ", polisirreducible(W))));
}
default(parisizemax, 4000000000);
main();
