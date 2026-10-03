\\ Bottom-shift proportionality (cycle bmd-20261009-aq, 9 October 2026); conventions of bmd_cherry_hankel.gp
\\ (leadcoef: entries truncated, exact at the window's least degrees).
\\ Tested statement (lem:cube-bottom-shift-proportionality): for p >= 1 and a set S of p negative integers, the
\\ coefficient of x^(A_p) eps^(B_p + e) in the cherry cross coordinate on S u [0, 2M-1-p] (e = excess of S) equals
\\ det[c(n+s)]_(s in -S, n < p) / det[c(n+s)]_(s = 1..p, n < p) times the coefficient of x^(A_p) eps^(B_p) on the window.
\\ M = 3, 4; every p; every S with excess e <= 2; three integer clusters each, so the ratio must be cluster-independent
\\ and equal to the predicted constant.
OUT = "research/results/bmd-20261009-aq/bottom-shift.txt";
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * (x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * eps^r * (x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, eps), A, x);
}
fdet(S) = { my(p = #S); matdet(matrix(p, p, i, n, cc(n - 1 - S[i]))); }
{
  my(bad = 0, tests = 0);
  for (M = 3, 4,
    my(clusters = [vector(M, i, i^2 + 1), vector(M, i, 3*i + (i > 2)), vector(M, i, 2^i + i)]);
    for (p = 1, M,
      my(A = 2*M^2 - 2*M*p + p^2 - p, B0 = p^2 - p + M, plus = [0 .. 2*M - 1 - p]);
      forsubset([p + 2, p], T,
        my(S = vecsort(apply(i -> -i, Vec(T))), e = -vecsum(S) - p*(p+1)/2);
        if (e > 2, next);
        my(pred = fdet(S) / fdet(vecsort(vector(p, i, -i))), rs = List());
        foreach(clusters, ys,
          my(w = coefat(ys, concat(vector(p, i, -p - 1 + i), plus), A, B0), v = coefat(ys, concat(S, plus), A, B0 + e));
          listput(rs, v / w));
        tests++;
        my(ok = #Set(Vec(rs)) == 1 && rs[1] == pred);
        if (!ok, bad++);
        write(OUT, "M = ", M, ", p = ", p, ", S = ", S, ", e = ", e, ": ratios ", Vec(rs), ", predicted ", pred, ", agree: ", ok))));
  write(OUT, tests, " tests, ", bad, " disagreements");
}
