\\ Route review follow-up tests (29 September 2026).
\\ (a) Rotated reality: are all zeros of Q_r purely imaginary, i.e. is Q_r(iS)/i^r real with only
\\     real simple zeros in S (Sturm count = degree), r <= 12?
\\ (b) Two double roots: with P = (x-u1)^2 (x-u2)^2 Q, the remainder identity puts the columns of
\\     Gamma_k in {f(0)=f(u1)=f(u2)=0}; predicted rank Gamma_k = k for k <= M-3 and
\\     det Gamma_k = 0 for k >= M-2. Random rational point, M = 4..8, lambda = 3/2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Qr(n) = { my(a = 1, b = 3*'T, c); if (n == 0, return(a)); for (k = 1, n - 1, c = (2*k+3)*'T*b + k*(k+2)*(1-'T^2)*a; a = b; b = c); b; };
beta(j) = binomial(-3/2, j);
Gp(P, m, n) = polcoeff(lift(Mod(x^n, P)), m, x);
G(P, M, m, n) = if (m < 0, 0, if (n < M, m == n, beta(n) / beta(m) * Gp(P, m, n)));
gam(P, M, k) = matrix(k, k, i, j, my(m = M - k + i - 1, D = M + j - 1); G(P, M, m, D + 1) - G(P, M, m - 1, D) - G(P, M, m, M) * G(P, M, M - 1, D));
main() = {
  my(res = vector(12, r, my(q = subst(Qr(r), 'T, I * 'S) / I^r); [r, poldegree(q), if (type(q) == "t_POL" && q == real(q), polsturm(q), "complex"), poldegree(gcd(q, deriv(q))) == 0]));
  emit(Str("Q_r(iS)/i^r [r, degree, real zeros in S, squarefree]: ", res));
  setrand(99);
  for (M = 4, 8,
    my(u1 = (random(201) - 100) / (random(9) + 1), u2 = (random(201) - 100) / (random(9) + 1), Q = prod(i = 1, M - 4, x - (random(2001) - 1000) / (random(13) + 1)));
    my(P = (x - u1)^2 * (x - u2)^2 * Q);
    emit(Str("M=", M, " two double roots: rank Gamma_k, k=1..M: ", vector(M, k, matrank(gam(P, M, k))), " predicted ", vector(M, k, if (k <= M - 3, Str(k), Str("<", k))))));
}
main();
