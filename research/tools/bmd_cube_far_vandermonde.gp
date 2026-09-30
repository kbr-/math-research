\\ Lowest coefficient of the far Wronskian at 0 (cycle bmd-20260930-zzp).
\\ Lemma tested: W(f) = det(T) * prod_{i<j} (rho_j - rho_i) * x^(sum rho - binom(R,2)) * (1 + O(x)), where rho are the
\\ local exponents of F_k at 0 and T = blockdiag(T_c) over the monodromy classes c, T_c[i,j] = coefficient of
\\ x^(rho_j) in the i-th basis function of class c.  Compared with the constant term of the script's W_k
\\ (bmd_cube_far_wronskian.gp normalization: W(f) = prod x^al (1+x)^be (x(1+x))^(-binom(R,2)) det[p_{i,m}]).
default(parisizemax, 2000000000);
read("research/tools/bmd_cube_far_wronskian_lib.gp");
check(e, l) = {
  my(F = funcs(e, l), R = #F, M = matrix(R, R), Wp, v0, ints = List(), halfs = List());
  for (i = 1, R, my(al = F[i][1], be = F[i][2], p = F[i][3]);
    for (m = 0, R - 1, M[i, m + 1] = p; p = (al - m)*(1 + x)*p + (be - m)*x*p + x*(1 + x)*deriv(p, x)));
  Wp = matdet(M); v0 = valuation(Wp, x);
  my(clow = polcoef(Wp, v0, x), sumal = sum(i = 1, R, F[i][1]));
  \\ exponents at 0 from the peeling theorem
  my(rho = List());
  for (j = -(Rn(l) + 2), -3, listput(rho, j));
  for (j = 0, Rn(e) + 4*e, listput(rho, j));
  for (i = 4*e - 4*e*l, 4*e + 4*l - 1, listput(rho, -7/2 + i));
  rho = Vec(rho); if (#rho != R, error("exponent count ", #rho, " vs ", R));
  \\ classes: integral alpha (+ integral exponents) and half-integral
  my(detT = 1);
  foreach([0, 1/2], cls,
    my(idx = [i | i <- [1..R], frac(F[i][1]) == cls], ex = [r | r <- rho, frac(r) == cls], n = #idx);
    if (n != #ex, error("class size"));
    my(T = matrix(n, n), sh = if (cls, 1/2, 0), lo = vecmin(ex) - sh, L = ceil(vecmax(ex) - lo) + 3);
    for (a = 1, n, my(fi = F[idx[a]], ser = x^(fi[1] - sh - lo) * (1 + x + O(x^L))^fi[2] * fi[3]);
      for (b = 1, n, T[a, b] = polcoef(ser, ex[b] - sh - lo, x)));
    detT *= matdet(T));
  my(V = prod(i = 1, R, prod(j = i + 1, R, rho[j] - rho[i])));
  my(pred = detT * V, ratio = clow / pred);
  print("(e,l) = ", [e, l], ": order of W(f) at 0: ", sumal - binomial(R, 2) + v0, " (predicted ", vecsum(rho) - binomial(R, 2), "); lowest coefficient / (det T * Vandermonde) = ", ratio);
  print("   Vandermonde prime support above 13: ", [p | p <- primes([17, 60]), valuation(V, p) != 0], "; valuations at 17..53: ", vector(#primes([17,53]), k, [primes([17,53])[k], valuation(V, primes([17,53])[k]), valuation(detT, primes([17,53])[k])]));
}
check(1, 1); check(1, 2); check(2, 1);
