\\ Cherry cross block: Hankel form of the window coefficients, and the cube-root-of-unity cluster (7 October 2026;
\\ cycle bmd-20261007-t).  Conventions as in bmd_cherry_wbasis.gp.
\\ Part 1 tests L_j(y) = c_(M,j) * Vand(y)^2 * H_(M-j+1)(y), where H_m(y) = det[p_(a+b)(y)]_(a,b<m) is the power-sum
\\ Hankel determinant (= sum over m-subsets S of Vand(y_S)^2 / ... by Andreief): exact for M = 3 (symbolic), and for
\\ M = 4, 5 at three random integer points (the ratio L_j / (Vand^2 H) must be the same at all three).
\\ Part 2 takes the exact cherry join x*D ∪ {1, 1+e} with D = {1, w3, w3^2} (cube roots of unity, H_2(D) = 0) and
\\ x = e = s, the regime j = 2 of M = 3.  The reparametrized roots are eps = -e/(1+e) and b = x y/(1 - x y), exactly.
\\ It computes the s-adic valuation of the w-basis Plucker coordinate of the cross block on every 6-subset of
\\ [-5, 7], lists the minimizers, and does the same for the generic control D = {1, 2, 5}.  It also prints the Taylor
\\ minor of the pair rows of D (columns 0..2), the Taylor-dominance input of conj:cube-cherry-join-limits.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\\ variable priorities: series variables s, T above the number-field variable z
vv = [x, eps, s, T]; vz = z;
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
hank(ys, m) = matdet(matrix(m, m, a, b, sum(s = 1, #ys, ys[s]^(a + b - 2))));
vand(ys) = prod(s = 1, #ys, prod(t = s + 1, #ys, ys[t] - ys[s]));
\\ leading window coefficient, as in bmd_cherry_wbasis.gp (truncated entries, exact at the predicted degrees)
leadcoef(ys, M, j) = {
  my(A = 2*M^2 - 2*M*j + j^2 - j, B = j^2 - j + M, L = vector(2*M, u, u - 1 - j), G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * (x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * eps^r * (x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, eps), A, x);
}
{
emit("Part 1: L_j / (Vand^2 * H_(M-j+1))");
my(ys = [y1, y2, y3]);
for (j = 1, 3, emit(Str("M = 3, j = ", j, ": ", simplify(leadcoef(ys, 3, j) / (vand(ys)^2 * hank(ys, 4 - j))))));
for (M = 4, 5, for (j = 1, M,
  my(r = vector(3, z, my(ys = vector(M, s, 10 * s + random(10))); leadcoef(ys, M, j) / (vand(ys)^2 * hank(ys, M - j + 1))));
  emit(Str("M = ", M, ", j = ", j, ": ratios ", r, ", equal: ", r[1] == r[2] && r[2] == r[3]))));
}
\\ Part 2
NS = 18;
{
emit("Part 2: s-adic valuations of the cross-block Plucker coordinates, x = e = s, M = 3");
my(w3 = Mod(z, z^2 + z + 1));
foreach([[[1, w3, w3^2], "cube roots of unity"], [[1, 2, 5], "control {1,2,5}"]], cas,
  my(ys = cas[1], M = 3, eps0 = -s / (1 + s) + O(s^NS), cols = [-5 .. 7], rows = matrix(2*M, #cols), best = oo, arg = List());
  for (q = 1, M, my(b = s * ys[q] / (1 - s * ys[q]) + O(s^NS));
    for (u = 1, #cols, my(t = cols[u]);
      rows[q, u] = if (t >= 0, cc(t) * b^t, 0);
      rows[M + q, u] = sum(r = max(1, -t), NS, cc(r) * cc(t + r) * eps0^r * b^(t + r))));
  forsubset([#cols, 2*M], S, my(v = valuation(lift(matdet(vecextract(rows, "..", Vec(S)))), s));
    if (v < best, best = v; arg = List());
    if (v == best, listput(arg, apply(u -> cols[u], Vec(S)))));
  my(tay = matdet(matrix(3, 3, a, k, my(pr = [[1, 2], [1, 3], [2, 3]][a]);
    polcoef((1 + ys[pr[1]] * T)^(-lam) * (1 + ys[pr[2]] * T)^(-lam) + O(T^4), k - 1, T))));
  emit(Str(cas[2], ": H_2 = ", hank(ys, 2), ", Taylor minor of D = ", tay, ", least valuation ", best, " at ", Vec(arg))));
}
