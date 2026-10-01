\\ Anti-Stokes test for the zeros of the last-step far polynomials (3 October 2026; cycle bmd-20261003-zt).
\\ Heuristic: after the polynomial block is removed, F_(b-1) is built from functions of size |1+x|^(-N), |x|^(-N) and
\\ |x(1+x)|^(-N), N ~ n = R_e; zeros of such exponential-type Wronskians accumulate where two dominant sizes balance:
\\   C1: |x| = |1+x| (Re x = -1/2),  C2: |1+x| = 1,  C3: |x| = 1.
\\ For each root r of W_(b-1) (e = 1, 2, 3; saved) let a = log|r|, c = log|1+r| and dist = min(|a - c|, |c|, |a|) (log scale).
\\ Reports the mean and maximum of dist, and the share of roots within 0.05 / 0.1 / 0.2 of some curve, per curve.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
{
for (e = 1, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), r = polroots(W), m = #r, D = vector(m), which = vector(3));
  for (i = 1, m, my(a = log(abs(r[i])), c = log(abs(1 + r[i])), v = [abs(a - c), abs(c), abs(a)]);
    D[i] = vecmin(v); for (j = 1, 3, if (v[j] == D[i], which[j]++; break)));
  emit(Str("e=", e, ": deg ", m, ", mean dist ", precision(vecsum(D) / m, 6), ", max dist ", precision(vecmax(D), 6),
    ", share within 0.05/0.1/0.2: ", [#select(t -> t < 0.05, D), #select(t -> t < 0.1, D), #select(t -> t < 0.2, D)], "/", m,
    ", nearest curve counts [Re=-1/2, |1+x|=1, |x|=1]: ", which)));
}
