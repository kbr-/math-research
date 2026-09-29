\\ Binary-face components of the caterpillar: predicted positions (29 September 2026; cycle bmd-20260929-x).
\\ Tested statement (prop:cube-caterpillar-binary-face-components): in the caterpillar a_j = c_j eps^(j-1), the
\\ component at scale |T| ~ 1/eps is the binary face of N roots pulled back by T_face = 1 + 2 c_2 S, S = eps T,
\\ so its r = binom(N-2,2) Weierstrass points sit at T ~ (T_0 - 1)/(2 c_2 eps), Q_r(T_0) = 0.
\\ Prints the predicted scale exponents log|T|/log(1/eps) for the saved runs (N = 5: c = (1,2,-3,5,-7),
\\ eps = 1e-6, 1e-8; N = 6: c = (1,2,-3,5,-7,11), eps = 1e-8, 1e-10), to compare with the observed exponents
\\ near 1 in research/results/bmd-20260929-t/caterpillar-scales.txt and bmd-20260929-v/caterpillar-rings.txt.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
Q(r) = { my(a = 1, b = 3 * T); if (r == 0, return(a)); for (k = 1, r - 1, [a, b] = [b, (2 * k + 3) * T * b + k * (k + 2) * (1 - T^2) * a]); b; }
main() = {
  foreach ([[5, 2, [10^-6, 10^-8]], [6, 2, [10^-8, 10^-10]]], d,
    my(N = d[1], c2 = d[2], r = binomial(N - 2, 2), z = polroots(Q(r)));
    foreach (d[3], eps,
      my(ex = vecsort(vector(r, i, 1 + log(abs((z[i] - 1) / (2 * c2))) / log(1 / eps))));
      emit(Str("N=", N, " eps=", eps, ": predicted exponents of the scale-1 component: ", apply(e -> round(e * 1000) / 1000., ex)))));
}
main();
