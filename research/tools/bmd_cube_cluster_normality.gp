\\ Diagonal normality of the ratio system of a cluster (30 September 2026; cycle bmd-20260930-zzb).
\\ For a cluster of m shapes b_1..b_m, F_j(v) = sqrt((1 - b_j v)/(1 - b_1 v)) - 1 = sum_(k >= 1) f^(j)_k v^k,
\\ j = 2..m.  Delta_(m,d) = det[ f^(j)_(a+e) ]_(rows a = 1..(m-1)(d+1); columns (j, e), j = 2..m, 0 <= e <= d).
\\ thm:cube-cluster-cost-bound needs Delta_(m,d) != 0 for the d it uses.  This script evaluates Delta_(m,d) modulo
\\ the prime q = 2^61 - 1 (a nonzero residue proves the rational value nonzero, hence Delta_(m,d) not identically
\\ zero as a polynomial in the shapes) at two rational shape vectors, for 2 <= m <= 30 and (m-1)(d+1) <= 60.
\\ Control: m = 2 must be nonzero for every d (Jacobi weight on [b_1, b_2]).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
PR = 2^61 - 1;
Delta(b, d) = {
  my(m = #b, S = (m - 1) * (d + 1), K = S + d + 2);
  my(f = vector(m - 1, jj, Vec(((1 - b[jj + 1] * x + O(x^(K + 1))) / (1 - b[1] * x + O(x^(K + 1))))^(1/2) - 1)));
  \\ Vec of a series starting at x^1: f[jj][k] = coefficient of x^k
  my(M = matrix(S, S, a, col, my(jj = (col - 1) \ (d + 1) + 1, e = (col - 1) % (d + 1)); Mod(f[jj][a + e], PR)));
  matdet(M);
}
main() = {
  my(bad = List(), count = 0);
  for (m = 2, 30,
    my(b1 = vector(m, k, (7 * k^2 - 3 * k + 1) / (k + 2)), b2 = vector(m, k, (-1)^k * (5 * k + 2) / (k^2 + 1)), ds = List());
    for (d = 0, 60, if ((m - 1) * (d + 1) > 60, break);
      my(z1 = Delta(b1, d), z2 = Delta(b2, d)); count++;
      if (z1 == 0 || z2 == 0, listput(bad, [m, d, z1 == 0, z2 == 0])); listput(ds, d));
    emit(Str("m=", m, ": d = 0..", vecmax(Vec(ds)), " checked")));
  emit(Str(count, " determinants; zero cases [m, d, zero at b1, zero at b2]: ", Vec(bad)));
}
main();
quit
