\\ Block structure of the reduced merge far space (5 October 2026; cycle bmd-20261005-l).  With lem:cube-far-euler-image,
\\ X(n,k) = w^(P+2) (P3' + w^gamma P4').  Question: does the Wronskian of the polynomial block P3' (dimension k-1) have zeros
\\ off {0,1}?  If not, P3' is determined by its local exponents at 0, 1, infinity (a hypergeometric-type space) and the far
\\ points come only from the coupling with the n-dimensional block.  Output per (n,k): degrees of P3' generators, the
\\ factorization type of W(P3'), and the same for W(P4').
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
closed(E, s) = {
  my(q = #E, phi = x -> prod(i = 1, q, x - E[i]));
  sum(r = 0, q, sum(i = 0, r, (-1)^(r - i) * binomial(r, i) * phi(s + i)) * binomial(1/2, r) * (-1)^r * 'w^r * (1 - 'w)^(q - r));
}
wr(v) = { my(d = #v, M = matrix(d, d)); for (i = 1, d, my(g = v[i]); for (m = 1, d, M[i, m] = g; g = deriv(g, 'w))); matdet(M); }
offbranch(R) = { if (R == 0, return(-1)); while (subst(R, 'w, 0) == 0, R = R / 'w); while (subst(R, 'w, 1) == 0, R = R / ('w - 1)); poldegree(R); }
{
foreach(eval(getenv("NK")), v,
  my(n = v[1], k = v[2], C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)));
  my(P3 = vector(k - 1, j, 'w^(j - 1) * closed(E, j - 1) / 'w^(P + 2)));
  my(P4 = vector(n, j, 'w^(j - 1) * closed(E, 1/2 - (n - 1) + j - 1) / 'w^((k - 1) * n)));
  emit(Str("(n,k) = ", [n, k], ": deg P3' ", apply(poldegree, P3), ", W(P3') zeros off {0,1}: ", offbranch(wr(P3)),
    "; deg P4' ", apply(poldegree, P4), ", W(P4') zeros off {0,1}: ", offbranch(wr(P4)))));
}
quit;
