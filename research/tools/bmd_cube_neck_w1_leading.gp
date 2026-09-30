\\ Leading term of the neck windows with block size w = 1 (30 September 2026; cycle bmd-20260930-zh).
\\ Tested statement: for w = 1 and 1 <= c <= l, the level sum at level c(c-1) of the window W_c is
\\   S = +- prod_{j<c} binom(-lambda, j) * t'_1^(l-c) * H_c * G_c,
\\ with H_c = det[t'_(s+j)]_{s=1..c, j=0..c-1} (a Hankel determinant of t'_m = binom(-5/2, m+n-1)) and G_c the
\\ determinant of the high parts of y^(-1) Delta_j phi mod U (j = c..l-1) on the columns M..M+l-c-1, in the
\\ divided-difference normalization; and every level below c(c-1) sums to zero.  The level sums are computed
\\ from the rows f_s = (tau - 1) y^(n-1) phi_s directly (Cauchy-Binet over one pole order per double, as in
\\ bmd_cube_neck_psi_sums.gp), independently of the formula; the ratio S / formula is printed (+-1 expected).
\\ Also checked: reversing columns, det[binom(x, a+i+j)]_{i,j<c} = +- det[binom(x, sigma+i-j)], sigma = a+c-1, the
\\   rectangle Schur function s_(c^sigma)(1^x) = prod over cells (x + content)/hook (dual Jacobi-Trudi and the
\\   hook-content formula, as in hierarchical attainment), nonzero at non-integer x; checked at x = -5/2.
\\ Modulo 2^61 - 1 at beta = (2, -3, 5, -7)/3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
poch(x, k) = prod(i = 0, k - 1, x + i);
hankform(x, a, c) = my(sg = a + c - 1); prod(r = 0, sg - 1, prod(k = 0, c - 1, (x + k - r) / (c - k + sg - r - 1)));
run(e, l) = {
  my(n = 4 * e, M = n * l, K = l, extra = l * (l - 1), qmax = 1 + extra, Y = M + K + qmax + 8, lam = -7/2);
  my(bet = vector(l, s, Mod([2, -3, 5, -7][s], q0) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q0) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A, W = Y + qmax);
  my(red(v) = for (d = 0, M - 1, my(x = v[d + qmax + 1]); if (x != 0, for (r = 1, Y, v[r + qmax] -= x * G[d + 1, r]))); v);
  \\ psi_{s,q} rows
  my(P = vector(l, s, vector(qmax, q, my(v = vector(W)); for (r = 1, Y, my(col = r - 1 - q); if (col >= -qmax, v[col + qmax + 1] += phi[s][r])); red(v))));
  my(tp = vector(2 * qmax + 4, m, Mod(binomial(-5/2, m + n - 1), q0)));
  \\ divided-difference coefficients (Newton): Delta_j = sum_s dd[j][s] * (row s)
  my(dd = vector(l, j, vector(l, s, if (s > j, 0, 1 / prod(i = 1, j, if (i == s, 1, bet[s] - bet[i]))))));
  for (cc = 1, l,
    my(cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)), L0 = cc * (cc - 1));
    my(S = vector(extra + 1));
    forvec(qv = vector(l, s, [1, qmax]), my(lev = vecsum(qv) - l); if (lev <= L0,
      my(Mx = matrix(K, K, a, b, P[a][qv[a]][cols[b]]), d = matdet(Mx));
      if (d != 0, S[lev + 1] += d * prod(s = 1, l, tp[qv[s]]))));
    my(firstnz = -1); for (L = 0, L0, if (S[L + 1] != 0, firstnz = L; break));
    \\ formula: Hankel H_c and G_c from divided differences of psi_{.,1} for j = cc..l-1 on the high columns
    my(Hc = matdet(matrix(cc, cc, s, j, tp[s + j - 1])));
    my(Gc = if (cc == l, 1, matdet(matrix(l - cc, l - cc, a, b, my(j = cc + a - 1); sum(s = 1, l, dd[j + 1][s] * P[s][1][cols[cc + b]])))));
    my(form = prod(j = 0, cc - 1, Mod(binomial(lam, j), q0)) * tp[1]^(l - cc) * Hc * Gc);
    \\ S computed in the original rows equals the divided-difference version times det(dd)^(-1)
    my(ddet = prod(j = 0, l - 1, dd[j + 1][j + 1]), ratio = if (form != 0, S[L0 + 1] * ddet / form, "form zero"));
    emit(Str("e=", e, " l=", l, " c=", cc, ": first nonzero level ", firstnz, " (predicted ", L0, "); H_c ",
      if (Hc != 0, "nonzero", "ZERO"), ", G_c ", if (Gc != 0, "nonzero", "ZERO"), "; S / formula = ", ratio)));
}
\\ G_c alone (no level sums), for larger l: nonvanishing of the genericity determinant for every c < l
gonly(e, l) = {
  my(n = 4 * e, M = n * l, K = l, qmax = 2, Y = M + K + 8, lam = -7/2);
  my(bet = vector(l, s, Mod(prime(s + 1) * (-1)^s, q0) / 3));
  my(phi = vector(l, s, vector(Y, r, Mod(binomial(lam, r - 1), q0) * bet[s]^(r - 1))));
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A, W = Y + qmax);
  my(P1 = vector(l, s, my(v = vector(W)); for (r = 1, Y, my(col = r - 2); if (col >= -qmax, v[col + qmax + 1] += phi[s][r]));
    for (d = 0, M - 1, my(x = v[d + qmax + 1]); if (x != 0, for (r = 1, Y, v[r + qmax] -= x * G[d + 1, r]))); v));
  my(dd = vector(l, j, vector(l, s, if (s > j, 0, 1 / prod(i = 1, j, if (i == s, 1, bet[s] - bet[i]))))));
  my(res = vector(l - 1, cc, matdet(matrix(l - cc, l - cc, a, b, my(j = cc + a - 1); sum(s = 1, l, dd[j + 1][s] * P1[s][M + b - 1 + qmax + 1]))) != 0));
  emit(Str("e=", e, " l=", l, ": G_c nonzero for c = 1..l-1: ", res));
}
main() = {
  if (getenv("GONLY"), foreach (eval(getenv("GONLY")), el, gonly(el[1], el[2])); return);
  my(bad = 0);
  for (c = 1, 6, for (a = 1, 30, my(x = -5/2, direct = matdet(matrix(c, c, i, j, binomial(x, a + i + j - 2))));
    if (direct != hankform(x, a, c) && direct != -hankform(x, a, c), bad++)));
  emit(Str("Hankel = +- hook-content rectangle value at x = -5/2, 1 <= c <= 6, 1 <= a <= 30: mismatches ", bad));
  foreach (if (getenv("LS"), eval(getenv("LS")), [2, 3]), l, run(1, l));
}
default(parisizemax, 2000000000);
main();
quit
