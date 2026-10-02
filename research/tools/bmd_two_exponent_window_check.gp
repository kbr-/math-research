\\ Two-exponent window check (7 October 2026; cycle bmd-20261007-o).  Tested statement (thm:cube-two-exponent-window):
\\ for a not an integer, a - b not an integer, b - p + 1 > 0 (b not in {1..p-1}), the (n+p)-square matrix of the
\\ coefficients of T^d..T^(d+n+p-1) of T^i (1+T)^(-a) (i < n) and T^l (1+T)^(-b) (l < p) is nonsingular.  Cases: the
\\ triple-root windows a = 7/2, b = 5, n = 3M, p = 3 (M <= 8, d <= 30); random rational cases; controls with
\\ b - a an integer in {1-n.., ...} where a combination can vanish (b = a - 1 with p = 1 is singular; b = a with p >= 1
\\ shares rows).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
co(a, k) = if (k < 0, 0, (-1)^k * prod(i = 0, k - 1, a + i) / k!);
win(a, b, n, p, d) = matrix(n + p, n + p, r, c, my(k = d + c - 1); if (r <= n, co(a, k - r + 1), co(b, k - (r - n - 1))));
{
my(bad = 0, cnt = 0);
for (M = 1, 8, for (d = 0, 30, cnt++; if (matdet(win(7/2, 5, 3 * M, 3, d)) == 0, bad++; emit(Str("SINGULAR triple M=", M, " d=", d)))));
emit(Str("triple-root windows: ", cnt, " checked, ", bad, " singular"));
setrand(20261007); cnt = 0; bad = 0;
for (t = 1, 300, my(n = 1 + random(8), p = 1 + random(4), a = (random(200) - 100) / 7 + 1/3, b = p + random(10) + 1/2 + (random(3)) / 5, d = random(15));
  if (denominator(a) == 1 || denominator(a - b) == 1, next); cnt++;
  if (matdet(win(a, b, n, p, d)) == 0, bad++; emit(Str("SINGULAR a=", a, " b=", b, " n=", n, " p=", p, " d=", d))));
emit(Str("random cases: ", cnt, " checked, ", bad, " singular"));
cnt = 0; bad = 0;
for (n = 2, 8, for (d = 0, 8, cnt++; if (matdet(win(7/2, 7/2 - 1, n, 1, d)) != 0, bad++); cnt++; if (matdet(win(7/2, 7/2, n, 2, d)) != 0, bad++)));
emit(Str("controls (a - b integer): ", cnt, " checked, ", bad, " nonsingular (expected 0)"));
}
