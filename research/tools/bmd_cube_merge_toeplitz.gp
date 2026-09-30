\\ Merge of a single root into a collapsed n-cluster (1 October 2026; cycle bmd-20261001-r, route review test).
\\ In V(n,1,...) the class of the single p1 = p0 + e with the cluster point p0 is sqrt((z-p0)(z-p1)) Pol_(<n)((z-p0)^-1),
\\ i.e. (z-p0)^(1-k) sqrt(1 - e/(z-p0)), k = 0..n-1.  Modulo the empty class H^0(O(inf + binom(n,2) p0)), the flat
\\ limit adds the pole orders binom(n,2)+1 .. binom(n,2)+n exactly when the matrix of coefficients
\\ M[k,r] = binom(1/2, j) (-1)^j, j = binom(n,2) + r + 1 - k (the powers of e factor by rows and columns), is invertible;
\\ then the empty class tends to H^0(O(inf + binom(n+1,2) p0)), that of V(n+1,...).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
  for (n = 2, 16, my(C = n*(n-1)/2, M = matrix(n, n, k, r, my(j = C + r + 1 - k); binomial(1/2, j) * (-1)^j));
    emit(Str("n=", n, ": det != 0: ", matdet(M) != 0)));
}
quit
