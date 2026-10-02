\\ Normality of the extended confluent Hermite-Pade table (8 October 2026; cycle bmd-20261008-zh), lambda = 3/2.
\\ Tested statement (conj:cube-confluent-tie-table-normality): for all a, b >= 0, every start s >= 0 and every
\\ c not in {0, 1}, the window of V(a,b) = (1+T)^(-5/2) Pol_(<a) + (1+cT)^(-3/2) Pol_(<b) + span{(1+T)^(-3),
\\ ((1+T)(1+cT))^(-3/2), T (1+T)^(-5/2) (1+cT)^(-3/2)} on the columns T^s .. T^(s+a+b+4) has full rank a+b+3.
\\ The confluent tie window of lem:cube-confluent-tie-reduction is (a, b, s) = (2m, m, binom(m,2)).
\\ Prints, for each (a, b, s), the exceptional polynomial (gcd over Q[c] of the maximal minors, powers of c and
\\ c-1 removed): its degree and factor degrees, or "none".  Range: a <= 5, b <= 3, s <= 4.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
strip(p) = { if (p == 0, return(0)); while (subst(p, 'c, 0) == 0, p = p / 'c); while (subst(p, 'c, 1) == 0, p = p / ('c - 1)); p; }
ess(p) = { my(q = strip(p)); if (q == 0, return("identically zero")); my(f = factor(q / content(q))); if (#f~ == 0, return("none")); [poldegree(q), vector(#f~, i, [poldegree(f[i, 1]), f[i, 2]])]; }
K = 5 + 3 + 4 + 5;
pw(u, e) = (1 + u * 'x + O('x^(K + 1)))^e;
ser(f) = vector(K + 1, k, polcoef(f, k - 1, 'x));
PHI = vector(5, i, ser('x^(i - 1) * pw(1, -5/2)));
PSI = vector(3, n, ser('x^(n - 1) * pw('c, -3/2)));
EXT = [ser(pw(1, -3)), ser(pw(1, -3/2) * pw('c, -3/2)), ser('x * pw(1, -5/2) * pw('c, -3/2))];
bad = 0;
{
  for (a = 0, 5, for (b = 0, 3,
    my(rows = concat([PHI[1 .. a], PSI[1 .. b], EXT]), r = #rows, P = matrix(r, K + 1, i, j, rows[i][j]), line = List());
    for (s = 0, 4,
      my(g = 0, cols = [s + 1 .. s + r + 2]);
      forsubset([#cols, r], S, g = gcd(g, matdet(vecextract(P, "..", vecextract(cols, Vec(S))))));
      my(e = ess(g)); if (e != "none", bad++); listput(line, Str("s=", s, ": ", e)));
    emit(Str("(a, b) = (", a, ", ", b, "): ", Vec(line)))));
  emit(Str("windows with an exceptional value off c(c-1): ", bad, " of 120"));
}
quit
