\\ Second-order separation of the two rows sharing the dominant exponential (cycle bmd-20261009-cl, 9 October 2026).
\\ Claim tested (prop:cube-triple-window-second-order-separation): for fixed distinct nonzero a with |a_1| > |a_2|, |a_3|,
\\ the rows R_12 = (12|3) and R_13 = (13|2) of U_3 (lem:cube-level-window-gegenbauer-form) satisfy, at the window,
\\   (n^2 / (m (m+1))) * [log(R_12(n+1)/R_13(n+1)) - log(R_12(n)/R_13(n))]  ->  -a_1 (a_2 - a_3) / ((a_1 - a_2)(a_1 - a_3))
\\ as m -> infinity (error O(1/m)). Prints the scaled difference at n = N0 = d + m for m = 10, 20, 40, 80 at two points,
\\ with the predicted constant. Exact rational arithmetic for the rows, then logs at 200 digits.
OUT = "research/results/bmd-20261009-cl/triple-window-second-order.txt";
default(realprecision, 200);
default(parisizemax, 4 * 10^9);
lam = 3/2;
row(a, i, j, k, m, top) = {
  my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)), rho = vector(top + 1), h);
  rho[1] = 1; for (n = 1, top, rho[n + 1] = rho[n] * n / (n + lam + m));
  h = vector(top + 1, t, rho[t] * e[t]);
  vector(2, s, my(n = top - 2 + s); sum(l = 0, m, binomial(m, l) * a[k]^l * h[n - l + 1]));
}
{
  foreach([[-5/3, 1, 2/7], [3 + 2*I, -1 + I, 1/2]], a,
    my(pred = -a[1] * (a[2] - a[3]) / ((a[1] - a[2]) * (a[1] - a[3])));
    write(OUT, "a = ", a, ": predicted ", precision(pred * 1., 8));
    foreach([10, 20, 40, 80], m, my(d = m * (m - 1) / 2, n = d + m);
      my(R12 = row(a, 1, 2, 3, m, n + 1), R13 = row(a, 1, 3, 2, m, n + 1));
      my(v = log(R12[2] / R13[2]) - log(R12[1] / R13[1]));
      write(OUT, "  m = ", m, ": scaled difference ", precision(v * n^2 / (m * (m + 1)), 8))));
}
