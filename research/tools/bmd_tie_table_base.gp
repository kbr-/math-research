\\ Base case of the confluent tie table (8 October 2026; cycle bmd-20261008-zi), lambda = 3/2.
\\ Tested statements, for every start s >= 0 and c not in {0, 1}:
\\  (E) the 3 x 5 window of E = span{(1+T)^(-3), g, g T/(1+T)}, g = ((1+T)(1+cT))^(-3/2), on T^s..T^(s+4) has rank 3;
\\  (G) the 3 x 4 window of Pol_(<=2) G, G = ((1+T)(1+cT))^(-5/2), on T^s..T^(s+3) has rank 3.
\\ (E) follows from (G) through M = (1+T) d/dT + 3 (see the entry).  Prints, for s = 0..40, the exceptional
\\ polynomial of each window (gcd over Q[c] of the maximal minors, powers of c and c-1 removed), and also the
\\ factor degrees of the consecutive 3 x 3 Toeplitz minor of (G) on T^s..T^(s+2).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
strip(p) = { if (p == 0, return(0)); while (subst(p, 'c, 0) == 0, p = p / 'c); while (subst(p, 'c, 1) == 0, p = p / ('c - 1)); p; }
ess(p) = { my(q = strip(p)); if (q == 0, return("identically zero")); my(f = factor(q / content(q))); if (#f~ == 0, return("none")); [poldegree(q), vector(#f~, i, [poldegree(f[i, 1]), f[i, 2]])]; }
K = 46;
pw(u, e) = (1 + u * 'x + O('x^(K + 1)))^e;
ser(f) = vector(K + 1, k, polcoef(f, k - 1, 'x));
E = [ser(pw(1, -3)), ser(pw(1, -3/2) * pw('c, -3/2)), ser('x * pw(1, -5/2) * pw('c, -3/2))];
G = vector(3, j, ser('x^(j - 1) * pw(1, -5/2) * pw('c, -5/2)));
PE = matrix(3, K + 1, i, j, E[i][j]);
PG = matrix(3, K + 1, i, j, G[i][j]);
gcdwin(P, cols) = { my(g = 0); forsubset([#cols, 3], S, g = gcd(g, matdet(vecextract(P, "..", vecextract(cols, Vec(S)))))); g; }
{
  my(badE = 0, badG = 0);
  for (s = 0, 40,
    my(eE = ess(gcdwin(PE, [s + 1 .. s + 5])), eG = ess(gcdwin(PG, [s + 1 .. s + 4])), t = ess(matdet(vecextract(PG, "..", [s + 1 .. s + 3]))));
    if (eE != "none", badE++); if (eG != "none", badG++);
    emit(Str("s = ", s, ": (E) ", eE, "; (G) ", eG, "; Toeplitz minor on s..s+2: ", t)));
  emit(Str("starts with an exceptional value off c(c-1): (E) ", badE, " of 41, (G) ", badG, " of 41"));
}
quit
