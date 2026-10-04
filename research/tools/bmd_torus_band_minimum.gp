\\ Torus band of the triple window (cycle bmd-20261009-kfp, 9 October 2026; sub-idea s1 of the triple window uniform
\\ entry). Tested prediction: near the equal-modulus torus, where prop:cube-triple-window-uniform-large-m does not apply
\\ and the leading-order determinant is proportional to 1 + rho e^{-2S} (prop:cube-triple-window-phase), the minimum
\\ over the band of the normalized measure of U_3 (largest 3x3 minor over the product of row norms) is of order m^-2
\\ (first-order terms rescue the rank), not smaller. Parametrization: a = ((1 + x1/m) e^{i al}, (1 + x2/m) e^{i be}, 1),
\\ x1, x2 in [-4, 4], angles at distance >= 0.25 from each other and from 0 (away from collisions). Method: grid at
\\ m = 16, pattern-search refinement of the ten lowest grid points, then each minimum followed to m = 24 and 32 by the
\\ same refinement started from the previous minimizer in the scaled coordinates (x1, x2, al, be). Output: for every
\\ tracked minimum and m, the minimizer, the measure and m^2 * measure; also the band's grid median at m = 16.
\\ MODE=points (added after review): locates the predicted points of the corrected leading model, where all three
\\ rows are balanced (equal moduli of the two leading parts, filter factors (1 + z e^{c1})^m with c1 = (m+1)/n
\\ included) and the model ratio rho' = alpha1 beta3 gamma2 / (alpha2 beta1 gamma3) satisfies rho'^2 = 1 (both
\\ branch signs), by Newton's method from an angle grid, for m = 16, 24, 32, and evaluates the true measure there.
\\ Usage: env MODE=size|run|points OUT=path gp -q bmd_torus_band_minimum.gp
OUT = getenv("OUT"); MODE = getenv("MODE");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 60);
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
pt(v, m) = [(1 + v[1] / m) * exp(I * v[3]), (1 + v[2] / m) * exp(I * v[4]), 1];
admissible(v) = {
  my(al = v[3] % (2 * Pi), be = v[4] % (2 * Pi), dist(x) = min(x % (2 * Pi), 2 * Pi - x % (2 * Pi)));
  abs(v[1]) <= 4 && abs(v[2]) <= 4 && dist(al) >= 0.25 && dist(be) >= 0.25 && dist(al - be) >= 0.25;
}
f(v, m) = if (admissible(v), meas(U3(pt(v, m), m)), 10.);
refine(v0, m) = {
  my(v = v0, fv = f(v, m), h = [0.5, 0.5, 0.08, 0.08], it = 0);
  while (vecmax(h) > 1e-3 && it < 400, it++;
    my(improved = 0);
    for (c = 1, 4, foreach([1, -1], sg, my(w = v); w[c] += sg * h[c]; my(fw = f(w, m));
      if (fw < fv, v = w; fv = fw; improved = 1)));
    if (!improved, h = h / 2));
  [v, fv];
}
coef(a, i, j, k, m) = {
  my(n = m * (m - 1) / 2 + m, c1 = (m + 1) / n, z = -a[k] / a[i]);
  (1 - a[j] / a[i])^(-lam) * (1 + z * exp(c1))^m * a[i]^n;
}
model(v, m) = {
  my(a = pt(v, m), al1 = coef(a, 1, 2, 3, m), al2 = coef(a, 2, 1, 3, m), be1 = coef(a, 1, 3, 2, m),
    be3 = coef(a, 3, 1, 2, m), ga2 = coef(a, 2, 3, 1, m), ga3 = coef(a, 3, 2, 1, m), r = al1 * be3 * ga2 / (al2 * be1 * ga3));
  [log(abs(al1 / al2)), log(abs(be1 / be3)), log(abs(r)), imag(r / abs(r))];
}
newton(v0, m) = {
  my(v = v0, h = 1e-20);
  for (it = 1, 60, my(F = model(v, m)); if (normlp(F) < 1e-30, return(v));
    my(J = matrix(4, 4, r, c, my(w = v); w[c] += h; (model(w, m)[r] - F[r]) / h));
    my(st = iferr(J^-1 * F~, E, 0)); if (st == 0, return(0)); v = v - st~; if (normlp(v[1..2]) > 50, return(0)));
  if (normlp(model(v, m)) < 1e-20, v, 0);
}
{
  if (MODE == "points",
    foreach([16, 24, 32], m, my(sols = List());
      for (ia = 1, 16, for (ib = 1, 16, my(v = newton([0., 0., 2 * Pi * ia / 16 - 0.05, 2 * Pi * ib / 16 + 0.05], m));
        if (v != 0 && admissible(v), my(w = [v[1], v[2], v[3] % (2 * Pi), v[4] % (2 * Pi)]);
          if (!#select(u -> normlp(u - w) < 1e-6, Vec(sols)), listput(sols, w)))));
      emit(Str("m = ", m, ": ", #sols, " admissible predicted points (balanced, rho'^2 = 1)"));
      foreach(Vec(sols), w, my(mu = f(w, m));
        emit(Str("  x1 = ", precision(w[1], 5), ", x2 = ", precision(w[2], 5), ", al = ", precision(w[3], 6), ", be = ",
          precision(w[4], 6), ": measure ", precision(mu, 5), ", m^2 * measure ", precision(mu * m^2, 5)))));
    quit);
  if (MODE == "size",
    my(t = getabstime()); for (r = 1, 5, f([0.3 * r, -0.2 * r, 2 + 0.1 * r, 4 - 0.1 * r], 16));
    emit(Str("m = 16: ", (getabstime() - t) / 5, " ms per evaluation"));
    t = getabstime(); f([0.3, -0.2, 2, 4], 32); emit(Str("m = 32: ", getabstime() - t, " ms per evaluation")); quit);
  my(m = 16, grid = List());
  forstep(x1 = -3, 3, 1.5, forstep(x2 = -3, 3, 1.5, for (ia = 1, 12, for (ib = 1, 12,
    my(v = [x1, x2, 2 * Pi * ia / 12 - 0.1, 2 * Pi * ib / 12 + 0.1]); if (admissible(v), listput(grid, [f(v, m), v]))))));
  my(G = vecsort(Vec(grid), 1));
  emit(Str("grid at m = 16: ", #G, " admissible points; minimum ", precision(G[1][1], 5), ", median ",
    precision(G[(#G + 1) \ 2][1], 5), ", m^2 * minimum ", precision(G[1][1] * m^2, 5)));
  for (q = 1, 10, my(v = G[q][2]);
    foreach([16, 24, 32], mm, my(res = refine(v, mm)); v = res[1];
      emit(Str("start ", q, ", m = ", mm, ": x1 = ", precision(v[1], 4), ", x2 = ", precision(v[2], 4), ", al = ",
        precision(v[3] % (2 * Pi), 5), ", be = ", precision(v[4] % (2 * Pi), 5), ", measure ", precision(res[2], 5),
        ", m^2 * measure ", precision(res[2] * mm^2, 5)))));
  quit;
}
