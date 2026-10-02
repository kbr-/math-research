\\ Doubled cluster determinant (7 October 2026; cycle bmd-20261007-k).  Tested statement: for lambda = 3/2 (and a
\\ second exponent as control), the 2M-square matrix of the Taylor coefficients (columns 0..2M-1) of the rows
\\ phi_(y_i) = (1+y_i T)^(-lambda) and T phi_(y_i), i = 1..M, equals c_M(lambda) * prod_(i<j) (y_j - y_i)^4.
\\ Prints the quotient (must be a constant) and its factorization, for M = 1..MMAX with symbolic y.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
co(lam, m) = if (m < 0, 0, binomial(-lam, m));
{
my(MMAX = eval(getenv("MMAX")));
foreach([3/2, 5/2, 1/3], lam,
  for (M = 1, MMAX,
    my(ys = vector(M, i, eval(Str("y", i))), A = matrix(2 * M, 2 * M), d, v, q);
    for (i = 1, M, for (c = 1, 2 * M, A[i, c] = co(lam, c - 1) * ys[i]^(c - 1); A[M + i, c] = if (c >= 2, co(lam, c - 2) * ys[i]^(c - 2), 0)));
    d = matdet(A); v = prod(i = 1, M, prod(j = i + 1, M, (ys[j] - ys[i])^4)); q = simplify(d / v);
    emit(Str("lambda = ", lam, ", M = ", M, ": det / Vand^4 = ", q, if (type(q) == "t_FRAC" || type(q) == "t_INT", Str("  factored ", factor(q)), "  NOT CONSTANT")))));
}
