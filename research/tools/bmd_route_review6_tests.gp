\\ Tests of the route review of 8 October 2026 (cycle bmd-20261008-a) on the confluent tie window.
\\ L1 (Mahler's perfect binomial systems): the one-point subsystem, rows T^i (1+T)^(-5/2) (i < 2m) and (1+T)^(-3), is
\\    nonsingular on the first 2m + 1 window columns T^d .. T^(d+2m) (the type I problem for (1, (1+T)^(-5/2), (1+T)^(-3))
\\    with degrees (d, 2m, 1), normal by Mahler since the exponent differences 5/2, 3, 1/2 are not integers).  m = 1..8.
\\ L2 (zero coprimeness of bivariate polynomial matrices, Youla-Gnavi): at m = 2 writes a Singular script that tests
\\    whether the ideal of the maximal minors of W(L, c), each divided by their gcd G, is the unit ideal of Q[L, c].
\\ B2 (identifiability of negative binomial mixtures): after T -> -T every window entry is >= 0 for c > 0; records the
\\    sign patterns of all maximal minors at c = 1/5, 1/2, 4/5, 2, 5 (m = 2..4) and whether each pattern is constant
\\    on (0, 1) and on (1, oo).
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k, L) = {
  if (r <= 2 * m, return(bn(-L - 1, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-L, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-2 * L, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-L, a) * bn(-L, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-L - 1, a) * bn(-L, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m, L) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1, L)); }
minors(W) = { my(w = #W, L = List()); for (i = 1, w, for (j = i + 1, w,
  listput(L, matdet(vecextract(W, "..", select(t -> t != i && t != j, [1 .. w])))))); Vec(L); }
{
my(res = List());
for (m = 1, 8, my(W = winmat(m, 3/2), rows = concat([1 .. 2 * m], [3 * m + 1]));
  listput(res, [m, matdet(vecextract(W, rows, [1 .. 2 * m + 1])) != 0]));
emit(Str("L1: [m, one-point subsystem nonsingular on the first 2m+1 columns] = ", Vec(res)));
my(D = minors(winmat(2, 'L)), G = 0, sing);
for (i = 1, #D, G = gcd(G, D[i]));
sing = Str("LIB \"primdec.lib\";\nring r = 0, (L, c), dp;\nideal J = ");
for (i = 1, #D, sing = Str(sing, if (i > 1, ",\n", ""), D[i] / G));
sing = Str(sing, ";\nideal S = std(J);\nprint(\"L2: standard basis of the quotient-minor ideal at m = 2 has \" + string(size(S)) + \" elements, vdim \" + string(vdim(S)) + \", dim \" + string(dim(S)));\nprint(S);\nlist P = primdecGTZ(J);\nfor (int i = 1; i <= size(P); i++) { print(\"L2 component: radical \" + string(P[i][2]) + \", multiplicity \" + string(vdim(std(P[i][1])))); }\nquit;\n");
write("research/results/bmd-20261008-a/zero-coprime-m2.sing", sing);
emit(Str("L2: wrote the Singular script for the ", #D, " quotient minors at m = 2"));
foreach([2, 3, 4], m,
  my(W = winmat(m, 3/2), w = #W, sg = vector(5), cs = [1/5, 1/2, 4/5, 2, 5]);
  W = matrix(#W[, 1], w, r, j, W[r, j] * (-1)^(j - 1));
  my(D = minors(W));
  for (t = 1, 5, sg[t] = apply(x -> sign(subst(x, 'c, cs[t])), D));
  emit(Str("B2, m = ", m, ": minors with all entries >= 0 after T -> -T; sign patterns equal on (0,1): ",
    sg[1] == sg[2] && sg[2] == sg[3], ", on (1,oo): ", sg[4] == sg[5], "; positive/negative/zero counts at c = 1/2: ",
    [#select(x -> x > 0, sg[2]), #select(x -> x < 0, sg[2]), #select(x -> x == 0, sg[2])], ", at c = 2: ",
    [#select(x -> x > 0, sg[4]), #select(x -> x < 0, sg[4]), #select(x -> x == 0, sg[4])])));
}
quit
