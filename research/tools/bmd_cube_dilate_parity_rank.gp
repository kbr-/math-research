\\ Compensation on the symmetric stratum of the dilate contact equations (1 October 2026; cycle bmd-20261001-f).
\\ Equations E_k: sum_(r+s=k) f_r f_s M_rs = 0 (k = 0..R+1), f_0 = 1, M_rs = sum_(i!=j) C_ij a_i^r a_j^s, C symmetric
\\ zero-diagonal; the coefficient of f_k in E_k is 2 M_0k = 2 sum_j sigma_j a_j^k, sigma = row sums of C.
\\ Symmetric stratum: a = (b_1, -b_1, ..., b_m, -b_m), sigma_(2t-1) = sigma_(2t), sum sigma = 0.  Then M_0k = 0 for odd k,
\\ so the odd f_k are not pivots.  Solve the even E_k for the even f_k (pivots, M_0k != 0 at random points), and
\\ compute the rank of the Jacobian of the odd E_k with respect to the free odd f_k at a random point.
\\ Prediction: full rank (#odd equations) for generic C with symmetric sigma, rank 0 for parity-invariant C
\\ (C_(i'j') = C_ij under a_i -> -a_i), where every odd E_k vanishes identically.  Modulo 2^61 - 1, random points.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
rnd() = Mod(1 + random(q - 1), q);
\\ random symmetric zero-diagonal C with prescribed row sums sigma: start random, then correct with a row-sum fixing term
Cwith(N, sig) = {
  my(C = matrix(N, N));
  for (i = 1, N, for (j = i + 1, N, C[i, j] = C[j, i] = rnd()));
  \\ adjust: add x_i + x_j off the diagonal to hit the row sums: sum_(j!=i)(x_i + x_j) = (N-2) x_i + X
  my(cur = vector(N, i, sum(j = 1, N, C[i, j])), d = sig - cur);
  \\ solve (N-2) x + X 1 = d: X = sum d / (2N-2), x_i = (d_i - X)/(N-2)
  my(X = vecsum(d) / (2 * N - 2), x = vector(N, i, (d[i] - X) / (N - 2)));
  for (i = 1, N, for (j = i + 1, N, C[i, j] += x[i] + x[j]; C[j, i] = C[i, j]));
  C;
}
test(m, inv) = {
  my(N = 2 * m, R = N * (N - 1) / 2, K = R + 1, b = vector(m, t, rnd()));
  my(a = concat(vector(m, t, [b[t], -b[t]])));
  my(C);
  if (inv,
    \\ parity-invariant C: C_(i'j') = C_ij with i' the partner of i
    C = matrix(N, N); my(pr(i) = if (i % 2, i + 1, i - 1));
    for (i = 1, N, for (j = i + 1, N, if (C[i, j] == 0, my(v = rnd()); C[i, j] = C[j, i] = v; my(i2 = pr(i), j2 = pr(j)); if (i2 != j2, C[i2, j2] = C[j2, i2] = v))));
    \\ make the total row sum zero by adjusting the partner-pair entries C_(2t-1,2t)
    my(tot = sum(i = 1, N, sum(j = 1, N, C[i, j]))); C[1, 2] -= tot / 2; C[2, 1] = C[1, 2],
    my(s = vector(m, t, rnd())); s[m] = -vecsum(s[1..m - 1]); my(sig = concat(vector(m, t, [s[t], s[t]])) / 2);
    C = Cwith(N, sig));
  my(sig = vector(N, i, sum(j = 1, N, C[i, j])), pw = matrix(N, K + 1, i, r, a[i]^(r - 1)));
  my(M = matrix(K + 1, K + 1, r, s, sum(i = 1, N, sum(j = 1, N, if (i != j, C[i, j] * pw[i, r] * pw[j, s], 0)))));
  \\ unknowns: odd f's free (symbolic variables via numeric Jacobian by finite differences is not exact); use exact
  \\ polynomial arithmetic over F_q with variables x_1.. for the odd f_k
  my(nodd = (K + 1) \ 2, vars = vector(nodd, t, varhigher(Str("x", t))), f = vector(K + 1));
  f[1] = Mod(1, q); \\ f_0
  my(oddeqs = List(), E0 = M[1, 1]);
  for (k = 1, K,
    if (k % 2 == 1, f[k + 1] = vars[(k + 1) / 2]);
    my(e = sum(r = 0, k, f[r + 1] * f[k - r + 1] * M[r + 1, k - r + 1]));
    if (k % 2 == 0,
      \\ e = 2 M_0k f_k + rest with f_k unknown: solve (f_k currently 0 in the sum)
      f[k + 1] = 0; my(rest = sum(r = 1, k - 1, f[r + 1] * f[k - r + 1] * M[r + 1, k - r + 1]));
      if (M[1, k + 1] == 0, error("even pivot vanished"));
      f[k + 1] = -rest / (2 * M[1, k + 1]),
      listput(oddeqs, e)));
  \\ Jacobian of the odd equations w.r.t. the odd variables at a random point
  my(pt = vector(nodd, t, rnd()), J = matrix(#oddeqs, nodd, i, j, my(g = deriv(oddeqs[i], vars[j])); for (t = 1, nodd, g = subst(g, vars[t], pt[t])); g));
  my(vals = vector(#oddeqs, i, my(g = oddeqs[i]); for (t = 1, nodd, g = subst(g, vars[t], pt[t])); g != 0));
  emit(Str("m=", m, " N=", N, " R=", R, if (inv, " parity-invariant C", " generic C with symmetric sigma"),
    ": E_0 = ", E0 == 0, "; odd equations ", #oddeqs, ", free odd coefficients ", nodd,
    ", nonzero odd equations at a random point ", vecsum(vals), ", Jacobian rank ", matrank(J)));
}
setrand(20261001);
foreach ([3, 4], m, test(m, 0); test(m, 1));
quit
