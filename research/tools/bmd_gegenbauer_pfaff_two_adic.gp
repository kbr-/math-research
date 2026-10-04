\\ Gegenbauer lead (cycle kem, 9 October 2026): the class M = 2 mod 4 of lem:cube-hankel-gegenbauer-two-adic.
\\ There d = binom(M-2,2) = 2D is even and Q(u)/a_D = F(z) = 2F1(-D, D+3/2; 1/2; z), z = x^2 = M/(2(M-1)).
\\ Pfaff: F(z) = (1-z)^D G(w), G(w) = 2F1(-D, -D-1; 1/2; w), w = z/(z-1) = mu/(1-mu), mu = M/2 odd.
\\ Claim: the terms T_j = (-D)_j (-D-1)_j / ((1/2)_j j!) w^j of G have a unique minimal 2-adic valuation:
\\ at j = 0 when mu = 3 mod 4, at j = D otherwise.  Checks, for M = 6, 10, ..., M1 (env, default 402):
\\ (a) exact identity Q(u) = a_D (1-z)^D G(w) for M <= 30; (b) the unique minimum and where; reports exceptions.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
poch(a, n) = prod(i = 0, n - 1, a + i);
Qval(M) = { my(d = binomial(M - 2, 2), D = d \ 2, u = 2 * M / (M - 1)); sum(k = 0, D, (-1)^k * poch(3/2, d - k) / (k! * (d - 2 * k)!) * u^(D - k)); }
Gterm(D, j, w) = poch(-D, j) * poch(-D - 1, j) / (poch(1/2, j) * j!) * w^j;
{
  my(M1 = if(getenv("M1") == 0 || getenv("M1") == "", 402, eval(getenv("M1"))), bad = List(), idbad = List());
  forstep(M = 6, M1, 4,
    my(d = binomial(M - 2, 2), D = d / 2, mu = M / 2, z = M / (2 * (M - 1)), w = mu / (1 - mu));
    if(M <= 30,
      my(aD = (-1)^D * poch(3/2, d - D) / (D! * (d - 2 * D)!), G = sum(j = 0, D, Gterm(D, j, w)));
      if(Qval(M) != aD * (1 - z)^D * G, listput(idbad, M)));
    \\ incremental: T_(j+1)/T_j = (j-D)(j-D-1) w / ((j+1/2)(j+1)), so the 2-adic increment is
    \\ v(D-j) + v(D+1-j) + 1 - v(j+1) - v(mu-1)  (v(j+1/2) = -1, v(w) = -v(mu-1))
    my(t = valuation(mu - 1, 2), v = vector(D + 1), V = 0);
    for(j = 0, D - 1, v[j + 1] = V; V += valuation(D - j, 2) + valuation(D + 1 - j, 2) + 1 - valuation(j + 1, 2) - t);
    v[D + 1] = V;
    if(M <= 30 && v != vector(D + 1, j, valuation(Gterm(D, j - 1, w), 2) - valuation(Gterm(D, 0, w), 2)), listput(idbad, [M, "valuations"]));
    my(m = vecmin(v), at = select(x -> x == m, v, 1));
    my(expect = if(mu % 4 == 3, 1, D + 1));
    if(#at != 1 || at[1] != expect, listput(bad, [M, Vec(at) - vector(#at, i, 1)])));
  emit(Str("(a) identity Q = a_D (1-z)^D G(w) fails for M in ", Vec(idbad), " (M = 6..30, M = 2 mod 4)"));
  emit(Str("(b) M = 6..", M1, ", M = 2 mod 4: exceptions to the predicted unique minimum [M, minimizing j]: ", Vec(bad)));
}
quit;
