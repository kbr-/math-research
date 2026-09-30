\\ Laplace split of the neck window minor into negative and high columns (1 October 2026; cycle bmd-20261001-c)
\\ Model of bmd_cube_neck_phi_generality.gp with independent random cluster series phi_s (phi_s(0) = 1) and random
\\ t'.  The window matrix has rows (j, p), j < l, p < w: sum_(q >= 1) t'_(p+q) eps^(p+q) D_j[q] on the window
\\ columns (negative 1..c, high M..M+K-c-1), with D_j[q] the reduction modulo U of y^(-q) psi_j, where psi_j is
\\ phi_j (basis "species") or the triangular combination psi_j = y^j chi_j of the phi_s (basis "dd").
\\ Exact order of det: l w^2 + 2E in these units (the conjecture's 2E; checked here).
\\ Question: is every Laplace term (c rows on the negative columns, the other K - c rows on the high columns) of
\\ order >= l w^2 + 2E?  Reports ord det, the minimum Laplace order, and the minimal orders of the negative and
\\ high minors over row sets.  Modulo 2^61 - 1 at random points (probabilistic finite check).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
rnd() = Mod(1 + random(q0 - 1), q0);
ordp(f) = if (f == 0, oo, valuation(f, 'x));
windowmat(e, l, w, cc, phi, tp, qmax) = {
  my(n = 4 * e, M = n * l, K = w * l, Y = #phi[1]);
  my(A = matrix(M, Y, a, b, 0), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++; for (r = 1, Y - i, A[row, r + i] = phi[s][r])));
  my(G = A[, 1..M]^(-1) * A, W = Y + qmax);
  my(D = vector(l, j, vector(qmax, q, my(v = vector(W));
    for (r = 1, Y, my(col = r - 1 - q); if (col >= -qmax, v[col + qmax + 1] += phi[j][r]));
    for (d = 0, M - 1, my(z = v[d + qmax + 1]); if (z != 0, for (r = 1, Y, v[r + qmax] -= z * G[d + 1, r])));
    v)));
  my(cols = concat(vector(cc, j, -j + qmax + 1), vector(K - cc, j, M + j - 1 + qmax + 1)));
  matrix(K, K, a, b, my(j = (a - 1) \ w + 1, p = (a - 1) % w);
    sum(q = 1, qmax - p, tp[p + q] * 'x^(p + q) * D[j][q][cols[b]]));
}
main() = {
  setrand(20261001);
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 2, 3], [1, 2, 2, 4], [1, 3, 2, 4], [1, 3, 2, 5], [1, 2, 3, 4], [1, 2, 3, 5]]));
  foreach (cases, cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4], n = 4 * e, K = l * w, E = assignE(l, w, cc));
    my(qmax = l * w * (w - 1) / 2 + 2 * E + 3, Y = n * l + K + qmax + 8);
    my(tp = vector(qmax + w + 2, m, rnd()));
    my(phi0 = vector(l, s, vector(Y, r, if (r == 1, Mod(1, q0), rnd()))));
    \\ dd basis: psi_j = sum_s c_(j,s) phi_s with psi_j = O(y^(j-1)) (j = 1..l), by solving on the first j-1 coefficients
    my(phidd = vector(l, j, if (j == 1, phi0[1],
      my(Mt = matrix(j - 1, j, r, s, phi0[s][r]), k = matker(Mt)[, 1]); vector(Y, r, sum(s = 1, j, k[s] * phi0[s][r])))));
    \\ basis "echelon": rows T * (dd rows), T making the type-I coefficient matrix (coefficients of y^p psi_j at
    \\ y^0..y^(K-1)) the identity, so that row k is Row(f_k) with f_k = y^(k-1) + O(y^K) in W'
    my(Fdd = matrix(K, K, a, b, my(j = (a - 1) \ w + 1, p = (a - 1) % w); if (b - 1 - p >= 0, phidd[j][b - p], 0)), Tech = Fdd^(-1));
    foreach ([["species", phi0, 1], ["dd", phidd, 1], ["echelon", phidd, Tech]], bb,
      my(C = bb[3] * windowmat(e, l, w, cc, bb[2], tp, qmax), od = ordp(matdet(C)));
      my(best = oo, bneg = oo, bhigh = oo, arg = 0);
      forsubset([K, cc], R, my(Rv = Vec(R), Rc = setminus([1..K], Rv));
        my(on = ordp(matdet(matrix(cc, cc, a, b, C[Rv[a], b]))));
        my(oh = if (K == cc, 0, ordp(matdet(matrix(K - cc, K - cc, a, b, C[Rc[a], cc + b])))));
        bneg = min(bneg, on); bhigh = min(bhigh, oh);
        if (on + oh < best, best = on + oh; arg = Rv));
      emit(Str("e=", e, " l=", l, " w=", w, " c=", cc, " [", bb[1], "]: expected l w^2 + 2E = ", l * w^2 + 2 * E,
        "; ord det = ", od, "; min Laplace term order = ", best, " (negative rows ", arg, ")",
        "; min negative minor ", bneg, ", min high minor ", bhigh));
      if (getenv("DETAIL"), forsubset([K, cc], R, my(Rv = Vec(R), Rc = setminus([1..K], Rv));
        my(on = ordp(matdet(matrix(cc, cc, a, b, C[Rv[a], b]))), oh = if (K == cc, 0, ordp(matdet(matrix(K - cc, K - cc, a, b, C[Rc[a], cc + b])))));
        if (on + oh < l * w^2 + 2 * E, emit(Str("    low term: negative rows ", Rv, " orders ", on, " + ", oh))))));
  );
}
default(parisizemax, 2000000000);
main();
quit
