\\ Local root pattern at the minimal spacing of the last-step far polynomials (3 October 2026; cycle bmd-20261003-zza).
\\ For W_(b-1), e = 5..9 (saved: research/results/bmd-20261003-zw/ (e <= 6), -zy (e = 7), -zz (e = 8, 9)): the location of the
\\ closest pair of roots, and the 8 roots nearest to its midpoint, as offsets (r - mid) * e^2, sorted by modulus.  Question: does
\\ the closest pair sit at a converging location, with a converging scaled local pattern (a candidate local limit)?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 100);
default(parisizemax, 6000000000);
f3(z) = Str("(", precision(real(z), 3) * 1., ", ", precision(imag(z), 3) * 1., ")");
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz"));
{
for (e = 5, 9,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), r = polroots(W), m = #r, best = [1e9, 0, 0]);
  for (i = 1, m, for (j = i + 1, m, my(d = abs(r[i] - r[j])); if (d < best[1], best = [d, i, j])));
  my(mid = (r[best[2]] + r[best[3]]) / 2, off = vecsort(vector(m, i, (r[i] - mid) * e^2), z -> abs(z)));
  emit(Str("e=", e, ": closest pair at ", f3(r[best[2]]), " and ", f3(r[best[3]]), ", distance x e^2 = ", precision(best[1] * e^2, 4) * 1.,
    "; nearest 8 roots to the midpoint, (r - mid) e^2: ", strjoin(vector(8, i, f3(off[i])), " "))));
}
