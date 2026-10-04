\\ Filter resonance near a collision (cycle bmd-20261009-kfq, 9 October 2026). Tested statements:
\\ (1) Hermite law: for the filtered e_1-part of row (13|2) of the triple window U_3 at its first column n = N0,
\\     A(q) = sum_l binom(m,l) (-q)^l g(l), g(l) = rho_{n-l}/rho_n * ((n-l)/n)^(lambda-1) (the Darboux phi ratio), on the
\\     resonance line q = a_2/a_1 = e^{-c1} (1 + i s y), s = sqrt(2 c2), c1, c2 the first two Taylor coefficients of
\\     log g at l = 0, satisfies A ~ (-i s)^m He_m(y) * e^{O(1)}: |A| / (s^m |He_m(y)|) stays bounded above and below
\\     away from the zeros of He_m, and |A| has m near-zeros close to the zeros x_k of He_m.
\\ (2) Whether the window degenerates there: the normalized measure of U_3(a), a = (1, q, a3), a3 = 0.5 e^{i}, along the
\\     same line, against its values off resonance.
\\ Usage: env OUT=path gp -q bmd_filter_resonance.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
lam = 3/2;
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 5, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  my(rho = vector(top + 1)); rho[1] = 1; for (n = 1, top, rho[n + 1] = rho[n] * n / (n + lam + m));
  for (r = 1, 3, my([i, j, k] = prs[r]);
    my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)));
    for (col = 1, 5, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rho[n - l + 1] * e[n - l + 1], 0))));
  U;
}
meas(U) = {
  my(best = 0); forsubset([5, 3], S, my(Sv = Vec(S)); best = max(best, abs(matdet(matrix(3, 3, r, t, U[r, Sv[t]])))));
  best / prod(r = 1, 3, sqrt(norml2(U[r, ])));
}
{
  foreach([16, 24], m,
    my(n = m * (m - 1) / 2 + m, L = lam + m);
    my(lg(l) = lngamma(n + L + 1) - lngamma(n - l + L + 1) + lngamma(n - l + 1) - lngamma(n + 1) + (lam - 1) * log((n - l) / n));
    my(c1 = psi(n + L + 1) - psi(n + 1) - (lam - 1) / n);
    my(c2 = (lg(1e-15) + lg(-1e-15) - 2 * lg(0)) / 1e-30 / 2);
    my(s = sqrt(2 * c2), He = polhermite(m) , Hs = subst(He, 'x, 'x / sqrt(2)) / 2^(m / 2)); \\ probabilists' He_m
    my(zr = vecsort(real(polroots(Hs))));
    emit(Str("m = ", m, ": n = ", n, ", c1 = ", precision(c1, 8), ", c2 = ", precision(c2, 6), ", s = ", precision(s, 6),
      ", He_m zeros in [", precision(zr[1], 5), ", ", precision(zr[#zr], 5), "]"));
    my(A(q) = sum(l = 0, m, binomial(m, l) * (-q)^l * exp(lg(l))));
    \\ (1) ratio |A| / (s^m |He_m(y)|) at midpoints between consecutive zeros, and |A| minima near each zero
    my(rat = List(), nearz = List());
    for (k = 1, #zr - 1, my(y = (zr[k] + zr[k + 1]) / 2, q = exp(-c1) * (1 + I * s * y));
      listput(rat, abs(A(q)) / (s^m * abs(subst(Hs, 'x, y)))));
    for (k = 1, #zr, my(best = [1e9, 0]);
      for (j = -40, 40, my(y = zr[k] + j * 0.0025 * (1 + abs(zr[k])), q = exp(-c1) * (1 + I * s * y), v = abs(A(q)));
        if (v < best[1], best = [v, y]));
      my(ymid = if (k < #zr, (zr[k] + zr[k + 1]) / 2, zr[k] + 1), qm = exp(-c1) * (1 + I * s * ymid));
      listput(nearz, [best[2] - zr[k], best[1] / abs(A(qm))]));
    emit(Str("  (1) per Hermite zero x_k: [x_k, offset of the scan minimum, depth]: ",
      vector(#zr, k, [precision(zr[k], 4), precision(nearz[k][1], 3), precision(nearz[k][2], 3)])));
    emit(Str("  (1) |A|/(s^m |He_m|) at midpoints: min ", precision(vecmin(Vec(rat)), 5), ", max ", precision(vecmax(Vec(rat)), 5)));
    emit(Str("  (1) near-zero offsets y - x_k: max |.| ", precision(vecmax(apply(v -> abs(v[1]), Vec(nearz))), 4),
      "; depth |A(min)|/|A(midpoint)|: min ", precision(vecmin(apply(v -> v[2], Vec(nearz))), 4), ", max ", precision(vecmax(apply(v -> v[2], Vec(nearz))), 4)));
    \\ (2) window measure along the line and off resonance
    my(a3 = 0.5 * exp(I), ms = List());
    forstep(y = zr[1] - 1, zr[#zr] + 1, (zr[#zr] - zr[1] + 2) / 300, my(q = exp(-c1) * (1 + I * s * y));
      listput(ms, [meas(U3([1, q, a3], m)), y]));
    my(V = vecsort(Vec(ms), 1));
    my(off = [meas(U3([1, exp(-c1) * (1 + I * s * 3 * sqrt(m)), a3], m)), meas(U3([1, exp(0.5 * I), a3], m)),
      meas(U3([1, 0.8, a3], m))]);
    emit(Str("  (2) measure on the line: min ", precision(V[1][1], 5), " at y = ", precision(V[1][2], 5), ", median ",
      precision(V[(#V + 1) \ 2][1], 5), ", max ", precision(V[#V][1], 5), "; m^2 * min ", precision(V[1][1] * m^2, 5)));
    emit(Str("  (2) off resonance: y = 3 sqrt(m) ", precision(off[1], 5), "; q = e^{0.5 i} ", precision(off[2], 5),
      "; q = 0.8 ", precision(off[3], 5))));
  quit;
}
