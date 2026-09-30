\\ First-order variation of the merge far points along the merge parameter (2 October 2026; cycle bmd-20261002-q).
\\ Merge far limit (lem:cube-merge-far-limit): in the chart z = eps w the classes are chi_c(w) {g(eps w) : g in G_c}, with
\\ G_T = <x^-C..x^-1> + H(p) (pair space of p_2..p_k), G_0 = x^-(n-1) blocks {x^m (1-x/p_j)^(1/2), m < n}, G_1 = {(1-x/p_j)^(1/2)},
\\ G_01 = <x^-(n-1)..x^0>, with consecutive exponent sets at x = 0.  To first order in eps only the top echelon element of classes
\\ T, 0, 1 changes: x^e_top -> w^e_top + a_c eps w^(e_top + 1).  So d/deps W(F_eps) = sum_c a_c W_c, W_c the Wronskian of F with the
\\ top element of class c replaced by the next monomial.  Question: can a root of the far polynomial R be a common root of W_T,
\\ W_0, W_1 (all taken off w = 0, 1)?  And how do the a_c depend on the shape p?
\\ Reports, for each (n,k): deg R; deg gcd(R, W_c) for each c; deg gcd(R, W_T, W_0, W_1); det of (a_T, a_0, a_1) at three
\\ shapes p (run; "ZERO" means the three vectors are dependent), then their rank and normalized rows (run2), and the control
\\ deg of Q*/(B R') mod R (run3), which is small when the far points move to first order like a Moebius field.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
strip(N) = { while (subst(N, 'w, 0) == 0, N = N / 'w); while (subst(N, 'w, 1) == 0, N = N / ('w - 1)); N / pollead(N); }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)));
}
Fcls(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  [[0, 0, vector(C + 2 + P, t, 'w^(t - 1 - C))], [1/2, 0, vector((k - 1) * n, t, 'w^(t - n))],
   [0, 1/2, vector(k - 1, t, 'w^(t - 1))], [1/2, 1/2, vector(n, t, 'w^(t - n))]];
}
\\ replace the top element of class c (1 = T, 2 = 0, 3 = 1) by the next monomial
bump(F, c) = { my(G = F, v = G[c][3]); v[#v] = v[#v] * 'w; G[c][3] = v; G; }
\\ coefficient a_c: echelon of G_c at x = 0, coefficient of x^(top+1) in the element with leading x^top (reduced against lower ones)
echelon_next(fs, E, prec) = {
  \\ fs: list of series in x; E: their exponent set (sorted, consecutive); return coefficient of x^(max E + 1) in the reduced
  \\ echelon element with leading term x^(max E)
  my(lo = E[1], m = #fs, M = matrix(m, #E + 1));
  for (i = 1, m, for (j = 1, #E + 1, M[i, j] = polcoef(fs[i] + O('x^prec), lo + j - 1, 'x)));
  \\ solve for the combination with coordinates e_top on the first #E columns
  my(A = matrix(m, #E, i, j, M[i, j]), target = vector(#E, j, j == #E), sol = matsolve(A~, target~));
  sum(i = 1, m, sol[i] * M[i, #E + 1]);
}
acoef(n, k, p) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, prec = (k - 1) * n + P + 5);
  my(sq(j) = (1 - 'x / p[j] + O('x^prec))^(1/2));
  \\ class T: pair space H(p) (the negative powers do not affect the reduced top element)
  my(H = List([1 + O('x^prec), 'x + O('x^prec)]));
  for (j = 1, #p, for (l = j + 1, #p, listput(H, sq(j) * sq(l))));
  my(aT = echelon_next(Vec(H), vector(2 + P, t, t - 1), prec));
  \\ class 0: x^(n-1) G_0 = blocks x^m sq(j), exponents 0..(k-1)n-1
  my(B0 = List()); for (j = 1, #p, for (m = 0, n - 1, listput(B0, 'x^m * sq(j))));
  my(a0 = echelon_next(Vec(B0), vector((k - 1) * n, t, t - 1), prec));
  my(B1 = vector(#p, j, sq(j)), a1 = echelon_next(B1, vector(k - 1, t, t - 1), prec));
  [aT, a0, a1];
}
\\ raw Wronskian (no stripping or normalization), so that Q_1 = sum a_c W_c^raw is the true eps-derivative up to one common factor
wrraw(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  numerator(matdet(M));
}
run2(n, k) = {
  my(F = Fcls(n, k), R = wr(F), Wr = vector(3, c, wrraw(bump(F, c))));
  my(shapes = [[-2, 3, -5/2, 7/3, 11/4], [5, -3/2, 2/7, -4, 9/5], [1/3, -7, 13/4, 3/2, -2/9]]);
  my(A = matrix(3, 3, i, j, acoef(n, k, shapes[i][1..k - 1])[j]));
  my(res = vector(3, i, my(Q = sum(c = 1, 3, A[i, c] * Wr[c])); if (Q == 0, -1, poldegree(gcd(R, Q)))));
  emit(Str("(n,k)=", [n, k], ": rank of (a_T, a_0, a_1) over three shapes ", matrank(A), "; normalized rows ",
    vector(3, i, A[i, ] / A[i, 1]), "; deg gcd(R, Q_1) at the three shapes (-1 if Q_1 = 0): ", res));
}
\\ Control: if the first-order motion were a vector field v(w) d/dw, then Q* = v R' mod R, and Q* would vanish at every double
\\ root whatever gcd(R, Q*) is for this R.  Report deg of (Q* / R' mod R) (a small degree <= 2 would signal a Moebius field).
run3(n, k) = {
  my(F = Fcls(n, k), R = wr(F), Wr = vector(3, c, wrraw(bump(F, c))), a = acoef(n, k, [-2, 3, -5/2, 7/3, 11/4][1..k - 1]));
  my(Q = sum(c = 1, 3, a[c] * Wr[c]), B = wrraw(F) / R, v = lift(Mod(Q, R) / Mod(B * deriv(R), R)));
  emit(Str("(n,k)=", [n, k], ": deg of Q*/(B R') mod R, B = W(F)/R the branch factor: ", poldegree(v), " (deg R ", poldegree(R), ")",
    if (poldegree(v) <= 2, Str("; v = ", v), "")));
}
run(n, k) = {
  my(F = Fcls(n, k), R = wr(F), W = vector(3, c, wr(bump(F, c))));
  my(g = vector(3, c, poldegree(gcd(R, W[c]))), gall = poldegree(gcd(gcd(R, W[1]), gcd(W[2], W[3]))));
  my(shapes = [[-2, 3, -5/2, 7/3, 11/4], [5, -3/2, 2/7, -4, 9/5], [1/3, -7, 13/4, 3/2, -2/9]]);
  my(A = matrix(3, 3, i, j, acoef(n, k, shapes[i][1..k - 1])[j]));
  emit(Str("(n,k)=", [n, k], ": deg R ", poldegree(R), "; deg gcd(R, W_T), gcd(R, W_0), gcd(R, W_1): ", g,
    "; deg gcd(R, W_T, W_0, W_1): ", gall, "; det of (a_T, a_0, a_1) at three shapes: ", (if (matdet(A) != 0, "nonzero", "ZERO"))));
}
\\ Cycle bmd-20261002-r: correction.  wrraw takes numerator(), which clears a different power of w and w - 1 for each bumped
\\ space, so sum_c a_c wrraw(bump(F, c)) mixes differently scaled Wronskians; run2's gcd and run3's control used it.  run4 uses the
\\ Wronskians as rational functions (wrrat), combines them, and only then clears one common denominator.
wrrat(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  matdet(M);
}
run4(n, k) = {
  my(F = Fcls(n, k), R = wr(F), a = acoef(n, k, [-2, 3, -5/2, 7/3, 11/4][1..k - 1]));
  my(Qr = sum(c = 1, 3, a[c] * wrrat(bump(F, c))), Wf = wrrat(F), D = lcm(denominator(Qr), denominator(Wf)));
  my(Qn = Qr * D, Wn = Wf * D, B = Wn / R);
  if (type(B) != "t_POL", error("R does not divide the cleared Wronskian"));
  my(v = lift(Mod(Qn, R) / Mod(B * deriv(R), R)));
  emit(Str("(n,k)=", [n, k], " [corrected]: deg gcd(R, Q) ", poldegree(gcd(R, Qn)), "; deg of Q/(B R') mod R: ", poldegree(v),
    " (deg R ", poldegree(R), ")", if (poldegree(v) <= 2, Str("; v = ", v), "")));
}
MODE = getenv("MODE");
{
if (MODE == "corrected", foreach([[2, 3], [3, 3], [2, 4], [4, 3], [3, 4]], v, run4(v[1], v[2])),
  foreach([[2, 3], [3, 3], [2, 4], [4, 3], [3, 4]], v, run(v[1], v[2]));
  foreach([[2, 3], [3, 3], [2, 4], [4, 3], [3, 4]], v, run2(v[1], v[2]));
  foreach([[2, 3], [3, 3], [2, 4], [4, 3], [3, 4]], v, run3(v[1], v[2])));
}
