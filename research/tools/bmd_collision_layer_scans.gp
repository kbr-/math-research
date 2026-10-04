\\ Collision layer of the triple window (cycle bmd-20261009-kfq, 9 October 2026, added after review). Tested statement
\\ (conj:cube-triple-window-collision-layer): there is C with m^2 * measure(U_3(a)) bounded below by a constant
\\ for m |1 - q| >= C, q = a_2/a_1, a = (1, q, a3), and the transition scales like 1/m. Radial scans q = 1 - r e^{i phi},
\\ phi in {0, pi/2, pi, 3pi/2}, a3 in {0.5 e^i, -0.7 + 0.2 i}, m in {16, 24}, m r on a grid 1..12: for each scan the
\\ smallest grid value of m r from which m^2 * measure stays >= 0.1, and m^2 * measure at m r = 4, 6, 8, 12.
\\ Usage: env OUT=path gp -q bmd_collision_layer_scans.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
lam = 3/2;
U3(a, m) = {
  my(d = m * (m - 1) / 2, N0 = d + m, top = N0 + 5, U = matrix(3, 5), prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
  my(rho = vector(top + 1)); rho[1] = 1; for (n = 1, top, rho[n + 1] = rho[n] * n / (n + lam + m));
  for (r = 1, 3, my([i, j, k] = prs[r]);
    my(e = Vec(((1 + a[i] * 'T + O('T^(top + 1))) * (1 + a[j] * 'T))^(-lam)));
    for (col = 1, 5, my(n = N0 + col - 1);
      U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rho[n - l + 1] * e[n - l + 1], 0))));
  U;
}
meas(U) = {
  my(best = 0); forsubset([5, 3], S, my(Sv = Vec(S)); best = max(best, abs(matdet(matrix(3, 3, r, t, U[r, Sv[t]])))));
  best / prod(r = 1, 3, sqrt(norml2(U[r, ])));
}
{
  my(grid = vector(45, k, 1 + (k - 1) / 4));
  foreach([16, 24], m, foreach([0.5 * exp(I), -0.7 + 0.2 * I], a3, foreach([0, 1, 2, 3], j, my(phi = j * Pi / 2);
    my(v = vector(#grid, k, meas(U3([1, 1 - grid[k] / m * exp(I * phi), a3], m)) * m^2));
    my(from = 0); forstep(k = #grid, 1, -1, if (v[k] < 0.1, from = if (k < #grid, grid[k + 1], oo); break));
    if (from == 0, from = grid[1]);
    my(at(x) = v[4 * (x - 1) + 1]);
    emit(Str("m = ", m, ", a3 = ", precision(a3, 3), ", phi = ", j, "pi/2: m^2*measure >= 0.1 from m r = ", from,
      "; at m r = 4, 6, 8, 12: ", precision(at(4), 3), ", ", precision(at(6), 3), ", ", precision(at(8), 3), ", ",
      precision(at(12), 3), "; min over m r in [1, 2]: ", precision(vecmin(v[1..5]), 3))))));
  quit;
}
