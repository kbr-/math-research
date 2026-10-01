\\ Local test of conj:cube-last-far-two-term-law at e = 10, 11 (3 October 2026; cycle bmd-20261003-zzb).
\\ Uses W_(b-1) written by bmd_cube_last_far_two_term_test.gp (research/results/bmd-20261003-zzb/W_last_e10.gp, e11.gp).
\\ Crossing x_e: for even e the real root in (-0.5, -0.4); for odd e from the local roots at -0.455.  Neighbours: roots of the
\\ degree-40 Taylor truncation of W at x_e in y = (x - x_e) e^2, |y| < 4.  Prediction: y = i(2j+1) h_e e^2 (odd e) or 2ij h_e e^2
\\ (even e), h_e = pi |x_e(1+x_e)|/(n+7/2); reports e^2 * 2h_e (predicted limit pi/4 = 0.7854).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 120);
default(parisizemax, 6000000000);
Rn(n) = n * (2 * n - 1);
localroots(W, c, e) = { my(T = subst(W, 'x, c + 'y / e^2), P = sum(i = 0, 40, polcoef(T, i, 'y) * 'y^i)); select(z -> abs(z) < 4, polroots(P)); }
f6(z) = precision(z, 6) * 1.;
{
for (e = 10, 11,
  my(n = Rn(e), N = n + 7/2, W = read(Str("research/results/bmd-20261003-zzb/W_last_e", e, ".gp")), xe, h, loc);
  if (e % 2 == 0,
    my(rr = select(z -> z > -0.5 && z < -0.4, polrootsreal(W)));
    xe = rr[1],
    my(c = -0.455, L = localroots(W, c, e), zz = select(z -> imag(z) > 0, L), z0 = zz[1]);
    foreach (zz, z, if (imag(z) < imag(z0), z0 = z)); xe = c + real(z0) / e^2);
  h = Pi * abs(xe * (1 + xe)) / N; loc = vecsort(localroots(W, xe, e), z -> imag(z));
  emit(Str("e=", e, ": crossing x_e = ", f6(xe), "; local roots (x - x_e) e^2 with |.| < 4: ",
    strjoin(apply(z -> Str("(", f6(real(z)), ", ", f6(imag(z)), ")"), loc), " "), "; formula h_e e^2 = ", f6(h * e^2), ", e^2 x 2h_e = ", f6(2 * h * e^2))));
}
