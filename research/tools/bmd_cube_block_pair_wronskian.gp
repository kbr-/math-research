\\ Multi-class block-pair Wronskians (3 October 2026; cycle bmd-20261003-zzu).
\\ Tested statement (lem:block-pair-wronskian): for classes c = 1..r with a_c pairwise incongruent mod Z, each a_c
\\ non-integral or an integer <= -max(p_c, q_c),
\\ V = sum_c x^(a_c) P_<p_c (+) (1+x)^(a_c) P_<q_c has W(V) = C x^alpha (1+x)^beta R(x), R a polynomial prime to x(1+x),
\\   deg R = P Q - sum_c min(p_c, q_c)^2   (P = sum p_c, Q = sum q_c),
\\   alpha = sum_c (p_c a_c + binom(p_c, 2)) + binom(Q, 2) - binom(K, 2), beta symmetric,
\\   |C| = |V(mu0)| * |V(y)| / sf(Q),  mu0 = {a_c + i (i < p_c)} u {0..Q-1},  y = {a_c + i (i < q_c)}.
\\ Also a control with one integral class a = -n-3 (p = q = 1), as in the class integrals of the far terms, and boundary
\\ integral classes a = -max(p, q) with p, q <= 3 beside a half-integral class.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ff(a, r) = prod(s = 0, r - 1, a - s);
sf(m) = prod(i = 0, m - 1, i!);
vdm(v) = prod(i = 1, #v, prod(j = i + 1, #v, v[j] - v[i]));
\\ columns: list of [kind, exponent] with kind 0 = x^e, 1 = (1+x)^e
test(A, Pp, Qq) = {
  my(cols = List(), K, M, D, al, be, R, P = vecsum(Pp), Q = vecsum(Qq), r = #A);
  for (c = 1, r, for (i = 0, Pp[c] - 1, listput(cols, [0, A[c] + i])));
  for (c = 1, r, for (i = 0, Qq[c] - 1, listput(cols, [1, A[c] + i])));
  K = #cols;
  \\ divide column j by x^(e_j) or (1+x)^(e_j): entries ff(e, r) x^(-r) or ff(e, r) (1+x)^(-r)
  M = matrix(K, K, rr, j, ff(cols[j][2], rr - 1) * if (cols[j][1] == 0, x, 1 + x)^(1 - rr));
  D = matdet(M);
  \\ W = D * x^(sum of X exponents) (1+x)^(sum of Y exponents); alpha relative shift
  my(sx = sum(c = 1, r, sum(i = 0, Pp[c] - 1, A[c] + i)), sy = sum(c = 1, r, sum(i = 0, Qq[c] - 1, A[c] + i)));
  al = sum(c = 1, r, Pp[c] * A[c] + binomial(Pp[c], 2)) + binomial(Q, 2) - binomial(K, 2);
  be = sum(c = 1, r, Qq[c] * A[c] + binomial(Qq[c], 2)) + binomial(P, 2) - binomial(K, 2);
  \\ R = D * x^(sx - al) (1+x)^(sy - be), must be a polynomial (integer shifts)
  R = D * x^(sx - al) * (1 + x)^(sy - be);
  my(ok = (type(R) == "t_POL" || type(R) == "t_INT" || type(R) == "t_FRAC") && subst(R, x, 0) != 0 && subst(R, x, -1) != 0);
  my(mu0 = concat(vector(P, j, cols[j][2]), vector(Q, j, j - 1)), y = vector(Q, j, cols[P + j][2]));
  my(Cpred = abs(vdm(mu0)) * abs(vdm(y)) / sf(Q));
  [ok, if (ok, poldegree(R), -1), P * Q - sum(c = 1, r, min(Pp[c], Qq[c])^2), if (ok, abs(subst(R, x, 0)), 0), Cpred];
}
{
my(cnt = 0, bad = 0);
my(As = [[-47/2, -20 - 1/3], [1/2, 1/3, -1/5], [-61/2, -7/3]]);
foreach (As, A,
  my(r = #A);
  forvec (v = vector(2 * r, i, [0, 3]),
    my(Pp = v[1..r], Qq = v[r + 1..2 * r]);
    if (vecsum(Pp) + vecsum(Qq) == 0 || vecsum(Pp) + vecsum(Qq) > 8, next);
    my(T = test(A, Pp, Qq)); cnt++;
    if (!T[1] || T[2] != T[3] || T[4] != T[5], bad++; emit(Str("mismatch A=", A, " p=", Pp, " q=", Qq, ": ", T)))));
emit(Str("block-pair Wronskian: ", cnt, " cases (3 exponent sets, 2-3 classes, p_c, q_c <= 3, K <= 8), mismatches ", bad));
\\ integral class control: a = -n-3 with p = q = 1 beside a half-integral class, as in the far terms
my(bad2 = 0, cnt2 = 0);
for (n = 5, 9, for (pp = 1, 4, for (qq = 1, 4,
  my(T = test([-n - 7/2, -n - 3], [pp, 1], [qq, 1])); cnt2++;
  if (!T[1] || T[2] != T[3] || T[4] != T[5], bad2++; emit(Str("integral-class mismatch n=", n, " p=", pp, " q=", qq, ": ", T))))));
emit(Str("with an integral class -n-3 (p = q = 1): ", cnt2, " cases, mismatches ", bad2));
my(bad3 = 0, cnt3 = 0);
forvec (v = [[0, 3], [0, 3], [0, 2], [0, 2]], my(pi = v[1], qi = v[2], ph = v[3], qh = v[4]);
  if (max(pi, qi) == 0, next);
  my(T = test([-max(pi, qi), -5/2], [pi, ph], [qi, qh])); cnt3++;
  if (!T[1] || T[2] != T[3] || T[4] != T[5], bad3++; emit(Str("boundary mismatch p=", [pi, ph], " q=", [qi, qh], ": ", T))));
emit(Str("boundary integral class a = -max(p, q) (p, q <= 3) beside -5/2 (p, q <= 2): ", cnt3, " cases, mismatches ", bad3));
}
