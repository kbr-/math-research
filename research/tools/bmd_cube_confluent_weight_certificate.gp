\\ Confluent weight certificate for the one-double-root collision stratum.
\\
\\ Tested statement (for each N in NLIST, at one integer configuration a* with a double root
\\ value A and simple roots S): the confluent pair space
\\   Phi = < f_ik (i<k in S), f_Ak, g_k (k in S), h >,
\\   f_xy = ((1+xT)(1+yT))^(-3/2),  g_k = T(1+AT)^(-5/2)(1+a_kT)^(-3/2),  h = (1+AT)^(-3),
\\ of dimension R = binom(N,2) has no finite non-branch point of Weierstrass weight >= 3.
\\ Method: P(t) = det[ [X^j] (row_r / prefactor_r)(t+X) ]_{r,j<R} * prod_c (1+c t)^E,
\\ E = R(R-1)/2, is a polynomial of degree <= (N-1)E+N-2 with Z[1/2] coefficients whose
\\ roots at finite non-branch t have multiplicity equal to the weight. It is computed
\\ exactly modulo p by evaluation at deg+1 points and interpolation (deterministic
\\ reduction of the characteristic-zero polynomial). The script then compares the degree
\\ and the multiplicities at the branch values with the minimal values predicted by the
\\ local exponent formula, and reports gcd(P0,P0',P0'') for the non-branch part P0.
\\ Output: one line per N, printed and appended to the file named by env OUT.

p = 2^61 - 1;
OUT = getenv("OUT");
bc(al, m) = Mod(binomial(al, m), p);
serpow(u, al, L) = vector(L, m, bc(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
shiftX(A, L) = vector(L, n, if (n == 1, Mod(0, p), A[n - 1]));

rowmatrix(A, S, t, L) = {
  my(ua = Mod(A, p) / (1 + A * t), us = vector(#S, k, Mod(S[k], p) / (1 + S[k] * t)), rows = List());
  for (i = 1, #S, for (k = i + 1, #S,
    listput(rows, mul(serpow(us[i], -3/2, L), serpow(us[k], -3/2, L), L))));
  for (k = 1, #S,
    listput(rows, mul(serpow(ua, -3/2, L), serpow(us[k], -3/2, L), L));
    my(b = mul(serpow(ua, -5/2, L), serpow(us[k], -3/2, L), L));
    listput(rows, t * b + shiftX(b, L)));
  listput(rows, serpow(ua, -3, L));
  matrix(L, L, r, j, rows[r][j]);
}

certify(N, A, S) = {
  my(R = binomial(N, 2), E = R * (R - 1) / 2, D = (N - 1) * E + N - 2, vals = concat([A], S));
  if (#S != N - 2, error("need N-2 simple roots"));
  my(xs = List(), ys = List(), t = 0);
  while (#xs < D + 3,
    t++;
    my(tm = Mod(t, p));
    if (prod(c = 1, #vals, 1 + vals[c] * tm) == 0, next);
    listput(xs, tm);
    listput(ys, matdet(rowmatrix(A, S, tm, R)) * prod(c = 1, #vals, (1 + vals[c] * tm)^E)));
  if (#ys == 0, error("no points"));
  my(P = polinterpolate(Vec(xs)[1..D+1], Vec(ys)[1..D+1], 'x));
  my(extra_ok = (subst(P, 'x, xs[D+2]) == ys[D+2]) && (subst(P, 'x, xs[D+3]) == ys[D+3]));
  \\ predicted minimal multiplicities (local exponent formula, weight zero at branch points and infinity)
  my(Rs = N - 1, simple_sum = -3/2 * Rs + binomial(Rs, 2) + binomial(R - Rs, 2));
  my(m_simple = E + (simple_sum - binomial(R, 2)) + 3/2 * Rs);
  my(q2 = binomial(N - 2, 2), dbl_sum = -5/2 * 2 * (N - 2) + binomial(2 * (N - 2), 2) - 3 + binomial(q2, 2));
  my(m_double = E + (dbl_sum - binomial(R, 2)) + 4 * (N - 2) + 3);
  my(deg_pred = (N - 3) * R * (R - 1) / 2 + N - 2);
  if (P == 0, error("P vanishes identically"));
  my(P0 = P, mult = vector(#vals));
  for (c = 1, #vals,
    my(r = -1 / Mod(vals[c], p), lin = 'x - r);
    while (subst(P0, 'x, r) == 0, P0 = P0 \ lin; mult[c]++));
  my(G = gcd(P0, gcd(deriv(P0), deriv(deriv(P0)))), G2 = gcd(P0, deriv(P0)));
  my(line = Str("N=", N, " A=", A, " S=", S, " p=", p, " R=", R, " E=", E, " formal_deg_bound=", D,
    " extra_points_ok=", extra_ok, " deg_P=", poldegree(P), " deg_pred=", deg_pred,
    " mult_double=", mult[1], " pred_double=", m_double,
    " mult_simple=", mult[2..#vals], " pred_simple=", m_simple,
    " deg_P0=", poldegree(P0), " deg_gcd(P0,P0')=", poldegree(G2), " deg_gcd(P0,P0',P0'')=", poldegree(G)));
  print(line);
  if (OUT != 0 && OUT != "", write(OUT, line));
}

NLIST = [[5, 1, [2, 3, -1]], [6, 1, [2, 3, -1, 5]], [7, 1, [2, 3, 5, -1, -4]]];
for (i = 1, #NLIST, certify(NLIST[i][1], NLIST[i][2], NLIST[i][3]));
