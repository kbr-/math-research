\\ Local root pattern at the minimal spacing, e = 10, 11 (3 October 2026; cycle bmd-20261003-zzb).
\\ Same measurement as bmd_cube_last_far_local_pattern.gp (closest pair of roots of W_(b-1), 8 nearest roots to its midpoint
\\ scaled by e^2) on research/results/bmd-20261003-zzb/W_last_e10.gp, e11.gp, with all roots from polroots; plus the prediction
\\ of conj:cube-last-far-two-term-law: half-spacing h_e e^2 = pi |x_e(1+x_e)| e^2/(n+7/2) at x_e = Re(midpoint), and e^2 * 2h_e.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 100);
default(parisizemax, 6000000000);
Rn(n) = n * (2 * n - 1);
f4(z) = Str("(", precision(real(z), 4) * 1., ", ", precision(imag(z), 4) * 1., ")");
{
for (e = 10, 11,
  my(W = read(Str("research/results/bmd-20261003-zzb/W_last_e", e, ".gp")), r = polroots(W), m = #r, best = [1e9, 0, 0], N = Rn(e) + 7/2);
  for (i = 1, m, for (j = i + 1, m, my(d = abs(r[i] - r[j])); if (d < best[1], best = [d, i, j])));
  my(mid = (r[best[2]] + r[best[3]]) / 2, off = vecsort(vector(m, i, (r[i] - mid) * e^2), z -> abs(z)), xe = real(mid), h = Pi * abs(xe * (1 + xe)) / N);
  emit(Str("e=", e, ": closest pair at ", f4(r[best[2]]), " and ", f4(r[best[3]]), ", distance x e^2 = ", precision(best[1] * e^2, 5) * 1.,
    "; nearest 8 roots to the midpoint, (r - mid) e^2: ", strjoin(vector(8, i, f4(off[i])), " "),
    "; formula h_e e^2 = ", precision(h * e^2, 5) * 1., ", e^2 x 2h_e = ", precision(2 * h * e^2, 5) * 1.)));
}
