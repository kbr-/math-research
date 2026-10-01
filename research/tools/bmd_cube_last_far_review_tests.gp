\\ Cheap tests of the far-input route review (3 October 2026; cycle bmd-20261003-zp), on the saved last even-peeling
\\ far polynomials W_(b-1), b = e + 2, e = 1, 2, 3 (research/results/bmd-20261003-zl/W_last_e*.gp).
\\ (a) Real-rootedness (AT-system / multiple-orthogonality and interlacing leads): number of real roots, and how many
\\     lie in (-1, 0).
\\ (b) Frobenius transfer (reduction-mod-p lead): modulo a prime p > d = R_b, p-th powers are constants for d/dx, so
\\     x^(-7/2) = x^((p-7)/2) (x^(-1/2))^p etc.; W(F_(b-1)) mod p is a constant multiple of W(P_p), with P_p the polynomial
\\     space with exponents shifted into [0, p).  Check: the non-branch part of W(P_p) equals W_(b-1) mod p up to a scalar.
\\ (c) Factorization patterns of W_(b-1) mod p for primes p < 400 not dividing the leading coefficient: primes with a
\\     repeated factor, and primes where W mod p splits into linear factors; at the latter, the p-adic Newton
\\     polygons of W at x = 0 and x = -1 (a segment of horizontal length l carries l roots of equal valuation; a triple
\\     root needs a segment of length >= 3 at its residue point).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
\\ blocks [g, b, cnt]: (1+x)^g x^b P_<cnt, with half-integral g, b shifted into [0, p) modulo p
hp(a, p) = lift(Mod(numerator(a), p) / denominator(a));
pblocks(e, p) = apply(B -> [hp(B[1], p), hp(B[2], p), B[3]], [[0, 0, Rn(e)], [-3, 0, 1], [0, -3, 1], [-7/2, 0, 4 * e], [0, -7/2, 4 * e], [-5/2, -7/2, 4]]);
wronsk(L, p) = {
  my(V = List());
  foreach (L, B, for (j = 0, B[3] - 1, listput(V, Mod(1, p) * (1 + 'x)^B[1] * 'x^(B[2] + j))));
  my(d = #V, M = matrix(d, d));
  for (j = 1, d, my(h = V[j]); for (i = 1, d, M[i, j] = h; h = deriv(h, 'x)));
  matdet(M);
}
strip(P) = { if (P == 0, return(0)); my(a = valuation(P, 'x)); P /= 'x^a; while (subst(P, 'x, -1) == 0, P /= (1 + 'x)); P; }
{
for (e = 1, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), d = Rn(e + 2), rr = polrootsreal(W), lc = pollead(W));
  emit(Str("e=", e, ": deg W = ", poldegree(W), ", real roots ", #rr, ", in (-1,0): ", #select(r -> r > -1 && r < 0, rr)));
  forprime (p = d + 1, d + 12,
    if (lc % p == 0, next);
    my(P = strip(wronsk(pblocks(e, p), p)), Wp = W * Mod(1, p));
    emit(Str("  Frobenius transfer p=", p, ": deg stripped W(P_p) = ", poldegree(P), ", proportional to W mod p: ",
      poldegree(P) == poldegree(Wp) && P * pollead(Wp) == Wp * pollead(P))));
  my(rep = List(), split = List());
  forprime (p = 3, 400, if (lc % p == 0, next);
    my(F = factormod(W, p), degs = vector(#F~, i, poldegree(F[i, 1])));
    if (vecmax(F[, 2]) > 1, listput(rep, [p, vecmax(F[, 2])]));
    if (vecmax(degs) == 1, listput(split, p)));
  emit(Str("  primes < 400 with a repeated factor [p, max multiplicity]: ", Vec(rep)));
  emit(Str("  primes < 400 where W splits into linear factors: ", Vec(split)));
  foreach (split, p, my(F = factormod(W, p));
    emit(Str("  p=", p, ": W mod p = ", vector(#F~, i, [F[i, 1], F[i, 2]]),
      "; p-adic Newton slopes at x = 0: ", newtonpoly(W, p), "; at x = -1: ", newtonpoly(subst(W, 'x, 'x - 1), p)))));
}
