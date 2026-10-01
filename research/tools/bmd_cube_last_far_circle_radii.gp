\\ Radii of the far-root circles on the scale 1/e (3 October 2026; cycle bmd-20261003-zzg).
\\ For e = 6..9 (saved W_(b-1)): roots conforming to the four-circle law (nearest neighbour in log t, modulo 2 pi i, with
\\ |D| N/(2 pi) in [0.8, 1.25] and |Re D|/|D| < 0.3; N = n + 7/2), the values e log|t|, and a histogram on bins of width 0.25
\\ over [-4, 4].  Question: are there stable peaks in e log|t| (circles at |t| = exp(c_i/e)), as the scale count requires?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz"));
{
for (e = 6, 9,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), r = polroots(W), L = apply(x -> log(x / (1 + x)), r), N = Rn(e) + 7/2, m = #L, keep = List());
  for (i = 1, m, my(best = 1e9, D = 0);
    for (j = 1, m, if (j != i, my(d = L[j] - L[i]); d -= 2 * Pi * I * round(imag(d) / (2 * Pi)); if (abs(d) < best, best = abs(d); D = d)));
    if (abs(D) * N / (2 * Pi) >= 0.8 && abs(D) * N / (2 * Pi) <= 1.25 && abs(real(D)) / abs(D) < 0.3, listput(keep, e * real(L[i]))));
  my(h = vector(32), v = Vec(keep));
  foreach (v, y, my(b = floor((y + 4) / 0.25) + 1); if (b >= 1 && b <= 32, h[b]++));
  emit(Str("e=", e, ": conforming ", #v, "/", m, "; histogram of e log|t| on [-4,4] in steps of 0.25: ", h)));
}
