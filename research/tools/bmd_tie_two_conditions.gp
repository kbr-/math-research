\\ Basis factorization of the confluent tie window (8 October 2026; cycle bmd-20261008-s).
\\ u_a(M) = (Q e_a)(M) as in lem:cube-tie-propagation-candidates (q primitive over Q[k, c]).  Every u_a(d+s) is a
\\ combination, rational in c, of the five basis values b = (e_1(d), e_2(d), e_2(d+1), e_3(d), e_3(d+1)).  So the
\\ 3 x 5 matrix U = (u_a(d+s))_(a, s<5) equals B C_5, with B the 3 x 5 block matrix of basis values (rank 3 for
\\ c != 0) and C_5 the 5 x 5 coordinate matrix.  A special value needs det C_5 = 0 and the left kernel vector nu of
\\ C_5 in the row space of B: A_2 = nu_2 e_2(d+1) - nu_3 e_2(d) = 0 and A_3 = nu_4 e_3(d+1) - nu_5 e_3(d) = 0.
\\ Prints, for m = 2, 3, 4: the factor degrees of D = det C_5 off c(c-1) (numerator), the degree off c(c-1) of
\\ gcd(D, A_2 over all adjugate rows), of gcd(D, A_3 ...), and of gcd(D, A_2, A_3); which factors of D are the shifted
\\ apparent factors S(d+j, c) of q_(3m); and the degree of gcd(D, staircase minors): the gcd of the maximal minors of the
\\ five staircase vectors q(M, c), M = d..d+4, padded into C^(3m+5) (0 = staircase independent at every root of D).
default(parisizemax, 6 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
st(q) = { if (q == 0, return(0)); q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q; }
bn(a, k) = if (k < 0, 0, binomial(a, k));
coords(Sh, J) = {
  my(v = vector(J + 1)); v[1] = [1, 0]; v[2] = [0, 1];
  for (j = 2, J, v[j + 1] = subst(Sh[1], 'k, 'k + j - 2) * v[j - 1] + subst(Sh[2], 'k, 'k + j - 2) * v[j]);
  v;
}
{
MS = if (getenv("MS") == 0 || getenv("MS") == "", [2, 3, 4], eval(getenv("MS")));
foreach(MS, m,
  my(n = 3 * m, d = m * (m - 1) / 2, A = matrix(n, n + 1), q, C = matrix(5, 5), D, adj, e2, e3, G2 = 0, G3 = 0, G23 = 0,
     rf = r -> prod(i = 0, r - 1, -('k + i - 2 * m + 7/2) / ('k + i + 1)),
     rg = r -> prod(i = 0, r - 1, -'c * ('k + i - m + 5/2) / ('k + i + 1)),
     S2 = [-'c * ('k + 3) / ('k + 2), -(1 + 'c) * ('k + 5/2) / ('k + 2)],
     S3 = [-'c * ('k + 3) / ('k + 1), -((1 + 'c) * ('k + 1) + (3 + 'c) / 2) / ('k + 1)]);
  for (j = 0, 2 * m - 1, for (r = 0, n, A[j + 1, r + 1] = rf(r) * ('k + r)^j));
  for (j = 0, m - 1, for (r = 0, n, A[2 * m + j + 1, r + 1] = rg(r) * ('k + r)^j));
  q = matker(A)[, 1]; my(den = 1); for (r = 1, n + 1, den = lcm(den, denominator(q[r]))); q = q * den;
  my(g = 0); for (r = 1, n + 1, g = gcd(g, q[r])); q = q / g;
  \\ row 1 of C: u_1(d+s)/e_1(d), e_1(k) = (-1)^k (k+1)(k+2)/2
  for (s = 0, 4, C[1, s + 1] = sum(r = 0, n, subst(q[r + 1], 'k, d + s) * (-1)^(s + r) * (d + s + r + 1) * (d + s + r + 2) / ((d + 1) * (d + 2))));
  foreach([[S2, 2], [S3, 4]], SB, my(Cs = coords(SB[1], n + 6));
    for (s = 0, 4, my(v = sum(r = 0, n, subst(q[r + 1], 'k, d + s) * subst(Cs[s + r + 1], 'k, d)));
      C[SB[2], s + 1] = v[1]; C[SB[2] + 1, s + 1] = v[2]));
  D = st(numerator(matdet(C)));
  e2 = [polcoef(((1 + 'x) * (1 + 'c * 'x))^(-3/2) + O('x^(d + 3)), j, 'x) | j <- [d, d + 1]];
  e3 = [polcoef('x * (1 + 'x)^(-5/2) * (1 + 'c * 'x)^(-3/2) + O('x^(d + 3)), j, 'x) | j <- [d, d + 1]];
  adj = matadjoint(C);
  \\ (cycle bmd-20261008-u, env RESID=1 only) normalized residuals at the roots of D: |sin| of the angle between the
  \\ e_2 block of the left kernel vector nu of C_5(z) and (e_2(d), e_2(d+1)), same for e_3; minimum per irreducible factor
  if (getenv("RESID") == "1",
    my(F = factor(D), res = List()); default(realprecision, 80);
    for (t = 1, #F[, 1], my(mn2 = 1e9, mn3 = 1e9);
      foreach(polroots(F[t, 1]), z, my(Az = substvec(adj, ['c], [z]), b = 1, nu, e2z = subst(e2, 'c, z), e3z = subst(e3, 'c, z), s2, s3);
        for (i = 2, 5, if (norml2(Az[i, ]) > norml2(Az[b, ]), b = i)); nu = Az[b, ];
        s2 = abs(nu[2] * e2z[2] - nu[3] * e2z[1]) / sqrt(norml2([nu[2], nu[3]]) * norml2(e2z));
        s3 = abs(nu[4] * e3z[2] - nu[5] * e3z[1]) / sqrt(norml2([nu[4], nu[5]]) * norml2(e3z));
        mn2 = min(mn2, s2); mn3 = min(mn3, s3));
      listput(res, [poldegree(F[t, 1], 'c), round(mn2 * 10^6) / 10.^6, round(mn3 * 10^6) / 10.^6]));
    emit(Str("m = ", m, ": [factor degree, min |sin| e_2 block, min |sin| e_3 block] over the roots of D: ", Vec(res)));
    next);
  \\ (cycle bmd-20261008-u, env RES=1 only) (a) the resultant in c of D and A_2 (fixed integer combination of the adjugate rows): its prime factors
  \\ below 10^4 and the size of the cofactor; (b) Dumas test: the p-adic Newton polygon of the minor of U on columns
  \\ 0, 2, 4 (essential part) at p = 2, 3, 5, 7: number of segments and slope denominators
  if (getenv("RES") == "1",
    my(a2 = st(numerator(sum(i = 1, 5, [3, -5, 7, 11, -13][i] * (adj[i, ][2] * e2[2] - adj[i, ][3] * e2[1])))), R, sm = List(), Bm = matrix(3, 5), Mn, np = List());
    R = abs(numerator(polresultant(D, a2, 'c))); if (R == 0, emit(Str("m = ", m, ": resultant zero")); next);
    forprime(p = 2, 10^4, my(v = valuation(R, p)); if (v > 0, listput(sm, [p, v]); R /= p^v));
    emit(Str("m = ", m, ": Res_c(D, A_2): primes below 10^4 with exponents ", Vec(sm), "; remaining cofactor has ", #digits(R), " digits"));
    Bm[1, 1] = (-1)^d * (d + 1) * (d + 2) / 2; Bm[2, 2] = e2[1]; Bm[2, 3] = e2[2]; Bm[3, 4] = e3[1]; Bm[3, 5] = e3[2];
    Mn = st(numerator(matdet(vecextract(Bm * C, "..", [1, 3, 5])))); Mn = Mn / content(Mn);
    foreach([2, 3, 5, 7], p, my(NP = newtonpoly(Mn, p)); listput(np, [p, #Set(NP), apply(x -> denominator(x), Set(NP))]));
    emit(Str("m = ", m, ": minor (0,2,4) of degree ", poldegree(Mn, 'c), ": Newton polygon [p, distinct slopes, slope denominators]: ", Vec(np)));
    next);
  \\ left kernel of C at a root: rows of adj(C) (adj(C) C = det I)
  for (i = 1, 5, my(nu = adj[i, ], a2 = numerator(nu[2] * e2[2] - nu[3] * e2[1]), a3 = numerator(nu[4] * e3[2] - nu[5] * e3[1]));
    G2 = gcd(G2, a2); G3 = gcd(G3, a3); G23 = gcd(G23, gcd(a2, a3)));
  my(F = factor(D), Sf = 1, Fq = factor(q[n + 1]), sh = List(), St, Gs = 0);
  for (t = 1, #Fq[, 1], if (poldegree(Fq[t, 1], 'k) > 0 && poldegree(Fq[t, 1], 'c) > 0, Sf = Fq[t, 1]));
  for (j = 0, 6, my(v = st(subst(Sf, 'k, d + j))); for (t = 1, #F[, 1], if (poldegree(gcd(F[t, 1], v), 'c) > 0, listput(sh, [t, j]))));
  St = matrix(3 * m + 5, 5, i, j, my(r = i - j); if (r >= 0 && r <= n, subst(q[r + 1], 'k, d + j - 1), 0));
  forsubset([3 * m + 5, 5], R, Gs = gcd(Gs, matdet(vecextract(St, Vec(R), ".."))); if (Gs != 0 && poldegree(st(gcd(D, Gs)), 'c) == 0, break));
  \\ (cycle bmd-20261008-t; MS env selects m, default [2, 3, 4]) gcd of the 3 x 3 minors of U = B C_5 itself, off c(c-1)
  my(Bm = matrix(3, 5), U, Gu = 0); Bm[1, 1] = (-1)^d * (d + 1) * (d + 2) / 2; Bm[2, 2] = e2[1]; Bm[2, 3] = e2[2]; Bm[3, 4] = e3[1]; Bm[3, 5] = e3[2];
  U = Bm * C; forsubset([5, 3], R, Gu = gcd(Gu, numerator(matdet(vecextract(U, "..", Vec(R))))));
  emit(Str("m = ", m, ": gcd of the 3 x 3 minors of U, off c(c-1), has degree ", poldegree(st(Gu), 'c)));
  my(L = List()); forsubset([5, 3], R, my(f = st(numerator(matdet(vecextract(U, "..", Vec(R)))))); listput(L, [Vec(R) - [1, 1, 1], poldegree(f, 'c), if (f == 0, "zero", apply(g -> poldegree(g, 'c), factor(f)[, 1]~))]));
  emit(Str("m = ", m, ": minors [columns s, essential degree, factor degrees]: ", Vec(L)));
  \\ (cycle bmd-20261008-u) valuations at c = 0 and degrees (c = oo) of D and of the A_2 numerators
  emit(Str("m = ", m, ": numerator of det C_5: c-order ", valuation(numerator(matdet(C)), 'c), ", degree ", poldegree(numerator(matdet(C)), 'c),
    "; A_2 over adjugate rows: c-orders ", vector(5, i, my(f = numerator(adj[i, ][2] * e2[2] - adj[i, ][3] * e2[1])); if (f == 0, -1, valuation(f, 'c))),
    ", degrees ", vector(5, i, poldegree(numerator(adj[i, ][2] * e2[2] - adj[i, ][3] * e2[1]), 'c))));
  emit(Str("m = ", m, ": factors of D sharing a root with S(d+j, c) (factor index, j): ", Vec(sh),
    "; degree of gcd(D, staircase minors) off c(c-1): ", poldegree(st(gcd(D, Gs)), 'c)));
  emit(Str("m = ", m, ": det C_5 off c(c-1) has degree ", poldegree(D, 'c), ", factor degrees ", vector(#F[, 1], t, [poldegree(F[t, 1], 'c), F[t, 2]]),
    "; degree off c(c-1) of gcd(D, A_2) = ", poldegree(st(gcd(D, G2)), 'c), ", of gcd(D, A_3) = ", poldegree(st(gcd(D, G3)), 'c),
    ", of gcd(D, A_2, A_3) = ", poldegree(st(gcd(D, G23)), 'c))));
}
quit
