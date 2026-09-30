\\ Two cheap tests of the peeling route review (30 September 2026; cycle bmd-20260930-zd).
\\ (1) Hankel lead: the per-double elimination in the neck needs the Hankel minors
\\     H_r(a) = det[binom(-5/2, a + p + q)]_{0 <= p, q < r}, r = 1..4, nonzero for every shift a >= 1.  Printed:
\\     nonvanishing for a = 1..60 and the largest prime factor of each numerator and denominator
\\     (small primes indicate a product formula of hook or Pochhammer type).
\\ (2) Transport bridge: the greedy count E_(l,w)(c) (increasing pairing of columns 1..c with the c largest
\\     pole indices) equals the optimal assignment cost min sum max(0, sigma - r - 1) over all injective
\\     assignments of the columns to the multiset {0..w-1}^l, computed by dynamic programming over columns with
\\     per-index usage counts; and its increments are the integers not divisible by l.  Cases w = 2..6, l = 2..5.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
greedyE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
\\ DP: state = vector of usage counts per index r (each <= l); columns processed in order 1..cc
optE(l, w, cc) = {
  my(S = Map(), T);
  mapput(S, vector(w), 0);
  for (sg = 1, cc,
    T = Map();
    foreach (Mat(S)~, kv, my(st = kv[1], v = kv[2]);
      for (r = 0, w - 1, if (st[r + 1] < l,
        my(ns = st, nv = v + max(0, sg - r - 1)); ns[r + 1]++;
        my(old); if (!mapisdefined(T, ns, &old) || nv < old, mapput(T, ns, nv)))));
    S = T);
  vecmin(Mat(S)[, 2]);
}
nu(l, j) = j + (j - 1) \ (l - 1);
main() = {
  my(bad = 0);
  for (r = 1, 4,
    my(vals = vector(60, a, matdet(matrix(r, r, p, qq, binomial(-5/2, a + p + qq - 2)))), z = #select(x -> x == 0, vals));
    my(pm = vecmax(vector(60, a, my(f = factor(abs(numerator(vals[a])) * denominator(vals[a]))); if (#f~, vecmax(f[, 1]), 1))));
    emit(Str("Hankel r=", r, ": zero for ", z, " of a = 1..60; largest prime factor over all a: ", pm)));
  for (w = 2, 6, for (l = 2, 5,
    my(ok = 1);
    for (cc = w, w * l, if (greedyE(l, w, cc) != optE(l, w, cc), ok = 0));
    for (cc = w, w * l - 1, if (greedyE(l, w, cc + 1) - greedyE(l, w, cc) != nu(l, cc - w + 1), ok = 0));
    if (!ok, bad++);
    emit(Str("transport w=", w, " l=", l, ": greedy = optimum and increments = nu_j: ", if (ok, "yes", "NO")))));
  emit(Str("transport failures: ", bad));
}
main();
