\\ Heine-Stieltjes test (route review bmd-20260930-zzo): does the far polynomial W satisfy a linear ODE
\\ A W'' + B W' + C W = 0 (order 2) or A W''' + B W'' + C W' + D W = 0 (order 3) with polynomial coefficients
\\ of degree <= d?  If such an ODE exists with A vanishing only at 0 and -1, every root of W outside {0,-1}
\\ is simple (order 2) or at most double (order 3).  Reports the least d with a solution and the roots of A.
default(parisizemax, 2000000000);
test(W, ord, dmax) = {
  my(D = vector(ord + 1));
  D[1] = W; for (j = 2, ord + 1, D[j] = deriv(D[j - 1], x));
  for (d = 0, dmax,
    \\ unknowns: coefficients of the ord+1 coefficient polynomials, each of degree <= d
    my(nv = (ord + 1) * (d + 1), degmax = poldegree(W) + d, M = matrix(degmax + 1, nv));
    for (j = 0, ord, for (t = 0, d,
      my(term = x^t * D[ord + 1 - j], col = j * (d + 1) + t + 1);
      for (r = 0, degmax, M[r + 1, col] = polcoef(term, r, x))));
    my(K = matker(M));
    if (#K > 0,
      my(v = K[, 1], A = sum(t = 0, d, v[t + 1] * x^t));
      print("  order ", ord, ": least degree ", d, ", kernel dimension ", #K, ", leading coefficient A = ", factor(A));
      return(d)));
  print("  order ", ord, ": none with degree <= ", dmax);
  -1;
}
{
  foreach(["research/results/bmd-20260930-zzn/W_1_1.gp", "research/results/bmd-20260930-zzn/W_1_2.gp"], f,
    my(W = read(f));
    print(f, ": degree ", poldegree(W));
    test(W, 2, 12); test(W, 3, 12));
}
