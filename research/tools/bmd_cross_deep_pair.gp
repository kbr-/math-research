\\ Deep-pair coalescence order of the M = 4 cross coordinates (8 October 2026; cycle bmd-20261008-zm), lambda = 3/2.
\\ conj:cube-tie-cluster-penalty-sharing on all arcs needs, for every p = 1 coordinate set Lambda and every eps-order
\\ beyond its least one, a coalescence order >= 4 in the deep pair (b1 - b2): otherwise a deep enough pair (large d)
\\ makes that term undercut b(Lambda) + 2 val Vand + pi_3.  Rows as in thm:cube-cherry-lattice-splitting with
\\ beta = (2, 1, b1, b2) (the tie pair at fixed generic values, the deep pair symbolic).  For each Lambda = {-1} u
\\ (7 columns in [0, 9]) prints the multiplicity of (b1 - b2) in the eps-coefficients least+0..least+2, and the
\\ number of sets with a multiplicity below 4 beyond the least order.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
cc(n) = binomial(-3/2, n);
NE = 2; M = 4; T0 = -1; T1 = 9;
\\ Second version (same cycle): the first measured the multiplicity of (b1 - b2) at generic b1, which is the wrong
\\ quantity (it gave (4, 4, 2) for all 120 sets, but the deep arcs then showed no cap).  On the arc the deep pair is
\\ small, b = eta z, so the relevant order is the eta-valuation with z generic: BS = (2, 1, 3 eta, 5 eta).
BS = [2, 1, 3 * 'et, 5 * 'et];
mult(f) = if (f == 0, oo, valuation(f, 'et));
{
  my(nc = T1 - T0 + 1, P = matrix(2 * M, nc), bad = 0, tot = 0, hist = Map());
  for (s = 1, M, for (j = 1, nc, my(t = T0 + j - 1);
    if (t >= 0, P[s, j] = cc(t) * BS[s]^t);
    P[M + s, j] = sum(m = max(1, -t), max(1, -t) + M + NE + 1, cc(m) * 'ep^m * cc(t + m) * BS[s]^(t + m))));
  forsubset([nc - 1, 2 * M - 1], S,
    my(cols = concat([1], apply(j -> j + 1, Vec(S))), D = matdet(vecextract(P, "..", cols)));
    if (D != 0, tot++; my(lo = valuation(D, 'ep), ms = vector(NE + 1, i, mult(polcoef(D, lo + i - 1, 'ep))), key = Str(ms), old);
      if (mapisdefined(hist, key, &old), mapput(hist, key, old + 1), mapput(hist, key, 1));
      if (vecmin(ms[2 .. NE + 1]) < 4, bad++)));
  my(K = Mat(hist)); for (i = 1, matsize(K)[1], emit(Str("multiplicities (least+0, +1, +2) = ", K[i, 1], ": ", K[i, 2], " sets")));
  emit(Str("p = 1 sets {-1} u 7 of [0, 9]: ", tot, " nonzero; with an order beyond the least below 4: ", bad));
}
quit
