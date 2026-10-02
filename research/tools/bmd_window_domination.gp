\\ Window domination test (8 October 2026; cycle bmd-20261008-zz).
\\ Each u^n term of a cross coordinate P_Lambda (x = 1, eps = u) is a point (X, E, v) = (Sigma Lambda + n, n, val_q F)
\\ with arc valuation X wx + E we + v. Tested statement (window domination): every term of a non-window coordinate is
\\ dominated by some window term: X' <= X, E' <= E, v' <= v. If it holds, the windows contain a minimizer on every arc
\\ (wx, we > 0), and a non-window can tie only when equality holds in all three. Also reports terms dominated only
\\ weakly (a window term with all three equal). Columns [-M, 2M], u-orders up to NU, eta = q = 1000003.
OUT = "research/results/bmd-20261008-zz/window-domination.txt";
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
NU = 20;
LEADONLY = 0;  \\ 1: use only the windows' leading terms (u^(B_p)) as dominators
terms(Y) = {
  my(M = #Y, cols = [-M .. 2 * M], win = List(), non = List(), dropped = 0);
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), p = #select(t -> t < 0, L));
    if(p <= M,
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(D = matdet(X), sL = vecsum(L), isw = (L == [-p .. 2 * M - 1 - p]), any = 0);
      for (n = 0, NU, my(v = vq(polcoef(D, n, 'u)));
        if(v < oo, any = 1; if(isw, if(n == p * (p - 1) / 2 + p * (p + 1) / 2 + M - p || !LEADONLY, listput(win, [sL + n, n, v, p])), listput(non, [sL + n, n, v, L]))));
      if(!any, dropped++)));
  [win, non, dropped];
};
domtest(name, Y) = {
  my(M = #Y, T = terms(Y), win = T[1], non = T[2], fail = List(), onlyeq = 0, badeq = List());
  for (i = 1, #non, my(a = non[i], strict = 0, eqp = List());
    for (j = 1, #win, my(b = win[j]);
      if(b[1] <= a[1] && b[2] <= a[2] && b[3] <= a[3],
        if(b[1] == a[1] && b[2] == a[2] && b[3] == a[3], listput(eqp, b[4]), strict = 1)));
    if(!strict && #eqp == 0, listput(fail, a));
    if(!strict && #eqp > 0, onlyeq++;
      \\ allowed by (W'): Lambda inside the (2M+1)-interval of a window it ties with, i.e. [-p-1, 2M-1-p] or [-p, 2M-p]
      my(L = a[4], allowed = 0);
      for (k = 1, #eqp, my(p = eqp[k]);
        if((vecmin(L) >= -p - 1 && vecmax(L) <= 2 * M - 1 - p) || (vecmin(L) >= -p && vecmax(L) <= 2 * M - p), allowed = 1));
      if(!allowed, listput(badeq, a))));
  write(OUT, name, " M=", M, ": ", #win, " window terms, ", #non, " non-window terms, dropped coordinates ", T[3],
    "; undominated: ", #fail, "; dominated only with equality: ", onlyeq, ", of which outside the tied window's interval: ", #badeq);
  for (i = 1, min(#fail, 8), write(OUT, "   undominated: (X,E,v) = ", fail[i][1..3], " Lambda = ", fail[i][4]));
  for (i = 1, min(#badeq, 8), write(OUT, "   equality outside interval: (X,E,v) = ", badeq[i][1..3], " Lambda = ", badeq[i][4]));
};
{
  my(e = q);
  my(cfg = [
    ["cherry top", [1, 1 + e, 2, 5]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3]],
    ["two separated cherries", [1, 1 + e, 2, 2 + e^2]],
    ["tie over cherry", [2, 1, 3 * e, 3 * e + 5 * e^2]],
    ["cherry over deep cherry", [1, 1 + e, 2 * e^2, 3 * e^3]]]);
  foreach([0, 1], lo, LEADONLY = lo; write(OUT, if(lo, "-- dominators: windows' leading terms only", "-- dominators: all window terms"));
    for (i = 1, #cfg, domtest(cfg[i][1], cfg[i][2])));
}
