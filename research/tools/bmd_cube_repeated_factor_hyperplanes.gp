\\ Hyperplane test of the six-root repeated factor (30 September 2026); driven by
\\ bmd_cube_repeated_factor_hyperplanes.py, which defines SEEDS, A, B (line alpha, beta as rows) and
\\ G (the exponent-four factor on each line). See the driver's docstring for the tested statement.
p = 2^61 - 1;
N = 6;
L = #G;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ratroots(g) = vecsort(apply(r -> lift(r), polrootsmod(g, p)));
normc(c) = my(k = 1); while (c[k] == 0, k++); c / c[k];
\\ hyperplanes c.a = 0 through one point of S[r] on each line r <= k (plus c.1 = 0 if transl),
\\ confirmed by a point of S[l] on every further line l
hyper(S, k, transl) = {
  my(res = List(), tried = 0);
  forvec(ix = vector(k, j, [1, #S[j]]),
    tried++;
    my(M = matrix(k + transl, N, r, i, if (r <= k, Mod(A[r, i], p) + Mod(B[r, i], p) * S[r][ix[r]], Mod(1, p))));
    my(K = matker(M)); if (#K != 1, next);
    my(c = K[, 1]~, ok = 1);
    for (l = k + 1, L,
      my(ca = sum(i = 1, N, c[i] * A[l, i]), cb = sum(i = 1, N, c[i] * B[l, i]));
      if (cb == 0, ok = 0; break);
      if (!setsearch(S[l], lift(-ca / cb)), ok = 0; break));
    if (ok, listput(res, normc(c))));
  [Set(Vec(res)), tried];
}
\\ smallest integer polynomial of degree <= 2 with coefficients <= 12 in absolute value vanishing at x
recog(x) = {
  my(best = "none", bh = 13);
  forvec(v = [[-12, 12], [-12, 12], [-12, 12]],
    if ((v[1] != 0 || v[2] != 0) && vecmax(abs(v)) < bh && v[1] * x^2 + v[2] * x + v[3] == 0,
      best = v; bh = vecmax(abs(v))));
  best;
}
main() = {
  my(S = vector(L, l, ratroots(Mod(1, p) * G[l])));
  emit(Str("seeds ", SEEDS, "; F_p-rational roots of the exponent-four factor per line: ", apply(length, S)));
  my(fd = vector(L, l, my(f = factormod(G[l], p)); vecsort(vector(#f~, k, poldegree(f[k, 1])))));
  emit(Str("factor degrees per line: ", fd));
  my(Coll = vector(L, l, my(v = List());
    for (i = 1, N, for (j = i + 1, N, listput(v, lift(-Mod(A[l, i] - A[l, j], p) / (B[l, i] - B[l, j])))));
    vecsort(Vec(v))));
  setrand(20260930);
  my(Rnd = vector(L, l, vecsort(vector(16, t, random(p)))));
  foreach ([[1, 4, "T (c.1 = 0)"], [0, 5, "G (general)"]], st,
    my(tr = st[1], k = st[2]);
    my(hc = hyper(Coll, k, tr), hr = hyper(Rnd, k, tr), h = hyper(S, k, tr));
    emit(Str("stage ", st[3], ": positive control (collision parameters) finds ", #hc[1], " hyperplanes of ", hc[2],
      " candidates: ", apply(c -> lift(c), hc[1])));
    emit(Str("stage ", st[3], ": negative control (random parameters) finds ", #hr[1], " of ", hr[2]));
    emit(Str("stage ", st[3], ": exponent-four roots give ", #h[1], " hyperplanes of ", h[2], " candidates"));
    if (#h[1],
      my(H = h[1], perms = vector(720, t, numtoperm(N, t - 1)));
      for (t = 1, #H,
        my(c = H[t], stab = 0, orb = List());
        foreach (perms, s, my(d = normc(vector(N, i, c[s[i]]))); if (d == c, stab++); listput(orb, d));
        orb = Set(Vec(orb));
        emit(Str("  hyperplane ", t, ": c = ", lift(c), "; c.1 = ", lift(vecsum(c)),
          "; stabilizer order ", stab, ", S6-orbit size ", #orb, ", of which found ", #setintersect(orb, H),
          "; ratios c_i/c_1 recognized as roots of ", vector(N - 1, i, recog(c[i + 1] / c[1]))))));
  );
}
main();
