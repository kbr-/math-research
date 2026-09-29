\\ Window minors of the half-integral neck coefficient matrix.
\\
\\ Tested statement (neck window conjecture, part (i)): in the annulus 1 < |T| < 1/(eps max|b|),
\\ the 2M cross rows phi_s phi_(eps b_i), phi_t phi_(eps b_i) (phi_x = (1+xT)^(-3/2), s = 1,
\\ t = -1) are T^(-3/2) sum_d C_(row,d) T^d with
\\   C_((sigma,i),d) = sum_(m >= max(0,d)) beta_(m-d) sigma^(m-d) beta_m (eps b_i)^m,
\\ beta_j = binom(-3/2, j). For the window W_k = {-M+k, ..., M-1+k}, the minor det C[:, W_k] has
\\ eps-valuation M(M-1) + k(k+1), k = 0..M. Computed exactly over Q with eps symbolic, the series
\\ truncated at m <= 2M^2 + 2 (enough for the valuations tested; higher m only adds higher powers).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j) = binomial(-3/2, j);
entry(sig, bb, d, mmax) = sum(m = max(0, d), mmax, beta(m - d) * sig^(m - d) * beta(m) * (bb * 'e)^m);
run(M, b) = {
  my(mmax = 2 * M^2 + 2, res = []);
  for (k = 0, M,
    my(W = vector(2 * M, j, -M + k + j - 1));
    my(C = matrix(2 * M, 2 * M, r, c, my(i = (r - 1) % M + 1, sig = if (r <= M, 1, -1)); entry(sig, b[i], W[c], mmax)));
    my(D = matdet(C), v = valuation(D, 'e));
    res = concat(res, [[k, v, M * (M - 1) + k * (k + 1), polcoeff(D, v, 'e) != 0]]));
  emit(Str("M=", M, " b=", b, " [k, valuation, predicted, leading nonzero]: ", res));
}
\\ M = 2..4 exactly over Q; M = 5 modulo p = 2^61-1 (MODP=1). Reduction can only raise a
\\ valuation, so at M = 5 the observed values bound the characteristic-zero valuations from above.
default(parisizemax, 4000000000);
MODP = eval(getenv("MODP"));
if (MODP == 1, beta(j) = Mod(binomial(-3/2, j), 2^61 - 1));
if (MODP != 1, run(2, [1, 2]); run(3, [1, 2, -3]); run(4, [1, 2, -3, 5]));
if (MODP == 1, run(5, [1, 2, -3, 5, 7]));
