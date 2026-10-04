\\ Growth test before registering conj:cube-triple-window-collision-scaling (cycle bmd-20261009-kfs, 9 October 2026).
\\ Conjectured: m^2 * measure(U_3(a)) >= c(eps) delta^2 when the collision distance delta = |a_1 - a_2| >= C log(m)/m
\\ (other separations >= eps). Test: at delta = 2 log(m)/m (C = 2), a = (1, 1 - delta e^{i phi}, a3),
\\ phi in {0, pi/2, pi, 3pi/2}, a3 in {0.5 e^i, -0.7 + 0.2 i}, m in {16, 24, 32, 40, 56, 72}: the ratio
\\ m^2 * measure / delta^2 must stay bounded below as m grows (a decrease towards 0 refutes the form).
\\ Usage: env OUT=path gp -q bmd_collision_scaling_growth.gp
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 200);  \\ filter cancellation costs about m log10(2/delta) digits (about 90 at m = 72)
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
  my(ms = [16, 24, 32, 40, 56, 72]);
  foreach([0.5 * exp(I), -0.7 + 0.2 * I], a3, foreach([0, 1, 2, 3], j, my(phi = j * Pi / 2);
    my(v = vector(#ms, t, my(m = ms[t], dl = 2 * log(m) / m); m^2 * meas(U3([1, 1 - dl * exp(I * phi), a3], m)) / dl^2));
    emit(Str("a3 = ", precision(a3, 3), ", phi = ", j, "pi/2: m^2 * measure / delta^2 at delta = 2 log(m)/m, m = 16..72: ",
      apply(x -> precision(x, 4), v)))));
  quit;
}
