\\ Route review test (9 October 2026; cycle bmd-20261009-a). Copy of bmd_window_domination.gp with:
\\ (1) a new cluster size, M = 5, columns [-5, 9] (falsification attempt for conj:cube-window-domination);
\\ (2) the dominators restricted to windows Lambda_j with |j - p| <= 1, p the non-window's number of negative
\\     indices (the "Fermi sea" bridge: a particle-hole excitation loses to the sea of the same or adjacent filling).
\\ Prints undominated counts for all windows and for the adjacent windows only. One prime, q = 1000003.
default(parisizemax, 4 * 10^9);
OUT = "research/results/bmd-20261009-a/review-tests.txt";
ADJ = 0;
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
vq(x) = if(x == 0, oo, valuation(x, q));
NU = 26;  \\ >= the largest leading order M^2 = 25
LEADONLY = 0;  \\ 1: use only the windows' leading terms (u^(B_p)) as dominators
terms(Y) = {
  my(M = #Y, cols = [-M .. 2 * M - 1], win = List(), non = List(), dropped = 0);
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), p = #select(t -> t < 0, L));
    if(p <= M,
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(D = matdet(X), sL = vecsum(L), isw = (L == [-p .. 2 * M - 1 - p]), any = 0);
      for (n = 0, NU, my(v = vq(polcoef(D, n, 'u)));
        if(v < oo, any = 1; if(isw, listput(win, [sL + n, n, v, p]), listput(non, [sL + n, n, v, L, p]))));
      if(!any, dropped++)));
  [win, non, dropped];
};
domtest(name, Y, T) = {
  my(M = #Y, win = T[1], non = T[2], fail = List(), onlyeq = 0, badeq = List());
  for (i = 1, #non, my(a = non[i], strict = 0, eqp = List());
    for (j = 1, #win, my(b = win[j]); if(ADJ && abs(b[4] - a[5]) > 1, next);
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
    ["cherry top", [1, 1 + e, 2, 5, 7]],
    ["nested cherries", [1, 1 + e, 1 + e + e^3, 3, 4]]]);
  my(Ts = vector(#cfg, i, terms(cfg[i][2])));
  foreach([0, 1], a, ADJ = a; write(OUT, if(a, "-- dominators: windows with |j - p| <= 1", "-- dominators: all window terms"));
    for (i = 1, #cfg, domtest(cfg[i][1], cfg[i][2], Ts[i])));
}
