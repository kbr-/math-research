\\ Wide support condition at Hankel cancellation (cycle bmd-20261009-ak, 9 October 2026); same candidate and
\\ least-value method as bmd_hankel_cancellation_wprime.gp and bmd_route_review21_tests.gp.
\\ Tested statement (support hypothesis of prop:cube-cherry-step-wide): along the arc with weights (wx, we), the union of
\\ the supports of all least-value cross coordinates (columns [-M, 2M]) has at most 2M + 2 elements. Reports, per tree,
\\ the rates where the union exceeds 2M + 1 (outside (W'')) and 2M + 2 (outside the wide step), with their leaders.
\\ Trees, q-adic with q = 1000081 (w a cube root of unity in Z_q): M = 3 equilateral (1, w, w^2) and (3, 2+w, 2+w^2)
\\ (all values of valuation 0, as the exact constant arc); M = 4 tie moduli (c0, 1, q, q + q^2), c0 = (1 +- 2 sqrt(-2))/3,
\\ control c0 = 2; M = 4 three-root level (1, w, w^2, q); M = 5 tie modulus (c0, 1, q, q + q^2, q + q^2 + q^3) with
\\ 4c0^2 - 2c0 + 4 = 0, control c0 = 2. Weights (a/10, b/10), 1 <= a, b <= 30.
OUT = "research/results/bmd-20261009-ak/wide-support.txt";
default(parisizemax, 4 * 10^9);
default(threadsizemax, 4 * 10^8);
\\ q = 1000081: -2, -3 and -15 are squares mod q (1000003 has no sqrt(-15)).
q = 1000081;
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
  my(n1 = 0, n2 = 0, mx = 0, ex = List());
  foreach(concat(vector(30, a, vector(30, b, [a / 10, b / 10]))), w,
    my(vals = apply(r -> vecmin(apply(t -> t[1] * w[1] + t[2] * w[2] + t[3], r[3])), cand), m = vecmin(vals));
    my(Ls = apply(i -> cand[i][1], select(i -> vals[i] == m, [1 .. #cand])), U = Set(concat(Ls)));
    mx = max(mx, #U);
    if (#U > 2 * M + 1, n1++; listput(ex, [w, #U, Ls]));
    if (#U > 2 * M + 2, n2++));
  write(OUT, name, " (M = ", M, "): ", #cand, " candidates; union > 2M+1 at ", n1, " rates, > 2M+2 at ", n2, "; largest union ", mx);
  foreach(ex, x, write(OUT, "     ", x));
};
{
  my(w = truncate((-1 + sqrt(-3 + O(q^30))) / 2), r2 = sqrt(-2 + O(q^30)), r15 = sqrt(-15 + O(q^30)));
  run("equilateral (1, w, w^2)", [1, w, w^2]);
  run("equilateral (3, 2+w, 2+w^2)", [3, 2 + w, 2 + w^2]);
  run("tie modulus (1+2sqrt(-2))/3", [truncate((1 + 2 * r2) / 3), 1, q, q + q^2]);
  run("tie modulus (1-2sqrt(-2))/3", [truncate((1 - 2 * r2) / 3), 1, q, q + q^2]);
  run("control c0 = 2, M = 4", [2, 1, q, q + q^2]);
  run("three-root level (1, w, w^2) over q", [1, w, w^2, q]);
  run("tie modulus M = 5, (1+sqrt(-15))/4", [truncate((1 + r15) / 4), 1, q, q + q^2, q + q^2 + q^3]);
  run("control c0 = 2, M = 5", [2, 1, q, q + q^2, q + q^2 + q^3]);
}
