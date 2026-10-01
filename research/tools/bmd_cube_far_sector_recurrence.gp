\\ Recurrence test for the Cauchy sector parts (4 October 2026; route review bmd-20261004-s).
\\ A mixed row f = (1+x)^alpha x^beta satisfies x(1+x) f' = (alpha x + beta (1+x)) f, so its Taylor coefficients c_N at
\\ x = r satisfy  r(1+r)(N+1) c_(N+1) + ((1+2r)N - alpha r - beta(1+r)) c_N + (N-1-alpha-beta) c_(N-1) = 0.
\\ Tested statement: the keyhole parts I_-1(N) (and I_0 = c - I_-1) satisfy the same recurrence for N >= 2 (the Cauchy
\\ transform's ODE is inhomogeneous only by a polynomial of low degree), so the sector split is a splitting of the
\\ solution space of a second-order recurrence (Poincare-Perron). Reports max relative residuals for N = 2..NMAX at a
\\ few points r, for the j = 0 mixed row (1+x)^(-5/2) x^(-7/2) and for c as a control. Uses the hairpin code of
\\ bmd_cube_far_chain_coprime.gp (copied functions; cut along the ray from -1 pointing away from r).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 100);
brpow(y, b) = exp(b * if (arg(y) < 0, log(y) + 2 * Pi * I, log(y)));
cpow(z, a, u) = u^a * brpow(z / u, a);
taylorb(g, b, r, u1, u0, N0, N1) = { my(h = 'h, S = cpow(1 + r, g, u1) * (1 + h / (1 + r) + O(h^(N1 + 1)))^g * cpow(r, b, u0) * (1 + h / r + O(h^(N1 + 1)))^b);
  vector(N1 - N0 + 1, i, polcoef(S, N0 + i - 1, 'h)); }
loopb(g, b, r, u1, u0, N0, N1) = {
  my(rho = abs(1 + r) / 50, eps = rho / 100, F = y -> cpow(1 + y, g, u1) * cpow(y, b, u0) * vector(N1 - N0 + 1, i, (y - r)^(-(N0 + i))));
  my(Y = w -> -1 + u1 * w, wl = sqrt(rho^2 - eps^2) - I * eps, wu = sqrt(rho^2 - eps^2) + I * eps, th0 = arg(wu));
  my(low = -intnum(v = 0, 1, F(Y(wl + (1 - v) / v)) * u1 / v^2));
  my(circ = intnum(th = -th0, -(2 * Pi - th0), F(Y(rho * exp(I * th))) * u1 * I * rho * exp(I * th)));
  my(up = intnum(v = 0, 1, F(Y(wu + (1 - v) / v)) * u1 / v^2));
  (low + circ + up) / (2 * Pi * I); }
res(v, r, al, be, N0) = vecmax(vector(#v - 2, k, my(N = N0 + k); abs(r * (1 + r) * (N + 1) * v[k + 2] + ((1 + 2 * r) * N - al * r - be * (1 + r)) * v[k + 1] + (N - 1 - al - be) * v[k]) / max(abs(r * (1 + r) * (N + 1) * v[k + 2]), abs((N - 1 - al - be) * v[k]))));
{
my(al = -5/2, be = -7/2, NMAX = 30);
foreach ([1/2 + I/2, -1/2 + 3*I/5, -2 + I, 1 + 2*I], r,
  my(u1 = (-1 - r) / abs(1 + r), u0 = -r / abs(r), c = taylorb(al, be, r, u1, u0, 1, NMAX), m = loopb(al, be, r, u1, u0, 1, NMAX));
  emit(Str("r = ", r, ": max relative residual, N = 2..", NMAX - 1, ": c ", precision(res(c, r, al, be, 1), 3) * 1., "; I_-1 ", precision(res(m, r, al, be, 1), 3) * 1., "; I_0 = c - I_-1 ", precision(res(c - m, r, al, be, 1), 3) * 1.)));
}
