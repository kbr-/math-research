\\ Combinatorial check (30 September 2026; bmd-20260930-zm): is the neck assignment count E_(l,w)(c) (as in
\\ bmd_cube_neck_dd_levels.gp) equal to (c^2 + S - l w^2)/2, where S is the sum of squares of the most balanced
\\ split of lw - c into l - 1 parts?  All 2 <= l <= 12, 1 <= w <= 8, w <= c <= lw.  Reports the mismatches.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
bal(r, m) = my(q = r \ m, t = r % m); t * (q + 1)^2 + (m - t) * q^2;
main() = {
  my(tot = 0, bad = List());
  for (l = 2, 12, for (w = 1, 8, for (c = w, l * w,
    tot++; if (2 * assignE(l, w, c) != c^2 + bal(l * w - c, l - 1) - l * w^2, listput(bad, [l, w, c])))));
  emit(Str("windows checked: ", tot, "; mismatches: ", #bad, if (#bad, Str(" first ", Vec(bad)[1..min(10, #bad)]), "")));
}
main();
quit
