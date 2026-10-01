\\ Frobenius-degeneration lead (3 October 2026; cycle bmd-20261003-zp).  For the saved last even-peeling far polynomials
\\ W_(b-1), e = 1, 2, 3 (research/results/bmd-20261003-zl/W_last_e*.gp), and each prime d < p < 2d + 12 (d = R_b) not
\\ dividing the leading coefficient: the multiplicities of x and 1 + x in W mod p, the largest multiplicity of any other
\\ factor, and the p-adic Newton polygons of W at x = 0 and x = -1 as segments [horizontal length, height].
\\ Certificate test: W has no triple root if every other factor mod p is at most double and every Newton segment at
\\ 0 and -1 of length >= 3 has gcd(length, height) = 1 (an irreducible factor over Q_p: distinct roots) -- a segment
\\ of length l with gcd 1 carries l distinct conjugate roots; a segment with gcd g > 1 is undecided at this order.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Rn(n) = n * (2 * n - 1);
segs(P, p) = {
  my(s = newtonpoly(P, p), L = List(), i = 1, v = valuation(P, 'x));
  while (i <= #s, my(j = i); while (j < #s && s[j + 1] == s[i], j++);
    if (s[i] != 0, listput(L, [j - i + 1, (j - i + 1) * s[i]])); i = j + 1);
  Vec(L);
}
ok(S) = { for (k = 1, #S, my(l = S[k][1], h = S[k][2]); if (l >= 3 && (denominator(h) != 1 || gcd(l, h) != 1), return(0))); 1; }
{
for (e = 1, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), d = Rn(e + 2), lc = pollead(W));
  emit(Str("e=", e, ": d = ", d, ", deg W = ", poldegree(W), "; W(0) = ", factor(polcoef(W, 0)), ", W(-1) = ", factor(subst(W, 'x, -1)),
    ", lc = ", factor(lc), ", content ", factor(content(W))));
  forprime (p = d + 1, 2 * d + 12, if (lc % p == 0, next);
    my(F = factormod(W, p), m0 = 0, m1 = 0, mo = 0);
    for (i = 1, #F~, my(f = lift(F[i, 1]));
      if (f == 'x, m0 = F[i, 2], if (f == 'x + 1, m1 = F[i, 2], mo = max(mo, F[i, 2]))));
    if (m0 + m1 == 0 && mo <= 2, next);
    my(S0 = segs(W, p), S1 = segs(subst(W, 'x, 'x - 1), p));
    emit(Str("  p=", p, ": mult of x ", m0, ", of 1+x ", m1, ", max other ", mo,
      "; segments at 0 ", S0, ", at -1 ", S1, "; certificate ", if (mo <= 2 && ok(S0) && ok(S1), "YES", "no")))));
}
