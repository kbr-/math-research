\\ Hankel determinants of the binomials c_n = binom(-3/2, n) (8 October 2026; cycle bmd-20261008-zp).
\\ Input of the deficiency-one deep-row reduction: H_p = det[c_(j+k-1)]_(j,k=1..p) must be nonzero (window negatives
\\ {-1..-p}).  Prints H_p for p <= 12, factored, and for p <= 4 the number of vanishing p x p minors
\\ det[c_(j-1+k)]_(j <= p, k in N) over all negative sets N of size p in {1..8} (non-window sets).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
cc(n) = binomial(-3/2, n);
{
  for (p = 1, 12, my(H = matdet(matrix(p, p, j, k, cc(j + k - 1)))); emit(Str("p = ", p, ": H_p = ", H, (if (H == 0, "  ZERO", "")))));
  for (p = 1, 4, my(z = 0, tot = 0);
    forsubset([8, p], N, tot++; if (matdet(matrix(p, p, j, i, cc(j - 1 + N[i]))) == 0, z++));
    emit(Str("p = ", p, ": vanishing minors over negative sets N in {1..8}: ", z, " of ", tot)));
}
quit
