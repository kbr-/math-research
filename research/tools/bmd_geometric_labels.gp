\\ Geometric-label specialization (5 October 2026; cycle bmd-20261005-f).  Proof route for Delta_(n,2) != 0 mod 3 for
\\ every n: at labels 0, t, t^2, ..., t^(N-1), if the top coefficient in t of Delta has a closed form that is a 3-adic
\\ unit, nonvanishing follows for every N.  Output per N: degree in t and the factored top and bottom coefficients over Q,
\\ and the t-degree of Delta mod 3 (to compare).  Env NS.
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
mark(lab) = {
  my(N = #lab, D = N * (N - 1) / 2 + 2, bh = vector(D, j, binomial(1/2, j - 1)), M = matrix(D, D), row = 2);
  M[1, 1] = 1; M[2, 2] = 1;
  for (i = 1, N, for (j = i + 1, N, row++;
    for (kk = 1, D, M[row, kk] = sum(u = 0, kk - 1, bh[u + 1] * bh[kk - u] * lab[i]^u * lab[j]^(kk - 1 - u)))));
  matdet(M);
}
{
my(t = 't);
foreach(eval(getenv("NS")), N,
  my(t0 = getwalltime(), dl = mark(vector(N, i, if(i == 1, 0, t^(i - 1)))));
  my(top = pollead(dl), v = valuation(dl, t), bot = polcoef(dl, v), d3 = dl * Mod(1, 3), v3 = if(d3 == 0, -1, valuation(lift(d3), t)));
  if (v3 > v, emit(Str("N = ", N, ": coefficient at the mod-3 valuation t^", v3, " over Q: ", factor(polcoef(dl, v3)))));
  emit(Str("N = ", N, ": deg_t ", poldegree(dl), ", val_t ", v, "; top coefficient ", factor(top), "; bottom coefficient ", factor(bot),
    "; mod 3: ", if(d3 == 0, "identically 0", Str("deg ", poldegree(lift(d3)), ", val ", valuation(lift(d3), t))), " (", getwalltime() - t0, " ms)")));
}
quit;
