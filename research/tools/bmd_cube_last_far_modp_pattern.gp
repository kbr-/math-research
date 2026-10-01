\\ Factorization pattern of the non-branch factor G_p modulo window primes (3 October 2026; cycle bmd-20261003-zr).
\\ For W = W_(b-1) (saved, e = 1, 2, 3) and window primes max(d, 2n) < p <= 2n+8e+7: G_p = W mod p without x, 1+x.
\\ Reports the multiset of irreducible factor degrees over F_p, and whether G_p splits over F_(p^2) (all degrees <= 2),
\\ as for Hasse/supersingular polynomials; also the symmetry x -> -1-x (whether G_p(-1-x) is proportional to G_p) and
\\ x -> 1/x type reciprocity, which would indicate a Moebius-invariant description.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
prop(A, B) = poldegree(A) == poldegree(B) && A * pollead(B) == B * pollead(A);
{
for (e = 1, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), n = Rn(e), d = Rn(e + 2));
  forprime (p = max(d, 2 * n) + 1, 2 * n + 8 * e + 7,
    my(G = W * Mod(1, p)); while (subst(G, 'x, 0) == 0, G /= 'x); while (subst(G, 'x, -1) == 0, G /= (1 + 'x));
    if (poldegree(G) == 0, emit(Str("e=", e, " p=", p, ": G_p constant")); next);
    my(F = factormod(G, p), degs = vecsort(vector(#F~, i, poldegree(F[i, 1]))), m = poldegree(G));
    emit(Str("e=", e, " p=", p, ": deg G_p = ", m, ", factor degrees ", degs, ", max multiplicity ", vecmax(F[, 2]),
      if (vecmax(degs) <= 2, ", splits over F_p^2", ""),
      ", G(-1-x) ~ G: ", prop(subst(G, 'x, -1 - 'x), G), ", reciprocal x^m G(1/x) ~ G: ", prop(polrecip(G), G)))));
}
