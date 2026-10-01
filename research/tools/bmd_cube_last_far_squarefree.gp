\\ Squarefreeness of the saved last even-peeling far polynomials W_(b-1), b = e + 2, e = 1, 2, 3
\\ (3 October 2026; cycle bmd-20261003-zo).  Records the multiplicity pattern that an Adler-Moser
\\ (monodromy-free, triangular-multiplicity) formulation of the Calogero-Moser lead concerns; squarefree
\\ polynomials fit every such pattern, so this records a fact, not a test.  Reports deg gcd(W, W')
\\ over Q and the rational factorization pattern.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
for (e = 1, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), g, F);
  g = gcd(W, deriv(W)); F = factor(W);
  emit(Str("e=", e, ": deg W = ", poldegree(W), ", deg gcd(W, W') = ", poldegree(g),
    ", irreducible factor degrees with multiplicities ", vector(#F~, i, [poldegree(F[i, 1]), F[i, 2]]))));
}
