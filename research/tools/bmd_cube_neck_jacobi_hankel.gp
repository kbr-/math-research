\\ Hankel determinants of Jacobi moments (3 October 2026; cycle bmd-20261003-h)
\\ Tested statement (classical, used for the neck sequence): with mu_m = (alpha)_m/(gamma)_m and beta = gamma - alpha,
\\   det[mu_(i+j)]_(i,j<k) = prod_(j<k) j! (alpha)_j (beta)_j (gamma-1)_j / ((gamma-1)_(2j) (gamma)_(2j))
\\ as an identity of rational functions in alpha, gamma (exact symbolic check for k <= KMAX).  Control: the neck
\\ values H_k for t'_m = binom(-5/2, m+n-4), n = 4, 8, computed directly, versus the formula at
\\ alpha = n - 1/2, gamma = n - 2 times the prefactor, for k <= KMAX.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
poch(x, j) = prod(i = 0, j - 1, x + i);
formula(k, al, ga) = prod(j = 0, k - 1, j! * poch(al, j) * poch(ga - al, j) * poch(ga - 1, j) / (poch(ga - 1, 2 * j) * poch(ga, 2 * j)));
KMAX = if (getenv("KMAX"), eval(getenv("KMAX")), 6);
main() = {
for (k = 1, KMAX,
  my(D = matdet(matrix(k, k, i, j, poch('al, i + j - 2) / poch('ga, i + j - 2))), F = formula(k, 'al, 'ga));
  emit(Str("symbolic k=", k, ": identity ", if (D - F == 0, "holds", "FAILS"))));
\\ neck control: H_k = det[t'_(1+i+j)], t'_m = binom(-5/2, m+n-4); t'_(1+i+j) = (-1)^N (5/2)_N / N!, N = n-3+i+j
for (t = 1, 2, my(n = 4 * t, r = n - 3);
  for (k = 1, KMAX,
    my(H = matdet(matrix(k, k, i, j, binomial(-5/2, i + j - 2 + r))));
    my(mur = poch(5/2, r) / r!, pred = (-1)^(r * k) * mur^k * formula(k, r + 5/2, r + 1));
    emit(Str("neck n=", n, " k=", k, ": H_k = ", H, "; formula ", if (H == pred, "agrees", "DISAGREES"), "; nonzero ", H != 0))));
}
main();
quit
