\\ Appell lead entry four (cycle ker, 9 October 2026): local exponents of the triple window's joint operator.
\\ For the least-order joint operator L = sum_(s<=6) P_s(M) S^s of the pair sequences g_ij (as in
\\ bmd_triple_operator_structure.gp), P_6(M - 6) and P_0(M) are the indicial polynomials at T = 0 and T = infinity of
\\ the associated differential operator (of order deg P_s = 6m+6).  Lists their rational roots j/den (den | 12,
\\ |j/den| <= 150) with multiplicities, and the degree left over, for m = 2..5 at two root triples, modulo p = 1000003
\\ (a root modulo p is evidence of a rational root).  Question: are the exponents independent of the moduli, and do
\\ they follow from the F1 parameters (1; 3/2, 3/2; 5/2 - m) and the factor P of degree 3m?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
p = 1000003;
lam = 3/2;
seqs(av, m, N) = {
  my(P = prod(l = 1, 3, (1 + av[l] * 'T)^m), pr = [[1, 2], [1, 3], [2, 3]]);
  vector(3, w, my(a = av[pr[w][1]], b = av[pr[w][2]], s = ((1 + a * 'T) * (1 + b * 'T) + O('T^N))^(-lam), rho = Mod(1, p), c = vector(N));
    for(k = 0, N - 1, if(k > 0, rho *= Mod(k, p) / Mod(k + lam - m, p)); c[k + 1] = rho * Mod(polcoef(s, k, 'T), p));
    my(S = Mod(1, p) * P * Ser(c, 'T)); vector(N, k, polcoef(S, k - 1, 'T)));
}
op6(X, K0) = {
  for(q = 6, 60, my(r = 6, nun = (r + 1) * (q + 1), per = nun \ 3 + 10);
    my(A = matrix(3 * per, nun, i, j, my(w = (i - 1) \ per + 1, k = K0 + (i - 1) % per, s = (j - 1) \ (q + 1), e = (j - 1) % (q + 1)); Mod(k, p)^e * X[w][k + s + 1]));
    my(K = matker(A)); if(#K, return([q, #K, vector(r + 1, s, Pol(vector(q + 1, e, K[(s - 1) * (q + 1) + q + 2 - e, 1]), 'M))])));
  0;
}
rroots(f) = {
  my(L = List(), g = f); for(den = 1, 12, if(12 % den, next); for(j = -150 * den, 150 * den, if(gcd(j, den) != 1, next); my(r = Mod(j, p) / den, k = 0);
    while(poldegree(g) > 0 && subst(g, (M), r) == 0, g = g / ((M) - r); k++); if(k, listput(L, [j / den, k]))));
  [vecsort(Vec(L), 1), poldegree(g)];
}
{
  foreach([[2, 5, -3], [1/3, -4, 7/2]], av, for(m = 2, 5, my(X = seqs(av, m, 900), R = op6(X, 3 * m + 5), Pc = R[3]);
    emit(Str("roots ", av, " m=", m, ": deg ", R[1], "; P_6(M-6) roots [root, mult] (exponents at 0): ", rroots(subst(Pc[7], (M), (M) - 6))));
    emit(Str("        P_0(M) roots (exponents at infinity, up to sign): ", rroots(Pc[1])))));
}
quit;
