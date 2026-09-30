\\ Contact at the mark for cyclic root configurations (30 September 2026; bmd-20260930-zk).
\\ V_a = <1, z, w_ij>, w_ij^2 = (z+a_i)(z+a_j), mark P over z = oo, t = 1/z: a section is
\\ sigma(t) = c0 t + c1 + sum c_ij phi_ij(t), phi_ij = sqrt((1+a_i t)(1+a_j t)).  The script computes the vanishing
\\ orders n_0 < ... < n_(R+1) of V_a at P (echelon form of the Taylor matrix through order R+8), modulo a prime
\\ p = 1 mod N, for a = the N-th roots of unity (rotation z -> zeta z fixes the mark and permutes the roots) and for
\\ one random separated a as a control.  It reports the ramification weight sum(n_m - m) and whether some section
\\ has contact >= R+4 (the contact locus K), for N = 5..14.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
orders(a, p, L) = {
  my(N = #a, rows = List(), bc = vector(L, k, Mod(binomial(1/2, k - 1), p)));
  listput(rows, vector(L, k, Mod(k == 2, p))); listput(rows, vector(L, k, Mod(k == 1, p)));
  for (i = 1, N, for (j = i + 1, N,
    my(u = vector(L, k, bc[k] * a[i]^(k - 1)), v = vector(L, k, bc[k] * a[j]^(k - 1)));
    listput(rows, vector(L, m, sum(r = 1, m, u[r] * v[m + 1 - r])))));
  my(M = Mat(Vec(rows)~), ords = List(), n = matsize(M)[1]);
  \\ vanishing orders: row echelon by columns (lowest order first)
  my(used = vector(n));
  for (col = 1, L, my(piv = 0);
    for (r = 1, n, if (!used[r] && M[r, col] != 0, piv = r; break));
    if (piv, used[piv] = 1; listput(ords, col - 1);
      for (r = 1, n, if (r != piv && M[r, col] != 0, M[r, ] = M[r, ] - M[r, col] / M[piv, col] * M[piv, ]))));
  [Vec(ords), n - vecsum(used)];
}
main() = {
  setrand(20260930);
  for (N = 5, 14,
    my(R = binomial(N, 2), p = N * 10^9 + 1);
    while (!isprime(p), p += N);
    my(g = znprimroot(p), z = g^((p - 1) / N), roots = vector(N, i, z^(i - 1)));
    my(rnd = vector(N, i, Mod(random(p), p)));
    foreach ([["roots of unity", roots], ["random", rnd]], cs,
      my(o = orders(cs[2], p, R + 8), ords = o[1]);
      my(wt = if (#ords == R + 2, sum(m = 1, R + 2, ords[m] - (m - 1)), "incomplete"));
      emit(Str("N=", N, " R=", R, " ", cs[1], ": sections found ", #ords, " of ", R + 2, ", weight ", wt,
        ", top orders ", ords[max(1, #ords - 3)..#ords], ", contact >= R+4: ", #ords == R + 2 && ords[R + 2] >= R + 4))));
}
main();
quit
