\\ Exact Delta_nu for n = 2 degree vectors in PARI/GP, with its factorization over Q (bmd-r132).
\\
\\ Statement examined.  conj:cube-monotone-squarefree for n = 2: the part of Delta_nu(a1, a2) prime to a1, a2, a1 - a2
\\ is squarefree.  With a1 = 1, a2 = x, Delta_nu(1, x) is the determinant of the truncated expansions at T = 0 of
\\ T^j w1^r1 w2^r2 (j <= nu_r), w1 = (1 + T)^(1/2), w2 = (1 + x T)^(1/2), as in bmd_cube_nu_noncollision.py (sympy),
\\ which it replaces for larger vectors.  Prints the factorization with multiplicities; the collision forms are x and
\\ x - 1 (a1 is the dehomogenizing variable).
\\ Usage: gp -q THIS with the list NUS defined before reading, e.g. echo 'NUS=[[4,2,2,0]]; read("THIS")' | gp -q
sqrtser(a, N) = vector(N, k, binomial(1/2, k - 1) * a^(k - 1));
ser_mul(p, q, N) = vector(N, c, sum(i = 1, c, p[i] * q[c - i + 1]));
delta(nu) = {
  my(N = sum(i = 1, 4, nu[i] + 1), rows = List(), one, w, v);
  one = vector(N, k, k == 1);
  \\ index r = 1..4 corresponds to (r1, r2) = (0,0), (1,0), (0,1), (1,1)
  for (r = 1, 4,
    w = one;
    if (r == 2 || r == 4, w = ser_mul(w, sqrtser(1, N), N));
    if (r == 3 || r == 4, w = ser_mul(w, sqrtser('x, N), N));
    for (j = 0, nu[r],
      v = vector(N, k, if (k <= j, 0, w[k - j]));
      listput(rows, v)));
  matdet(matrix(N, N, i, j, rows[i][j]));
}
{
  for (t = 1, #NUS,
    my(nu = NUS[t], D = delta(nu), F = factor(D));
    print("nu=", nu, " deg_x=", poldegree(D), " factors:");
    for (i = 1, matsize(F)[1], print("  ", F[i, 1], "  ^", F[i, 2])));
}
