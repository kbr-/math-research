\\ Least Cauchy-Binet terms of the unreduced cherry over a double root (7 October 2026; cycle bmd-20261007-zy).
\\ In the basis psi, w psi for the double root, the unreduced E-block is B K with the common Toeplitz kernel
\\ K(m, t) = c_(m-t) eps^(m-t) (m-t >= 1) and B the double-node row structure (simple c_m beta_q^m; double e_m beta^m and
\\ e_(m-1) beta^(m-1)), as the I-block.  So P_Lambda = sum_(N1, N2) +- det B[N1] det B[N2] det K[N2, Lambda minus N1], with
\\ det B[N] of valuation f*(N) (lem:cube-double-node-alternant).  Term valuation: f*(N1) + f*(N2) + w_e (Sum N2 - Sum Lambda2),
\\ N2 elementwise least.  Compares the least term over N1 with the exact window valuation, six arcs, all windows.
\\ The reduced row R = U w psi - c_1 eps psi does not factor this way; this computes the unreduced bound.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
P = 1000003;
vv(x) = if (x == 0, oo, valuation(x, P));
\\ slot weights sorted decreasingly, mu* of the double root
slots(roots, a) = { my(L = List(), mud = 0); foreach(roots, r, my(mu = a + r[1]); listput(L, mu); if (r[3], listput(L, mu); mud = mu)); [vecsort(Vec(L), , 4), mud]; }
fstar(N, sw) = { my(Ns = vecsort(N)); sum(i = 1, #Ns, Ns[i] * sw[1][i]) - sw[2]; }
least(roots, a, b, j) = {
  my(sw = slots(roots, a), M = #sw[1], Lam = [-j .. 2*M - 1 - j], pos = select(t -> t >= 0, Lam), best = oo);
  forsubset([#pos, M], S, my(N1 = vecextract(pos, Vec(S)), L2 = vecsort(setminus(Set(Lam), Set(N1))), N2 = vector(M));
    for (i = 1, M, N2[i] = max(L2[i] + 1, i - 1); if (i > 1, N2[i] = max(N2[i], N2[i - 1] + 1)));
    best = min(best, fstar(N1, sw) + fstar(N2, sw) + b * (vecsum(N2) - vecsum(L2))));
  best;
}
build(roots, a, b, cols) = {
  my(R = 80, eps0 = -P^b / (1 + P^b), n = #cols, rows = List(), rE = List());
  foreach(roots, r, my(bb = P^(a + r[1]) * r[2]);
    listput(rows, vector(n, u, my(t = cols[u]); if (t >= 0, cc(t) * bb^t, 0)));
    listput(rE, vector(n, u, my(t = cols[u]); sum(s = max(1, -t), R, cc(s) * eps0^s * if (t + s >= 0, cc(t + s) * bb^(t + s), 0))));
    if (r[3], listput(rows, vector(n, u, my(t = cols[u]); if (t >= 1, cc(t) * t * bb^(t - 1), 0)));
      listput(rE, vector(n, u, my(t = cols[u]); sum(s = max(1, -t), R, cc(s) * eps0^s * if (t + s >= 1, cc(t + s) * (t + s) * bb^(t + s - 1), 0))))));
  matconcat([Mat(Vec(rows)~); Mat(Vec(rE)~)]);
}
{
foreach([
    [[[0, 3, 1], [2, -2, 0]], 1, 2], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 1], [[[0, 3, 0], [1, -2, 1], [3, 5, 0]], 1, 1],
    [[[0, 3, 0], [1, -2, 0], [2, 5, 1]], 1, 1], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 3], [[[0, 3, 0], [2, -2, 1], [3, 5, 0]], 2, 1]], c,
  my(roots = c[1], a = c[2], b = c[3], M = #roots + 1, out = List());
  for (j = 0, M, my(cols = [-j .. 2*M - 1 - j]); listput(out, [j, vv(matdet(build(roots, a, b, cols))), least(roots, a, b, j)]));
  emit(Str("roots ", roots, ", (a,b) = (", a, ",", b, "): [j, exact, least unreduced factored term] = ", Vec(out))));
}
quit
