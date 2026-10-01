\\ Root geometry of the last-step far polynomials (3 October 2026; cycle bmd-20261003-zs): asymptotic-separation lead.
\\ For W_e = W_(b-1), e = 1, 2, 3 (saved): the minimal root distance, the ratio of minimal to median nearest-neighbour
\\ distance (near 0 means clustering, bounded below means lattice-like separation), the root radius range, and the minimal
\\ distance of a root to the branch points 0, -1.  A uniform separation pattern would support an asymptotic argument
\\ (scaled zeros converging to a separated limit) plus a finite check.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
{
for (e = 1, 3,
  my(W = read(Str("research/results/bmd-20261003-zl/W_last_e", e, ".gp")), r = polroots(W), m = #r, nn = vector(m));
  for (i = 1, m, nn[i] = vecmin(vector(m - 1, j, my(k = if (j < i, j, j + 1)); abs(r[i] - r[k]))));
  my(s = vecsort(nn));
  emit(Str("e=", e, ": deg ", m, ", min root distance ", precision(s[1], 10), ", median nearest-neighbour ", precision(s[(m + 1) \ 2], 10),
    ", ratio ", precision(s[1] / s[(m + 1) \ 2], 10), ", |r| in [", precision(vecmin(abs(r)), 10), ", ", precision(vecmax(abs(r)), 10),
    "], min distance to {0,-1} ", precision(vecmin(concat(abs(r), abs(r + vectorv(m, i, 1)))), 10))));
}
