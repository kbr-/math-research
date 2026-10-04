\\ Tests of the goal-level review of 9 October 2026 (cycle bmd-20261009-kgf), the triple window's residue matrix C(e)
\\ (prop:cube-triple-window-symmetric-factorization; residues as in research/tools/bmd_triple_window_symmetric_export.gp).
\\ (T2) Total positivity / nodeless symmetric factor: for m = 3..6 and 300 random real triples 0 < a1 < a2 < a3 (rational, seed fixed),
\\      the sign of each of the ten minors det C_S(e(a)); reports, per S, whether the sign is constant (a necessary condition for a
\\      sign-regular kernel R_n(z) on the positive half-line).
\\ (T3) Interlacing in chart B (e1 = 0, e3 = 1): for m = 3..7, the univariate minors G_S(e2) = det C_S(0, e2, 1) for S = {1,2,3} and
\\      {3,4,5}: degrees, number of real roots, and whether their real roots strictly interlace (a Hermite-Biehler-type route to
\\      coprimality, uniform in m if it held).
\\ Usage: env OUT=path gp -q bmd_review_kgf_tests.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
det3(A) = A[1,1] * (A[2,2] * A[3,3] - A[2,3] * A[3,2]) - A[1,2] * (A[2,1] * A[3,3] - A[2,3] * A[3,1]) + A[1,3] * (A[2,1] * A[3,2] - A[2,2] * A[3,1]);
residues(m, e1, e2, e3) = {
  my(N0 = m * (m + 1) / 2, top = N0 + 4, f = 'x^3 - e1 * 'x^2 + e2 * 'x - e3, z = Mod('x, f), s = e1 - z, p = e2 - e1 * z + z^2);
  my(g = vector(top + 1)); g[1] = Mod(1, f);
  for (r = 1, top, g[r + 1] = -(s * (r - 1 + lam) * g[r] + if (r >= 2, p * (r - 2 + 2 * lam) * g[r - 1], 0)) / r);
  my(C = matrix(3, 5));
  for (col = 1, 5, my(n = N0 + col - 1, R = sum(l = 0, m, if (n - l >= 0, binomial(m, l) * z^l * rq(-m, n - l) * g[n - l + 1], 0)));
    my(L = lift(R)); for (i = 0, 2, C[i + 1, col] = polcoef(L, i, 'x)));
  C;
}
{
  setrand(20261009);
  for (m = 3, 6,
    my(Cs = residues(m, 'a, 'b, 'c), signs = matrix(10, 2), subsets = List());
    forsubset([5, 3], S, listput(subsets, Vec(S)));
    my(G = vector(10, t, det3(matrix(3, 3, r, u, Cs[r, subsets[t][u]]))));
    for (trial = 1, 300,
      my(v = vecsort(vector(3, i, (random(10^6) + 1) / 10^5)));
      my(e = [v[1] + v[2] + v[3], v[1] * v[2] + v[1] * v[3] + v[2] * v[3], v[1] * v[2] * v[3]]);
      for (t = 1, 10, my(x = sign(substvec(G[t], ['a, 'b, 'c], e))); if (x > 0, signs[t, 1]++, if (x < 0, signs[t, 2]++))));
    emit(Str("(T2) m = ", m, ": per minor (positive, negative) counts over 300 positive triples: ", vector(10, t, [signs[t, 1], signs[t, 2]]),
      "; constant sign for ", sum(t = 1, 10, signs[t, 1] == 0 || signs[t, 2] == 0), " of 10")));
  for (m = 3, 7,
    my(CB = residues(m, 0, 'b, 1), G1 = det3(matrix(3, 3, r, u, CB[r, u])), G2 = det3(matrix(3, 3, r, u, CB[r, u + 2])));
    my(R1 = polroots(G1), R2 = polroots(G2), real1 = vecsort(real(select(z -> abs(imag(z)) < 1e-20, R1))), real2 = vecsort(real(select(z -> abs(imag(z)) < 1e-20, R2))));
    my(merged = vecsort(concat(apply(x -> [x, 1], real1), apply(x -> [x, 2], real2)), 1), inter = 1);
    for (i = 2, #merged, if (merged[i][2] == merged[i - 1][2], inter = 0));
    emit(Str("(T3) m = ", m, ": deg G_123 = ", poldegree(G1), " (", #real1, " real roots), deg G_345 = ", poldegree(G2), " (", #real2,
      " real roots); real roots strictly interlace: ", if (#merged > 1, inter, "n/a"))));
  quit;
}
