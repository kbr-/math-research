\\ Five-root Taylor cofactor and its flow order at distinct roots (cycle bmd-20261009-bo, 9 October 2026).
\\ F = p_T0 / Vand^3 (M = 5, R = 10). Question: is j_F(y) = ord_t F(y/(1+ty)) <= 1 at every distinct-root point, i.e. do F and
\\ DF (D = -sum y_i^2 d/dy_i) have no common zero with distinct coordinates? (prop:cube-cblock-spread-bound, part (4).)
\\ (1) F on the slice y = (0, 1, 3, a, b): factorization, and comparison with the pairing product (the degree count
\\     deg F = 3 binom(M,4) = 15 matches the number of pairings, but the recorded tie value rules the product out).
\\ (2) Common zeros of F and G = p_T0' / Vand^3 (equivalently F and DF, at distinct roots) on the slice, with distinct
\\     coordinates: resultant in b, then exact gcds over each factor's number field.
OUT = "research/results/bmd-20261009-bo/five-cofactor-flow.txt";
default(parisizemax, 4 * 10^9);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
pairmat(Y, K) = {
  my(M = #Y, R = M * (M - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, M, for (j = i + 1, M, r++; my(h = H(Y[i], Y[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  P;
}
cof(Y) = { my(M = #Y, R = M * (M - 1) / 2); matdet(pairmat(Y, R - 1)) / prod(i = 1, M, prod(j = i + 1, M, Y[i] - Y[j]))^(M - 2); }
{
  my(Y = [0, 1, 3, 'a, 'b], F = cof(Y));
  write(OUT, "(1) F(0, 1, 3, a, b): total degree ", poldegree(substvec(F, ['a, 'b], ['t * 'a, 't * 'b]), 't), "; factorization:");
  my(fa = factor(F)); for (i = 1, #fa~, write(OUT, "    ", fa[i, 1], "  ^", fa[i, 2]));
  \\ By prop:cube-cblock-spread-bound (4), at distinct roots j_F >= 2 iff wt_0(V) >= 2 iff p_T0 = p_T0' = 0, with
  \\ T0' = {0..8, 10}; both minors are divisible by Vand^3. (Earlier runs computed DF directly: five symbolic variables,
  \\ stopped after 30 minutes; then a flowed series in t over Q[a, b], which timed out at 900 s.)
  my(P11 = pairmat(Y, 10), cols = concat([1 .. 9], [11]), G = matdet(matrix(10, 10, i, j, P11[i, cols[j]])) / prod(i = 1, 5, prod(j = i + 1, 5, Y[i] - Y[j]))^3);
  my(Fs = F, DFs = G);
  write(OUT, "    G = p_T0' / Vand^3 on the slice: total degree ", poldegree(substvec(G, ['a, 'b], ['t * 'a, 't * 'b]), 't));
  my(res = polresultant(Fs, DFs, 'b), fr = factor(res));
  write(OUT, "(2) Res_b(F, G) on the slice: ", #fr~, " irreducible factors in a, degrees ", vector(#fr~, i, poldegree(fr[i, 1], 'a)));
  \\ exact common zeros: for each factor q(a), gcd over Q[a]/q of F and G in b, minus coincidences
  my(found = List());
  for (i = 1, #fr~, my(q = fr[i, 1]); if (poldegree(q, 'a) < 1, next);
    \\ the number-field generator needs a variable of lower priority than 'b (a first run used Mod('a, q), which
    \\ PARI read in the wrong ring and returned trivial gcds)
    my(vv = varlower("vv"), A = Mod(vv, subst(q, 'a, vv)), Fb = subst(Fs, 'a, A), Db = subst(DFs, 'a, A), g = gcd(Fb, Db));
    if (poldegree(g, 'b) < 1, next);
    my(co = 'b * ('b - 1) * ('b - 3) * ('b - A), gcoinc = gcd(g, co));
    my(dist = poldegree(g, 'b) - poldegree(gcoinc, 'b));
    my(acoinc = (subst(q, 'a, 0) == 0) || (subst(q, 'a, 1) == 0) || (subst(q, 'a, 3) == 0));
    listput(found, [q, poldegree(g, 'b), dist, acoinc]));
  write(OUT, "    factors q(a) with a common zero: [q, degree of gcd in b, roots b off coincidences, a at a coincidence] =");
  foreach(found, z, write(OUT, "      ", z));
  write(OUT, "    distinct-root common zeros of F and G (weight at least 2) on the slice exist: ", #select(z -> z[3] > 0 && !z[4], Vec(found)) > 0);
}
