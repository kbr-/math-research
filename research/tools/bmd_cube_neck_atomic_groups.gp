\\ Atomic decomposition of the neck window minors (3 October 2026; cycle bmd-20261003-e)
\\ Tested statement.  For a moment sequence t'_m = sum_(k<=r) c_k lambda_k^m, T(eps/y) = sum_k c_k a_k/(y - a_k) with
\\ a_k = lambda_k eps, and modulo U = sum_s Pol_(<n) phi_s the neck row of y^p phi_s is sum_k c_k a_k^p F_(s,k),
\\ F_(s,k) = a_k phi_s/(y - a_k).  By Cauchy-Binet, det C = sum_J prod_s (prod_(k in J_s) c_k) Vand(a_(J_s)) D(J),
\\ J = (J_1..J_l) w-subsets of atoms, D(J) the window determinant of the U basis and the F_(s,k), (s,k) in J.
\\ Distinct multiplicity vectors m_k = #{s : k in J_s} give distinct monomials in c, so the vanishing of the
\\ level sums below 2E for every t' is equivalent to: for every multiplicity vector, the group sum
\\ G(m) = sum_(J of type m) prod_s Vand(lambda_(J_s)) D'(J), D' = D / eps^(lw) (rows phi_s/(y - a_k)),
\\ has eps-order >= l w (w-1)/2 + 2E_(l,w)(c).  The script reports, per multiplicity pattern, the minimal order of
\\ the single terms and the order of the group sum, against that target.  Modulo 2^61 - 1, random lambda, beta
\\ (probabilistic finite check); eps truncated at order TR, valuations below TR exact.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q0 = 2^61 - 1;
rnd() = Mod(1 + random(q0 - 1), q0);
assignE(l, w, cc) = my(rows = vecsort(concat(vector(w, r, vector(l, s, r - 1)))), top = rows[#rows - cc + 1..#rows]); sum(i = 1, cc, max(0, i - top[i] - 1));
ordp(f) = if (f == 0, oo, valuation(f, 'x));
trunc(f, TR) = f + O('x^TR);
\\ window determinant D'(J): rows y^i phi_s (i < n), phi_s/(y - a_k) for (s,k) in J; columns -cc .. L-cc-1
dprime(n, l, w, cc, phic, lam, J, TR) = {
  my(L = l * (n + w), cols = vector(L, j, j - 1 - cc), A = matrix(L, L), row = 0);
  for (s = 1, l, for (i = 0, n - 1, row++;
    for (b = 1, L, my(m = cols[b]); A[row, b] = if (m >= i, phic[s][m - i + 1], 0))));
  for (s = 1, l, foreach (J[s], k, row++; my(a = lam[k] * 'x, fa = trunc(sum(i = 0, TR, phic[s][i + 1] * a^i), TR));
    for (b = 1, L, my(m = cols[b]);
      A[row, b] = if (m < 0, trunc(fa * a^(-m - 1), TR), trunc(sum(i = m + 1, m + TR, phic[s][i + 1] * a^(i - 1 - m)), TR)))));
  matdet(A);
}
vand(v) = prod(i = 1, #v, prod(j = i + 1, #v, v[j] - v[i]));
\\ all ordered l-tuples of w-subsets of [1..u] covering every atom
tuples(u, l, w) = {
  my(subs = List()); forsubset([u, w], S, listput(subs, Vec(S)));
  my(res = List(), idx = vector(l, i, 1), N = #subs);
  forvec(v = vector(l, i, [1, N]), my(J = vector(l, s, subs[v[s]]), cov = vector(u));
    for (s = 1, l, foreach (J[s], k, cov[k]++)); if (vecmin(cov) >= 1, listput(res, [J, cov])));
  Vec(res);
}
main() = {
  setrand(20261003);
  my(cases = if (getenv("CASES"), eval(getenv("CASES")), [[1, 2, 4, 5]]), TR = if (getenv("TR"), eval(getenv("TR")), 40));
  foreach (cases, cs,
    my(e = cs[1], l = cs[2], w = cs[3], cc = cs[4], n = 4 * e, E = assignE(l, w, cc), target = l * w * (w - 1) / 2 + 2 * E);
    my(beta = vector(l, s, rnd()), phic = vector(l, s, vector(n + l * w + TR + 8, i, binomial(-7/2, i - 1) * beta[s]^(i - 1))));
    emit(Str("e=", e, " l=", l, " w=", w, " c=", cc, ": target order for group sums l w (w-1)/2 + 2E = ", target));
    for (u = if (getenv("UMIN"), eval(getenv("UMIN")), max(w, cc)), if (getenv("UMAX"), if (eval(getenv("UMAX")) == 0, cc, eval(getenv("UMAX"))), l * w),
      my(lam = vector(u, k, rnd()), T = tuples(u, l, w), groups = Map());
      foreach (T, tj, my(key = tj[2], term = prod(s = 1, l, vand(vector(w, i, lam[tj[1][s][i]]))) * dprime(n, l, w, cc, phic, lam, tj[1], TR));
        my(cur); if (mapisdefined(groups, key, &cur), mapput(groups, key, [cur[1] + term, min(cur[2], ordp(term)), cur[3] + 1]), mapput(groups, key, [term, ordp(term), 1])));
      my(M = Mat(groups));
      for (i = 1, #M~, my(g = M[i, 2]); emit(Str("  u=", u, " mult ", M[i, 1], ": ", g[3], " assignments, min single-term order ", g[2],
        ", group-sum order ", ordp(g[1]), if (ordp(g[1]) < target, "  BELOW TARGET", "")))));
  );
}
default(parisizemax, 4000000000);
main();
quit
