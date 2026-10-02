\\ Collision cone valuations (7 October 2026; cycle bmd-20261007-l).  Tested statement (lem:cube-collision-cone-limit-types):
\\ for a_k = F(q^k), F(x) = (x-q^i)(x-q^j)(x-r), val r = rho, q = Q (Q-adic valuation), and k not in {i,j}:
\\ val a_k = nu(k) = min(k,i)+min(k,j)+min(k,rho) unless k = rho with cancellation; the roots with k > max(j,rho)
\\ satisfy val(a_k - F(0)) > V = i+j+rho = val F(0); if rho is an integer with j < rho, the root k = rho has
\\ val a_k = val(a_k - F(0)) = V (it sits on the level of the double root); all others have val(a_k - F(0)) = nu(k) < V.
\\ Generic leading coefficient for r (r = 3 Q^rho), so no cancellation at k = rho; one control with r = Q^rho exactly
\\ (cancellation at k = rho, where the formula must fail).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(Q = 1000003, N = 9, ok = 0, tot = 0);
foreach([[2, 4, 6, 3], [3, 7, 2, 5], [1, 2, 8, 7], [4, 6, 5, 11], [2, 5, 3, 7], [3, 6, 4, -1]], cs,
  my(i = cs[1], j = cs[2], rho = cs[3], cr = cs[4], r = cr * Q^rho, F = x -> (x - Q^i) * (x - Q^j) * (x - r), c0 = F(0), V = i + j + rho);
  for (k = 1, N, if (k == i || k == j, next);
    my(a = F(Q^k), nu = min(k, i) + min(k, j) + min(k, rho), va = valuation(a, Q), vd = valuation(a - c0, Q), inL = (k > max(j, rho)), onV = (k == rho && rho > j), good);
    good = if (inL, vd > V, if (onV, vd == V, (vd == nu) && (nu < V))); tot++; if ((va == nu) && good, ok++, emit(Str("MISMATCH i=", i, " j=", j, " rho=", rho, " k=", k, ": val a=", va, " nu=", nu, " val(a-c0)=", vd, " V=", V)))));
emit(Str("generic leading coefficient: ", ok, " of ", tot, " roots as predicted"));
my(i = 2, j = 6, rho = 4, r = Q^rho, F = x -> (x - Q^i) * (x - Q^j) * (x - r));
emit(Str("control r = Q^rho exactly (i=2, j=6, rho=4): val a_4 = ", valuation(F(Q^4), Q), " (exact zero gives +oo), nu(4) = ", 2 + 4 + 4));
}
