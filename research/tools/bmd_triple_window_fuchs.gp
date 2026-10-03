\\ Global Wronskian (Fuchs) count for the triple window (cycle bmd-20261009-ce, 9 October 2026).
\\ V' = Pol_(<d) + sum_i (1+a_i T)^(-lam) Pol_(<m) + span of the three pair functions, D = d + 3m + 3, d = binom(m,2).
\\ Fuchs relation: sum over all points P of (sum of exponents at P - binom(D,2)) = -D(D-1). Lower bounds for the exponent
\\ sums at the singular points (direct sums of exponent classes, each class with orders 0,1,2,...) give an upper bound for
\\ the weight at T = 0: wt_0 <= -D(D-1) - sum_(i=1..3) (E_i - binom(D,2)) - (E_inf - binom(D,2)).
\\ wt_0 <= 2 suffices for full rank (orders <= D+1). Prints the bound for m = 2..10, and the general
\\ formula fitted by interpolation in m.
OUT = "research/results/bmd-20261009-ce/triple-window-fuchs.txt";
lam = 3/2;
bnd(m) = {
  my(d = m * (m - 1) / 2, D = d + 3 * m + 3, B = D * (D - 1) / 2);
  \\ at -1/a_i: holomorphic class dim d+2m+1 (orders 0..), singular class (1+a_i T)^(-lam) * G, dim G = m+2
  my(Hd = d + 2 * m + 1, Gd = m + 2, Ep = Hd * (Hd - 1) / 2 + Gd * (Gd - 1) / 2 - lam * Gd);
  \\ at infinity (u = 1/T): integer class: polynomials T^0..T^(d-1) (orders -(d-1)..0) and the three pairs (orders >= 2 lam,
  \\ 2 lam+1, 2 lam+2); half-integer class: 3m singles with orders >= lam-(m-1), consecutive
  my(Einf = sum(j = 0, d - 1, -j) + (2 * lam) + (2 * lam + 1) + (2 * lam + 2) + sum(j = 0, 3 * m - 1, lam - (m - 1) + j));
  -D * (D - 1) - 3 * (Ep - B) - (Einf - B);
}
{
  for (m = 2, 10, write(OUT, "m = ", m, ": Fuchs bound on the weight at T = 0: ", bnd(m)));
  write(OUT, "interpolated: ", polinterpolate(vector(6, i, i + 1), vector(6, i, bnd(i + 1)), 'm));
}
