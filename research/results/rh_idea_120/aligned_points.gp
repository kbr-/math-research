\\ Statement tested: part (4) of prop:prime-sum-premise-zero-weight. For tau >= 3, L >= 42 with tau L >= 180,
\\ 0 < beta <= 1, y0 = 2^N, a = log y0, b = a + log 2, l = 1/tau, E(z) = e^(z(b+l)) - e^(zb) - e^(za) + e^(z(a-l)),
\\ points z_k = beta + i d_k, d_k = 2 pi k/log 2, k0 = ceil(tau L log 2/(2 pi)) <= k <= k1, k1 >= 2 k0 - 1:
\\     |sum_k E(z_k)/(l z_k^2)| >= 0.05 y0^beta / L.
\\ Expected, written before the run: every row prints "ok", the ratio of the sum to y0^beta/L lying above 0.05
\\ (the proof's own figure is about 0.06 at the least and up to about 0.11 (2^beta + 1)/2 for large L); the
\\ control rows, the same number of points with heights moved off the progression by a fixed irrational step,
\\ print a ratio far below the aligned one.
\\ Refuted by: an aligned row whose ratio is below 0.05, or a control row whose ratio is as large as its aligned row.
\\ Possible because: the bound for the rotating terms or for the cubic error in the proof could be wrong, and the
\\ alignment could be an artefact of the reduction to g(u) and not a property of the four exponentials.
\\ Independent route: the sum is evaluated from the four exponentials of E directly, in logarithmic form, and
\\ never through the reduced function g(u) = 2^beta u - (2^beta + 1) + 1/u that the proof uses.
default(realprecision, 60);
rhE(z, a, b, l) = exp(z*(b+l)) - exp(z*b) - exp(z*a) + exp(z*(a-l));
rhrow(tau, L, beta, N, mult, shift) = {
  my(a = N*log(2), b, l = 1/tau, c = 2*Pi/log(2), k0, k1, P = 0, z, y0b, ratio);
  b = a + log(2);
  k0 = ceil(tau*L/c); k1 = mult*k0;
  for(k = k0, k1, z = beta + I*(c*k + shift*(k - k0)); P += rhE(z, a, b, l)/(l*z^2));
  y0b = exp(beta*a);
  ratio = abs(P)*L/y0b;
  print(if(shift == 0, "aligned", "control"), " tau=", tau, " L=", L, " beta=", beta, " N=", N, " points=", k1 - k0 + 1,
        " |P| L / y0^beta = ", precision(ratio, 6), " ", if(shift == 0, if(ratio >= 0.05, "ok", "FAIL"), ""));
  ratio
}
{
  my(cases = [[50, 42, 0.9, 12, 2], [50, 42, 1, 12, 2], [50, 42, 0.6, 12, 2], [200, 60, 0.75, 16, 3],
              [1000, 100, 0.9, 20, 2], [3, 60, 0.9, 4, 2], [1000, 42, 0.51, 20, 20]], ra, rc, bad = 0);
  for(i = 1, #cases,
    ra = rhrow(cases[i][1], cases[i][2], cases[i][3], cases[i][4], cases[i][5], 0);
    rc = rhrow(cases[i][1], cases[i][2], cases[i][3], cases[i][4], cases[i][5], sqrt(2)/7);
    if(ra < 0.05 || rc >= ra/3, bad++));
  print(#cases, " cases; ", bad, " with an aligned ratio below 0.05 or a control at a third of it or more");
}
print("done");
