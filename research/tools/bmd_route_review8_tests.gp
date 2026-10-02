\\ Tests of the route review of 8 October 2026 (cycle bmd-20261008-n) on the confluent tie window.
\\ S1 (Stohr-Voloch lead): modulo p, by lem:cube-tie-lucas-reduction, the window's rows are polynomials:
\\    T^i (1+T)^((p-5)/2), T^n (1+cT)^((p-3)/2), (1+T)^(p-3), (1+T)^((p-5)/2) (1+cT)^((p-3)/2) u, with the low part L.
\\    For random parameters (P, Q, alpha, u, c over F_p; L the part of the sum below T^d), is the Wronskian of the five
\\    terms nonzero (classical orders 0..4) or identically zero (non-classical, which would give extra vanishing)?
\\    m = 2, 3; p = the first primes >= m^2+m+5 and two larger ones; 3 random trials each.
\\ F1 (weights): the gcd over Q[k] of the weighted f-images k^(falling i) (k+lambda+1-j)_(j-i), i < 2m, j = 2m-1,
\\    lambda = 3/2 (a rational weight factor R(k) keeping every image polynomial must have denominator dividing it).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
poch(x, n) = prod(t = 0, n - 1, x + t);
ff(x, n) = prod(t = 0, n - 1, x - t);
{
setrand(20261008);
foreach([2, 3], m, my(d = m * (m - 1) / 2, ps = List(), q = m^2 + m + 5);
  while (!isprime(q), q++); listput(ps, q); listput(ps, nextprime(q + 20)); listput(ps, nextprime(q + 60));
  foreach(Vec(ps), p, my(res = List());
    for (trial = 1, 3,
      my(c = Mod(random(p - 2) + 2, p), P = sum(i = 0, 2 * m - 1, Mod(random(p), p) * 'x^i), Q = sum(i = 0, m - 1, Mod(random(p), p) * 'x^i),
         al = Mod(random(p - 1) + 1, p), u = Mod(random(p), p) * (1 + 'x) + Mod(random(p), p) * 'x,
         g1 = P * (1 + 'x)^((p - 5) / 2), g2 = Q * (1 + c * 'x)^((p - 3) / 2), g3 = al * (1 + 'x)^(p - 3),
         g4 = u * (1 + 'x)^((p - 5) / 2) * (1 + c * 'x)^((p - 3) / 2), F = g1 + g2 + g3 + g4,
         L = sum(k = 0, d - 1, polcoef(F, k) * 'x^k), gs = if (d > 0, [g1, g2, g3, g4, -L], [g1, g2, g3, g4]), k = #gs,
         Wr = matdet(matrix(k, k, i, j, my(f = gs[i]); for (t = 1, j - 1, f = deriv(f)); f)));
      listput(res, Wr != 0));
    emit(Str("S1, m = ", m, ", p = ", p, ": Wronskian of the five terms nonzero in 3 random trials: ", Vec(res)))));
foreach([2, 3, 4, 5], m, my(j = 2 * m - 1, lam = 3/2, g = 0);
  for (i = 0, 2 * m - 1, g = gcd(g, ff('k, i) * poch('k + lam + 1 - j, j - i)));
  emit(Str("F1, m = ", m, ": gcd of the weighted f-images over Q[k] = ", g)));
}
quit
