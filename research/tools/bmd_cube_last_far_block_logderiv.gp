\\ Block log-derivative margins of the last-step far polynomial (3 October 2026; cycle bmd-20261003-zzp).
\\ Tested statement (lem:far-logderivative-criterion). Split P = A + t^c B (A = P mod t^c). Every zero tau of P with
\\ A(tau)B(tau) != 0 satisfies tau P'(tau) = A(tau) (tau A'/A - tau B'/B - c), so it is simple unless tau(A'/A - B'/B) = c.
\\ For a long Newton edge [m1, m2] of P(t) = (1-t)^d W(t/(1-t)) (W = saved W_(b-1)) with radius r = exp(-slope), cut
\\ c = floor((m1+m2)/2), the a priori sufficient condition on the circle |t| = r is
\\   rho := (sup |tA'/A - m1| + sup |tB'/B - (m2 - c)|) / (m2 - m1) < 1,
\\ (then every zero of P where both deviations stay below their sups is simple). We report rho on a grid of 2 deg P points
\\ of the circle and of the two circles r exp(+-pi/L) bounding the band of the edge's roots, for e = 4..11, and, for e <= 5,
\\ the same deviations at the actual roots nearest to each circle. Falsifier: rho >= 1 on a long edge.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
default(realprecision, 120);
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", if (e <= 9, "research/results/bmd-20261003-zz", "research/results/bmd-20261003-zzb")));
hull(pts) = {
  my(H = List());
  foreach (pts, p, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (p[1] - H[#H][1]) <= (p[2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H)); listput(H, p));
  Vec(H);
}
\\ deviations at a point t: [|tA'/A - m1|, |tB'/B - (m2 - c)|]
devs(A, dA, B, dB, t, m1, m2c) = [abs(t * subst(dA, 't, t) / subst(A, 't, t) - m1), abs(t * subst(dB, 't, t) / subst(B, 't, t) - m2c)];
{
for (e = 4, 11,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), d = poldegree(W), P = numerator(subst(W, 'x, 't / (1 - 't)) * (1 - 't)^d), D = poldegree(P), Nn = e * (2 * e - 1) + 7/2);
  my(pts = select(p -> p != 0, vector(D + 1, j, my(cc = polcoef(P, j - 1, 't)); if (cc, [j - 1, log(abs(cc))], 0))));
  my(H = hull(pts), edges = List());
  for (i = 1, #H - 1, my(L = H[i + 1][1] - H[i][1]); if (L >= Nn / 2, listput(edges, [H[i][1], H[i + 1][1], -(H[i + 1][2] - H[i][2]) / L])));
  emit(Str("e=", e, ": deg P = ", D, ", N = ", Nn, ", long edges [m1, m2] = ", apply(v -> [v[1], v[2]], Vec(edges))));
  my(Pr = P * 1.);
  my(R = if (e <= 5, polroots(Pr), []));
  for (i = 1, #edges,
    my(m1 = edges[i][1], m2 = edges[i][2], u = edges[i][3], L = m2 - m1, c = (m1 + m2) \ 2, A = Pr % 't^c, B = Pr \ 't^c, dA = deriv(A, 't), dB = deriv(B, 't), K = 2 * D);
    my(res = vector(3), j = 0);
    foreach ([-1, 0, 1], s,
      my(r = exp(u + s * Pi / L), sa = 0., sb = 0.);
      for (k = 0, K - 1, my(t = r * exp(2 * Pi * I * (k + 1/2) / K), v = devs(A, dA, B, dB, t, m1, m2 - c)); sa = max(sa, v[1]); sb = max(sb, v[2]));
      j++; res[j] = [precision(sa, 4) * 1., precision(sb, 4) * 1., precision((sa + sb) / L, 4) * 1.]);
    my(rootline = "");
    if (#R,
      my(lo = u - Pi / L, hi = u + Pi / L, sel = select(z -> abs(z) > 0 && log(abs(z)) >= lo && log(abs(z)) <= hi, R), worst = 0., fail = 0);
      foreach (sel, z, my(v = devs(A, dA, B, dB, z, m1, m2 - c), q = abs(z * (subst(dA, 't, z) / subst(A, 't, z) - subst(dB, 't, z) / subst(B, 't, z)) - c) / L); worst = max(worst, (v[1] + v[2]) / L); if (q < 1/2, fail++));
      rootline = Str("; roots in band ", #sel, ", max (devA+devB)/L at roots ", precision(worst, 4) * 1., ", roots with |tau(A'/A-B'/B)-c| < L/2: ", fail));
    emit(Str("  edge ", i, ": [", m1, ", ", m2, "], L = ", L, ", e*u = ", precision(e * u, 4) * 1., ", cut ", c, "; [supA, supB, rho] on circles r e^(-pi/L), r, r e^(pi/L): ", res, rootline)));
);
}
