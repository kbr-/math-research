\\ Leading coefficient of the last-step far polynomial (4 October 2026; cycle bmd-20261004-a).
\\ Question: does lc(W_(b-1)) (saved primitive polynomials, e = 1..11) have prime factors only below the window
\\ max(d, 2n) < p <= 2n + 8e + 7, and what is its largest prime factor against n, d, 8e+7? Also W_(b-1)(0) and W_(b-1)(-1),
\\ whose window primes enter to the first power by the Eisenstein count. Output: largest prime of |lc|, primes of |lc| in
\\ the window, and the window primes of W(0), W(-1) with their exponents.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 3, "research/results/bmd-20261003-zl", if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", if (e <= 9, "research/results/bmd-20261003-zz", "research/results/bmd-20261003-zzb"))));
{
for (e = 1, 11,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), n = Rn(e), d = Rn(e + 2), lo = max(d, 2 * n), hi = 2 * n + 8 * e + 7);
  my(lc = abs(pollead(W)), w0 = abs(subst(W, 'x, 0)), w1 = abs(subst(W, 'x, -1)));
  my(flc = factor(lc)[, 1], P = vecmax(concat([1], flc~)), inw = select(p -> p > lo && p <= hi, flc~));
  my(win = List()); forprime (p = lo + 1, hi, listput(win, [p, valuation(w0, p), valuation(w1, p)]));
  emit(Str("e=", e, ": n=", n, ", d=", d, ", window (", lo, ", ", hi, "]; largest prime of |lc| ", P, " (8e+7 = ", 8 * e + 7, ", n+8e = ", n + 8 * e, "); lc primes in window ", inw,
    "; [p, v_p W(0), v_p W(-1)] over window primes: ", Vec(win))));
}
