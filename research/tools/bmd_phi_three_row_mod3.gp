\\ Three-row Schur coefficients of Phi_N modulo 3 (5 October 2026; cycle bmd-20261005-h).  For a symmetric polynomial,
\\ Phi(x1, x2, x3, 0, ..., 0) = sum over partitions lambda with at most 3 parts of c_lambda s_lambda(x1, x2, x3).  Phi is
\\ evaluated there as the eps^0 term of Delta / V^N at labels (x1, x2, x3, eps*y4, ..., eps*yN), computed exactly in
\\ F_(3^K)[eps].  Question: is the coefficient of the shape (b, b, b), b = binom(N,4), a unit mod 3 for every N?
\\ Env NS, K, EXTRA, SEED.
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
mark(lab, one) = {
  my(N = #lab, D = N * (N - 1) / 2 + 2, bh = vector(D, j, lift(binomial(1/2, j - 1) * Mod(1, 3))), M = matrix(D, D), row = 2);
  M[1, 1] = one; M[2, 2] = one;
  for (i = 1, N, for (j = i + 1, N, row++;
    for (kk = 1, D, M[row, kk] = one * sum(u = 0, kk - 1, bh[u + 1] * bh[kk - u] * lab[i]^u * lab[j]^(kk - 1 - u)))));
  matdet(M);
}
schur3(lam, x) = {
  my(l = concat(lam, vector(3 - #lam)));
  matdet(matrix(3, 3, i, j, x[i]^(l[j] + 3 - j))) / matdet(matrix(3, 3, i, j, x[i]^(3 - j)));
}
{
my(K = eval(getenv("K")), g = ffgen(ffinit(3, K, 'a), 'a), one = g^0, EX = eval(getenv("EXTRA")), e = 'e);
setrand(eval(getenv("SEED")));
foreach(eval(getenv("NS")), N,
  my(deg = 3 * binomial(N, 4), b = binomial(N, 4), parts = List(), t0 = getwalltime());
  forpart(p = deg, listput(parts, Vecrev(p)), , 3);
  parts = Vec(parts);
  my(P = #parts, A = matrix(P + EX, P), rhs = vector(P + EX), y = vector(N - 3, i, random(g)));
  for (r = 1, P + EX,
    my(x = vector(3, i, random(g)), lab = concat(x, e * y), V = prod(i = 1, N, prod(j = i + 1, N, lab[j] - lab[i])));
    my(q = mark(lab, one) / V^N);
    rhs[r] = subst(q, e, 0);
    for (c = 1, P, A[r, c] = schur3(parts[c], x)));
  my(sol = matsolve(A[1..P, ], rhs[1..P]~));
  my(chk = vecmax(apply(r -> if(A[r, ] * sol == rhs[r], 0, 1), vector(EX, i, P + i))));
  my(nz = List(), cb = 0); for (c = 1, P, if (sol[c] != 0, listput(nz, [parts[c], sol[c]])); if (parts[c] == [b, b, b], cb = sol[c]));
  emit(Str("N = ", N, ": ", P, " partitions of ", deg, " with at most 3 parts; extra-point check ", if(chk == 0, "passed", "FAILED"),
    "; coefficient of (", b, ",", b, ",", b, "): ", cb, "; nonzero three-row coefficients (", #nz, "): ", Vec(nz), " (", getwalltime() - t0, " ms)")));
}
quit;
