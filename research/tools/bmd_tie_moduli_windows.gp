\\ Window domination at the excluded tie moduli (cycle bmd-20261009-v, 9 October 2026); variant of
\\ bmd_window_domination.gp. Tree: a cherry above a tie over a caterpillar (cor:cube-cherry-above-caterpillar-tie),
\\ M = 4 roots y = (c0, 1, eta, eta + eta^2), eta = q = 1000003. The two excluded moduli are the roots of
\\ 3 c0^2 - 2 c0 + 3 = 0, where Hank_1(c0, 1, 0, 0) = 0; c0 = (1 +- 2 sqrt(-2))/3 lies in Z_q since -2 is a square
\\ mod q, and is used through an integer congruent to it mod q^PREC; on this tree Hank_1 then has valuation 1 (deeper roots).
\\ Tested statement (conj:cube-window-domination, restricted to Hankel-cancelling tie moduli): every u-term
\\ (X, E, v) = (Sigma Lambda + n, n, val_q [u^n] P_Lambda) of a non-window coordinate (columns [-M, 2M]) is dominated
\\ by a window term (X' <= X, E' <= E, v' <= v, not all equal). Also: for (wx, we) in a grid, whether the least
\\ arc value over all coordinates is attained by a window. Control: c0 = 2 (generic tie modulus).
OUT = "research/results/bmd-20261009-v/tie-moduli-windows.txt";
q = 1000003;
PREC = 14;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
NU = 20;
coordterms(Y, L) = {
  my(M = #Y, p = #select(t -> t < 0, L));
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(D = matdet(X), sL = vecsum(L), res = List());
  for (n = 0, NU, my(v = vq(polcoef(D, n, 'u))); if(v < oo, listput(res, [sL + n, n, v])));
  [L, p, L == [-p .. 2 * M - 1 - p], Vec(res)];
};
export(q, NU, c, vq, coordterms);
run(name, Y) = {
  my(M = #Y, cols = [-M .. 2 * M], subs = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]])); if(#select(t -> t < 0, L) <= M, listput(subs, L)));
  my(R = parapply(L -> coordterms(Y, L), Vec(subs)));
  my(win = List(), non = List());
  foreach(R, r, foreach(r[4], t, if(r[3], listput(win, concat(t, r[2])), listput(non, concat(t, [r[1]])))));
  my(hq = vq(sum(i = 1, M, sum(j = i + 1, M, (Y[i] - Y[j])^2))));
  write(OUT, name, ": M=", M, ", val_q Hank_1 = ", hq, "; ", #win, " window terms, ", #non, " non-window terms");
  for (p = 0, M, my(t = select(x -> x[4] == p, win)); write(OUT, "  window Lambda_", p, " first terms ", vector(min(3, #t), i, t[i][1..3])));
  my(fail = List());
  for (i = 1, #non, my(a = non[i], ok = 0);
    for (j = 1, #win, my(b = win[j]); if(b[1] <= a[1] && b[2] <= a[2] && b[3] <= a[3] && (b[1] < a[1] || b[2] < a[2] || b[3] < a[3]), ok = 1; break));
    if(!ok, listput(fail, a)));
  write(OUT, "  non-window terms not strictly dominated: ", #fail);
  for (i = 1, min(#fail, 10), write(OUT, "   ", fail[i]));
  my(lead = List());
  foreach(concat(vector(30, a, vector(30, b, [a / 10, b / 10]))), w,
    my(bw = oo, bn = oo, arg = 0);
    foreach(win, t, bw = min(bw, t[1] * w[1] + t[2] * w[2] + t[3]));
    foreach(non, t, my(val = t[1] * w[1] + t[2] * w[2] + t[3]); if(val < bn, bn = val; arg = t[4]));
    if(bn < bw, listput(lead, [w, bn, bw, arg])));
  write(OUT, "  weights (wx, we) in (1/10)[1..30]^2 at which a non-window is strictly least: ", #lead);
  for (i = 1, min(#lead, 15), write(OUT, "   ", lead[i]));
};
{
  my(r = sqrt(-2 + O(q^PREC)));
  my(cA = truncate((1 + 2 * r) / 3), cB = truncate((1 - 2 * r) / 3));
  run("tie modulus (1 + 2 sqrt(-2))/3", [cA, 1, q, q + q^2]);
  run("tie modulus (1 - 2 sqrt(-2))/3", [cB, 1, q, q + q^2]);
  run("control: tie modulus 2", [2, 1, q, q + q^2]);
}
