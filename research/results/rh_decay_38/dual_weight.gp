\\ The transformed weight of the imported preprint (its equation for V_*^sharp, line 1752) for the weight
\\ W(y) = exp(-(log y)^2/(2 s^2)), V_*(y) = sqrt(y) W(y), whose Mellin transform is
\\ hat V_*(t) = s sqrt(2 pi) exp(s^2 (t + 1/2)^2 / 2):
\\   V^sharp(x) = (1/(2 pi)) int_R hat V_*(-i u) G(u) (C x)^(-i u) du,   C = (2 pi)^4 / 27,
\\   G(u) = Gamma(7/6 + i u) Gamma(5/6 + i u) / (Gamma(7/6 - i u) Gamma(5/6 - i u)).
\\ Output: x, |V^sharp(x)| for s = 1, to predict where the completed sum must decay.
default(realprecision, 38);
rhC = (2*Pi)^4/27;
\\ Trapezoid rule with step 1/200 on [-12/s, 12/s]: for an analytic integrand with Gaussian decay it converges
\\ geometrically, and it does not undersample the oscillation as a double-exponential rule with few nodes did
\\ in a first attempt (which gave values near 0.8 at x = 10^5, where the weight must be negligible).
rhF(u, x, s) = s*sqrt(2*Pi)*exp(s^2*(1/2 - I*u)^2/2) * gamma(7/6 + I*u)*gamma(5/6 + I*u)/(gamma(7/6 - I*u)*gamma(5/6 - I*u)) * exp(-I*u*log(rhC*x));
rhV(x, s) = my(h = 1/200, n = ceil(12/(s*h))); h*sum(k = -n, n, rhF(k*h, x, s))/(2*Pi);
{
  my(xs = [0.001, 0.003, 0.01, 0.03, 0.1, 0.2, 0.3, 0.5, 1, 2, 5, 10, 30, 100, 300, 1000, 3000, 10000, 100000]);
  for(i = 1, #xs, print(xs[i], " ", abs(rhV(xs[i], 1))));
}
