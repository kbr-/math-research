\\ The merge far spaces on the Klein cover as trigonometric KP tau-functions (2 October 2026; cycle bmd-20261002-o).
\\ Cover: w = (t + 1/t)^2 / 4, w^(1/2) = (t + 1/t)/2, (w - 1)^(1/2) = (t - 1/t)/2.  F(n,k) = A1 + A2 + B3 + B4 (pure-reduction
\\ entry) pulls back to a space of Laurent polynomials in t, i.e. of exponential sums sum_m a_m e^(m y), t = e^y, with a frequency
\\ set Lambda.  Its Wronskian in theta = t d/dt is tau(t) = sum_S Delta_S(A) V(S) t^(sum S) over d-subsets S of Lambda (Cauchy-Binet),
\\ a trigonometric KP tau-function; its zeros off the branch preimages are the pulled-back far points.
\\ Tests, for (n,k) = (2,3), (3,3), (2,4):
\\  1. tau(t) of the space times its common denominator, with its factors t, t^2 - 1, t^2 + 1 removed, equals
\\     R_(n,k)((t + 1/t)^2/4) t^(2 deg R) up to a constant (so the particle
\\     positions off the branch preimages are exactly the pulled-back far points, 4 deg R of them).
\\  2. The second KP flow e^(m y) -> q^(m^2) e^(m y) (frequencies centred so that t -> 1/t is m -> -m) keeps the Klein symmetry
\\     (t -> -t, t -> 1/t); whether it leaves the (rigid) class is not compared here.  Reported at q = 2: the number of tau-zeros off
\\     the branch preimages, invariance under t -> 1/t and t -> -t, and squarefreeness.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
\\ far polynomial R_(n,k) from the pure reduction (same Wronskian helper)
strip(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / pollead(N); }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)));
}
Fcls(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
   [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]];
}
\\ pull back one class to Laurent polynomials in t (as t^-big times a polynomial, returned as a rational function in t)
pull(c) = {
  my(W = ('t + 1/'t)^2 / 4, u = ('t + 1/'t) / 2, v = ('t - 1/'t) / 2, fac = (if (c[1] == 1/2, u, 1)) * (if (c[2] == 1/2, v, 1)));
  apply(f -> subst(f, 'w, W) * fac, c[3]);
}
\\ theta-Wronskian of a list of Laurent polynomials, with optional KP time s (flow e^(m y) -> e^(m y + m^2 s))
\\ theta-Wronskian: multiply every function by one power t^K making it a polynomial; theta^j(t^K f) = t^K (theta + K)^j f, a
\\ unitriangular change of columns, so the determinant only gains the factor t^(dK), removed by branchstrip.  Evaluated at
\\ 2 + d * degree integer points and interpolated, avoiding determinants over Q(t).
\\ The pulled-back functions have poles at the preimages t = 0, +-i of w = infinity, 0: multiply all by their common denominator
\\ D (supported there), which multiplies the Wronskian by D^d and changes nothing off the branch preimages.
thetawr(L, s) = {
  my(d = #L, D = lcm(apply(f -> denominator(f), L)), P = apply(f -> f * D, L));
  my(Q = vector(d, i, my(g = P[i], v = vector(d)); for (j = 1, d, v[j] = g; g = 't * deriv(g, 't)); v));
  my(dg = d * vecmax(apply(p -> poldegree(p, 't), P)) + 1, xs = vector(dg + 1, i, i), ys = vector(dg + 1));
  for (i = 1, dg + 1, ys[i] = matdet(matrix(d, d, a, b, subst(Q[a][b], 't, xs[i]))));
  polinterpolate(xs, ys, 't);
}
flow(f, s) = {
  \\ apply e^(m y) -> e^(m y + m^2 s) to a Laurent polynomial f(t): coefficient of t^m times exp(m^2 s); s given as the formal
  \\ multiplier q with q^(m^2), q a rational number
  my(N = numerator(f), D = denominator(f), e = -valuation(D, 't), g = 0);
  \\ D is a monomial c t^a
  my(a = poldegree(D, 't), cD = pollead(D));
  for (j = 0, poldegree(N, 't), my(cf = polcoef(N, j, 't), m = j - a); if (cf != 0, g += cf / cD * s^(m^2) * 't^m));
  g;
}
branchstrip(T) = {
  my(N = numerator(T));
  while (subst(N, 't, 0) == 0, N = N / 't);
  foreach([1, -1], r, while (subst(N, 't, r) == 0, N = N / ('t - r)));
  while (polcoef(N % ('t^2 + 1), 0, 't) == 0 && polcoef(N % ('t^2 + 1), 1, 't) == 0, N = N / ('t^2 + 1));
  N / pollead(N);
}
run(n, k) = {
  my(F = Fcls(n, k), R = wr(F), L = concat(apply(pull, F)), d = #L);
  my(T0 = thetawr(L, 1), N0 = branchstrip(T0));
  \\ push R(w) up: numerator of R((t+1/t)^2/4) times t^(2 deg R)
  my(Rup = subst(R, 'w, ('t + 1/'t)^2 / 4) * 't^(2 * poldegree(R)), Rup1 = Rup / pollead(Rup));
  my(same = (N0 == Rup1));
  \\ KP flow with multiplier q = 2 (a generic value): flow every function, recompute
  \\ centre the frequencies (lo + hi = 0) so that t -> 1/t acts by m -> -m, which the flow multiplier q^(m^2) respects
  my(D = lcm(apply(f -> denominator(f), L)), Lp = apply(f -> f * D, L));
  my(lo = vecmin(apply(p -> valuation(p, 't), Lp)), hi = vecmax(apply(p -> poldegree(p, 't), Lp)));
  if ((lo + hi) % 2, error("odd frequency span"));
  my(Lq = apply(p -> flow(p * 't^(-(lo + hi) / 2), 2), Lp), Tq = thetawr(Lq, 1), Nq = branchstrip(Tq));
  my(inv1 = (subst(Nq, 't, 1/'t) * 't^poldegree(Nq) / pollead(subst(Nq, 't, 1/'t) * 't^poldegree(Nq)) == Nq));
  my(inv2 = (subst(Nq, 't, -'t) / pollead(subst(Nq, 't, -'t)) == Nq));
  my(sq0 = (poldegree(gcd(N0, deriv(N0))) == 0), sqq = (poldegree(gcd(Nq, deriv(Nq))) == 0));
  emit(Str("(n,k)=", [n, k], ": dim ", d, "; deg R ", poldegree(R), "; particles off branch preimages at s=0: ", poldegree(N0),
    "; equals R pulled back: ", same, "; squarefree: ", sq0,
    "; after KP flow (q=2): particles ", poldegree(Nq), ", invariant under t->1/t: ", inv1, ", under t->-t: ", inv2, ", squarefree: ", sqq));
}
foreach([[2, 3], [3, 3], [2, 4]], v, run(v[1], v[2]));
