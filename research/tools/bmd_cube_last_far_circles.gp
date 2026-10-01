\\ Circle structure of the last-step far roots in t = x/(1+x) (3 October 2026; cycle bmd-20261003-zzd).
\\ Prediction (four-circle picture): with N = n + 7/2, W(F) ~ sum_{m <= 4} A_m s^m, s = t^N, so the far roots lie near the
\\ circles |t| = |s_i|^(1/N), i = 1..4, about N roots each, nearly equally spaced in arg t.
\\ For e = 4..9 (saved polynomials): sort |t| over all roots, split into groups at gaps larger than 8 x the median consecutive
\\ gap, and report per group: size, |t| range, and the spread of consecutive angle steps (min/max of the sorted arg differences
\\ times N/(2 pi), 1 for exact equal spacing).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 3, "research/results/bmd-20261003-zl", if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", "research/results/bmd-20261003-zz")));
f4(z) = precision(z, 4) * 1.;
{
for (e = 4, 9,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), r = polroots(W), t = apply(x -> x / (1 + x), r), N = Rn(e) + 7/2);
  my(idx = vecsort(vector(#t, i, i), (i, j) -> sign(abs(t[i]) - abs(t[j]))), a = vector(#t, i, abs(t[idx[i]])));
  my(g = vector(#a - 1, i, a[i + 1] - a[i]), mg = vecsort(g)[(#g + 1) \ 2], cuts = select(i -> g[i] > 8 * mg, [1..#g]), groups = List(), s = 1);
  foreach (concat(cuts, [#a]), c, listput(groups, [s, c]); s = c + 1);
  emit(Str("e=", e, ": deg ", poldegree(W), ", N = ", N, ", groups ", #groups));
  foreach (groups, G, my(ids = vector(G[2] - G[1] + 1, i, idx[G[1] + i - 1]), args = vecsort(apply(i -> arg(t[i]), ids)));
    my(steps = if (#args > 1, concat(vector(#args - 1, i, args[i + 1] - args[i]), [2 * Pi + args[1] - args[#args]]), [2 * Pi]));
    emit(Str("  group of ", #ids, " roots: |t| in [", f4(a[G[1]]), ", ", f4(a[G[2]]), "]; angle steps x N/(2 pi): min ", f4(vecmin(steps) * N / (2 * Pi)),
      ", median ", f4(vecsort(steps)[(#steps + 1) \ 2] * N / (2 * Pi)), ", max ", f4(vecmax(steps) * N / (2 * Pi))))));
}
