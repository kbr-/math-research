\\ Route review (cycle kfk, 9 October 2026), Outside lead test (Toda lattice / Hirota bilinear identity).
\\ Tested translation: along the Moebius flow y -> y/(1 - t y), the Hankel determinants of the power sums satisfy a
\\ Toda-type bilinear identity Hank_k * D^2 Hank_k - (D Hank_k)^2 = c_k * Hank_(k+1) * Hank_(k-1) with a constant c_k,
\\ D = d/dt at t = 0. Exact, random integer clusters, M = 4, 5, k = 1, 2: the ratio must be the same at every cluster.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
hk(Y, k) = { my(ps = vector(2 * k + 1, n, sum(i = 1, #Y, Y[i]^(n - 1)))); matdet(matrix(k + 1, k + 1, a, b, ps[a + b - 1])); }
flow(Y, k) = { my(Z = vector(#Y, i, Y[i] / (1 - 't * Y[i]) + O('t^3))); hk(Z, k); }
{
  setrand(20261009);
  foreach([4, 5], M, for (k = 1, 2,
    my(r = vector(4));
    for (j = 1, 4, my(Y); until (#Set(Y) == M, Y = vector(M, i, random(21) - 10));
      my(H = flow(Y, k), h0 = polcoef(H, 0, 't), h1 = polcoef(H, 1, 't), h2 = 2 * polcoef(H, 2, 't));
      r[j] = (h0 * h2 - h1^2) / (hk(Y, k + 1) * hk(Y, k - 1)));
    emit(Str("M=", M, " k=", k, ": ratios ", r, "  constant: ", #Set(r) == 1))));
  quit;
}
