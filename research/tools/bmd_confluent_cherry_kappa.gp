\\ Checks of the confluent cherry theorem (7 October 2026; cycle bmd-20261007-zf).
\\ Reduced expansion of the cross block: rows V_q (columns t >= 0, c_t beta^t), w^(-1) V_q (t >= -1, c_(t+1) beta^(t+1))
\\ and E'_q (sum_(r >= 2) c_r c_(t+r) eps^r beta^(t+r)), lambda = 3/2, c_n = binomial(-lambda, n), along caterpillar arcs
\\ beta_q = P^a y_q / (1 - P^a y_q), y_q = CS_q P^(v_q), eps = -P^b / (1 + P^b), P = 1000003 (exact rationals).
\\ (A) Hankel product formula: det[c_(u+r+s)]_(r,s<h) = c_u^h prod_(n<h) n! (lambda+u)_n (1-lambda)_n / ((u+n)_n (u+1)_(2n)),
\\     as rational functions of lambda, h <= 7, u <= 4.
\\ (B) For EVERY window [-j, 3M-1-j], 2 <= j <= M+1: the exact valuation equals F'_j =
\\     sum_(i<j) beta_i 5(i-1) + sum_(i>=j) beta_i (9i-3j-3) + w (j^2-3j+2M+2), beta_i = a + v_(M+1-i), and the leading
\\     coefficient (unit part mod P) equals +-kappa_(M,j) * prod_q CS_q^(e_q) * (-1)^R, where
\\     kappa = prod_(n<=j-2) c_n * H_(j-1)(2) * c_2^k * prod_(2<=i<=j-1) H_2(2i-3) * prod_(j<=i<=M) H_3(3i-j-3),
\\     H_h(u) = det[c_(u+r+s)]_(r,s<h), e_q the exponent of root q in the block family, R = j(j-1) + 2k, k = M+1-j.
\\ (C) The brute-force minimizers (N1, C2) of the least term valuation are exactly the predicted block family.
\\ (D) Non-window bound: for every 3M-subset L of a column range, the exact valuation is >= the proved bound
\\     B(L) = sum_(i<M)(beta_i - beta_(i+1)) L_i(p+1) + (a + w) Q(L) - w (Sum L + M), p = #(L n (-oo,-2]), strictly above
\\     F'_(p+1) unless L is that window (p = 0 uses j = 1); minors with p > M must vanish.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
cn(n) = if (n < 0, 0, prod(z = 0, n - 1, -L - z) / n!);
poch(x, n) = prod(z = 0, n - 1, x + z);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
CS = [1, 3, -2, 5];
P = 1000003;
H(h, u) = matdet(matrix(h, h, r, s, cc(u + r + s - 2)));
\\ ---- (A)
{
my(ok = 1);
for (h = 1, 7, for (u = 0, 4,
  my(lhs = matdet(matrix(h, h, r, s, cn(u + r + s - 2))), rhs = cn(u)^h * prod(n = 0, h - 1, n! * poch(L + u, n) * poch(1 - L, n) / (poch(u + n, n) * poch(u + 1, 2 * n))));
  if (lhs != rhs, ok = 0; emit(Str("(A) mismatch at h = ", h, ", u = ", u)))));
emit(Str("(A) Hankel product formula for h <= 7, u <= 4: ", if (ok, "holds", "FAILS")));
}
\\ ---- predicted values
betas(M, a, vv) = vector(M, i, a + vv[M + 1 - i]);
Fp(M, a, w, vv, j) = { my(bt = betas(M, a, vv));
  sum(i = 1, j - 1, bt[i] * 5 * (i - 1)) + sum(i = j, M, bt[i] * (9*i - 3*j - 3)) + w * (j^2 - 3*j + 2*M + 2); }
kap(M, j) = { my(k = M + 1 - j);
  prod(n = 0, j - 2, cc(n)) * H(j - 1, 2) * cc(2)^k * prod(i = 2, j - 1, H(2, 2*i - 3)) * prod(i = j, M, H(3, 3*i - j - 3)); }
