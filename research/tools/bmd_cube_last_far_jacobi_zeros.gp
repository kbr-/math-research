\\ Zeros of the Jacobi factor of the six-space against the far roots (3 October 2026; cycle bmd-20261003-zzc).
\\ u_1 = t^(n+k+3) P_k^(n+7/2, -k-3/2)(1-2t) (prop:cube-last-far-six-space).  For e = 6..9: the k zeros of the Jacobi factor,
\\ mapped to x = t/(1-t); their |x| and Re x range, and the distance from each to the nearest root of W_(b-1) (saved polynomials),
\\ compared with the median nearest-neighbour spacing of the far roots.  Question: do the Jacobi zeros sit on the dense chains
\\ (then strong Jacobi asymptotics give one of the two terms) or elsewhere?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
jacobi(k, al, be) = my(z = 1 - 2 * 't); sum(s = 0, k, binomial(k + al, k - s) * binomial(k + be, s) * ((z - 1) / 2)^s * ((z + 1) / 2)^(k - s));
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz"));
f4(z) = precision(z, 4) * 1.;
{
for (e = 6, 9,
  my(n = Rn(e), k = 4 * e, J = jacobi(k, n + 7/2, -k - 3/2), tz = polroots(J), xz = apply(t -> t / (1 - t), tz));
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), r = polroots(W), d = apply(z -> vecmin(abs(r - vector(#r, i, z)~)), xz));
  emit(Str("e=", e, ": Jacobi zeros in x: |x| in [", f4(vecmin(abs(xz))), ", ", f4(vecmax(abs(xz))), "], Re x in [", f4(vecmin(real(xz))), ", ", f4(vecmax(real(xz))),
    "]; distance to nearest far root x e^2: min ", f4(vecmin(d) * e^2), ", median ", f4(vecsort(d)[(#d + 1) \ 2] * e^2), ", max ", f4(vecmax(d) * e^2), " (far-root median NN x e^2 about 1.85)")));
}
