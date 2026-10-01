\\ Confluent window check (7 October 2026; cycle bmd-20261007-i).  Tested statement (thm:cube-confluent-window): for
\\ a not an integer, b - a not in {1-n, ..., 0} and b not in {0, -1, ..., 1-d}, the (n+1)-square matrix with rows
\\ T^i (1+T)^(-a) (0 <= i < n) and (1+T)^(-b) on the columns d, ..., d+n is nonsingular.  Checked exactly for the
\\ cherry-join cases a = 3/2 + j, b = 3 (1 <= j <= M+1, n in {2M, 2M+1}, M <= 8, every start d <= 30), and for
\\ random rational a, b; controls b = a - 1 and b = a - n + 1 (inside the excluded set) must be singular.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
co(a, k) = (-1)^k * prod(i = 0, k - 1, a + i) / k!;
win(a, b, n, d) = matrix(n + 1, n + 1, r, c, my(k = d + c - 1); if (r <= n, if (k >= r - 1, co(a, k - r + 1), 0), co(b, k)));
{
my(bad = 0, cnt = 0, ctl = 0, ctlbad = 0);
for (M = 1, 8, for (j = 1, M + 1, foreach([2 * M, 2 * M + 1], n, for (d = 0, 30,
  cnt++; if (matdet(win(3/2 + j, 3, n, d)) == 0, bad++; emit(Str("SINGULAR a=", 3/2 + j, " n=", n, " d=", d)))))));
emit(Str("cherry-join cases: ", cnt, " windows, ", bad, " singular"));
setrand(20261007); cnt = 0; bad = 0;
for (t = 1, 300, my(a = (random(200) - 100) / 7 + 1/3, b = (random(200) - 100) / 11 + 1/5, n = 1 + random(10), d = random(20));
  if (denominator(a) == 1, next); cnt++; if (matdet(win(a, b, n, d)) == 0, bad++; emit(Str("SINGULAR a=", a, " b=", b, " n=", n, " d=", d))));
emit(Str("random cases: ", cnt, " windows, ", bad, " singular"));
for (n = 2, 10, for (d = 0, 10, foreach([3/2 + n, 7/3 + n], a,
  ctl++; if (matdet(win(a, a - 1, n, d)) != 0, ctlbad++); ctl++; if (matdet(win(a, a - n + 1, n, d)) != 0, ctlbad++))));
emit(Str("controls b = a - 1, a - n + 1: ", ctl, " windows, ", ctlbad, " nonsingular (expected 0)"));
}
