\\ Window minors of the neck coefficient matrix for a general exponent lambda (mechanism test).
\\
\\ Rows (1+sigma y)^(-lambda) (1+eps b_i T)^(-lambda), sigma = +-1, y = 1/T, expanded as
\\ C_((sigma,i),d) = sum_(m >= max(0,d)) beta_(m-d) sigma^(m-d) beta_m (eps b_i)^m,
\\ beta_j = binom(-lambda, j). For windows W_k = {-M+k..M-1+k}, report val det C[:,W_k] against
\\ M(M-1)+k(k+1) (the conjecture at lambda = 3/2). Mechanism prediction: the formula persists for
\\ non-integer lambda (the odd Pade table of tanh(lambda artanh y) is normal, since its Gauss
\\ continued fraction has partial numerators (lambda^2-n^2) y^2 != 0), and changes for integer
\\ lambda (tau rational, partial numerators vanish at n = lambda). Exact over Q, eps symbolic,
\\ series truncated at m <= 2M^2+2.
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
entry(lam, sig, bb, d, mmax) = sum(m = max(0, d), mmax, binomial(-lam, m - d) * sig^(m - d) * binomial(-lam, m) * (bb * 'e)^m);
run(lam, M, b) = {
  my(mmax = 2 * M^2 + 2, res = []);
  for (k = 0, M,
    my(W = vector(2 * M, j, -M + k + j - 1));
    my(C = matrix(2 * M, 2 * M, r, c, my(i = (r - 1) % M + 1, sig = if (r <= M, 1, -1)); entry(lam, sig, b[i], W[c], mmax)));
    my(D = matdet(C), v = if (D == 0, "zero", valuation(D, 'e)));
    res = concat(res, [[k, v, M * (M - 1) + k * (k + 1)]]));
  emit(Str("lambda=", lam, " M=", M, " [k, valuation, formula]: ", res));
}
foreach ([3/2, 5/2, 1/2, 7/3, 1, 2], lam, run(lam, 3, [1, 2, -3]); run(lam, 4, [1, 2, -3, 5]));
