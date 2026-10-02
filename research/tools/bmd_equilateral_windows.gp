\\ Equilateral roots (cycle bmd-20261009-u, 9 October 2026); variant of bmd_window_domination_m5.gp for constant arcs.
\\ At M = 3 the lowest coefficient of the k = 1 window kernel determinant D_{0} is proportional to
\\ sum_{i<j} (y_i - y_j)^2, which vanishes at y = c + r(1, w, w^2), w^2 + w + 1 = 0, with all roots separated.
\\ Tested statements, on the constant arc at such roots (valuation 0 or oo for every coefficient):
\\  (a) conj:cube-kernel-arc-minimality at k = 1: lowest u-order of D_{j} >= that of D_{0}, j = 1..4;
\\  (b) conj:cube-window-domination: every term (X, E) = (Sigma Lambda + n, n) of a non-window cross coordinate
\\      (columns [-M, 2M-1]) is dominated by a window term (X' <= X, E' <= E; values are all 0 here);
\\      also lists, for each window, its lowest u-order, and the weights at which window Lambda_2 leads.
\\ Controls: the real triangle (1, 2, 4), where sum (y_i - y_j)^2 != 0.
OUT = "research/results/bmd-20261009-u/equilateral-windows.txt";
Zv = varhigher("zz");
Uv = 'u; Wv = varlower("ww"); W = Mod(Wv, Wv^2 + Wv + 1);
c(n) = if(n < 0, 0, binomial(-3/2, n));
NU = 12;
T1(F) = { my(d = poldegree(F, Zv)); sum(i = 0, d, polcoef(F, i, Zv) * c(i + 1) / c(i) * Zv^(i + 1)) };
lowu(D) = { my(n = 0); while(n <= NU && polcoef(D, n, 'u) == 0, n++); if(n > NU, oo, n) };
kernelorders(P, M, p, JM) = {
  my(k = M - p, NUk = NU);
  my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NUk - n, c(m) * c(n + m) * 'u^(n + m) * Zv^m), P))); vector(M, s, polcoef(r, s - 1, Zv))));
  my(kcol = vector(JM + 1, i, my(F = P * Zv^(i - 1), col = vector(M));
    for (m = 1, NUk, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, Zv) * 'u^m));
    col));
  vector(JM + 1, j, lowu(matdet(matrix(M, M, r, jj, if(jj <= p, ncol[jj][r], kcol[j][r])))));
};
run(name, Y, P) = {
  my(M = #Y, cols = [-M .. 2 * M - 1], win = List(), non = List());
  write(OUT, name, " M=", M, ":");
  write(OUT, "  k=1 (p=", M - 1, ") kernel determinants D_{j}, j = 0..4, lowest u-orders: ", kernelorders(P, M, M - 1, 4));
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]]), p = #select(t -> t < 0, L));
    if(p <= M,
      my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
        if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
          my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
      my(D = matdet(X), sL = vecsum(L), isw = (L == [-p .. 2 * M - 1 - p]));
      for (n = 0, NU, if(polcoef(D, n, 'u) != 0, if(isw, listput(win, [sL + n, n, p]), listput(non, [sL + n, n, L]))))));
  for (p = 0, M, my(t = select(x -> x[3] == p, win)); write(OUT, "  window Lambda_", p, ": lowest term (X, E) = ", if(#t, [t[1][1], t[1][2]], "none"), ", B_p = ", p^2 - p + M));
  my(fail = List());
  for (i = 1, #non, my(a = non[i], ok = 0);
    for (j = 1, #win, my(b = win[j]); if(b[1] <= a[1] && b[2] <= a[2] && (b[1] < a[1] || b[2] < a[2]), ok = 1; break));
    if(!ok, listput(fail, a)));
  write(OUT, "  ", #non, " non-window terms (orders <= ", NU, "), not strictly dominated: ", #fail);
  for (i = 1, min(#fail, 8), write(OUT, "   ", fail[i]));
};
{
  run("equilateral c = 0", [1, W, W^2], Zv^3 - 1);
  run("equilateral c = 2", [3, 2 + W, 2 + W^2], (Zv - 2)^3 - 1);
  run("control: real triangle (1, 2, 4)", [1, 2, 4], (Zv - 1) * (Zv - 2) * (Zv - 4));
}
