\\ Minimal terms of the factored cherry-over-a-double-root expansion (7 October 2026; cycle bmd-20261007-zz).
\\ Formula of lem:cube-cherry-double-lower-bound: P_Lambda = sum_(N1, N2) +- det B[N1] det B[N2] det K[N2, Lambda2], with B
\\ the double-node rows (basis psi, w psi) and K(m, t) = c_(m-t) eps^(m-t), m - t >= 1.  For each window, lists the minimal
\\ terms (N1 with N2 elementwise least, valuation W'_j), the number of them, the slots of the double root (zone: choice =
\\ the k shallowest, forced = the j deepest), and the sum of their leading coefficients modulo P, computed from exact
\\ block minors (each minor's unit part mod P) and the Laplace sign.  A zero sum means cancellation of the minimal terms.
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
cc(n) = if (n < 0, 0, binomial(-3/2, n));
ee(n) = if (n < 0, 0, binomial(-5/2, n));
P = 1000003;
vv(x) = if (x == 0, oo, valuation(x, P));
unit(x, v) = my(y = x / P^v); Mod(numerator(y), P) / Mod(denominator(y), P);
\\ B rows evaluated on an exponent list N: simple c_n beta^n, double e_n beta^n and e_(n-1) beta^(n-1)
Brows(roots, a, N) = {
  my(L = List()); foreach(roots, r, my(bb = P^(a + r[1]) * r[2]);
    if (r[3], listput(L, vector(#N, u, ee(N[u]) * bb^N[u])); listput(L, vector(#N, u, if (N[u] >= 1, ee(N[u] - 1) * bb^(N[u] - 1), 0))),
      listput(L, vector(#N, u, cc(N[u]) * bb^N[u]))));
  Mat(Vec(L)~);
}
slots(roots, a) = { my(L = List(), mud = 0); foreach(roots, r, my(mu = a + r[1]); listput(L, mu); if (r[3], listput(L, mu); mud = mu)); [vecsort(Vec(L), , 4), mud]; }
fstar(N, sw) = { my(Ns = vecsort(N)); sum(i = 1, #Ns, Ns[i] * sw[1][i]) - sw[2]; }
\\ sign of the Laplace term choosing columns S (positions in Lambda) for the first block
lsign(S, n) = { my(k = #S); (-1)^(vecsum(S) - k * (k + 1) / 2); }
{
foreach([
    [[[0, 3, 1], [2, -2, 0]], 1, 2], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 1], [[[0, 3, 0], [1, -2, 1], [3, 5, 0]], 1, 1],
    [[[0, 3, 0], [1, -2, 0], [2, 5, 1]], 1, 1], [[[0, 3, 1], [1, -2, 0], [3, 5, 0]], 1, 3], [[[0, 3, 0], [2, -2, 1], [3, 5, 0]], 2, 1]], c,
  my(roots = c[1], a = c[2], b = c[3], sw = slots(roots, a), M = #sw[1], out = List(), eps0 = -P^b / (1 + P^b));
  for (j = 1, M, my(Lam = [-j .. 2*M - 1 - j], n = #Lam, terms = List(), best = oo);
    forsubset([n, M], S, my(Sv = Vec(S), N1 = vector(M, i, Lam[Sv[i]]));
      if (vecmin(N1) < 0, next);
      my(C = select(u -> !setsearch(Set(Sv), u), [1 .. n]), L2 = vector(M, i, Lam[C[i]]), N2 = vector(M));
      for (i = 1, M, N2[i] = max(L2[i] + 1, i - 1); if (i > 1, N2[i] = max(N2[i], N2[i - 1] + 1)));
      my(T = fstar(N1, sw) + fstar(N2, sw) + b * (vecsum(N2) - vecsum(L2)));
      if (T < best, best = T; terms = List()); if (T == best, listput(terms, [Sv, N1, N2, L2])));
    my(tot = Mod(0, P));
    foreach(terms, tm, my(D1 = matdet(Brows(roots, a, tm[2])), D2 = matdet(Brows(roots, a, tm[3])));
      my(K = matrix(M, M, x, y, my(r = tm[3][x] - tm[4][y]); if (r >= 1, cc(r) * eps0^r, 0)), DK = matdet(K));
      my(prod = D1 * D2 * DK, v = vvv = vv(prod)); if (v == best, tot += lsign(tm[1], n) * unit(prod, v)));
    listput(out, [j, best, #terms, lift(tot) != 0]));
  emit(Str("roots ", roots, ", (a,b) = (", a, ",", b, "): [j, W'_j, #minimal terms, sum nonzero] = ", Vec(out))));
}
quit
