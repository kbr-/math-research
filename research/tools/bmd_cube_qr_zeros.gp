\\ Zeros of the binary-face polynomials Q_r (D^r (1-T^2)^(-3/2) = (1-T^2)^(-3/2-r) Q_r):
\\ are they purely imaginary, i.e. are there no Weierstrass points of the limit space on the real
\\ axis (a Chebyshev-system / Hermite-Pade normality statement on the real line)? r = binom(M,2),
\\ M = 3..8. Reports the largest |Re| of the zeros and the number of real zeros (Sturm count).
default(realprecision, 200);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Qr(n) = { my(a = 1, b = 3*'T, c); if (n == 0, return(a)); for (k = 1, n - 1, c = (2*k+3)*'T*b + k*(k+2)*(1-'T^2)*a; a = b; b = c); b; };
for (M = 3, 8, my(n = binomial(M, 2), q = Qr(n), z = polroots(q)); emit(Str("M=", M, " r=", n, " real zeros (Sturm)=", polsturm(q), " max|Re|=", strprintf("%.3e", vecmax(apply(x -> abs(real(x)), z))), " min|Im| over nonzero=", strprintf("%.4f", vecmin([abs(imag(x)) | x <- z, abs(x) > 1e-50])))));
