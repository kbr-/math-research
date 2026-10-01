\\ Two-block monomial Wronskians (3 October 2026; cycle bmd-20261003-zzs; outside lead of the far-radius review).
\\ Question: is W(x^a P_<p (+) (1+x)^b P_<q) equal to c x^alpha (1+x)^beta with no far zeros, and is c the leading-order
\\ value n^(pq) W(f) W(g) of the sigma-step, up to a closed product? Exact over Q: pull x^a from the X columns and
\\ (1+x)^b from the Y columns; entries (a+i)_r x^(i-r) and (b+i)_r (1+x)^(i-r) (falling factorials).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ff(a, r) = prod(s = 0, r - 1, a - s);
twoblock(a, b, p, q) = {
  my(K = p + q, M = matrix(K, K, r, c, if (c <= p, ff(a + c - 1, r - 1) * x^(c - r), ff(b + c - p - 1, r - 1) * (1 + x)^(c - p - r))));
  my(D = matdet(M), nu = numerator(D), de = denominator(D), v0 = valuation(nu, x), v1 = valuation(nu, 1 + x), far = nu / x^v0 / (1 + x)^v1);
  [poldegree(far), far, v0, v1, de];
}
{
foreach ([[-7/2 - 20, -7/2 - 20], [-1/2 - 30, 1/2 - 30], [1/3, 2/5], [-7/2 - 40, -3 - 40]], ab,
  for (p = 1, 4, for (q = 1, 4,
    my(R = twoblock(ab[1], ab[2], p, q));
    emit(Str("a=", ab[1], " b=", ab[2], " p=", p, " q=", q, ": far-part degree ", R[1], if (R[1] == 0, Str(", constant ", factor(R[2])), Str(", far part ", R[2])))))));
}
