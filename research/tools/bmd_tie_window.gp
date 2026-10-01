\\ Tie window matrices (6 October 2026; cycle bmd-20261006-n).  Reduction: at a top tie (roots c and 1 above a deep
\\ cluster of m roots), the limit rows outside the deep cluster's span e_0..e_(R''-1), R'' = binom(m,2), are the series
\\ T^n (1+cT)^(-3/2), T^n (1+T)^(-3/2) (0 <= n < m) and ((1+cT)(1+T))^(-3/2).  On the square window of columns
\\ R''..R''+2m their determinant L(c) is the tie leading coefficient (compare research/results/bmd-20261006-k/); on the
\\ contact window R''..R''+2m+2 the tested statement is: the (2m+1) x (2m+3) matrix has full rank for every c not 0, 1,
\\ i.e. the gcd of its maximal minors has no root off c = 0, 1.  Env MS (list of m), OUT.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
b(k) = if (k < 0, 0, binomial(-3/2, k));
row_t(t, n, cols) = vector(#cols, j, b(cols[j] - n) * t^(cols[j] - n));
row_top(cols) = vector(#cols, j, sum(i = 0, cols[j], b(i) * b(cols[j] - i) * 'c^i));
winmat(m, w) = {
  my(R2 = m * (m - 1) / 2, cols = vector(w, j, R2 + j - 1), rows = List());
  for (n = 0, m - 1, listput(rows, row_t('c, n, cols)));
  for (n = 0, m - 1, listput(rows, row_t(1, n, cols)));
  listput(rows, row_top(cols));
  matrix(#rows, w, i, j, rows[i][j]);
}
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
foreach(eval(getenv("MS")), m,
  my(M = winmat(m, 2 * m + 1), L = strip01(matdet(M)));
  emit(Str("m=", m, " (N=", m + 2, ", top tie): square-window L(c) off c=0,1 factors: ", factor(L)[, 1]~));
  my(W = winmat(m, 2 * m + 3), g = 0);
  forsubset([2 * m + 3, 2 * m + 1], S, g = gcd(g, matdet(vecextract(W, "..", Vec(S)))));
  g = strip01(g);
  emit(Str("  contact window: gcd of maximal minors off c=0,1: ", g, if (poldegree(g) == 0, "  -> full rank for every c != 0,1", "  -> DEFECT")));
  \\ PURE=1 (cycle bmd-20261006-o): list the maximal minors that are c^a (c-1)^b times a constant, i.e. never vanish
  \\ off c = 0, 1 by themselves; such a minor would prove full rank at that m alone.
  if (getenv("PURE") == "1",
    my(pure = List());
    forsubset([2 * m + 3, 2 * m + 1], S, my(d = matdet(vecextract(W, "..", Vec(S)))); if (d != 0 && poldegree(strip01(d)) == 0,
      listput(pure, setminus([1 .. 2 * m + 3], Vec(S)) - [1, 1])));
    emit(Str("  pure minors (dropped window columns, 0-based): ", Vec(pure))));
  \\ ROOTS=1 (cycle bmd-20261006-q): moduli of the roots of L(c) and, over all maximal minors of the contact window, how
  \\ many roots off c = 0, 1 lie on |c| = 1 (to 1e-30) and how many minors have all their roots there.
  if (getenv("ROOTS") == "1",
    my(onc(f) = my(z = polroots(f)); [#select(x -> abs(abs(x) - 1) < 1e-30, Vec(z)), #z]);
    my(rl = onc(L));
    emit(Str("  L(c): roots on |c|=1: ", rl[1], " of ", rl[2], if (rl[2], Str(", moduli range ", round(vecmin(apply(abs, Vec(polroots(L)))) * 10^6) / 10^6., "..", round(vecmax(apply(abs, Vec(polroots(L)))) * 10^6) / 10^6.), "")));
    my(allon = 0, tot = 0, ron = 0, rtot = 0);
    forsubset([2 * m + 3, 2 * m + 1], S, my(d = strip01(matdet(vecextract(W, "..", Vec(S))))); if (poldegree(d) > 0,
      my(r = onc(d)); tot++; ron += r[1]; rtot += r[2]; if (r[1] == r[2], allon++)));
    emit(Str("  contact-window minors: ", allon, " of ", tot, " have all roots on |c|=1; roots on |c|=1 overall: ", ron, " of ", rtot));
    \\ minors with no root on |c| = 1: each is coprime to L if L has all roots on the circle (dropped columns, 0-based)
    my(offc = List());
    forsubset([2 * m + 3, 2 * m + 1], S, my(d = strip01(matdet(vecextract(W, "..", Vec(S))))); if (poldegree(d) > 0 && onc(d)[1] == 0,
      listput(offc, setminus([1 .. 2 * m + 3], Vec(S)) - [1, 1])));
    emit(Str("  minors with no root on |c|=1 (dropped columns): ", Vec(offc))));
  \\ COPRIME=1 (cycle bmd-20261006-r): the dropped column pairs whose minor is coprime to L(c), written relative to the
  \\ window end as [2m+2-j, 2m+2-i], so that a rule uniform in m shows up as the same pair for every m.
  if (getenv("COPRIME") == "1",
    my(cp = List());
    forsubset([2 * m + 3, 2 * m + 1], S, my(d = strip01(matdet(vecextract(W, "..", Vec(S)))));
      if (poldegree(gcd(d, L)) == 0, my(dr = setminus([1 .. 2 * m + 3], Vec(S)) - [1, 1]); listput(cp, vecsort([2 * m + 2 - dr[2], 2 * m + 2 - dr[1]]))));
    emit(Str("  minors coprime to L (dropped columns counted from the window end): ", #cp, ": ", Vec(cp))));
  \\ INTERLACE=1 (cycle bmd-20261006-r): D_m = the minor dropping window columns 2m and 2m+2; report its degree, roots on
  \\ |c| = 1, and the merged angular order of the unit-circle roots of L and D in (0, pi] (L as 'L', D as 'D'), since both
  \\ polynomials have real coefficients and conjugate roots.
  if (getenv("INTERLACE") == "1",
    my(D = strip01(matdet(vecextract(W, "..", setminus([1 .. 2 * m + 3], [2 * m + 1, 2 * m + 3])))));
    my(aL = select(t -> t > 1e-20, apply(z -> arg(z), select(z -> abs(abs(z) - 1) < 1e-30, Vec(polroots(L))))));
    my(zD = Vec(polroots(D)), onD = select(z -> abs(abs(z) - 1) < 1e-30, zD), aD = select(t -> t > 1e-20, apply(z -> arg(z), onD)));
    my(mrg = vecsort(concat(apply(t -> [t, "L"], aL), apply(t -> [t, "D"], aD)), 1), word = concat(apply(x -> x[2], mrg)));
    emit(Str("  D_m: degree ", poldegree(D), ", roots on |c|=1: ", #onD, " of ", #zD, "; gcd with L: ", poldegree(gcd(D, L)),
      "; angular order in (0,pi]: ", word)));
  \\ STABLE=1 (cycle bmd-20261006-s): the width-(2m+2) window W' has the Cramer kernel vector v_j = (-1)^j det(W' minus
  \\ column j); v_(2m+1) and v_(2m) are, up to c^a (c-1)^b and constants, L and D_m.  Report the factor structure of the
  \\ last two coordinates and, for f = v_(2m) + v_(2m+1) and v_(2m) - v_(2m+1) (stripped of c, c-1 only through the
  \\ coordinates' common powers), the number of roots inside, on and outside |c| = 1.
  if (getenv("STABLE") == "1",
    my(Wp = winmat(m, 2 * m + 2), v = vector(2 * m + 2, j, (-1)^(j - 1) * matdet(vecextract(Wp, "..", setminus([1 .. 2 * m + 2], [j])))));
    my(A = v[2 * m + 2], B = v[2 * m + 1], g = gcd(A, B), io(f) = my(z = Vec(polroots(f))); [#select(x -> abs(x) < 1 - 1e-30, z), #select(x -> abs(abs(x) - 1) <= 1e-30, z), #select(x -> abs(x) > 1 + 1e-30, z)]);
    emit(Str("  Cramer coordinates: v_last = ", factor(A)[, 1]~, " exps ", factor(A)[, 2]~, " content ", content(A)));
    emit(Str("    v_prev factors: ", apply(f -> if (poldegree(f) <= 2, f, Str("deg ", poldegree(f))), factor(B)[, 1]~), " exps ", factor(B)[, 2]~, " content ", content(B)));
    my(a = A / g, b = B / g);
    \\ exact Schur-Cohn test over Q: all zeros in the open unit disc (Rouche: f and (a_n f - a_0 f*)/z have equally many
    \\ zeros inside when |a_0| < |a_n|).
    my(schur(f) = while (poldegree(f) > 0, my(a0 = polcoef(f, 0), an = pollead(f)); if (abs(a0) >= abs(an), return(0));
      f = (an * f - a0 * polrecip(f)) / 'c; f = f / content(f)); 1);
    emit(Str("    exact Schur-Cohn: v_prev - v_last stable inside: ", schur(b - a), "; reversal of v_prev + v_last stable inside: ", schur(polrecip(b + a))));
    foreach([1, -1], s, my(f = b + s * a);
      emit(Str("    v_prev/g ", if (s > 0, "+", "-"), " v_last/g: degree ", poldegree(f), ", roots inside/on/outside |c|=1: ", io(f), ", content ", content(f),
        ", factor degrees ", apply(poldegree, factor(f)[, 1]~)))));
  \\ WRONSKIAN=1 (cycle bmd-20261006-t): with L and D_m stripped, Q = 2c(D'L - DL') - DL is, on |c| = 1 and up to a unit
  \\ factor, the Wronskian in theta of the real functions e^(-i(d+1)theta/2) D and e^(-i d theta/2) L.  Report its factor
  \\ structure and its zeros on |c| = 1 (none would force interlacing).
  if (getenv("WRONSKIAN") == "1",
    my(D = strip01(matdet(vecextract(W, "..", setminus([1 .. 2 * m + 3], [2 * m + 1, 2 * m + 3])))));
    my(Q = 2 * 'c * (deriv(D, 'c) * L - D * deriv(L, 'c)) - D * L, F = factor(Q), z = Vec(polroots(Q)));
    emit(Str("  Wronskian Q: degree ", poldegree(Q), ", factor degrees ", apply(poldegree, F[, 1]~), " exps ", F[, 2]~,
      ", zeros inside/on/outside |c|=1: ", [#select(x -> abs(x) < 1 - 1e-30, z), #select(x -> abs(abs(x) - 1) <= 1e-30, z), #select(x -> abs(x) > 1 + 1e-30, z)]));
    emit(Str("    low-degree factors: ", select(f -> poldegree(f) <= 3, F[, 1]~)));
    \\ exact data (review of cycle t): degrees, self-reciprocity signs, stripped exponents of the two Cramer minors, and
    \\ an exact count of zeros of R = Q/(c-1) on |c| = 1: Cayley c = (1+it)/(1-it) gives S = A + iB, and zeros on the
    \\ circle other than c = -1 are the real common roots of A, B.
    my(R = Q / ('c - 1), recsign(P) = if (polrecip(P) == P, 1, if (polrecip(P) == -P, -1, 0)));
    my(Wp = winmat(m, 2 * m + 2), A1 = matdet(vecextract(Wp, "..", setminus([1 .. 2 * m + 2], [2 * m + 1]))), A2 = matdet(vecextract(Wp, "..", setminus([1 .. 2 * m + 2], [2 * m + 2]))));
    my(ex(P) = [valuation(P, 'c), valuation(P, 'c - 1)]);
    my(S = subst(R, 'c, (1 + I * 't) / (1 - I * 't)) * (1 - I * 't)^poldegree(R), SA = real(S), SB = imag(S), g = gcd(SA, SB));
    emit(Str("    exact: deg D = ", poldegree(D), ", deg L = ", poldegree(L), ", reciprocity signs D, L: ", [recsign(D), recsign(L)],
      "; [c, c-1] exponents of Delta_2m, Delta_2m+1: ", ex(A1), ", ", ex(A2),
      "; R(-1) = ", if (subst(R, 'c, -1), "nonzero", "0"), "; real common roots of Cayley parts: ", if (poldegree(g) > 0, polsturm(g), 0))));
  \\ SIGNS=1 (cycle bmd-20261006-p): signs of all maximal minors at c = 2, 3, 1/2 (a total-positivity test).
  if (getenv("SIGNS") == "1",
    foreach([2, 3, 1/2], c0, my(sg = List());
      forsubset([2 * m + 3, 2 * m + 1], S, listput(sg, sign(subst(matdet(vecextract(W, "..", Vec(S))), 'c, c0))));
      emit(Str("  c=", c0, ": minors positive ", #select(x -> x > 0, Vec(sg)), ", negative ", #select(x -> x < 0, Vec(sg)), ", zero ", #select(x -> x == 0, Vec(sg))))));
);
}
quit;
