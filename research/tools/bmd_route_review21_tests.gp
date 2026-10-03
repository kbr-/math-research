\\ Goal-level review tests (cycle bmd-20261009-ai, 9 October 2026).
\\ (1) Falsification attempt for (W'') (prop:cube-cherry-step-any-set): M = 4 cluster (1, w, w^2, q), a three-root level
\\     with cube-root coefficients over a deeper root, where Hank_1 = sum (y_i - y_j)^2 vanishes at leading order;
\\     w a cube root of unity in Z_q (q = 1000003 = 1 mod 3), q-adic. Over the 900 rates (a/10, b/10), the minimizing
\\     cross coordinates (columns [-M, 2M], u-orders <= 20) are tested for (W'') (all inside one set of 2M+1 columns)
\\     and for uniqueness; same method as bmd_hankel_cancellation_wprime.gp. Control: (1, 2, 4, q).
\\ (2) Lead test (irreducibility): for M = 4..16, d = binom(M-2,2), the Gegenbauer polynomial C^(3/2)_d(x), written as
\\     x^e Q(x^2), has Q irreducible over Q of degree >= 2, or else Q(M/(2(M-1))) != 0 is checked directly; either way
\\     the Hankel modulus (cos^2 theta = M/(2(M-1))) is not a zero.
OUT = "research/results/bmd-20261009-ai/review-tests.txt";
default(parisizemax, 2 * 10^9);
default(threadsizemax, 2 * 10^8);
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
NU = 20;
coordterms(Y, L) = {
  my(M = #Y, p = #select(t -> t < 0, L));
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(D = matdet(X), sL = vecsum(L), res = List());
  for (n = 0, NU, my(z = polcoef(D, n, 'u)); if(z != 0, listput(res, [sL + n, n, valuation(z, q)])));
  [L, L == [-p .. 2 * M - 1 - p], Vec(res)];
};
export(q, NU, c, coordterms);
run(name, Y) = {
  my(M = #Y, cols = [-M .. 2 * M], subs = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]])); if(#select(t -> t < 0, L) <= M, listput(subs, L)));
  my(R = parapply(L -> coordterms(Y, L), Vec(subs)));
  my(wt = List()); foreach(R, r, if(r[2], foreach(r[3], t, listput(wt, t))));
  my(cand = select(r -> r[2] || #select(a -> !#select(b -> b[1] <= a[1] && b[2] <= a[2] && b[3] <= a[3] && (b[1] < a[1] || b[2] < a[2] || b[3] < a[3]), Vec(wt)), r[3]), R));
  my(bad = 0, three = 0, ex = List(), lead = Set());
  foreach(concat(vector(30, a, vector(30, b, [a / 10, b / 10]))), w,
    my(vals = apply(r -> vecmin(apply(t -> t[1] * w[1] + t[2] * w[2] + t[3], r[3])), cand), m = vecmin(vals));
    my(Ls = apply(i -> cand[i][1], select(i -> vals[i] == m, [1 .. #cand])));
    my(U = Set(concat(Ls)));
    lead = setunion(lead, Set(Ls));
    if (#U > 2 * M + 1, bad++; if (#Ls >= 3, three++); if (#ex < 4, listput(ex, [w, Ls]))));
  write(OUT, "(1) ", name, ": ", #cand, " candidates; (W'') violated at ", bad, " of 900 rates (", three, " with three or more leaders); leaders somewhere: ", #lead);
  foreach(ex, x, write(OUT, "     ", x));
};
{
  my(w = truncate((-1 + sqrt(-3 + O(q^30))) / 2));
  run("three-root level (1, w, w^2) over q", [1, w, w^2, q]);
  run("control (1, 2, 4, q)", [1, 2, 4, q]);
  my(res = List());
  for (M = 4, 16, my(d = binomial(M - 2, 2), G = pollegendre(d + 1, 'x)', e = d % 2);
    my(Qp = substpol(G / 'x^e, 'x^2, 'y), r = M / (2 * (M - 1)), irr = polisirreducible(Qp));
    listput(res, [M, d, poldegree(Qp, 'y), irr, subst(Qp, 'y, r) != 0]));
  write(OUT, "(2) [M, d, deg_y Q, Q irreducible, Q(M/(2(M-1))) != 0] = ", Vec(res));
}
