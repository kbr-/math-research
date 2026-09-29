\\ The directional two-double-root pair space (29 September 2026).
\\ Space: double roots A (exact) and B (approached by B, B+eta), simple roots k. Rows:
\\   simple pairs phi_k phi_l; (A,k): phi_A phi_k, phi_A' phi_k; (B,k): phi_B phi_k, phi_B' phi_k;
\\   (A,A): phi_A^2; (B,B): phi_B^2; (A,B) block V7 = (1+AT)^(-5/2)(1+BT)^(-7/2) T^j, j = 0..3.
\\ Tested statements (N = 5, 6; A = 1, B = 2, simple -1 and 3):
\\  (1) the rows are independent (Wronskian not identically zero);
\\  (2) the cleared numerator has degree <= (N-4)E + 2N + 4 and non-branch degree <= T_dir(N) =
\\      (N-4)E - 4N + 2 - 2 Sigma_d - (N-4) m_s (local-exponent bound; equality iff minimal). Each
\\      V7 row contributes 3 to the degree bound (prefactor degree 6 minus the S^3 at infinity); a
\\      first run with contribution j instead of 3 found the degrees 6 above that wrong bound.
\\  (3) the non-branch part is squarefree (conj:cube-pair-degeneration-simplicity for this class);
\\  (4) symbolically in N: T_conf(N) = binom(N-2,2) + 2(N-2)(N-4) + T_dir(N) (additivity of the
\\      confluent cluster degeneration: binary face, confluent neck, directional bubble).
\\ Computation mod p = 2^61-1 by interpolation, checked at two extra points. The reduction mod p of
\\ the rational numerator has at most its degree; equal degrees and squarefree mod p imply
\\ squarefree over Q.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
serpow(u, al, L) = vector(L, m, binomial(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
tx(B, t, L) = vector(L, n, t * B[n] + if (n > 1, B[n - 1], 0));  \\ multiply by (t + X)
rowsdir(A, B, sim, t, L) = {
  my(R = List(), p(c, e) = serpow(c / (1 + c * t), e, L));
  for (i = 1, #sim, for (k = i + 1, #sim, listput(R, mul(p(sim[i], -3/2), p(sim[k], -3/2), L))));
  foreach ([A, B], D, foreach (sim, k,
    listput(R, mul(p(D, -3/2), p(k, -3/2), L));
    listput(R, tx(mul(p(D, -5/2), p(k, -3/2), L), t, L))));
  listput(R, p(A, -3)); listput(R, p(B, -3));
  my(v = mul(p(A, -5/2), p(B, -7/2), L));
  for (j = 0, 3, listput(R, v); v = tx(v, t, L));
  if (#R != L, error("row count"));
  matrix(L, L, r, j, R[r][j]);
}
main() = {
  my(p = 2^61 - 1);
  foreach ([5, 6], N,
    my(R = binomial(N, 2), E = binomial(R, 2), A = 1, B = 2, sim = if (N == 5, [-1], [-1, 3]), vals = concat([A, B], sim));
    my(rk = matrank(rowsdir(A, B, sim, 3, R)));
    my(D = (N - 2) * E + 3 * R, xs = List(), ys = List(), t = 1);
    while (#xs < D + 3, t++; if (prod(c = 1, #vals, 1 + vals[c] * t) % p == 0, next);
      my(tm = Mod(t, p)); listput(xs, tm); listput(ys, matdet(rowsdir(A, B, sim, tm, R)) * prod(c = 1, #vals, (1 + vals[c] * tm)^E)));
    my(P = polinterpolate(Vec(xs)[1..D+1], Vec(ys)[1..D+1], 'z));
    if (subst(P, 'z, xs[D + 2]) != ys[D + 2] || subst(P, 'z, xs[D + 3]) != ys[D + 3], error("interpolation check"));
    if (P == 0, emit(Str("N=", N, ": rank ", rk, " of ", R, ", Wronskian identically zero")); next);
    my(P0 = P, mult = vector(#vals));
    for (c = 1, #vals, while (subst(P0, 'z, Mod(-1, p) / vals[c]) == 0, P0 = P0 / ('z + Mod(1, p) / vals[c]); mult[c]++));
    my(ms = binomial(N - 1, 2) + binomial(R - N + 1, 2));
    my(Sd = -5 * (N - 2) + binomial(2 * N - 4, 2) - 3 + binomial(binomial(N - 2, 2), 2));
    my(Tdir = (N - 4) * E - 4 * N + 2 - 2 * Sd - (N - 4) * ms);
    emit(Str("N=", N, ": rank ", rk, " of ", R, "; deg P=", poldegree(P), " (bound ", (N - 4) * E + 2 * N + 4,
      "); branch multiplicities at A, B, simple: ", mult, " (minimal ", [Sd + 4 * N - 3, Sd + 2 * N + 5, ms], ")",
      "; non-branch degree ", poldegree(P0), " (T_dir ", Tdir, "); squarefree ", poldegree(gcd(P0, deriv(P0))) == 0)));
}
additivity() = {
  my(n = 'n, R = n*(n-1)/2, E = R*(R-1)/2, q = (n-2)*(n-3)/2, ms = (n-1)*(n-2)/2 + (R-n+1)*(R-n)/2);
  my(Sd = -5*(n-2) + (2*n-4)*(2*n-5)/2 - 3 + q*(q-1)/2);
  my(Tconf = (n-3)*E + n - 2 - (Sd + 4*n - 5) - (n-2)*ms, Tdir = (n-4)*E - 4*n + 2 - 2*Sd - (n-4)*ms);
  emit(Str("symbolic T_conf - binom(n-2,2) - 2(n-2)(n-4) - T_dir = ", Tconf - q - 2*(n-2)*(n-4) - Tdir));
}
main();
additivity();
