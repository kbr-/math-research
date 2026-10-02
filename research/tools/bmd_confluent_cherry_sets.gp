\\ Confluent cherry: leading coordinate sets of the cross block (7 October 2026; cycle bmd-20261007-z).
\\ A double root at 1 and a simple root at 1+e on one level with a cluster x D~ (lambda = 3/2).  In the basis
\\ w^(-lambda+t), w = 1+T, the cross block is spanned by V_q = (1+beta_q w)^(-lambda), w^(-1) V_q and
\\ Q_q = ((1+eps/w)^(-lambda) - 1) V_q, with exact reparametrized roots eps = -e/(1+e), beta_q = x y_q/(1 - x y_q).
\\ Question: which 3M-subsets Lambda of the integers carry the least valuation along arcs x = s^a, e = s^b,
\\ y_q = c_q s^(v_q)?  The arc parameter is specialized to the prime s = P = 1000003, entries are exact rationals
\\ (the eps-series truncated at r <= R with (R+1)(a+b) > NS, so every valuation below NS is exact), and the
\\ P-adic valuation of every 3M-minor on [lo, hi] is computed.  Prints the least valuation, the sets attaining it,
\\ and the least valuation among sets touching lo or hi (a range check).  PART=2 runs M = 2, otherwise M = 3.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
CS = [1, 3, -2, 5];
P = 1000003;
runcase(M, a, b, vv, lo, hi) = {
  my(cols = [lo .. hi], n = #cols, NS = (a + b) * (3*M^2 + 3*M) + 4 * M * vecsum(vv) + 10, R = NS \ (a + b) + 1);
  my(rows = matrix(3*M, n), best = oo, arg = List(), edge = oo);
  my(eps0 = -P^b / (1 + P^b), bet = vector(M, q, my(y = CS[q] * P^vv[q]); P^a * y / (1 - P^a * y)));
  for (q = 1, M, for (u = 1, n, my(t = cols[u]);
    rows[q, u] = if (t >= 0, cc(t) * bet[q]^t, 0);
    rows[M + q, u] = if (t >= -1, cc(t + 1) * bet[q]^(t + 1), 0);
    rows[2*M + q, u] = sum(r = max(1, -t), R, cc(r) * cc(t + r) * eps0^r * bet[q]^(t + r))));
  forsubset([n, 3*M], S, my(D = matdet(vecextract(rows, "..", Vec(S))));
    if (D != 0, my(v = valuation(D, P)); if (v < NS,
      if (S[1] == 1 || S[#S] == n, edge = min(edge, v));
      if (v < best, best = v; arg = List());
      if (v == best, listput(arg, apply(u -> cols[u], Vec(S)))))));
  emit(Str("M = ", M, ", (a,b) = (", a, ",", b, "), v = ", vv, ": least ", best, " at ", Vec(arg), "; least on range edge ", edge, "; NS ", NS));
}
{
if (getenv("PART") == "2",
runcase(2, 1, 1, [0, 0], -6, 8);
runcase(2, 1, 3, [0, 0], -6, 8);
runcase(2, 3, 1, [0, 0], -6, 8);
runcase(2, 1, 1, [0, 2], -6, 8);
runcase(2, 2, 1, [0, 3], -6, 8),
runcase(3, 1, 1, [0, 0, 0], -5, 9);
runcase(3, 1, 3, [0, 1, 2], -5, 9);
runcase(3, 3, 1, [0, 1, 2], -5, 9);
runcase(3, 1, 1, [0, 1, 2], -5, 9));
}