\\ exponent of the rank-i root (root q = M+1-i) in the block family: S_i
Sfam(M, j, i) = if (i < j, 5 * (i - 1), 9*i - 3*j - 3);
\\ least term valuation and minimizers by brute force (as bmd_confluent_cherry_windows2.gp)
fval(N, M, bq) = my(Ns = vecsort(N)); sum(i = 1, M, Ns[i] * bq[M + 1 - i]);
brute(M, a, w, vv, j) = {
  my(Lam = [-j .. 3*M - 1 - j], bq = vector(M, q, a + vv[q]), best = oo, arg = List());
  my(pos = select(t -> t >= 0, Lam));
  forsubset([#pos, M], S1, my(c1 = vecextract(pos, Vec(S1)), rest = select(t -> t >= -1 && !setsearch(Set(c1), t), Lam));
    forsubset([#rest, M], S2, my(c2 = vecextract(rest, Vec(S2)), L3 = vecsort(setminus(setminus(Set(Lam), Set(c1)), Set(c2))));
      my(N3 = vector(M));
      for (i = 1, M, N3[i] = max(L3[i] + 2, i - 1); if (i > 1, N3[i] = max(N3[i], N3[i - 1] + 1)));
      my(T = fval(c1, M, bq) + fval(apply(t -> t + 1, c2), M, bq) + fval(N3, M, bq) + w * (vecsum(N3) - vecsum(L3)));
      if (T < best, best = T; arg = List());
      if (T == best, listput(arg, [Set(c1), Set(c2)]))));
  [best, Set(Vec(arg))];
}
\\ predicted block family: N1 = {0} u one element of each block, C2 = {-1} u one element of each block
family(M, j) = {
  my(blocks = concat(vector(j - 2, i, [2*i - 1, 2*i]), vector(M + 1 - j, i, my(s = 2*j - 3 + 3*(i - 1)); [s, s + 1, s + 2])), out = List());
  my(choices = vector(#blocks, b, if (#blocks[b] == 2, [[1, 2], [2, 1]], [[1, 2], [2, 1], [1, 3], [3, 1], [2, 3], [3, 2]])));
  forvec(X = vector(#blocks, b, [1, #choices[b]]),
    my(n1 = [0], c2 = [-1]);
    for (b = 1, #blocks, my(ch = choices[b][X[b]]); n1 = concat(n1, blocks[b][ch[1]]); c2 = concat(c2, blocks[b][ch[2]]));
    listput(out, [Set(n1), Set(c2)]));
  Set(Vec(out));
}
\\ exact minor on an arbitrary column list
minor(M, a, b, vv, cols, NS) = {
  my(R = NS \ (a + b) + 1, n = #cols, rows = matrix(3*M, n));
  my(eps0 = -P^b / (1 + P^b), bet = vector(M, q, my(y = CS[q] * P^vv[q]); P^a * y / (1 - P^a * y)));
  for (q = 1, M, for (u = 1, n, my(t = cols[u]);
    rows[q, u] = if (t >= 0, cc(t) * bet[q]^t, 0);
    rows[M + q, u] = if (t >= -1, cc(t + 1) * bet[q]^(t + 1), 0);
    rows[2*M + q, u] = sum(r = max(2, -t), R, cc(r) * cc(t + r) * eps0^r * bet[q]^(t + r))));
  matdet(rows);
}
unitpart(D, v) = my(x = D / P^v); Mod(numerator(x), P) / Mod(denominator(x), P);
\\ ---- (B), (C)
{
foreach([[2, 1, 1, [0, 2]], [2, 2, 1, [0, 3]], [2, 1, 3, [0, 1]], [3, 1, 1, [0, 1, 2]], [3, 1, 3, [0, 1, 2]], [3, 3, 1, [0, 1, 2]],
         [3, 1, 2, [0, 2, 3]], [4, 1, 1, [0, 1, 2, 3]], [4, 2, 1, [0, 1, 3, 4]]], c,
  my(M = c[1], a = c[2], b = c[3], vv = c[4], NS = (a + b) * (3*M^2 + 3*M) + 6 * M * vecsum(vv) + 10);
  for (j = 2, M + 1,
    my(k = M + 1 - j, D = minor(M, a, b, vv, [-j .. 3*M - 1 - j], NS), v = valuation(D, P), F = Fp(M, a, b, vv, j));
    my(mono = prod(i = 1, M, CS[M + 1 - i]^Sfam(M, j, i)) * (-1)^(j*(j - 1) + 2*k), pred = Mod(kap(M, j) * mono, P), lc = unitpart(D, v));
    my(Bf = brute(M, a, b, vv, j), fam = family(M, j));
    emit(Str("(B,C) M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ", j = ", j, ": val ", v, ", F' ", F, ", brute least ", Bf[1],
      ", lc = +-kappa*mono: ", lc == pred || lc == -pred, ", minimizers = block family (", #fam, "): ", Bf[2] == fam))));
}
\\ ---- (D)
Lbd(M, i, j) = if (i <= j - 1, sum(c = -1, 2*i - 2, c) + i + i*(i - 1)/2, sum(c = -1, 3*i - j - 1, c) + i + 2*(i - j + 1) + (j - 1)*(j - 2)/2);
bound(M, a, w, vv, Lset) = {
  my(p = #select(t -> t <= -2, Lset), j = p + 1, bt = concat(betas(M, a, vv), [0]));
  my(Lp = select(t -> t >= -1, Lset), Q = vecsum(Lp) + 3*M - 2*p + p*(p - 1)/2);
  [p, sum(i = 1, M - 1, (bt[i] - bt[i + 1]) * Lbd(M, i, j)) + (a + w) * Q - w * (vecsum(Lset) + M)];
}
{
foreach([[2, 1, 1, [0, 2], [-5, 6]], [2, 1, 3, [0, 1], [-5, 6]], [3, 1, 1, [0, 1, 2], [-5, 7]], [3, 3, 1, [0, 1, 2], [-5, 7]]], c,
  my(M = c[1], a = c[2], b = c[3], vv = c[4], cols = [c[5][1] .. c[5][2]], NS = 2 * ((a + b) * (3*M^2 + 3*M) + 6 * M * vecsum(vv)) + 10);
  my(Fmin = vecmin(vector(M, j, Fp(M, a, b, vv, j + 1))), viol = 0, cnt = 0, strictbad = 0, pbig = 0, inexact = 0, tight = 0);
  my(thr = (NS \ (a + b) + 2) * (a + b) - abs(c[5][1]) * a);
  forsubset([#cols, 3*M], S, my(Ls = vecextract(cols, Vec(S)), Bd = bound(M, a, b, vv, Ls), D = minor(M, a, b, vv, Ls, NS)); cnt++;
    if (Bd[1] > M, if (D != 0, pbig++); next);
    my(v = if (D == 0, oo, valuation(D, P)));
    if (Bd[2] >= thr, inexact++; next);
    if (v < Bd[2], viol++);
    my(win = (Bd[1] >= 1 && Ls == [-(Bd[1] + 1) .. 3*M - 2 - Bd[1]]));
    if (win && v == Bd[2], tight++);
    if (!win && v <= Fmin, strictbad++));
  emit(Str("(D) M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ", columns ", c[5], ": ", cnt, " sets; bound violations ", viol,
    "; non-window sets at or below min F' ", strictbad, "; nonzero minors with p > M ", pbig, "; windows attaining the bound ", tight,
    "; bound beyond exactness threshold ", inexact)));
}
